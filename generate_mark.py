#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通达信 mark.dat 生成脚本（混合模式）
- 有研究数据的股票 → 替换为研究数据（行业地位/核心业务/目标估值等）
- 没有研究数据的股票 → 保留原始概念标签
- 新增股票 → 追加标记
"""

import re
import json
from pathlib import Path

MASTER_FILE = "data/stocks/stocks_master.json"
ORIGINAL_FILE = "mark.dat"
OUTPUT_FILE = "mark_merged.dat"
DEFAULT_COLOR = "65535"  # 黄色


def convert_code_to_mark_id(code: str) -> str | None:
    code = code.strip()
    if not code.isdigit():
        return None
    if code.startswith(('00', '30')):
        prefix = "00"
    elif code.startswith(('60', '688')):
        prefix = "01"
    elif code.startswith(('83', '43')):
        prefix = "02"
    else:
        return None
    return f"{prefix}{code}"


def parse_mark_dat(filepath):
    """解析 mark.dat 文件为分段字典"""
    sections = {"[MARK]": {}, "[TIME]": {}, "[TIPCOLOR]": {}, "[TIPWORD]": {}, "[TIP]": {}}
    order = []

    if not Path(filepath).exists():
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


def build_research_tip(stock, name):
    """从研究数据生成 TIP 内容"""
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

    # 收集估值
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


def build_research_tipword(stock):
    """从研究数据生成简标"""
    tags = []
    all_vals = []
    for art in stock.get("articles", []):
        all_vals.extend(art.get("target_valuation", []))
    if all_vals:
        first_val = list(set(all_vals))[0]
        nums = re.findall(r'[0-9,]+亿|约[0-9]+倍|[0-9]+%', first_val)
        if nums:
            tags.append(f"目标:{nums[0]}")
        else:
            tags.append("目标估值")
    industry_pos = stock.get("industry_position", [])
    if industry_pos:
        tags.append("龙头")
    return ",".join(tags[:2]) if tags else "目标估值"


def main():
    print("通达信 mark.dat 混合生成脚本\n")

    # 1. 解析原始 mark.dat
    orig_sections, orig_order = parse_mark_dat(ORIGINAL_FILE)
    orig_count = len(orig_sections["[MARK]"])
    print(f"原始 mark.dat: {orig_count} 只标记股票")

    # 2. 读取研究数据
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)
    stocks = master.get("stocks", {})
    print(f"研究数据: {len(stocks)} 只股票")

    # 3. 建立研究数据索引 (mark_id -> stock)
    research_map = {}
    for code, stock in stocks.items():
        mid = convert_code_to_mark_id(code)
        if not mid:
            continue
        name = stock.get("name", "")
        articles = stock.get("articles", [])
        last_updated = stock.get("last_updated", "")
        if articles or last_updated:
            research_map[mid] = (stock, name)

    print(f"有研究深度数据的股票: {len(research_map)} 只")

    # 4. 合并处理
    replaced_count = 0
    kept_count = 0
    new_added = 0

    # 从原始数据开始，逐条处理
    result_mark = {}
    result_time = {}
    result_tipcolor = {}
    result_tipword = {}
    result_tip = {}

    # 先处理原始数据中的所有股票
    for mark_id in orig_sections["[MARK]"]:
        has_research = mark_id in research_map

        # [MARK] 始终保留
        result_mark[mark_id] = orig_sections["[MARK]"].get(mark_id, "7")
        result_time[mark_id] = orig_sections["[TIME]"].get(mark_id, "1")

        if has_research:
            # 有研究数据 → 替换
            stock, name = research_map[mark_id]
            tip_text = build_research_tip(stock, name)
            tipword_text = build_research_tipword(stock)
            if tip_text:
                result_tip[mark_id] = tip_text
                result_tipword[mark_id] = tipword_text
                result_tipcolor[mark_id] = DEFAULT_COLOR
                replaced_count += 1
            else:
                # 有标记但无有效研究内容 → 保留原始
                if mark_id in orig_sections["[TIP]"]:
                    result_tip[mark_id] = orig_sections["[TIP]"][mark_id]
                if mark_id in orig_sections["[TIPWORD]"]:
                    result_tipword[mark_id] = orig_sections["[TIPWORD]"][mark_id]
                result_tipcolor[mark_id] = orig_sections["[TIPCOLOR]"].get(mark_id, DEFAULT_COLOR)
                kept_count += 1
        else:
            # 无研究数据 → 保留原始
            if mark_id in orig_sections["[TIP]"]:
                result_tip[mark_id] = orig_sections["[TIP]"][mark_id]
            if mark_id in orig_sections["[TIPWORD]"]:
                result_tipword[mark_id] = orig_sections["[TIPWORD]"][mark_id]
            if mark_id in orig_sections["[TIPCOLOR]"]:
                result_tipcolor[mark_id] = orig_sections["[TIPCOLOR]"][mark_id]
            kept_count += 1

    # 新增：研究数据中有但原始数据中没有的股票
    for mark_id, (stock, name) in research_map.items():
        if mark_id not in result_mark:
            tip_text = build_research_tip(stock, name)
            tipword_text = build_research_tipword(stock)
            if tip_text:
                result_mark[mark_id] = "7"
                result_time[mark_id] = "1"
                result_tip[mark_id] = tip_text
                result_tipword[mark_id] = tipword_text
                result_tipcolor[mark_id] = DEFAULT_COLOR
                new_added += 1

    print(f"\n处理结果:")
    print(f"  - 替换为研究数据: {replaced_count} 只")
    print(f"  - 保留原有标签: {kept_count} 只")
    print(f"  - 新增股票: {new_added} 只")
    print(f"  - 总计: {len(result_mark)} 只\n")

    # 5. 写入文件 (GBK)
    with open(OUTPUT_FILE, "w", encoding="gbk", errors="ignore") as f:
        # 确定段顺序：优先用原始顺序，补充新增段
        all_sections = ["[MARK]", "[TIME]", "[TIPCOLOR]", "[TIPWORD]", "[TIP]"]
        
        for section in all_sections:
            f.write(section + "\n")
            data_map = {
                "[MARK]": result_mark,
                "[TIME]": result_time,
                "[TIPCOLOR]": result_tipcolor,
                "[TIPWORD]": result_tipword,
                "[TIP]": result_tip,
            }.get(section, {})
            
            for key in sorted(data_map.keys()):
                val = data_map[key]
                if section == "[TIP]" and len(val) > 200:
                    val = val[:197] + "..."
                f.write(f"{key}={val}\n")
            f.write("\n")

    print(f"✅ 生成完成: {OUTPUT_FILE}")
    print(f"文件大小: {Path(OUTPUT_FILE).stat().st_size / 1024:.1f} KB\n")

    # 输出示例
    print("═══ 研究数据替换示例 ═══")
    shown = 0
    for key in sorted(result_tip.keys()):
        if "目标估值" in result_tip[key] and shown < 8:
            print(f"  {result_tip[key][:100]}")
            shown += 1

    print(f"\n═══ 保留原始标签示例 ═══")
    shown = 0
    for key in sorted(result_tip.keys()):
        if "【目标估值】" not in result_tip[key] and "【行业地位】" not in result_tip[key] and shown < 5:
            print(f"  {result_tip[key][:80]}")
            shown += 1


if __name__ == "__main__":
    main()