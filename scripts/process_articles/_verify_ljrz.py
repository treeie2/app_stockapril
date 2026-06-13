"""验证 ljrz 处理结果"""
import json
from pathlib import Path

# 加载
with open(r"e:\github\stock-research-backup\temp11\ljrz_output.json", encoding="utf-8") as f:
    d = json.load(f)
stocks = d.get("stocks", {})

print(f"ljrz独立JSON: {len(stocks)} 只股票\n")

# 名称异常
bad_names = [(c, s["name"]) for c, s in stocks.items()
             if not any(('\u4e00' <= ch <= '\u9fff') or ch.isupper() for ch in s["name"][:1])]
print(f"名称异常的股票: {len(bad_names)} 只")
for c, n in bad_names:
    print(f"  {c}: {n}")

# 提及最多的
top = sorted(stocks.items(), key=lambda x: x[1].get("mention_count", 0), reverse=True)[:15]
print("\n提及最多的15只:")
for c, s in top:
    print(f"  {s['name']}({c}): {s.get('mention_count',0)}次")

# 加载 master
with open(r"e:\github\stock-research-backup\data\stocks\stocks_master.json", encoding="utf-8") as f:
    master = json.load(f)
ms = master.get("stocks", {})
print(f"\nstocks_master.json: {len(ms)} 只股票")