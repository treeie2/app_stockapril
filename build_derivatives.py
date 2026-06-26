import json, gzip, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MASTER = "data/stocks/stocks_master.json"
META = "data/stocks/stocks_meta.json"
ARTICLES = "data/stocks/stocks_articles.json"
GZ = "data/stocks/stocks_master.json.gz"

print(f"Loading {MASTER}...")
with open(MASTER, "r", encoding="utf-8") as f:
    data = json.load(f)

stocks = data["stocks"]
total = len(stocks)
total_arts = sum(len(s.get("articles", [])) for s in stocks.values())
print(f"  {total} stocks, {total_arts} articles")

# 1. Meta (no articles)
print("Building stocks_meta.json...")
meta = {"version": "3.0", "updated_at": data.get("updated_at", ""), "stocks": {}}
for code, s in stocks.items():
    copy = {k: v for k, v in s.items() if k != "articles"}
    copy["article_count"] = len(s.get("articles", []))
    meta["stocks"][code] = copy

with open(META, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print(f"  -> {os.path.getsize(META)/1024/1024:.1f} MB ({os.path.getsize(META)*100/os.path.getsize(MASTER):.0f}%)")

# 2. Articles only
print("Building stocks_articles.json...")
arts_map = {code: s.get("articles", []) for code, s in stocks.items() if s.get("articles")}
with open(ARTICLES, "w", encoding="utf-8") as f:
    json.dump(arts_map, f, ensure_ascii=False, indent=2)
print(f"  -> {os.path.getsize(ARTICLES)/1024/1024:.1f} MB")

# 3. Gzip
print("Gzipping master...")
with open(MASTER, "rb") as fi, gzip.open(GZ, "wb") as fo:
    fo.writelines(fi)
print(f"  -> {os.path.getsize(GZ)/1024/1024:.1f} MB")

print(f"\nDone! Meta for fast startup, master for writes, articles for lazy load.")
