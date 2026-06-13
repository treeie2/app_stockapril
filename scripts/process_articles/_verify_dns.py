"""验证 dns 处理结果"""
import json

with open(r"e:\github\stock-research-backup\temp11\dns_output.json", encoding="utf-8") as f:
    d = json.load(f)
stocks = d.get("stocks", {})

print(f"dns独立JSON: {len(stocks)} 只股票\n")

top = sorted(stocks.items(), key=lambda x: x[1].get("mention_count", 0), reverse=True)[:15]
print("提及最多的15只:")
for c, s in top:
    print(f"  {s['name']}({c}): {s.get('mention_count',0)}次")

with open(r"e:\github\stock-research-backup\data\stocks\stocks_master.json", encoding="utf-8") as f:
    master = json.load(f)
ms = master.get("stocks", {})
print(f"\nstocks_master.json: {len(ms)} 只股票")