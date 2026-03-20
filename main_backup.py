# 临时测试：直接读取 stocks_master.json 而不是 .gz
import json
from pathlib import Path

MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'

with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data.get('stocks', [])
print(f"加载 {len(stocks)} 只股票")

found = any(s.get('code') == '600900' for s in stocks)
print(f"长江电力：{'存在' if found else '不存在'}")
