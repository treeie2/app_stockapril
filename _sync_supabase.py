"""
Sync stocks_master.json and groups.json to Supabase via SQL
Generates INSERT statements in batches
"""
import json, gzip, sys
from pathlib import Path

PROJECT = Path(r"e:\github\stock-research-backup")
BATCH_SIZE = 50

# 1. Read stocks
master_path = PROJECT / "data" / "stocks" / "stocks_master.json"
with open(master_path, "r", encoding="utf-8") as f:
    master = json.load(f)
stocks = master.get("stocks", {})
print(f"Stocks: {len(stocks)}")

# 2. Generate INSERT SQL for stocks in batches
all_inserts = []
stock_codes = list(stocks.keys())

def safe_val(s):
    """Escape string for SQL"""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def safe_json(v):
    """Convert Python value to JSONB-safe SQL string"""
    if v is None:
        return "'[]'::jsonb"
    if isinstance(v, str):
        return f"'{v}'"
    return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"

print("Generating stock INSERTs...")
count = 0
for code, s in stocks.items():
    name = safe_val(s.get("name", ""))
    board = safe_val(s.get("board", ""))
    industry = safe_val(s.get("industry", ""))
    concepts = safe_json(s.get("concepts", []))
    products = safe_json(s.get("products", []))
    core_biz = safe_json(s.get("core_business", []))
    ind_pos = safe_json(s.get("industry_position", []))
    chain = safe_json(s.get("chain", []))
    partners = safe_json(s.get("partners", []))
    mc = s.get("mention_count", 0)
    lu = safe_val(s.get("last_updated", ""))
    articles = safe_json(s.get("articles", []))
    dt = safe_json(s.get("detail_texts", []))
    
    sql = f"""INSERT INTO stocks (code, name, board, industry, concepts, products, core_business, industry_position, chain, partners, mention_count, last_updated, articles, detail_texts)
VALUES ({safe_val(code)}, {name}, {board}, {industry}, {concepts}, {products}, {core_biz}, {ind_pos}, {chain}, {partners}, {mc}, {lu}, {articles}, {dt})
ON CONFLICT (code) DO UPDATE SET
  name=EXCLUDED.name, board=EXCLUDED.board, industry=EXCLUDED.industry,
  concepts=EXCLUDED.concepts, products=EXCLUDED.products,
  core_business=EXCLUDED.core_business, industry_position=EXCLUDED.industry_position,
  chain=EXCLUDED.chain, partners=EXCLUDED.partners,
  mention_count=EXCLUDED.mention_count, last_updated=EXCLUDED.last_updated,
  articles=EXCLUDED.articles, detail_texts=EXCLUDED.detail_texts,
  updated_at=NOW();"""
    all_inserts.append(sql)
    count += 1

# Save SQL to file in batches
sql_path = PROJECT / "_supabase_stocks.sql"
with open(sql_path, "w", encoding="utf-8") as f:
    for i in range(0, len(all_inserts), BATCH_SIZE):
        batch = all_inserts[i:i+BATCH_SIZE]
        f.write("\n".join(batch))
        f.write("\n\n")

print(f"Generated {count} INSERTs to {sql_path}")
print(f"File size: {sql_path.stat().st_size // 1024 // 1024}MB")

# 3. Groups
groups_path = PROJECT / "data" / "groups" / "groups.json"
if groups_path.exists():
    with open(groups_path, "r", encoding="utf-8") as f:
        groups = json.load(f)
    print(f"Groups: {len(groups)}")
    
    group_sql = []
    for gid, g in groups.items():
        if isinstance(g, dict):
            name = safe_val(g.get("name", gid))
            desc = safe_val(g.get("description", ""))
            color = safe_val(g.get("color", "#3b82f6"))
            icon = safe_val(g.get("icon", ""))
            stocks_list = safe_json(g.get("stocks", []))
            ca = safe_val(g.get("created_at", ""))
            ua = safe_val(g.get("updated_at", ""))
            group_sql.append(f"""INSERT INTO groups_data (id, name, description, color, icon, stocks, created_at, updated_at)
VALUES ({safe_val(gid)}, {name}, {desc}, {color}, {icon}, {stocks_list}, {ca}, {ua})
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, stocks=EXCLUDED.stocks, updated_at=EXCLUDED.updated_at;""")
    
    gp_path = PROJECT / "_supabase_groups.sql"
    with open(gp_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(group_sql))
    print(f"Groups: {len(group_sql)} INSERTs -> {gp_path}")

print("\nDone! Run the SQL files via supabase_execute_sql in batches.")
