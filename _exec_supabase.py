"""Execute batch SQL files via Supabase. Run: python _exec_supabase.py <batch_start> <batch_end>"""
import sys, os

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end = int(sys.argv[2]) if len(sys.argv) > 2 else 35

for i in range(start, end):
    fn = f"_stock_batch_{i:02d}.sql"
    if not os.path.exists(fn):
        continue
    print(f"[{i}/{end}] {fn}...", end=" ")
    with open(fn, "r", encoding="utf-8") as f:
        sql = f.read()
    print(f"{len(sql)//1024}KB - READY")
    # Write the SQL to stdout for supabase_execute_sql
    print("=== SQL_START ===")
    print(sql)
    print("=== SQL_END ===")
