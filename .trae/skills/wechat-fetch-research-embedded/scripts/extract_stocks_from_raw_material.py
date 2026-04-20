#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract stock-level research info from raw_material markdown and merge into stocks_master JSON.

- Reads raw_material markdown formatted by fetch_wechat_to_raw_material.py ("## Article" blocks)
- Uses LLM (OpenAI-compatible) to:
  1) identify mentioned stocks (name/code)
  2) extract accidents/insights/key_metrics/target_valuation per stock for each article
- Maps stocks to a master list Excel (two columns: 股票代码, 股票简称)
- Merges into a JSON file following references/数据结构规范_v2.md
- Supports automatic API fallback between multiple endpoints

This script is intentionally opinionated for reliability and repeatability.
"""

import argparse
import datetime as dt
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
from openai import OpenAI


# ---------------------------
# Utilities
# ---------------------------

def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")


def write_json(path: str, obj: Any):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def load_stock_map(xls_path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Return (code_digits->name, name->code_digits)."""
    xls = pd.ExcelFile(xls_path)
    df = pd.read_excel(xls_path, sheet_name=xls.sheet_names[0])
    df = df[["股票代码", "股票简称"]].dropna()

    code_to_name = {}
    name_to_code = {}

    for _, r in df.iterrows():
        code_raw = str(r["股票代码"]).strip()
        name = str(r["股票简称"]).strip()
        if not code_raw or not name:
            continue
        m = re.match(r"^(\d{6})\.(SZ|SH)$", code_raw)
        if m:
            code = m.group(1)
            code_to_name[code] = name
            name_to_code.setdefault(name, code)

    return code_to_name, name_to_code


def board_from_code(code_digits: str) -> str:
    if code_digits.startswith("6"):
        return "SH"
    return "SZ"


def normalize_url(url: str) -> str:
    return url.replace("\\_", "_")


def compress_accident(s: str, limit: int = 60) -> str:
    s = re.sub(r"^[\s\d一二三四五六七八九十]+[、\.．)]\s*", "", s.strip())
    s = re.sub(r"[#【】]", "", s)
    s = re.sub(r"\s+", " ", s)
    if len(s) <= limit:
        return s
    return s[:40].rstrip() + "..."


@dataclass
class ArticleBlock:
    source: str
    fetched_at: str
    title: str
    date: str
    content: str


def parse_raw_material(md: str, default_date: str) -> List[ArticleBlock]:
    blocks: List[ArticleBlock] = []
    parts = re.split(r"(?m)^## Article\s*$", md)
    for part in parts[1:]:
        part = part.lstrip("\n")
        lines = part.strip("\n").split("\n")
        meta = {}
        content_lines = []
        in_meta = True
        for ln in lines:
            if in_meta and re.match(r"^(source|fetched_at|title|date):\s*", ln.strip()):
                k, v = ln.split(":", 1)
                meta[k.strip()] = v.strip()
            else:
                in_meta = False
                content_lines.append(ln)

        content = "\n".join(content_lines)
        content = re.sub(r"\n---\s*$", "", content.strip(), flags=re.S)

        source = normalize_url(meta.get("source", "").strip())
        if not source:
            continue
        blocks.append(
            ArticleBlock(
                source=source,
                fetched_at=meta.get("fetched_at", "").strip(),
                title=meta.get("title", "").strip(),
                date=meta.get("date", "").strip() or default_date,
                content=content.strip(),
            )
        )
    return blocks


# ---------------------------
# Config & API Manager
# ---------------------------

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from config.json in skill directory."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.json"
    else:
        config_path = Path(config_path)
    
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


class APIManager:
    """Manage multiple API endpoints with automatic fallback."""
    
    def __init__(self, config: Dict[str, Any]):
        self.apis = []
        
        # Primary API (火山引擎)
        if "api" in config:
            self.apis.append({
                "name": "火山引擎",
                "api_key": config["api"].get("api_key", ""),
                "base_url": config["api"].get("base_url", ""),
                "model": config["api"].get("model", "deepseek-v3-2-251201"),
                "client": None,
                "failed": False
            })
        
        # Fallback API (SiliconFlow)
        if "fallback_api" in config:
            self.apis.append({
                "name": "SiliconFlow",
                "api_key": config["fallback_api"].get("api_key", ""),
                "base_url": config["fallback_api"].get("base_url", ""),
                "model": config["fallback_api"].get("model", "Qwen/Qwen2.5-72B-Instruct"),
                "client": None,
                "failed": False
            })
        
        self.current_idx = 0
    
    def get_client_and_model(self) -> Tuple[OpenAI, str]:
        """Get current active client and model."""
        for i in range(len(self.apis)):
            idx = (self.current_idx + i) % len(self.apis)
            api = self.apis[idx]
            
            if api["failed"]:
                continue
            
            if api["client"] is None:
                kwargs = {"api_key": api["api_key"]}
                if api["base_url"]:
                    kwargs["base_url"] = api["base_url"]
                api["client"] = OpenAI(**kwargs)
            
            self.current_idx = idx
            return api["client"], api["model"]
        
        # All APIs failed, reset and try again
        for api in self.apis:
            api["failed"] = False
        return self.get_client_and_model()
    
    def mark_failed(self):
        """Mark current API as failed, switch to next."""
        old_name = self.apis[self.current_idx]["name"]
        self.apis[self.current_idx]["failed"] = True
        # Find next available
        for i in range(len(self.apis)):
            idx = (self.current_idx + i + 1) % len(self.apis)
            if not self.apis[idx]["failed"]:
                self.current_idx = idx
                break
        print(f"[API切换] {old_name} 失败 -> 切换到 {self.apis[self.current_idx]['name']}")
    
    def reset_failures(self):
        """Reset all failure flags."""
        for api in self.apis:
            api["failed"] = False


# ---------------------------
# LLM
# ---------------------------

SYSTEM_IDENTIFY = (
    "你是中文金融研报信息抽取助手。任务：从公众号文章正文中识别提到的A股个股名称/代码。\n"
    "约束：\n"
    "- 只输出 JSON（不要解释、不要 markdown）。\n"
    "- 若不确定，宁可不输出。\n"
    "- 允许输出 name 或 code（6位数字），能给 code 优先给 code。\n"
    "输出格式示例：{\"stocks\":[{\"name\":\"新雷能\",\"code\":\"300593\"}]}"
)

SYSTEM_EXTRACT = (
    "你是中文金融研报结构化抽取助手。\n"
    "你会收到：\n"
    "1) 一篇公众号文章（可能包含多只股票内容）\n"
    "2) 需要抽取的股票列表（已经映射到代码）\n"
    "请为每只股票生成一条 article 记录，字段必须符合下列 JSON Schema：\n"
    "{\n"
    "  \"items\": [\n"
    "    {\n"
    "      \"code\": \"6位数字\",\n"
    "      \"name\": \"股票简称\",\n"
    "      \"article\": {\n"
    "        \"title\": \"文章标题\",\n"
    "        \"date\": \"YYYY-MM-DD\",\n"
    "        \"source\": \"文章链接\",\n"
    "        \"accidents\": [\"事件/催化剂\"],\n"
    "        \"insights\": [\"投研观点/逻辑\"],\n"
    "        \"key_metrics\": [\"关键指标\"],\n"
    "        \"target_valuation\": [\"估值/目标市值\"]\n"
    "      }\n"
    "    }\n"
    "  ]\n"
    "}\n"
    "抽取规则：\n"
    "- accidents：只写事实事件，单条<=60字。\n"
    "- insights：保留原文或忠实改写。\n"
    "- key_metrics：只放指标/数字/市占率等。\n"
    "- target_valuation：估值、目标价、空间测算等。\n"
    "- 如果某字段无信息，输出空数组 []。\n"
    "- 只输出 JSON，不要解释。"
)


def llm_json(api_manager: APIManager, system: str, user: str, max_retries: int = 1) -> Any:
    """Call LLM and parse JSON response with automatic API fallback."""
    last_error = None
    
    for api_attempt in range(len(api_manager.apis)):
        client, model = api_manager.get_client_and_model()
        
        for retry in range(max_retries + 1):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                )
                txt = resp.choices[0].message.content.strip()
                if not txt:
                    raise ValueError("Empty response from LLM")
                
                # Clean and extract JSON
                txt = re.sub(r"^```json\s*", "", txt)
                txt = re.sub(r"^```\s*", "", txt)
                txt = re.sub(r"```\s*$", "", txt)
                
                # Find JSON boundaries
                json_start = -1
                for i, c in enumerate(txt):
                    if c in '{[':
                        json_start = i
                        break
                
                if json_start >= 0:
                    open_bracket = txt[json_start]
                    close_bracket = '}' if open_bracket == '{' else ']'
                    depth = 0
                    in_string = False
                    escape_next = False
                    json_end = -1
                    
                    for i in range(json_start, len(txt)):
                        c = txt[i]
                        if escape_next:
                            escape_next = False
                            continue
                        if c == '\\' and in_string:
                            escape_next = True
                            continue
                        if c == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        if in_string:
                            continue
                        if c == open_bracket:
                            depth += 1
                        elif c == close_bracket:
                            depth -= 1
                            if depth == 0:
                                json_end = i + 1
                                break
                    
                    if json_end > json_start:
                        txt = txt[json_start:json_end]
                
                result = json.loads(txt)
                api_manager.reset_failures()
                return result
                
            except Exception as e:
                last_error = e
                error_msg = str(e)[:200].lower()
                
                # API-level errors (timeout, connection, rate limit)
                if any(x in error_msg for x in ["timeout", "connection", "rate", "unavailable", "error"]):
                    print(f"[{api_manager.apis[api_manager.current_idx]['name']}错误] {str(e)[:100]}")
                    api_manager.mark_failed()
                    break
                else:
                    # JSON parse errors - retry
                    if retry < max_retries:
                        print(f"[JSON解析重试] {retry + 1}/{max_retries + 1}")
                        continue
                    else:
                        print(f"[JSON解析失败] {str(e)[:100]}")
                        api_manager.mark_failed()
                        break
    
    raise RuntimeError(f"所有API都无法完成请求: {last_error}")


def identify_stocks_in_article(api_manager: APIManager, article_text: str) -> List[Dict[str, str]]:
    user = f"文章正文如下（用三引号包裹）：\n\n'''\n{article_text}\n'''"
    obj = llm_json(api_manager, SYSTEM_IDENTIFY, user)
    stocks = obj.get("stocks", []) if isinstance(obj, dict) else []
    out = []
    for s in stocks:
        if not isinstance(s, dict):
            continue
        name = str(s.get("name", "")).strip()
        code = str(s.get("code", "")).strip()
        if code and re.fullmatch(r"\d{6}", code):
            out.append({"code": code, "name": name})
        elif name:
            out.append({"code": "", "name": name})
    return out


def extract_items(api_manager: APIManager, article: ArticleBlock, mapped_stocks: List[Dict[str, str]], batch_size: int = 5) -> List[Dict[str, Any]]:
    """Extract items in batches to avoid timeout on long articles."""
    all_items = []
    
    # If few stocks, process all at once
    if len(mapped_stocks) <= batch_size:
        stock_lines = "\n".join([f"- {s['name']} ({s['code']})" for s in mapped_stocks])
        user = (
            f"股票列表：\n{stock_lines}\n\n"
            f"文章链接：{article.source}\n"
            f"文章日期：{article.date}\n"
            f"文章标题（可能为空）：{article.title}\n\n"
            f"正文如下（三引号包裹）：\n\n'''\n{article.content}\n'''"
        )
        obj = llm_json(api_manager, SYSTEM_EXTRACT, user)
        items = obj.get("items", []) if isinstance(obj, dict) else []
        return items if isinstance(items, list) else []
    
    # Process in batches
    print(f"  [分批处理] {len(mapped_stocks)} 只股票，每批 {batch_size} 只")
    for i in range(0, len(mapped_stocks), batch_size):
        batch = mapped_stocks[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(mapped_stocks) + batch_size - 1) // batch_size
        print(f"  [批次 {batch_num}/{total_batches}] 处理: {', '.join([s['name'] for s in batch])}")
        
        stock_lines = "\n".join([f"- {s['name']} ({s['code']})" for s in batch])
        user = (
            f"股票列表：\n{stock_lines}\n\n"
            f"文章链接：{article.source}\n"
            f"文章日期：{article.date}\n"
            f"文章标题（可能为空）：{article.title}\n\n"
            f"正文如下（三引号包裹）：\n\n'''\n{article.content}\n'''"
        )
        try:
            obj = llm_json(api_manager, SYSTEM_EXTRACT, user)
            items = obj.get("items", []) if isinstance(obj, dict) else []
            if isinstance(items, list):
                all_items.extend(items)
                print(f"    成功提取 {len(items)} 条")
        except Exception as e:
            print(f"    批次失败: {str(e)[:100]}")
            continue
    
    return all_items


# ---------------------------
# Merge
# ---------------------------

def ensure_stock_base(code: str, name: str) -> Dict[str, Any]:
    return {
        "name": name,
        "code": code,
        "board": board_from_code(code),
        "industry": "",
        "concepts": [],
        "products": [],
        "core_business": [],
        "industry_position": [],
        "chain": [],
        "partners": [],
        "mention_count": 0,
        "articles": [],
    }


def merge_into_master(master: Dict[str, Any], items: List[Dict[str, Any]]):
    stocks = master.setdefault("stocks", [])
    by_code = {s.get("code"): s for s in stocks if isinstance(s, dict) and s.get("code")}

    for it in items:
        if not isinstance(it, dict):
            continue
        code = str(it.get("code", "")).strip()
        name = str(it.get("name", "")).strip()
        art = it.get("article", {})
        if not (re.fullmatch(r"\d{6}", code) and isinstance(art, dict)):
            continue

        s = by_code.get(code)
        if not s:
            s = ensure_stock_base(code, name or code)
            stocks.append(s)
            by_code[code] = s

        src = normalize_url(str(art.get("source", "")).strip())
        if not src:
            continue
        existing_sources = {a.get("source") for a in s.get("articles", []) if isinstance(a, dict)}
        if src in existing_sources:
            continue

        for k in ["accidents", "insights", "key_metrics", "target_valuation"]:
            v = art.get(k, [])
            if not isinstance(v, list):
                v = []
            if k == "accidents":
                v = [compress_accident(str(x)) for x in v if str(x).strip()]
            else:
                v = [str(x).strip() for x in v if str(x).strip()]
            art[k] = v

        art["source"] = src
        art["date"] = str(art.get("date") or "").strip() or dt.date.today().isoformat()
        art["title"] = str(art.get("title") or "").strip()

        s.setdefault("articles", []).append(
            {
                "title": art["title"],
                "date": art["date"],
                "source": art["source"],
                "accidents": art["accidents"],
                "insights": art["insights"],
                "key_metrics": art["key_metrics"],
                "target_valuation": art["target_valuation"],
            }
        )
        s["mention_count"] = len(s.get("articles", []))


def main():
    config = load_config()
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="raw_material markdown file")
    ap.add_argument("--stock_xls", required=True, help="Excel mapping: 股票代码, 股票简称")
    ap.add_argument("--out_json", required=True, help="Output JSON path")
    ap.add_argument("--mode", choices=["overwrite", "merge"], default="merge")
    ap.add_argument("--default_date", default=dt.date.today().isoformat())
    ap.add_argument("--config", help="Path to config.json")
    args = ap.parse_args()

    if args.config:
        config = load_config(args.config)

    # Create API Manager
    api_manager = APIManager(config)
    if not api_manager.apis:
        raise SystemExit("No API configured. Please set config.json with 'api' or 'fallback_api' section.")
    
    print(f"[API管理器] 已加载 {len(api_manager.apis)} 个API端点:")
    for i, api in enumerate(api_manager.apis):
        status = "✓" if i == 0 else "(备用)"
        print(f"  {status} {api['name']}: {api['base_url']} [{api['model']}]")

    code_to_name, name_to_code = load_stock_map(args.stock_xls)
    print(f"[股票映射] 已加载 {len(code_to_name)} 只股票")

    raw_md = read_text(args.raw)
    articles = parse_raw_material(raw_md, default_date=args.default_date)
    if not articles:
        raise SystemExit("No article blocks found in raw_material. Expect '## Article' blocks.")
    
    print(f"[文章解析] 找到 {len(articles)} 篇文章")

    master = {"stocks": []}
    out_path = Path(args.out_json)
    if args.mode == "merge" and out_path.exists():
        master = json.loads(out_path.read_text(encoding="utf-8"))
        if not isinstance(master, dict):
            master = {"stocks": []}
        print(f"[合并模式] 已加载现有数据，共 {len(master.get('stocks', []))} 只股票")

    for art in articles:
        print(f"\n{'='*60}")
        print(f"[处理文章] {art.title or art.source[:50]}...")
        
        # Step A: identify mentioned stocks
        candidates = identify_stocks_in_article(api_manager, art.content)

        mapped: List[Dict[str, str]] = []
        for c in candidates:
            code = c.get("code", "")
            name = c.get("name", "")
            if code and code in code_to_name:
                mapped.append({"code": code, "name": code_to_name[code]})
            elif name and name in name_to_code:
                mapped.append({"code": name_to_code[name], "name": name})

        # de-dup
        uniq = {}
        for s in mapped:
            uniq[s["code"]] = s
        mapped = list(uniq.values())

        if not mapped:
            print(f"  未识别到股票，跳过")
            continue

        print(f"  识别到 {len(mapped)} 只股票: {', '.join([s['name'] for s in mapped[:5]])}{'...' if len(mapped) > 5 else ''}")

        # Step B: extract structured items
        items = extract_items(api_manager, art, mapped)

        # Fill missing name via map
        for it in items:
            if isinstance(it, dict) and re.fullmatch(r"\d{6}", str(it.get("code", ""))):
                code = str(it["code"])
                it.setdefault("name", code_to_name.get(code, ""))
                if isinstance(it.get("article"), dict):
                    it["article"].setdefault("source", art.source)
                    it["article"].setdefault("date", art.date)
                    it["article"].setdefault("title", art.title)

        merge_into_master(master, items)
        print(f"  已提取 {len(items)} 条结构化数据")

    write_json(args.out_json, master)
    print(f"\n{'='*60}")
    print(f"[完成] 输出文件: {args.out_json}")
    print(f"[统计] 共 {len(master.get('stocks', []))} 只股票")


if __name__ == "__main__":
    main()