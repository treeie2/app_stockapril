"""Generate efficient Supabase SQL batches for stocks"""
import json, re
from pathlib import Path

PROJECT = Path(r"e:\github\stock-research-backup")

def safe_list(v, limit=None):
    """Handle both string and list values"""
    if isinstance(v, str):
        v = [v] if v.strip() else []
    if not isinstance(v, list):
        v = []
    return v[:limit] if limit else v

# Load stocks
with open(PROJECT / "data" / "stocks" / "stocks_master.json", "r", encoding="utf-8") as f:
    master = json.load(f)
stocks = master.get("stocks", {})

# Generate stocks SQL in batches of 100 (compact, no articles for first pass)
batch_size = 100
stock_list = list(stocks.items())
for batch_idx in range(0, len(stock_list), batch_size):
    batch = stock_list[batch_idx:batch_idx + batch_size]
    lines = []
    for code, s in batch:
        name = str(s.get("name", "")).replace("'", "''")
        board = str(s.get("board", "")).replace("'", "''")
        industry = str(s.get("industry", "")).replace("'", "''")
        mc = s.get("mention_count", 0)
        lu = str(s.get("last_updated", "")).replace("'", "''")
        concepts = json.dumps(safe_list(s.get("concepts"), 5), ensure_ascii=False).replace("'", "''")
        products = json.dumps(safe_list(s.get("products"), 5), ensure_ascii=False).replace("'", "''")
        cb = json.dumps(safe_list(s.get("core_business"), 3), ensure_ascii=False).replace("'", "''")
        ip = json.dumps(safe_list(s.get("industry_position"), 3), ensure_ascii=False).replace("'", "''")
        ch = json.dumps(safe_list(s.get("chain")), ensure_ascii=False).replace("'", "''")
        partners = json.dumps(safe_list(s.get("partners"), 3), ensure_ascii=False).replace("'", "''")
        
        # Articles: just store count for now
        articles_cnt = len(s.get("articles", []))
        
        lines.append(f"INSERT INTO stocks (code,name,board,industry,concepts,products,core_business,industry_position,chain,partners,mention_count,last_updated,articles,detail_texts) VALUES ('{code}','{name}','{board}','{industry}','{concepts}'::jsonb,'{products}'::jsonb,'{cb}'::jsonb,'{ip}'::jsonb,'{ch}'::jsonb,'{partners}'::jsonb,{mc},'{lu}','[]'::jsonb,'[]'::jsonb) ON CONFLICT (code) DO UPDATE SET name=EXCLUDED.name,board=EXCLUDED.board,industry=EXCLUDED.industry,concepts=EXCLUDED.concepts,products=EXCLUDED.products,mention_count=EXCLUDED.mention_count,last_updated=EXCLUDED.last_updated;")
    
    fname = PROJECT / f"_stock_batch_{batch_idx//batch_size:02d}.sql"
    with open(fname, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{fname.name}: {len(lines)} stocks, {fname.stat().st_size // 1024}KB")

print(f"\nGenerated {len(stock_list)//batch_size + 1} batches for {len(stock_list)} stocks")
