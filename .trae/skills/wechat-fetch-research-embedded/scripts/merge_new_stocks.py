import json
import re
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def normalize_code(code):
    """剥离 .SH/.SZ/.BJ 后缀，统一为纯数字 code"""
    return re.sub(r'\.(SH|SZ|BJ)$', '', code)

def merge_new_stocks(date_str=None):
    """合并当日新数据到 stocks_master.json 和日期分片"""
    if date_str is None:
        date_str = date.today().isoformat()
    
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
    
    # 1. 读取新数据
    new_data_paths = [
        PROJECT_ROOT / 'data' / f'stocks_master_{date_str}.json',
        BASE_DIR / 'data' / f'stocks_master_{date_str}.json',
        Path.cwd() / f'data/stocks_master_{date_str}.json',
        Path.cwd() / f'stocks_master_{date_str}.json'
    ]
    
    new_data_path = None
    for path in new_data_paths:
        if path.exists():
            new_data_path = path
            break
    
    if new_data_path is None:
        print(f'[ERROR] 找不到 stocks_master_{date_str}.json')
        print(f'  搜索路径: {[str(p) for p in new_data_paths]}')
        return False
    
    with open(new_data_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    new_stocks_list = new_data.get('stocks', [])
    for s in new_stocks_list:
        if 'code' in s:
            s['code'] = normalize_code(s['code'])
    new_stocks_dict = {s['code']: s for s in new_stocks_list if 'code' in s}
    print(f'[INFO] 新数据: {len(new_stocks_list)} 只股票')
    
    # 2. 读取主文件
    master_path = PROJECT_ROOT / 'data' / 'stocks' / 'stocks_master.json'
    with open(master_path, 'r', encoding='utf-8') as f:
        master = json.load(f)
    master_stocks = master.get('stocks', {})
    print(f'[INFO] 主文件: {len(master_stocks)} 只股票')
    
    # 3. 合并
    for code, new_s in new_stocks_dict.items():
        if code in master_stocks:
            old_articles = master_stocks[code].get('articles', [])
            new_articles = new_s.get('articles', [])
            existing_sources = {a.get('source', '') for a in old_articles}
            merged = False
            for a in new_articles:
                if a.get('source', '') not in existing_sources:
                    old_articles.append(a)
                    existing_sources.add(a.get('source', ''))
                    merged = True
            if merged:
                master_stocks[code]['articles'] = old_articles
                master_stocks[code]['mention_count'] = len(old_articles)
                master_stocks[code]['last_updated'] = date_str
            else:
                print(f'  [SKIP] {code} {new_s["name"]}: 无新文章')
        else:
            master_stocks[code] = new_s
            master_stocks[code]['last_updated'] = date_str
            print(f'  [NEW] {code} {new_s["name"]}: 新增股票')
    
    # 4. 保存主文件
    master['stocks'] = master_stocks
    with open(master_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f'[INFO] 主文件已更新: {master_path}')
    
    # 5. 更新分片
    shard_path = PROJECT_ROOT / 'data' / 'stocks' / f'{date_str}.json'
    if shard_path.exists():
        with open(shard_path, 'r', encoding='utf-8') as f:
            shard = json.load(f)
    else:
        shard = {'date': date_str, 'update_count': 0, 'stocks': {}}
    
    shard_stocks = shard.get('stocks', {})
    for code, new_s in new_stocks_dict.items():
        if code in shard_stocks:
            old_articles = shard_stocks[code].get('articles', [])
            new_articles = new_s.get('articles', [])
            existing_sources = {a.get('source', '') for a in old_articles}
            for a in new_articles:
                if a.get('source', '') not in existing_sources:
                    old_articles.append(a)
            shard_stocks[code]['articles'] = old_articles
            shard_stocks[code]['mention_count'] = len(old_articles)
        else:
            shard_stocks[code] = new_s
    
    shard['stocks'] = shard_stocks
    shard['update_count'] = len(shard_stocks)
    with open(shard_path, 'w', encoding='utf-8') as f:
        json.dump(shard, f, ensure_ascii=False, indent=2)
    
    # 6. 验证
    with open(master_path, 'r', encoding='utf-8') as f:
        verify = json.load(f)
    total = len(verify.get('stocks', {}))
    print(f'[OK] 验证完成: 主文件共 {total} 只股票')
    return True


def main():
    today_str = date.today().isoformat()
    success = merge_new_stocks(today_str)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()