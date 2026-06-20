#!/usr/bin/env python3
"""独立日期格式规范化脚本 (v2.8)

扫描 stocks_master.json 中所有股票的 last_updated 和 article.date，
将非 YYYY-MM-DD 格式自动转换为 YYYY-MM-DD。

用法:
    python scripts/normalize_dates.py          # 检查模式（只报告，不修改）
    python scripts/normalize_dates.py --fix    # 修复模式

也可作为模块导入:
    from scripts.normalize_dates import check_and_fix
"""

import sys
from pathlib import Path

# 添加 skill 根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.merge_utils import normalize_all_stock_dates, load_master, save_master, normalize_date_string

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def check_and_fix(fix: bool = False) -> dict:
    """检查并可选修复日期格式"""
    master = load_master(PROJECT_ROOT)
    stocks = master.get('stocks', {})

    # 先检查（干运行）
    stats = normalize_all_stock_dates(stocks)
    
    if stats['stocks_affected'] > 0:
        print(f'发现 {stats["stocks_affected"]} 只股票日期格式不一致:')
        print(f'  last_updated 需修复: {stats["last_updated"]}')
        print(f'  article.date 需修复: {stats["article_date"]}')
        
        if fix:
            master['stocks'] = stocks
            save_master(PROJECT_ROOT, master)
            print(f'[OK] 已修复并保存')
        else:
            print(f'[INFO] 运行 --fix 以自动修复')
    else:
        print(f'[OK] 所有日期格式均符合 YYYY-MM-DD 规范（{len(stocks)} 只股票）')
    
    return stats


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='规范化 stocks_master.json 日期格式')
    parser.add_argument('--fix', action='store_true', help='自动修复不一致的日期格式')
    args = parser.parse_args()
    check_and_fix(args.fix)
