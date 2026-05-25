# -*- coding: utf-8 -*-
"""列出所有有目标估值的个股"""
import re

INPUT = "target_valuations.md"

with open(INPUT, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"^\|\s*\d+\s*\|\s*(\d{6})\s*\|\s*([^\|]+)\s*\|\s*(.+?)\s*\|"
matches = re.findall(pattern, content, re.MULTILINE)

results = []
for code, name, val_text in matches:
    val_text = val_text.strip()
    if val_text in ("", "-", "—", "——", "*", "#"):
        continue
    results.append((code, name.strip()))

OUT = "valuations_stocks_list.txt"
with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"共有 {len(results)} 只有目标估值的个股：\n\n")
    f.write(f"{'序号':<4} {'代码':<8} {'名称':<12}\n")
    f.write("-" * 30 + "\n")
    for i, (code, name) in enumerate(results, 1):
        f.write(f"{i:<4} {code:<8} {name:<12}\n")
print(f"已保存到 {OUT}，共 {len(results)} 只")