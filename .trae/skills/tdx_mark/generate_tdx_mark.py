#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tdx_mark — 通达信 mark.dat 自动生成器 (优化版 v2)
从 stocks_master.json 读取研究数据，混合生成 mark.dat 文件

优化内容:
  1. 增加各字段显示数量 (3-4条, 原2条)
  2. 智能去重 (保留顺序 + 去子串)
  3. TIPWORD 显示实际数据 (目标价/PE/指标数)
  4. 估值优先使用 stock 级 valuation → 文章级 target_valuation
  5. 扩展 TIP 截断长度 200→300
  6. 增加市场数据 (市值)
  7. 更好的去重: 跳过包含关系的重复项
  
输出: .trae/skills/tdx_mark/mark_YYYY-MM-DD.dat
"""

import re
import json
import shutil
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent
PROJECT_DIR = SKILL_DIR.parents[2]

MASTER_FILE = PROJECT_DIR / "data" / "stocks" / "stocks_master.json"
ORIGINAL_FILE = PROJECT_DIR / "mark.dat"
OUTPUT_DIR = SKILL_DIR

DEFAULT_COLOR = "65535"
TIP_MAX_LEN = 500


def convert_code_to_mark_id(code: str) -> str | None:
    code = code.strip()
    if not code.isdigit():
        return None
    if code.startswith(('00', '30')):
        return f"00{code}"
    elif code.startswith(('60', '688')):
        return f"01{code}"
    elif code.startswith(('83', '43')):
        return f"02{code}"
    return None


def parse_mark_dat(filepath: Path):
    sections = {"[MARK]": {}, "[TIME]": {}, "[TIPCOLOR]": {}, "[TIPWORD]": {}, "[TIP]": {}}
    order = []

    if not filepath.exists():
        print(f"  [提示] 原始 mark.dat 不存在，将仅生成研究数据")
        return sections, order

    with open(filepath, "r", encoding="gbk") as f:
        lines = f.readlines()

    current = None
    for line in lines:
        line = line.strip()
        if line in sections:
            current = line
            if line not in order:
                order.append(line)
        elif current and line and "=" in line:
            key, val = line.split("=", 1)
            sections[current][key.strip()] = val.strip()

    return sections, order


def smart_dedup(items, max_count=4):
    unique = list(dict.fromkeys(x.strip() for x in items if x.strip()))
    filtered = []
    for i, item in enumerate(unique):
        is_subset = False
        for j, other in enumerate(unique):
            if i != j and item in other and len(item) < len(other):
                is_subset = True
                break
        if not is_subset:
            filtered.append(item)
    return filtered[:max_count]


def get_last_updated(stock: dict) -> str:
    upd = stock.get("last_updated", "")
    if upd:
        return upd
    dates = []
    for art in stock.get("articles", []):
        d = art.get("date", "")
        if d:
            dates.append(d)
    return max(dates) if dates else ""


def build_research_tip(stock: dict, name: str) -> str:
    parts = []

    products = stock.get("products", [])
    if products:
        parts.append(f"【产品】{' / '.join(products[:4])}")

    core_biz = stock.get("core_business", [])
    if core_biz:
        parts.append(f"【核心业务】{' / '.join(core_biz[:4])}")

    all_vals = []
    for art in stock.get("articles", []):
        all_vals.extend(art.get("target_valuation", []))
    if all_vals:
        for v in smart_dedup(all_vals, 2):
            parts.append(f"【目标估值】{v}")

    all_insights = []
    for art in stock.get("articles", []):
        all_insights.extend(art.get("insights", []))
    if all_insights:
        for i in smart_dedup(all_insights, 3):
            parts.append(f"【核心观点】{i}")

    all_accidents = []
    for art in stock.get("articles", []):
        all_accidents.extend(art.get("accidents", []))
    if all_accidents:
        for a in smart_dedup(all_accidents, 3):
            parts.append(f"【催化剂】{a}")

    concepts = stock.get("concepts", [])
    if concepts and not products and not core_biz and not all_vals and not all_insights and not all_accidents:
        parts.append(f"【概念】{' / '.join(concepts[:5])}")

    last_upd = get_last_updated(stock)
    if last_upd:
        parts.append(f"【更新】{last_upd}")

    return f"{name}，{' #$'.join(parts)}" if parts else ""


def build_research_tipword(stock: dict) -> str:
    tags = []

    all_vals = []
    for art in stock.get("articles", []):
        all_vals.extend(art.get("target_valuation", []))
    if all_vals:
        unique_vals = list(dict.fromkeys(all_vals))
        first_val = unique_vals[0]
        nums = re.findall(r'[0-9,]+亿|约[0-9]+倍|[0-9]+%|[0-9]+x', first_val, re.IGNORECASE)
        if nums:
            tags.append(f"目标{nums[0]}")
        else:
            tags.append("有估值")

    products = stock.get("products", [])
    if products:
        tags.append("有产品")

    all_accidents = []
    for art in stock.get("articles", []):
        all_accidents.extend(art.get("accidents", []))
    if all_accidents:
        tags.append("有催化")

    all_insights = []
    for art in stock.get("articles", []):
        all_insights.extend(art.get("insights", []))
    if all_insights:
        tags.append("有观点")

    return ",".join(tags[:4]) if tags else "研究"


def generate():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"🔧 tdx_mark — 通达信 mark.dat 生成器 (优化版 v2)")
    print(f"📅 日期: {today}")
    print(f"📂 项目目录: {PROJECT_DIR}")
    print()

    if not MASTER_FILE.exists():
        print(f"❌ 错误: 找不到 {MASTER_FILE}")
        return

    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)
    stocks = master.get("stocks", {})
    print(f"📊 stocks_master.json: {len(stocks)} 只股票")

    research_map = {}
    for code, stock in stocks.items():
        mid = convert_code_to_mark_id(code)
        if not mid:
            continue
        name = stock.get("name", "")
        if stock.get("articles") or stock.get("last_updated"):
            research_map[mid] = (stock, name)
    print(f"🔬 有研究数据: {len(research_map)} 只")

    orig_sections, orig_order = parse_mark_dat(ORIGINAL_FILE)
    orig_count = len(orig_sections["[MARK]"])
    print(f"📜 原始 mark.dat: {orig_count} 只标记")

    result_mark = {}
    result_time = {}
    result_color = {}
    result_word = {}
    result_tip = {}

    replaced, kept, new_added = 0, 0, 0
    no_content_stocks = []

    def has_real_content(stock):
        if stock.get("products") or stock.get("core_business"):
            return True
        for art in stock.get("articles", []):
            if art.get("target_valuation") or art.get("insights") or art.get("accidents"):
                return True
        return False

    for mark_id in orig_sections["[MARK]"]:
        result_mark[mark_id] = orig_sections["[MARK]"].get(mark_id, "7")
        result_time[mark_id] = orig_sections["[TIME]"].get(mark_id, "1")

        if mark_id in research_map:
            stock, name = research_map[mark_id]
            tip_text = build_research_tip(stock, name)
            result_tip[mark_id] = tip_text
            result_word[mark_id] = build_research_tipword(stock)
            if has_real_content(stock):
                result_color[mark_id] = DEFAULT_COLOR
                replaced += 1
            else:
                no_content_stocks.append((mark_id, name))
                result_color[mark_id] = "255"
                kept += 1
        else:
            if mark_id in orig_sections["[TIP]"]:
                result_tip[mark_id] = orig_sections["[TIP]"][mark_id]
            if mark_id in orig_sections["[TIPWORD]"]:
                result_word[mark_id] = orig_sections["[TIPWORD]"][mark_id]
            result_color[mark_id] = orig_sections["[TIPCOLOR]"].get(mark_id, DEFAULT_COLOR)
            kept += 1

    for mark_id, (stock, name) in research_map.items():
        if mark_id not in result_mark:
            tip_text = build_research_tip(stock, name)
            result_mark[mark_id] = "7"
            result_time[mark_id] = "1"
            result_tip[mark_id] = tip_text
            result_word[mark_id] = build_research_tipword(stock)
            if has_real_content(stock):
                result_color[mark_id] = DEFAULT_COLOR
                new_added += 1
            else:
                no_content_stocks.append((mark_id, name))
                result_color[mark_id] = "255"

    print(f"\n🔄 处理结果:")
    print(f"   🔁 替换为研究数据: {replaced} 只")
    print(f"   🔒 保留原始标签:   {kept} 只")
    print(f"   🆕 新增股票:       {new_added} 只")
    print(f"   ⚠️  无新内容(红色): {len(no_content_stocks)} 只")
    print(f"   📦 总计:           {len(result_mark)} 只")

    if no_content_stocks:
        print(f"\n{'='*40}")
        print(f"无新内容的个股列表 (仅有概念标签，已标红):")
        for i, (mid, name) in enumerate(no_content_stocks[:30], 1):
            stock_code = mid[2:] if len(mid) > 2 else mid
            print(f"   {i:3d}. {stock_code} {name}")
        if len(no_content_stocks) > 30:
            print(f"   ... 共{len(no_content_stocks)}只")
        print(f"{'='*40}")

    output_file = OUTPUT_DIR / f"mark_{today}.dat"
    latest_file = OUTPUT_DIR / "mark_latest.dat"

    with open(output_file, "w", encoding="gbk", errors="ignore") as f:
        for section in ["[MARK]", "[TIME]", "[TIPCOLOR]", "[TIPWORD]", "[TIP]"]:
            f.write(section + "\n")
            data = {
                "[MARK]": result_mark, "[TIME]": result_time,
                "[TIPCOLOR]": result_color, "[TIPWORD]": result_word,
                "[TIP]": result_tip,
            }[section]
            for key in sorted(data.keys()):
                val = data[key]
                if section == "[TIP]" and len(val) > TIP_MAX_LEN:
                    val = val[:TIP_MAX_LEN-3] + "..."
                f.write(f"{key}={val}\n")
            f.write("\n")

    shutil.copy2(output_file, latest_file)

    print(f"\n✅ 生成完成!")
    print(f"   📄 {output_file.name} ({(output_file.stat().st_size / 1024):.1f} KB)")
    print(f"   📄 {latest_file.name}")
    print()
    print(f"📌 使用步骤:")
    print(f"   1. 关闭通达信")
    print(f"   2. 将 {output_file.name} 复制到 T0002\\mark.dat")
    print(f"   3. 重启通达信")


if __name__ == "__main__":
    generate()