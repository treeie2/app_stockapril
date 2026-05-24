#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tdx_mark — 通达信 mark.dat 自动生成器
从 stocks_master.json 读取研究数据，混合生成 mark.dat 文件

输出: .trae/skills/tdx_mark/mark_YYYY-MM-DD.dat
"""

import re
import json
import shutil
from pathlib import Path
from datetime import datetime, time, timedelta

# ========== 路径配置 ==========
SKILL_DIR = Path(__file__).parent
PROJECT_DIR = SKILL_DIR.parents[2]  # .trae/../../ (项目根目录)

MASTER_FILE = PROJECT_DIR / "data" / "stocks" / "stocks_master.json"
ORIGINAL_FILE = PROJECT_DIR / "mark.dat"
OUTPUT_DIR = SKILL_DIR

DEFAULT_COLOR = "65535"  # 黄色


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
    """解析 mark.dat，返回分段字典"""
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


def build_research_tip(stock: dict, name: str) -> str:
    parts = []
    industry_pos = stock.get("industry_position", [])
    if industry_pos:
        parts.append(f"【行业地位】{' / '.join(industry_pos[:3])}")

    core_biz = stock.get("core_business", [])
    if core_biz:
        parts.append(f"【核心业务】{' / '.join(core_biz[:4])}")

    chain = stock.get("chain", [])
    if chain:
        parts.append(f"【产业链】{' / '.join(chain[:2])}")

    partners = stock.get("partners", [])
    if partners:
        parts.append(f"【合作伙伴】{' / '.join(partners[:4])}")

    concepts = stock.get("concepts", [])
    if concepts and not industry_pos:
        parts.append(f"【概念】{' / '.join(concepts[:5])}")

    all_vals = []
    for art in stock.get("articles", []):
        all_vals.extend(art.get("target_valuation", []))
    if all_vals:
        for v in list(set(all_vals))[:3]:
            parts.append(f"【目标估值】{v}")

    last_upd = stock.get("last_updated", "")
    if last_upd:
        parts.append(f"【更新】{last_upd}")

    return f"{name}，{' #$'.join(parts)}" if parts else ""


def build_research_tipword(stock: dict) -> str:
    tags = []
    all_vals = []
    for art in stock.get("articles", []):
        all_vals.extend(art.get("target_valuation", []))
    if all_vals:
        first_val = list(set(all_vals))[0]
        nums = re.findall(r'[0-9,]+亿|约[0-9]+倍|[0-9]+%', first_val)
        tags.append(f"目标:{nums[0]}" if nums else "目标估值")
    industry_pos = stock.get("industry_position", [])
    if industry_pos:
        tags.append("龙头")
    return ",".join(tags[:2]) if tags else "目标估值"


def generate():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"🔧 tdx_mark — 通达信 mark.dat 生成器")
    print(f"📅 日期: {today}")
    print(f"📂 项目目录: {PROJECT_DIR}")
    print()

    # 1. 读取研究数据
    if not MASTER_FILE.exists():
        print(f"❌ 错误: 找不到 {MASTER_FILE}")
        return

    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)
    stocks = master.get("stocks", {})
    print(f"📊 stocks_master.json: {len(stocks)} 只股票")

    # 建立研究索引
    research_map = {}
    for code, stock in stocks.items():
        mid = convert_code_to_mark_id(code)
        if not mid:
            continue
        name = stock.get("name", "")
        if stock.get("articles") or stock.get("last_updated"):
            research_map[mid] = (stock, name)
    print(f"🔬 有研究数据: {len(research_map)} 只")

    # 2. 解析原始 mark.dat
    orig_sections, orig_order = parse_mark_dat(ORIGINAL_FILE)
    orig_count = len(orig_sections["[MARK]"])
    print(f"📜 原始 mark.dat: {orig_count} 只标记")

    # 3. 混合处理
    result_mark = {}
    result_time = {}
    result_color = {}
    result_word = {}
    result_tip = {}

    replaced, kept, new_added = 0, 0, 0

    # 处理原始数据中的股票
    for mark_id in orig_sections["[MARK]"]:
        result_mark[mark_id] = orig_sections["[MARK]"].get(mark_id, "7")
        result_time[mark_id] = orig_sections["[TIME]"].get(mark_id, "1")

        if mark_id in research_map:
            stock, name = research_map[mark_id]
            tip_text = build_research_tip(stock, name)
            if tip_text:
                result_tip[mark_id] = tip_text
                result_word[mark_id] = build_research_tipword(stock)
                result_color[mark_id] = DEFAULT_COLOR
                replaced += 1
            else:
                if mark_id in orig_sections["[TIP]"]:
                    result_tip[mark_id] = orig_sections["[TIP]"][mark_id]
                if mark_id in orig_sections["[TIPWORD]"]:
                    result_word[mark_id] = orig_sections["[TIPWORD]"][mark_id]
                result_color[mark_id] = orig_sections["[TIPCOLOR]"].get(mark_id, DEFAULT_COLOR)
                kept += 1
        else:
            if mark_id in orig_sections["[TIP]"]:
                result_tip[mark_id] = orig_sections["[TIP]"][mark_id]
            if mark_id in orig_sections["[TIPWORD]"]:
                result_word[mark_id] = orig_sections["[TIPWORD]"][mark_id]
            result_color[mark_id] = orig_sections["[TIPCOLOR]"].get(mark_id, DEFAULT_COLOR)
            kept += 1

    # 新增研究中有但原文件没有的
    for mark_id, (stock, name) in research_map.items():
        if mark_id not in result_mark:
            tip_text = build_research_tip(stock, name)
            if tip_text:
                result_mark[mark_id] = "7"
                result_time[mark_id] = "1"
                result_tip[mark_id] = tip_text
                result_word[mark_id] = build_research_tipword(stock)
                result_color[mark_id] = DEFAULT_COLOR
                new_added += 1

    print(f"\n🔄 处理结果:")
    print(f"   🔁 替换为研究数据: {replaced} 只")
    print(f"   🔒 保留原始标签:   {kept} 只")
    print(f"   🆕 新增股票:       {new_added} 只")
    print(f"   📦 总计:           {len(result_mark)} 只")

    # 4. 写入文件
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
                if section == "[TIP]" and len(val) > 200:
                    val = val[:197] + "..."
                f.write(f"{key}={val}\n")
            f.write("\n")

    # 复制为最新版
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