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
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Fix Windows GBK encoding issues
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
    "【严格过滤原则】：\n"
    "- 仅识别文章中有实质性分析的个股（有具体业务进展、财务数据、订单、估值或独立判断），而非仅仅是行业背景举例。\n"
    "- 如果个股只是被罗列（如\"推荐A、B、C等\"），或仅作为行业背景提及（如\"像某某一样\"），不要识别。\n"
    "- 若不确定，宁可不输出。\n"
    "- 允许输出 name 或 code（6位数字），能给 code 优先给 code。\n"
    "- 只输出 JSON（不要解释、不要 markdown）。\n"
    "输出格式示例：{\"stocks\":[{\"name\":\"新雷能\",\"code\":\"300593\"}]}"
)

SYSTEM_EXTRACT = (
    "你是中文金融研报结构化抽取助手。\n"
    "正在处理一篇复杂的金融市场研报。你的任务是为每只个股提取结构化数据。\n\n"
    "你会收到：\n"
    "1) 一篇公众号文章（可能包含多只股票内容）\n"
    "2) 需要抽取的股票列表（已经映射到代码）\n\n"
    "【严格过滤原则】在提取前，对列表中每只股票做如下三步判断：\n"
    "1. 该公司是否有独立的事件/催化剂描述（非行业泛论）？\n"
    "2. 描述中是否有至少一个具体数字、时间节点或明确判断？\n"
    "3. 该公司是否被当作主角而非行业背景举例？\n\n"
    "全部为否 → 跳过该公司，不输出。\n"
    "至少一条为是 → 正常提取。但如果 accidents 为空：\n"
    "  - 有 insights 或 key_metrics → accidents 填写 [\"__THIN__\"] 作为标记\n"
    "  - 完全没有 insights/key_metrics → 跳过该公司\n\n"
    "请为每只股票生成一条 article 记录，字段必须符合下列 JSON Schema：\n"
    "{\n"
    "  \"items\": [\n"
    "    {\n"
    "      \"code\": \"6 位数字\",\n"
    "      \"name\": \"股票简称\",\n"
    "      \"article\": {\n"
    "        \"title\": \"文章标题\",\n"
    "        \"date\": \"YYYY-MM-DD\",\n"
    "        \"source\": \"文章链接\",\n"
    "        \"industry_background\": [\"行业/赛道背景\"],\n"
    "        \"accidents\": [\"事件/催化剂\"],\n"
    "        \"insights\": [\"投研观点/逻辑\"],\n"
    "        \"key_metrics\": [\"关键指标\"],\n"
    "        \"target_valuation\": [\"估值/目标市值\"]\n"
    "      },\n"
    "      \"products\": [\"产品/服务\"],\n"
    "      \"core_business\": [\"核心业务\"],\n"
    "      \"industry\": \"所属行业\",\n"
    "      \"industry_position\": [\"行业地位/竞争优势\"],\n"
    "      \"partners\": [\"合作伙伴/客户\"],\n"
    "      \"chain\": [\"产业链位置\"]\n"
    "    }\n"
    "  ]\n"
    "}\n"
    "抽取规则（严格执行 5 维度划分）：\n"
    "- industry_background：仅提取行业/赛道/产业链层面的宏观趋势、政策红利、供需变化。\n"
    "  ★ 严禁出现任何具体公司名称！若多只股票属同一赛道，此字段内容必须完全一致地复制到每只相关股票节点中。\n"
    "  ★ 若文章没有行业背景描述，返回空数组 []。\n"
    "- accidents：只写客观事实事件/催化剂/动作，单条<=60字。\n"
    "  ★ 严禁包含主观推测（如\"预计\"、\"可能\"、\"有望\"、\"看好\"等词汇，归入 insights）。\n"
    "- insights：仅写针对该具体个股的投资逻辑、竞争优势与受益逻辑。回答\"这家公司凭什么最受益\"。\n"
    "  ★ 严禁填充泛泛的行业科普。\n"
    "- key_metrics：关键量化指标，每一条必须包含具体的阿拉伯数字或百分比（%）。\n"
    "  ★ 纯定性描述（如\"大幅增长\"、\"遥遥领先\"）直接丢弃。\n"
    "- target_valuation：目标估值，必须包含市值数额（亿）、目标股价（元）或 PE/PB 等具体倍数。\n"
    "  ★ 无具体数字的表述（如\"估值极具吸引力\"）移入 insights。\n"
    "- products：主要产品、服务、技术（2-3个关键词）。\n"
    "- core_business：核心业务（1-2句话）。\n"
    "- industry：所属行业（如\"电子-半导体-集成电路\"）。\n"
    "- industry_position：行业地位、竞争优势、市场排名。\n"
    "- partners：主要客户、供应商、合作伙伴（公司名称）。\n"
    "- chain：产业链位置（如\"上游-原材料\"）。\n"
    "- 如果文章中没有某字段信息，严格返回空数组 [] 或空字符串，严禁臆测！\n"
    "- 只输出 JSON（不要解释、不要 markdown）。\n"
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
# 第一道防线：Python 启发式预过滤
# ---------------------------

SIGNAL_KEYWORDS = [
    "订单", "放量", "营收", "净利润", "市占率", "份额",
    "估值", "目标价", "PE", "催化", "突破", "中标", "预期",
    "产能", "量产", "扩产", "涨", "跌", "收购", "并购",
    "回购", "分红", "业绩", "毛利率", "净利率", "ROE",
    "新品", "客户", "合同", "项目",
]


# NOTE: is_valid_stock_context() removed in v2.5 — the 第一道防线 logic
# was redundant with AI prompt filtering (第二防线) + post-processing (第三防线).
# The SIGNAL_KEYWORDS list is kept for reference.

# ---------------------------
# Quality Filtering
# ---------------------------

DIGEST_TITLE_PATTERNS = [
    r'\d+月\d+日[一些]?首板逻辑',
    r'\d+月\d+日信息[整理汇总]',
    r'今天的一些信息整理',
    r'信息[汇总整理]',
    r'一周核心纪要',
    r'周度[汇总纪要]',
    r'周报',
    r'\d{6}信息汇总',
]

BROAD_LIST_TITLE_PATTERNS = [
    r'盈利最强[的]?\d+[家只]企业',
    r'\d+只主力重仓龙头',
    r'\d+家上市公司[受益对标]',
    r'全产业链[受益图谱布局]',
    r'A股全产业链',
    r'产业链全景解析',
    r'供应格局梳理',
    r'\d+家核心公司',
    r'全线涨停',
    r'龙头名单',
    r'核心公司[一览名单]',
    r'谁[吃瓜]?千亿',
    r'90%散户',
    r'伪[陷阱]?',
]


def is_digest_article(title: str) -> bool:
    """Check if article title indicates a daily digest/weekly roundup (skip entirely)."""
    for p in DIGEST_TITLE_PATTERNS:
        if re.search(p, title):
            return True
    return False


def is_broad_list_article(title: str) -> bool:
    """Check if article title indicates multi-stock rolisting / industry overview (skip entirely)."""
    for p in BROAD_LIST_TITLE_PATTERNS:
        if re.search(p, title):
            return True
    return False


def has_list_patterns_in_content(article: ArticleBlock) -> bool:
    """Check article content for multi-stock recommendation patterns."""
    content = article.content
    patterns = [
        r'推荐.*等[。，；]?$',
        r'#重点推荐[：:]',
        r'重点推荐.*等',
        r'港股[方面：:]',
        r'美股[方面：:]',
    ]
    for p in patterns:
        if re.search(p, content, re.MULTILINE):
            return True
    return False


def filter_items_by_quality(items: List[Dict], article: ArticleBlock) -> Tuple[List[Dict], List[Dict]]:
    """将提取结果分为"通过"和"仅第一层信息"两路。

    Rules:
    - 通过: 有实质投研内容（accidents+insights+metrics+valuation 有足够条目）→ 写完整 article
    - 轻量: 投研质量不足，但有 stock-level 字段（products/core_business/industry_position/chain/partners）
            → 不写 article，但静默合并第一层信息，不增加 mention_count
    - 丢弃: 无任何有效信息

    Returns: (passed_items, lightweight_items)
    """
    passed = []
    lightweight = []

    for it in items:
        if not isinstance(it, dict):
            continue
        art = it.get("article", {})
        if not isinstance(art, dict):
            continue

        accidents = art.get("accidents", []) or []
        insights = art.get("insights", []) or []
        metrics = art.get("key_metrics", []) or []
        valuation = art.get("target_valuation", []) or []

        # Check for multi-stock listing patterns: always reject
        if any(re.search(r'(推荐.*等|#重点推荐|重点推荐)', str(x)) for x in accidents):
            continue

        # 检测 __THIN__ 标记 → 降级为轻量模式
        if "__THIN__" in str(accidents):
            code = it.get("code", "?")
            name = it.get("name", "?")
            # 检查第一层字段是否有价值
            if _has_stock_level_info(it):
                print(f"  🔽 [{code} {name}] __THIN__ 标记：降级为轻量模式（仅更新第一层信息）")
                lightweight.append(it)
            continue

        # Total item count
        total = len(accidents) + len(insights) + len(metrics) + len(valuation)

        # Substantive analysis check
        substance = len(insights) + len(metrics) + len(valuation)

        if total > 2 and substance > 1:
            passed.append(it)
        elif _has_stock_level_info(it):
            code = it.get("code", "?")
            name = it.get("name", "?")
            print(f"  🔽 [{code} {name}] 投研内容不足(total={total}, substance={substance})：降级为轻量模式")
            lightweight.append(it)

    return passed, lightweight


def _has_stock_level_info(it: Dict) -> bool:
    """检查 item 是否包含有价值的股票第一层字段"""
    stock_fields = ["products", "core_business", "industry_position", "chain", "partners"]
    for field in stock_fields:
        val = it.get(field, None)
        if isinstance(val, list) and len(val) > 0:
            return True
        if isinstance(val, str) and val.strip():
            return True
    return False


# ---------------------------
# 第三道防线：后置数据清理
# ---------------------------

def clean_extracted_data(stock_data: Dict[str, Any]) -> Dict[str, Any] | None:
    """过滤掉无效的个股提取结果。

    规则：文章必须至少包含一个非空字段
    （industry_background/accidents/insights/key_metrics/target_valuation）。
    如果某股票下没有任何有效文章了，返回 None。
    """
    valid_articles = []

    for article in stock_data.get("articles", []):
        industry_bg = article.get("industry_background", [])
        accidents = article.get("accidents", [])
        insights = article.get("insights", [])
        key_metrics = article.get("key_metrics", [])
        target_val = article.get("target_valuation", [])

        # 核心逻辑：五个字段全为空 → 丢弃
        if any([industry_bg, accidents, insights, key_metrics, target_val]):
            # 额外清理 __THIN__ 残留
            accidents_clean = [a for a in accidents if a != "__THIN__"]
            if accidents_clean != accidents:
                article["accidents"] = accidents_clean
            valid_articles.append(article)

    stock_data["articles"] = valid_articles

    # 没有任何有效文章 → 返回 None
    if not valid_articles:
        return None

    return stock_data


# ---------------------------
# 后置数据规范清洗 (Hard Rule Enforcement)
# ---------------------------

def clean_extracted_stock(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    对 LLM 提取的个股数据进行硬性规则校验与清洗。
    确保 key_metrics 含数字、target_valuation 含估值单位、
    accidents 单条 <=60 字、industry_background 不混入公司名。
    """
    stock_name = stock_data.get("name", "")

    for article in stock_data.get("articles", []):

        # 1. 清洗 key_metrics：强制要求包含数字
        valid_metrics = []
        for metric in article.get("key_metrics", []):
            if re.search(r'\d', metric):  # 必须包含阿拉伯数字
                valid_metrics.append(metric)
        article["key_metrics"] = valid_metrics

        # 2. 清洗 target_valuation：强制要求包含估值单位/特征词
        valid_val = []
        val_keywords = ['亿', '元', 'PE', 'PB', '倍', '市值', '目标价']
        for val in article.get("target_valuation", []):
            if any(kw in val for kw in val_keywords) and re.search(r'\d', val):
                valid_val.append(val)
        article["target_valuation"] = valid_val

        # 3. 清洗 accidents：强制长度限制（单条 <=60 字）
        valid_accidents = []
        for acc in article.get("accidents", []):
            if len(acc) <= 60:
                valid_accidents.append(acc)
            # 超过 60 字直接丢弃（不在 Python 层面截断，避免产生无意义片段）
        article["accidents"] = valid_accidents

        # 4. 清洗 industry_background：去除偶然混入的公司名
        clean_bg = []
        for bg in article.get("industry_background", []):
            if stock_name and stock_name in bg:
                bg = bg.replace(stock_name, "业内相关公司")
            clean_bg.append(bg)
        article["industry_background"] = clean_bg

    return stock_data


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


def merge_lightweight_stock_info(master: Dict[str, Any], items: List[Dict[str, Any]]):
    """仅合并第一层个股信息，不写 article，不增加 mention_count。

    适用场景：投研质量不足以成为文章，但 LLM 提取到的 products/core_business/
    industry_position/chain/partners 仍有价值。
    """
    stocks = master.setdefault("stocks", [])
    by_code = {s.get("code"): s for s in stocks if isinstance(s, dict) and s.get("code")}

    merged_count = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        code = str(it.get("code", "")).strip()
        name = str(it.get("name", "")).strip()
        if not re.fullmatch(r"\d{6}", code):
            continue

        s = by_code.get(code)
        if not s:
            s = ensure_stock_base(code, name or code)
            stocks.append(s)
            by_code[code] = s

        any_merged = False
        for field in ["products", "core_business", "industry_position", "chain", "partners"]:
            val = it.get(field, None)
            if isinstance(val, list) and len(val) > 0:
                existing = set(s.get(field, []))
                new_items = [str(x).strip() for x in val if str(x).strip()]
                before = len(existing)
                for item in new_items:
                    existing.add(item)
                if len(existing) > before:
                    any_merged = True
                    s[field] = sorted(list(existing))

        if any_merged:
            merged_count += 1
            print(f"  [NOTE] [{code} {name}] 轻量合并第一层信息 (mention_count 不变)")

    return merged_count


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

        # 合并股票层级字段（products, core_business, industry_position, industry, partners, chain）
        for field in ["products", "core_business", "industry_position", "industry", "partners", "chain"]:
            val = it.get(field, None)
            if val:
                if field == "industry" and isinstance(val, str) and val.strip():
                    # industry 是字符串，直接赋值（如果不为空）
                    if not s.get(field) or s.get(field) == "":
                        s[field] = val.strip()
                elif isinstance(val, list) and len(val) > 0:
                    # 其他字段是列表，合并去重
                    existing = set(s.get(field, []))
                    for item in val:
                        if isinstance(item, str) and item.strip():
                            existing.add(item.strip())
                    s[field] = sorted(list(existing))

        # 处理 article 字段
        for k in ["industry_background", "accidents", "insights", "key_metrics", "target_valuation"]:
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
                "industry_background": art.get("industry_background", []),
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
    
    print(f"[API 管理器] 已加载 {len(api_manager.apis)} 个 API 端点:")
    for i, api in enumerate(api_manager.apis):
        status = "OK" if i == 0 else "(备用)"
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

        # ─── v2.7: 不再按标题整篇拒绝"每日汇总/首板逻辑"类文章 ───
        # 改由 AI 逐股判断 + __THIN__ 后置清洗，确保含有具体信息的个股不被误杀
        is_digest = is_digest_article(art.title)
        if is_digest:
            print(f"  ℹ️ 每日汇总/首板逻辑类文章，将逐股判断: {art.title}")

        # ─── 过滤层 2: 多股罗列/行业综述标题 → 整篇跳过 ───
        if is_broad_list_article(art.title):
            print(f"  ⛔ 多股罗列/行业综述文章，跳过: {art.title}")
            continue

        # ─── 过滤层 3: 内容含多股推荐模式（如 #重点推荐）→ 整篇跳过 ───
        if has_list_patterns_in_content(art):
            print(f"  ⛔ 内容含多股推荐模式，跳过")
            continue
        
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

        # ─── 过滤层 4: 分两路——通过(完整article) / 轻量(仅第一层信息) ───
        before_filter = len(items)
        passed_items, lightweight_items = filter_items_by_quality(items, art)
        if before_filter != len(passed_items) + len(lightweight_items):
            filtered_out = before_filter - len(passed_items) - len(lightweight_items)
            print(f"  质量过滤: {before_filter} -> {len(passed_items)} 通过 + {len(lightweight_items)} 轻量 (丢弃 {filtered_out} 条)")

        # 轻量合并：不写 article，只更新第一层字段
        if lightweight_items:
            for it in lightweight_items:
                if isinstance(it, dict) and re.fullmatch(r"\d{6}", str(it.get("code", ""))):
                    code = str(it["code"])
                    it.setdefault("name", code_to_name.get(code, ""))
            lw_merged = merge_lightweight_stock_info(master, lightweight_items)
            if lw_merged > 0:
                print(f"  [NOTE] 轻量模式合并了 {lw_merged} 只股票的第一层信息")

        if not passed_items:
            print(f"  无通过条目，继续")
            continue

        # Fill missing name via map
        for it in passed_items:
            if isinstance(it, dict) and re.fullmatch(r"\d{6}", str(it.get("code", ""))):
                code = str(it["code"])
                it.setdefault("name", code_to_name.get(code, ""))
                if isinstance(it.get("article"), dict):
                    it["article"].setdefault("source", art.source)
                    it["article"].setdefault("date", art.date)
                    it["article"].setdefault("title", art.title)

        merge_into_master(master, passed_items)
        print(f"  已提取 {len(passed_items)} 条结构化数据")

    # ─── 第三道防线：后置清理 ───
    stocks_list = master.get("stocks", [])
    before_clean = len(stocks_list)
    stocks_cleaned = []
    cleaned_count = 0
    for stock in stocks_list:
        result = clean_extracted_data(stock)
        if result is not None:
            stocks_cleaned.append(result)
        else:
            code = stock.get("code", "?")
            name = stock.get("name", "?")
            print(f"  🗑 [{code} {name}] 清理：无有效文章，移除股票节点")
            cleaned_count += 1
    master["stocks"] = stocks_cleaned
    after_clean = len(stocks_cleaned)
    if cleaned_count > 0:
        print(f"\n[第三道防线] 后置清理: {before_clean} -> {after_clean} 只 (移除 {cleaned_count} 只无效个股)\n")

    # ─── 后置硬性规则清洗：key_metrics 数字校验 / target_valuation 估值词校验 / accidents 长度 / industry_background 公司名清洗 ───
    print(f"[硬性规则清洗] 对 {after_clean} 只股票执行 key_metrics/target_valuation/accidents 硬性规则清洗...")
    stocks_final = []
    for stock in stocks_cleaned:
        stock = clean_extracted_stock(stock)
        # 清洗后再检查是否有有效文章
        if stock.get("articles"):
            stocks_final.append(stock)
    master["stocks"] = stocks_final
    print(f"[硬性规则清洗] 完成，剩余 {len(stocks_final)} 只股票\n")

    write_json(args.out_json, master)
    print(f"\n{'='*60}")
    print(f"[完成] 输出文件: {args.out_json}")
    print(f"[统计] 共 {len(master.get('stocks', []))} 只股票")


if __name__ == "__main__":
    main()