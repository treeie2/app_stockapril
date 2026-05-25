import json
from pathlib import Path

# 文件路径
DAILY_FILE = Path("e:/github/stock-research-backup/data/stocks/2026-05-17.json")
MASTER_16_FILE = Path("e:/github/stock-research-backup/data/stocks_master_2026-05-16.json")
MASTER_FILE = Path("e:/github/stock-research-backup/data/stocks/stocks_master.json")

print("=== 任务1：统一修改 last_updated 为 '05-17' ===")

# 1. 读取 2026-05-17.json 文件（包含DSP芯片概念股13只 + 今天的一些信息整理15只）
print("\n1. 处理 data/stocks/2026-05-17.json...")
with open(DAILY_FILE, "r", encoding="utf-8") as f:
    daily_data = json.load(f)

daily_stocks = daily_data.get("stocks", {})
dsp_stocks = list(daily_stocks.keys())[:13]  # DSP芯片概念股前13只
info_stocks = list(daily_stocks.keys())[13:]  # 今天的一些信息整理后15只

print(f"   DSP芯片概念股（13只）: {dsp_stocks}")
print(f"   今天的一些信息整理（15只）: {info_stocks}")

# 修改这些股票的 last_updated 为 "05-17"
count_17 = 0
for code in list(daily_stocks.keys()):
    daily_stocks[code]["last_updated"] = "05-17"
    count_17 += 1

# 保存
with open(DAILY_FILE, "w", encoding="utf-8") as f:
    json.dump(daily_data, f, ensure_ascii=False, indent=2)
print(f"   ✅ 修改了 {count_17} 只股票的 last_updated 为 '05-17'")

# 2. 读取 stocks_master_2026-05-16.json 文件
print("\n2. 处理 data/stocks_master_2026-05-16.json...")
with open(MASTER_16_FILE, "r", encoding="utf-8") as f:
    master_16_data = json.load(f)

master_16_stocks = master_16_data.get("stocks", [])
for stock in master_16_stocks:
    stock["last_updated"] = "05-17"

# 保存
with open(MASTER_16_FILE, "w", encoding="utf-8") as f:
    json.dump(master_16_data, f, ensure_ascii=False, indent=2)
print(f"   ✅ 修改了 {len(master_16_stocks)} 只股票的 last_updated 为 '05-17'")

print("\n=== 任务2：检查并修改其他属性字段 ===")

# 检查 stocks_master.json 中所有 last_updated 为 "05-17" 的股票，修改其他属性
print("\n1. 检查 data/stocks/stocks_master.json...")
with open(MASTER_FILE, "r", encoding="utf-8") as f:
    master_data = json.load(f)

master_stocks = master_data.get("stocks", {})
modified_count = 0

for code, stock in master_stocks.items():
    if stock.get("last_updated") == "05-17":
        # 检查并修改文章中的日期字段
        articles = stock.get("articles", [])
        for article in articles:
            # 如果文章日期是 "05-17"，改成 "05-16"
            if article.get("date") == "05-17":
                article["date"] = "05-16"
                modified_count += 1

# 保存
with open(MASTER_FILE, "w", encoding="utf-8") as f:
    json.dump(master_data, f, ensure_ascii=False, indent=2)
print(f"   ✅ 修改了 {modified_count} 个文章日期字段为 '05-16'")

# 检查并修改 stocks_master_2026-05-16.json
print("\n2. 检查 data/stocks_master_2026-05-16.json...")
modified_count_16 = 0
for stock in master_16_stocks:
    articles = stock.get("articles", [])
    for article in articles:
        if article.get("date") == "05-17":
            article["date"] = "05-16"
            modified_count_16 += 1

# 保存
with open(MASTER_16_FILE, "w", encoding="utf-8") as f:
    json.dump(master_16_data, f, ensure_ascii=False, indent=2)
print(f"   ✅ 修改了 {modified_count_16} 个文章日期字段为 '05-16'")

# 检查并修改 2026-05-17.json
print("\n3. 检查 data/stocks/2026-05-17.json...")
modified_count_daily = 0
for code, stock in daily_stocks.items():
    articles = stock.get("articles", [])
    for article in articles:
        if article.get("date") == "05-17":
            article["date"] = "05-16"
            modified_count_daily += 1

# 保存
with open(DAILY_FILE, "w", encoding="utf-8") as f:
    json.dump(daily_data, f, ensure_ascii=False, indent=2)
print(f"   ✅ 修改了 {modified_count_daily} 个文章日期字段为 '05-16'")

print("\n=== 操作完成 ===")
print(f"任务1：修改 last_updated 为 '05-17' 的股票数：{count_17 + len(master_16_stocks)}")
print(f"任务2：修改文章日期为 '05-16' 的数量：{modified_count + modified_count_16 + modified_count_daily}")