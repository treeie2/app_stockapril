#!/usr/bin/env python3
"""
压缩 stocks_master.json 文件
"""
import json
from pathlib import Path

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
COMPRESSED_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.min.json")

print("📥 正在读取 stocks_master.json...")
with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ 读取完成：{len(data)} 只股票")

# 压缩保存（移除空格和缩进）
print("💾 正在压缩保存...")
with open(COMPRESSED_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

# 显示文件大小
original_size = MASTER_FILE.stat().st_size / 1024 / 1024
compressed_size = COMPRESSED_FILE.stat().st_size / 1024 / 1024

print(f"\n📊 压缩结果:")
print(f"  原始大小：{original_size:.2f} MB")
print(f"  压缩后：{compressed_size:.2f} MB")
print(f"  压缩率：{(1 - compressed_size/original_size)*100:.1f}%")
