"""
Supabase 全量数据同步脚本
用法: python sync_supabase.py
前提: 已安装 psycopg2-binary (pip install psycopg2-binary)
"""
import json
from pathlib import Path
import psycopg2

PROJECT = Path(__file__).parent

# Supabase 连接信息 (从 Dashboard → Settings → Database → Connection string)
# 格式: postgresql://postgres:[YOUR_PASSWORD]@db.fcnzwhjpzfojeszzlyeo.supabase.co:5432/postgres
# 前往 https://supabase.com/dashboard/project/fcnzwhjpzfojeszzlyeo/settings/database 获取
CONN_STRING = input("请输入 Supabase 连接串 (或 .env 中的 DATABASE_URL): ").strip()

conn = psycopg2.connect(CONN_STRING)
conn.autocommit = True
cur = conn.cursor()

def safe_list(v):
    if isinstance(v, str):
        return [v] if v.strip() else []
    return v if isinstance(v, list) else []

# 1. 同步股票
print("=== 同步 stocks ===")
with open(PROJECT / "data" / "stocks" / "stocks_master.json", "r", encoding="utf-8") as f:
    master = json.load(f)
stocks = master.get("stocks", {})

batch = []
count = 0
for code, s in stocks.items():
    name = str(s.get("name", "")).replace("'", "''")[:200]
    board = str(s.get("board", ""))[:10]
    industry = str(s.get("industry", ""))[:200]
    mc = s.get("mention_count", 0) or 0
    lu = str(s.get("last_updated", ""))[:20]
    concepts = json.dumps(safe_list(s.get("concepts"))[:10], ensure_ascii=False)
    products = json.dumps(safe_list(s.get("products"))[:10], ensure_ascii=False)
    cb = json.dumps(safe_list(s.get("core_business"))[:5], ensure_ascii=False)
    ip = json.dumps(safe_list(s.get("industry_position"))[:5], ensure_ascii=False)
    chain = json.dumps(safe_list(s.get("chain"))[:5], ensure_ascii=False)
    partners = json.dumps(safe_list(s.get("partners"))[:5], ensure_ascii=False)
    
    batch.append(f"INSERT INTO stocks (code,name,board,industry,concepts,products,core_business,industry_position,chain,partners,mention_count,last_updated,articles,detail_texts) VALUES ('{code}','{name}','{board}','{industry}','{concepts}'::jsonb,'{products}'::jsonb,'{cb}'::jsonb,'{ip}'::jsonb,'{chain}'::jsonb,'{partners}'::jsonb,{mc},'{lu}','[]'::jsonb,'[]'::jsonb) ON CONFLICT (code) DO UPDATE SET name=EXCLUDED.name,board=EXCLUDED.board,industry=EXCLUDED.industry,mention_count=EXCLUDED.mention_count,last_updated=EXCLUDED.last_updated;")
    
    if len(batch) >= 100:
        cur.execute("\n".join(batch))
        count += len(batch)
        print(f"  {count}/{len(stocks)} stocks")
        batch = []

if batch:
    cur.execute("\n".join(batch))
    count += len(batch)
    print(f"  {count}/{len(stocks)} stocks - DONE!")

# 2. 同步分组
print("\n=== 同步 groups ===")
with open(PROJECT / "data" / "groups" / "groups.json", "r", encoding="utf-8") as f:
    groups = json.load(f)

batch = []
count = 0
for gid, g in groups.items():
    if not isinstance(g, dict):
        continue
    name = str(g.get("name", gid))[:200].replace("'", "''")
    desc = str(g.get("description", ""))[:500].replace("'", "''")
    color = g.get("color", "#3b82f6")[:20]
    icon = str(g.get("icon", ""))[:10]
    slist = json.dumps(g.get("stocks", []), ensure_ascii=False)
    ca = str(g.get("created_at", ""))[:20]
    ua = str(g.get("updated_at", ""))[:20]
    
    batch.append(f"INSERT INTO groups_data (id,name,description,color,icon,stocks,created_at,updated_at) VALUES ('{gid}','{name}','{desc}','{color}','{icon}','{slist}'::jsonb,'{ca}','{ua}') ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name,stocks=EXCLUDED.stocks;")
    
    if len(batch) >= 20:
        cur.execute("\n".join(batch))
        count += len(batch)
        print(f"  {count}/{len(groups)} groups")
        batch = []

if batch:
    cur.execute("\n".join(batch))
    count += len(batch)
    print(f"  {count}/{len(groups)} groups - DONE!")

# 3. 验证
cur.execute("SELECT count(*) FROM stocks")
print(f"\n✅ stocks: {cur.fetchone()[0]} rows")
cur.execute("SELECT count(*) FROM groups_data")
print(f"✅ groups: {cur.fetchone()[0]} rows")

cur.close()
conn.close()
print("\n🎉 同步完成!")
