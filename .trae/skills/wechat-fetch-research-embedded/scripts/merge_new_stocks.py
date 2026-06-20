"""合并当日新数据到 stocks_master.json 和日期分片 (v2.5)"""
import json
import re
import sys
from datetime import date
from pathlib import Path

from merge_utils import merge_articles, merge_set_fields, load_master, save_master, load_or_create_shard, save_shard

BASE_DIR = Path(__file__).parent.parent
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def normalize_code(code):
    """剥离 .SH/.SZ/.BJ 后缀，统一为纯数字 code"""
    return re.sub(r'\.(SH|SZ|BJ)$', '', code)


def merge_new_stocks(date_str=None):
    """合并当日新数据到 stocks_master.json 和日期分片"""
    if date_str is None:
        date_str = date.today().isoformat()
    
    # 1. 读取新数据
    new_data_paths = [
        PROJECT_ROOT / 'data' / f'stocks_master_{date_str}.json',
        BASE_DIR / 'data' / f'stocks_master_{date_str}.json',
        Path.cwd() / f'data/stocks_master_{date_str}.json',
        Path.cwd() / f'stocks_master_{date_str}.json'
    ]
    new_data_path = next((p for p in new_data_paths if p.exists()), None)
    
    if new_data_path is None:
        print(f'[ERROR] 找不到 stocks_master_{date_str}.json')
        return False
    
    with open(new_data_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    new_stocks_list = new_data.get('stocks', [])
    for s in new_stocks_list:
        if 'code' in s:
            s['code'] = normalize_code(s['code'])
    new_stocks_dict = {s['code']: s for s in new_stocks_list if 'code' in s}
    print(f'[INFO] 新数据: {len(new_stocks_list)} 只股票')
    
    # 2. 合并到主文件
    master = load_master(PROJECT_ROOT)
    master_stocks = master.get('stocks', {})
    print(f'[INFO] 主文件: {len(master_stocks)} 只股票')
    
    for code, new_s in new_stocks_dict.items():
        if code in master_stocks:
            old_count = len(master_stocks[code].get('articles', []))
            master_stocks[code]['articles'] = merge_articles(master_stocks[code].get('articles', []), new_s.get('articles', []))
            merge_set_fields(master_stocks[code], new_s)
            new_count = len(master_stocks[code]['articles'])
            if new_count > old_count:
                master_stocks[code]['mention_count'] = new_count
                master_stocks[code]['last_updated'] = date_str
            else:
                print(f'  [SKIP] {code} {new_s.get("name", "")}: 无新文章')
        else:
            master_stocks[code] = new_s
            master_stocks[code]['last_updated'] = date_str
            print(f'  [NEW] {code} {new_s.get("name", "")}: 新增股票')
    
    master['stocks'] = master_stocks
    save_master(PROJECT_ROOT, master)
    print(f'[INFO] 主文件已更新')
    
    # 3. 更新分片
    shard = load_or_create_shard(PROJECT_ROOT, date_str)
    shard_stocks = shard.get('stocks', {})
    for code, new_s in new_stocks_dict.items():
        if code in shard_stocks:
            shard_stocks[code]['articles'] = merge_articles(shard_stocks[code].get('articles', []), new_s.get('articles', []))
            shard_stocks[code]['mention_count'] = len(shard_stocks[code]['articles'])
        else:
            shard_stocks[code] = new_s
    shard['stocks'] = shard_stocks
    shard['update_count'] = len(shard_stocks)
    save_shard(PROJECT_ROOT, date_str, shard)
    
    # 4. 验证
    verify = load_master(PROJECT_ROOT)
    total = len(verify.get('stocks', {}))
    print(f'[OK] 验证完成: 主文件共 {total} 只股票')
    return True


def main():
    success = merge_new_stocks(date.today().isoformat())
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()