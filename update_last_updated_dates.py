import json
from pathlib import Path

# 文件路径
FILE_15 = Path("e:/github/stock-research-backup/data/stocks_master_2026-05-15.json")
FILE_16 = Path("e:/github/stock-research-backup/data/stocks_master_2026-05-16.json")
FILE_17 = Path("e:/github/stock-research-backup/data/stocks_master_2026-05-17.json")
MASTER_FILE = Path("e:/github/stock-research-backup/data/stocks/stocks_master.json")

print("=" * 60)
print("任务1：修改文件中的 last_updated 日期")
print("=" * 60)

# 收集三个文件中的所有股票代码
all_stock_codes = set()

# 处理 05-15 文件（不修改，只收集股票代码）
print("\n1. 读取 stocks_master_2026-05-15.json（不修改）...")
with open(FILE_15, "r", encoding="utf-8") as f:
    data_15 = json.load(f)

stocks_15 = data_15.get("stocks", [])
if isinstance(stocks_15, list):
    for stock in stocks_15:
        code = stock.get("code", "")
        if code:
            all_stock_codes.add(code)
elif isinstance(stocks_15, dict):
    for code in stocks_15.keys():
        all_stock_codes.add(code)

print(f"   ✅ 收集了 {len(stocks_15)} 只股票，last_updated 保持为 '05-15'")

# 处理 05-16 文件（修改为 05-17）
print("\n2. 修改 stocks_master_2026-05-16.json...")
with open(FILE_16, "r", encoding="utf-8") as f:
    data_16 = json.load(f)

stocks_16 = data_16.get("stocks", [])
count_16 = 0
if isinstance(stocks_16, list):
    for stock in stocks_16:
        code = stock.get("code", "")
        if code:
            all_stock_codes.add(code)
        stock["last_updated"] = "05-17"
        count_16 += 1
elif isinstance(stocks_16, dict):
    for code, stock in stocks_16.items():
        all_stock_codes.add(code)
        stock["last_updated"] = "05-17"
        count_16 += 1

with open(FILE_16, "w", encoding="utf-8") as f:
    json.dump(data_16, f, ensure_ascii=False, indent=2)

print(f"   ✅ 修改了 {count_16} 只股票的 last_updated 为 '05-17'")

# 处理 05-17 文件（已经是 05-17，再确认一遍）
print("\n3. 修改 stocks_master_2026-05-17.json...")
with open(FILE_17, "r", encoding="utf-8") as f:
    data_17 = json.load(f)

stocks_17 = data_17.get("stocks", [])
count_17 = 0
if isinstance(stocks_17, list):
    for stock in stocks_17:
        code = stock.get("code", "")
        if code:
            all_stock_codes.add(code)
        stock["last_updated"] = "05-17"
        count_17 += 1
elif isinstance(stocks_17, dict):
    for code, stock in stocks_17.items():
        all_stock_codes.add(code)
        stock["last_updated"] = "05-17"
        count_17 += 1

with open(FILE_17, "w", encoding="utf-8") as f:
    json.dump(data_17, f, ensure_ascii=False, indent=2)

print(f"   ✅ 修改了 {count_17} 只股票的 last_updated 为 '05-17'")

print(f"\n三个文件总共涉及 {len(all_stock_codes)} 只股票")
print(f"股票列表: {sorted(all_stock_codes)}")

print("\n" + "=" * 60)
print("任务2：处理 stocks_master.json")
print("=" * 60)

# 读取主文件
print("\n读取 data/stocks/stocks_master.json...")
with open(MASTER_FILE, "r", encoding="utf-8") as f:
    master_data = json.load(f)

master_stocks = master_data.get("stocks", {})

# 分两类股票
to_update = {}  # 在三个文件中的股票，保持不变
to_clear = {}   # 不在三个文件中的股票，清空 last_updated

for code, stock in master_stocks.items():
    if code in all_stock_codes:
        to_update[code] = stock
    else:
        # 清空 last_updated
        stock["last_updated"] = ""
        to_clear[code] = stock

# 保存
with open(MASTER_FILE, "w", encoding="utf-8") as f:
    json.dump(master_data, f, ensure_ascii=False, indent=2)

print(f"✅ 处理完成：")
print(f"   - 保持不变的股票: {len(to_update)} 只")
print(f"   - 清空 last_updated 的股票: {len(to_clear)} 只")

print("\n" + "=" * 60)
print("任务3：验证修改结果")
print("=" * 60)

# 重新读取验证
print("\n验证 stocks_master.json...")
with open(MASTER_FILE, "r", encoding="utf-8") as f:
    verify_data = json.load(f)

verify_stocks = verify_data.get("stocks", {})

# 统计
stats = {"05-15": [], "05-17": [], "其他": [], "空": []}
for code, stock in verify_stocks.items():
    lu = stock.get("last_updated", "")
    if lu == "05-15":
        stats["05-15"].append(code)
    elif lu == "05-17":
        stats["05-17"].append(code)
    elif lu == "":
        stats["空"].append(code)
    else:
        stats["其他"].append((code, lu))

print(f"\nstocks_master.json 中的 last_updated 统计：")
for status, codes in stats.items():
    if codes:
        if isinstance(codes, list) and len(codes) <= 20:
            print(f"  {status}: {len(codes)} 只")
            print(f"    股票: {codes}")
        else:
            print(f"  {status}: {len(codes)} 只")

print("\n" + "=" * 60)
print("✅ 所有修改已完成！")
print("=" * 60)
print(f"\n下一步：Firebase 数据库中，{len(to_clear)} 只股票的 last_updated 字段将被清空")
print("（这些数据将留待后续文件处理时再进行更新）")