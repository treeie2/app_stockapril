#!/usr/bin/env python3
"""同步 stocks_master.json 到 Supabase (v1.0)

支持两种模式:
  1. 全量同步: python scripts/sync_to_supabase.py --full
  2. 日期增量: python scripts/sync_to_supabase.py --date 2026-06-20

用法:
  python scripts/sync_to_supabase.py --full
  python scripts/sync_to_supabase.py --date 2026-06-20

前提: pip install supabase
"""
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
STOCKS_DIR = PROJECT_ROOT / "data" / "stocks"
MASTER_FILE = STOCKS_DIR / "stocks_master.json"

SUPABASE_URL = "https://fcnzwhjpzfojeszzlyeo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjbnp3aGpwemZvamVzenpseWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE5Mzc0MTUsImV4cCI6MjA5NzUxMzQxNX0.X44fD4gto39L4Wv6S4y05iukKqxuKudnTZS1PASyj1I"


def safe_list(v, limit=None):
    if isinstance(v, str):
        v = [v] if v.strip() else []
    if not isinstance(v, list):
        v = []
    return v[:limit] if limit else v


def sync_stocks(stocks_to_sync: dict, batch_size: int = 500) -> dict:
    """用 Supabase REST API 批量 upsert 股票数据"""
    try:
        from supabase import create_client
    except ImportError:
        import os
        os.system(f"{sys.executable} -m pip install supabase -q")
        from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    records = []

    for code, s in stocks_to_sync.items():
        rec = {
            "code": code,
            "name": s.get("name", ""),
            "board": s.get("board", ""),
            "industry": s.get("industry", ""),
            "concepts": safe_list(s.get("concepts"), 10),
            "products": safe_list(s.get("products"), 5),
            "core_business": safe_list(s.get("core_business"), 5),
            "industry_position": safe_list(s.get("industry_position"), 5),
            "chain": safe_list(s.get("chain"), 5),
            "partners": safe_list(s.get("partners"), 5),
            "mention_count": s.get("mention_count", 0) or 0,
            "last_updated": s.get("last_updated", ""),
            "articles": s.get("articles", []),
            "detail_texts": s.get("detail_texts", []) or [],
        }
        records.append(rec)

    total = len(records)
    success = 0
    errors = 0

    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        try:
            supabase.table("stocks").upsert(batch).execute()
            success += len(batch)
            print(f"  [{i + len(batch)}/{total}] OK")
        except Exception as e:
            errors += 1
            print(f"  [{i + len(batch)}/{total}] ERR: {str(e)[:80]}")

    return {"total": total, "success": success, "errors": errors}


def sync_full() -> dict:
    """全量同步 stocks_master.json 到 Supabase"""
    print(f"[sync_supabase] 全量同步模式")
    print(f"[sync_supabase] 读取 {MASTER_FILE} ...")

    if not MASTER_FILE.exists():
        print(f"[sync_supabase] ERROR: {MASTER_FILE} not found")
        return {"total": 0, "success": 0, "errors": 1}

    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)

    stocks = master.get("stocks", {})
    print(f"[sync_supabase] {len(stocks)} 只股票，准备同步 ...")

    result = sync_stocks(stocks)
    print(f"[sync_supabase] 完成: {result['success']} OK, {result['errors']} errors")
    return result


def sync_date(date_str: str) -> dict:
    """增量同步指定日期的数据"""
    print(f"[sync_supabase] 日期增量模式: {date_str}")

    if not MASTER_FILE.exists():
        print(f"[sync_supabase] ERROR: {MASTER_FILE} not found")
        return {"total": 0, "success": 0, "errors": 1}

    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        master = json.load(f)

    all_stocks = master.get("stocks", {})

    # 筛选当日更新的股票
    day_stocks = {
        code: s for code, s in all_stocks.items()
        if s.get("last_updated", "") == date_str
    }

    if not day_stocks:
        # 回退：检查 articles 中是否有当日文章
        for code, s in all_stocks.items():
            for a in s.get("articles", []):
                if a.get("date", "") == date_str:
                    day_stocks[code] = s
                    break

    print(f"[sync_supabase] 当日涉及 {len(day_stocks)} 只股票")

    if not day_stocks:
        print(f"[sync_supabase] WARN: 无当日数据，跳过")
        return {"total": 0, "success": 0, "errors": 0}

    result = sync_stocks(day_stocks)
    print(f"[sync_supabase] 完成: {result['success']} OK, {result['errors']} errors")
    return result


def main():
    parser = argparse.ArgumentParser(description="Sync stocks_master.json to Supabase")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--full", action="store_true", help="全量同步 stocks_master.json")
    group.add_argument("--date", type=str, help="增量同步指定日期 (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.full:
        result = sync_full()
    else:
        result = sync_date(args.date)

    sys.exit(0 if result["errors"] == 0 else 1)


if __name__ == "__main__":
    main()
