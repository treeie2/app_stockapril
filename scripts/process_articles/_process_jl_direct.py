#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接处理 jl 文件夹文章 → 识别个股 → 生成独立 JSON（无需 LLM API）
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


# ---------------------------
# 1. 加载个股映射表
# ---------------------------

def load_stock_map(xls_path: str) -> Dict[str, str]:
    xls = pd.ExcelFile(xls_path)
    df = pd.read_excel(xls_path, sheet_name=xls.sheet_names[0])
    df = df[["股票代码", "股票简称"]].dropna()
    name_to_code = {}
    for _, r in df.iterrows():
        code_raw = str(r["股票代码"]).strip()
        name = str(r["股票简称"]).strip()
        if not code_raw or not name:
            continue
        m = re.match(r"^(\d{6})\.(SZ|SH)$", code_raw)
        if m:
            code = m.group(1)
            name_to_code[name] = code
    return name_to_code


# ---------------------------
# 2. 解析 raw_material markdown
# ---------------------------

def parse_articles(md_text: str) -> List[dict]:
    blocks = re.split(r'\n## Article\n', md_text)
    articles = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        source_m = re.search(r'^source:\s*(\S+)', block, re.MULTILINE)
        title_m = re.search(r'^title:\s*(.+)', block, re.MULTILINE)
        date_m = re.search(r'^date:\s*(.+)', block, re.MULTILINE)
        source = source_m.group(1) if source_m else ""
        title = title_m.group(1) if title_m else ""
        date = date_m.group(1) if date_m else ""
        content_lines = []
        in_content = False
        for line in block.split('\n'):
            if line.startswith('fetched_at:'):
                in_content = True
                continue
            if in_content:
                content_lines.append(line)
        content = '\n'.join(content_lines).strip()
        articles.append({"source": source, "title": title, "date": date, "content": content})
    return articles


# ---------------------------
# 3. 从文章中识别个股
# ---------------------------

SIGNAL_KEYWORDS = [
    "订单", "放量", "营收", "净利润", "市占率", "份额",
    "估值", "目标价", "PE", "催化", "突破", "中标", "预期",
    "产能", "量产", "扩产", "涨", "跌", "收购", "并购",
    "回购", "分红", "业绩", "毛利率", "净利率", "ROE",
    "新品", "客户", "合同", "项目",
]


def find_stocks_in_text(text: str, name_to_code: Dict[str, str]) -> List[Tuple[str, str, str]]:
    sorted_names = sorted(name_to_code.keys(), key=len, reverse=True)
    found = {}

    def clean_name(raw_name: str) -> str:
        return re.sub(r'^[^\u4e00-\u9fffA-Za-z0-9]+', '', raw_name)

    # 模式1: 【代码 名称】
    for m in re.finditer(r'【(\d{6})\s+(\S+?)】', text):
        code, name = m.group(1), m.group(2)
        if code in name_to_code.values() or name in name_to_code:
            para = find_paragraph(text, m.group(0))
            found[code] = (name, para)

    # 模式2: 名称（代码）
    for m in re.finditer(r'(\S+?)[（(](\d{6})[）)]', text):
        name, code = m.group(1), m.group(2)
        clean = clean_name(name)
        if code in name_to_code.values() and clean:
            para = find_paragraph(text, m.group(0))
            found[code] = (clean, para)

    # 模式3: 名称(代码)
    for m in re.finditer(r'(\S+?)\((\d{6})\)', text):
        name, code = m.group(1), m.group(2)
        clean = clean_name(name)
        if code in name_to_code.values() and clean and code not in found:
            para = find_paragraph(text, m.group(0))
            found[code] = (clean, para)

    # 模式4: 单独名称
    for name in sorted_names:
        code = name_to_code[name]
        if code in found:
            continue
        if len(name) < 2:
            continue
        for m in re.finditer(re.escape(name), text):
            start = max(0, m.start() - 50)
            end = min(len(text), m.end() + 200)
            context = text[start:end]
            if any(kw in context for kw in SIGNAL_KEYWORDS) or len(context) > 100:
                para = find_paragraph(text, name)
                found[code] = (name, para)
                break

    return list(found.items())


def find_paragraph(text: str, keyword: str) -> str:
    paragraphs = re.split(r'\n\s*\n', text)
    for para in paragraphs:
        if keyword in para:
            return para.strip()
    return ""


def is_digest_article(title: str) -> bool:
    digest_patterns = [
        r'今天的一些信息整理', r'每日信息', r'市场总结',
        r'周报', r'日报', r'盘前', r'复盘', r'收评',
    ]
    for p in digest_patterns:
        if re.search(p, title):
            return True
    return False


def is_broad_list_article(title: str) -> bool:
    broad_patterns = [
        r'机构推荐.*狙击涨停', r'涨停', r'牛股', r'金股', r'板块.*梳理',
    ]
    for p in broad_patterns:
        if re.search(p, title):
            return True
    return False


def has_list_patterns_in_content(article: dict) -> bool:
    content = article.get("content", "")
    if '#重点推荐' in content:
        return True
    stock_mentions = re.findall(r'[\u4e00-\u9fa5]{2,6}[（(]\d{6}[）)]', content)
    if len(stock_mentions) > 15:
        return True
    return False


# ---------------------------
# 4. 生成提取结果
# ---------------------------

def extract_item_for_stock(code: str, name: str, context: str, article: dict) -> dict:
    item = {
        "code": code,
        "name": name,
        "article": {
            "title": article["title"],
            "source": article["source"],
            "date": article["date"],
            "accidents": [],
            "insights": [],
            "key_metrics": [],
            "target_valuation": [],
        }
    }
    if context:
        item["article"]["insights"].append(f"[jl] {context[:200]}")
        metrics = re.findall(r'[\d,.]+[亿万千元%倍]+', context)
        if metrics:
            item["article"]["key_metrics"] = [m for m in metrics[:5]]
    return item


# ---------------------------
# 5. 合并到 master
# ---------------------------

def merge_into_master(master: dict, items: List[dict]):
    stocks = master.setdefault("stocks", {})
    for item in items:
        code = item["code"]
        name = item["name"]
        article = item["article"]
        if code not in stocks:
            stocks[code] = {"code": code, "name": name, "articles": [], "mention_count": 0}
        stock = stocks[code]
        existing_sources = {a.get("source", "") for a in stock.get("articles", [])}
        if article["source"] and article["source"] not in existing_sources:
            stock.setdefault("articles", []).append(article)
            stock["mention_count"] = stock.get("mention_count", 0) + 1


def clean_extracted_data(master: dict) -> dict:
    stocks = master.get("stocks", {})
    cleaned = {}
    for code, stock in stocks.items():
        valid_articles = []
        for article in stock.get("articles", []):
            if article.get("insights") or article.get("key_metrics"):
                valid_articles.append(article)
        if valid_articles:
            stock["articles"] = valid_articles
            stock["mention_count"] = len(valid_articles)
            cleaned[code] = stock
    master["stocks"] = cleaned
    return master


# ---------------------------
# 主流程
# ---------------------------

def main():
    base = Path(r"e:\github\stock-research-backup")
    raw_md_path = base / "temp11" / "jl_raw_material.md"
    xls_path = base / ".trae" / "skills" / "wechat-fetch-research-embedded" / "assets" / "全部个股.xls"
    standalone_json_path = base / "temp11" / "jl_output.json"
    master_json_path = base / "data" / "stocks" / "stocks_master.json"

    for p in [raw_md_path, xls_path]:
        if not p.exists():
            raise FileNotFoundError(f"文件不存在: {p}")

    print(f"[加载] 个股映射: {xls_path}")
    name_to_code = load_stock_map(str(xls_path))
    print(f"  → {len(name_to_code)} 只股票")

    md_text = raw_md_path.read_text(encoding="utf-8")
    articles = parse_articles(md_text)
    print(f"[解析] {len(articles)} 篇文章")

    master = {"version": "2.3", "updated_at": "2026-06-13", "stocks": {}}
    total_filtered = 0

    for art_idx, article in enumerate(articles, 1):
        title = article.get("title", "")
        content = article.get("content", "")
        print(f"\n--- 文章 {art_idx}/{len(articles)}: {title[:40]}...")

        if is_digest_article(title):
            print(f"  ⛔ 每日汇总类型，跳过")
            total_filtered += 1
            continue
        if is_broad_list_article(title):
            print(f"  ⛔ 多股罗列标题，跳过")
            total_filtered += 1
            continue
        if has_list_patterns_in_content(article):
            print(f"  ⛔ 多股推荐内容，跳过")
            total_filtered += 1
            continue

        found_stocks = find_stocks_in_text(content, name_to_code)
        if not found_stocks:
            print(f"  - 未识别到个股")
            continue

        print(f"  ✓ 识别到 {len(found_stocks)} 只: {', '.join([s[1][0] for s in found_stocks[:8]])}{'...' if len(found_stocks) > 8 else ''}")

        items = [extract_item_for_stock(code, name, context, article) for code, (name, context) in found_stocks]
        merge_into_master(master, items)

    master = clean_extracted_data(master)

    # 使用标准名称
    code_to_name = {c: n for n, c in name_to_code.items()}
    for code, stock_data in master["stocks"].items():
        if code in code_to_name:
            stock_data["name"] = code_to_name[code]

    standalone_json_path.parent.mkdir(parents=True, exist_ok=True)
    standalone_json_path.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"[完成] 独立 JSON: {standalone_json_path}")
    print(f"[统计] 共 {len(master['stocks'])} 只股票")
    print(f"[过滤] 跳过 {total_filtered} 篇文章")

    # 合并到 master
    if master_json_path.exists():
        master_data = json.loads(master_json_path.read_text(encoding="utf-8"))
        existing_stocks = master_data.get("stocks", {})
        if isinstance(existing_stocks, list):
            existing_dict = {s.get("code", ""): s for s in existing_stocks if s.get("code")}
            existing_stocks = existing_dict

        new_stocks = master.get("stocks", {})
        merged_count = 0
        new_count = 0
        for code, stock_data in new_stocks.items():
            if code in existing_stocks:
                existing = existing_stocks[code]
                existing_articles = existing.setdefault("articles", [])
                existing_sources = {a.get("source", "") for a in existing_articles}
                for article in stock_data.get("articles", []):
                    if article["source"] not in existing_sources:
                        existing_articles.append(article)
                        existing["mention_count"] = existing.get("mention_count", 0) + 1
                        merged_count += 1
            else:
                existing_stocks[code] = stock_data
                new_count += 1

        master_data["stocks"] = existing_stocks
        master_data["updated_at"] = "2026-06-13"
        master_json_path.write_text(json.dumps(master_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[合并] 新股票: {new_count} 只, 新增文章: {merged_count} 篇")
        print(f"[完成] 更新 stocks_master.json: {master_json_path}")
        print(f"[总] stocks_master.json 共 {len(existing_stocks)} 只股票")
    else:
        print(f"[警告] stocks_master.json 不存在，跳过合并")


if __name__ == "__main__":
    main()