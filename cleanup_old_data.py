#!/usr/bin/env python3
"""
删除旧的数据文件，只保留最近一个月的
"""
import os
from pathlib import Path
from datetime import datetime, timedelta

# 数据目录
data_dir = Path("data/master/stocks")

# 只保留最近 30 天的数据
keep_days = 30
cutoff_date = datetime.now() - timedelta(days=keep_days)

# 获取所有 json 文件
json_files = list(data_dir.glob("*.json"))

kept = 0
removed = 0

for file_path in json_files:
    # 从文件名提取日期 (格式: YYYY-MM-DD.json)
    try:
        date_str = file_path.stem  # 获取文件名（不含扩展名）
        file_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        if file_date < cutoff_date:
            # 删除旧文件
            file_path.unlink()
            print(f"🗑️  删除: {file_path.name}")
            removed += 1
        else:
            print(f"✅ 保留: {file_path.name}")
            kept += 1
    except ValueError:
        # 文件名不符合日期格式，保留
        print(f"⚠️  保留（非日期格式）: {file_path.name}")
        kept += 1

print(f"\n📊 统计:")
print(f"   保留: {kept} 个文件")
print(f"   删除: {removed} 个文件")
