# -*- coding: utf-8 -*-
"""
一键同步 stocks_master.json + groups.json + hot_topics.json 到 Supabase
替代原有的 Firebase 同步脚本

使用方式：
  1. 先安装依赖: pip install supabase
  2. 在 supabase_config.json 中填入你的 Supabase URL 和 Key
  3. 运行: python sync_to_supabase.py
"""

import json
import sys
import io
from pathlib import Path
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent

# ============================================================
# 配置：从 supabase_config.json 读取
# ============================================================
CONFIG_FILE = BASE_DIR / "supabase_config.json"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
else:
    config_data = {}

SUPABASE_URL = config_data.get("SUPABASE_URL") or os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = config_data.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 未配置 Supabase 连接信息！")
    print("   请创建 supabase_config.json 或设置环境变量 SUPABASE_URL / SUPABASE_KEY")
    print(f"   格式: {{\"SUPABASE_URL\": \"https://xxx.supabase.co\", \"SUPABASE_KEY\": \"eyJ...\"}}")
    sys.exit(1)


def get_supabase_client():
    """获取 Supabase 客户端"""
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # 测试连接
        client.table("stocks").select("code", count="exact").limit(1).execute()
        return client
    except Exception as e:
        print(f"❌ Supabase 连接失败: {e}")
        return None


def sync_stocks(client):
    """同步 stocks_master.json 到 Supabase stocks 表"""
    data_file = BASE_DIR / "data" / "stocks" / "stocks_master.json"
    if not data_file.exists():
        print(f"  ⚠️ 文件不存在: {data_file}")
        return 0, 0

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stocks_dict = data.get('stocks', {})
    stocks_to_sync = [
        (code, stock) for code, stock in stocks_dict.items()
        if isinstance(stock, dict) and stock.get('name')
    ]

    print(f"\n📊 同步股票数据: {len(stocks_to_sync)} 只")
    success = 0
    failed = 0

    # 分批 upsert（每批 500 条）
    batch_size = 500
    for i in range(0, len(stocks_to_sync), batch_size):
        batch = stocks_to_sync[i:i + batch_size]
        rows = []
        for code, stock in batch:
            rows.append({
                "code": code,
                "name": stock.get("name", ""),
                "board": stock.get("board", ""),
                "industry": stock.get("industry", ""),
                "concepts": json.dumps(stock.get("concepts", [])),
                "products": json.dumps(stock.get("products", [])),
                "core_business": json.dumps(stock.get("core_business", [])),
                "industry_position": json.dumps(stock.get("industry_position", [])),
                "chain": json.dumps(stock.get("chain", [])),
                "partners": json.dumps(stock.get("partners", [])),
                "mention_count": stock.get("mention_count", 0),
                "last_updated": stock.get("last_updated", ""),
                "articles": json.dumps(stock.get("articles", [])),
                "detail_texts": json.dumps(stock.get("detail_texts", [])),
            })

        try:
            resp = client.table("stocks").upsert(rows, ignore_duplicates=False).execute()
            success += len(rows)
        except Exception as e:
            failed += len(rows)
            print(f"  ❌ 批次 {i//batch_size+1} 失败: {e}")

        batch_num = i // batch_size + 1
        total_batches = (len(stocks_to_sync) + batch_size - 1) // batch_size
        print(f"  [批次 {batch_num}/{total_batches}] {i+len(rows)}/{len(stocks_to_sync)}")

    return success, failed


def sync_groups(client):
    """同步 groups.json 到 Supabase groups_data 表"""
    data_file = BASE_DIR / "data" / "groups" / "groups.json"
    if not data_file.exists():
        print(f"  ⚠️ 文件不存在: {data_file}")
        return 0, 0

    with open(data_file, 'r', encoding='utf-8') as f:
        groups = json.load(f)

    rows = []
    for g in groups.get("groups", []):
        rows.append({
            "id": g["id"],
            "name": g["name"],
            "description": g.get("description", ""),
            "color": g.get("color", "#3b82f6"),
            "icon": g.get("icon", "📁"),
            "stocks": json.dumps(g.get("stocks", [])),
            "created_at": g.get("created_at", ""),
            "updated_at": g.get("updated_at", ""),
        })

    print(f"\n📁 同步分组数据: {len(rows)} 个")
    try:
        if rows:
            client.table("groups_data").upsert(rows, ignore_duplicates=False).execute()
        return len(rows), 0
    except Exception as e:
        print(f"  ❌ 分组同步失败: {e}")
        return 0, len(rows)


def sync_hot_topics(client):
    """同步 hot_topics.json 到 Supabase hot_topics 表"""
    data_file = BASE_DIR / "data" / "hot_topics" / "hot_topics.json"
    if not data_file.exists():
        print(f"  ⚠️ 文件不存在: {data_file}")
        return 0, 0

    with open(data_file, 'r', encoding='utf-8') as f:
        topics = json.load(f)

    rows = []
    for t in topics.get("topics", []):
        rows.append({
            "id": t["id"],
            "name": t["name"],
            "drivers": t.get("drivers", ""),
            "stocks": json.dumps(t.get("stocks", [])),
            "display": t.get("display", True),
            "created_at": t.get("created_at", ""),
            "updated_at": t.get("updated_at", ""),
        })

    print(f"\n🔥 同步热点数据: {len(rows)} 个")
    try:
        if rows:
            client.table("hot_topics").upsert(rows, ignore_duplicates=False).execute()
        return len(rows), 0
    except Exception as e:
        print(f"  ❌ 热点同步失败: {e}")
        return 0, len(rows)


def main():
    print(f"{'='*60}")
    print(f"  同步到 Supabase")
    print(f"{'='*60}")

    client = get_supabase_client()
    if not client:
        return

    # 1. 同步股票
    s_s, s_f = sync_stocks(client)
    print(f"  ✅ 股票: {s_s} 成功, {s_f} 失败")

    # 2. 同步分组
    g_s, g_f = sync_groups(client)
    print(f"  ✅ 分组: {g_s} 成功, {g_f} 失败")

    # 3. 同步热点
    h_s, h_f = sync_hot_topics(client)
    print(f"  ✅ 热点: {h_s} 成功, {h_f} 失败")

    print(f"\n{'='*60}")
    print(f"  🎉 同步完成!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()