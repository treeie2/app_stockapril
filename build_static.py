#!/usr/bin/env python3
"""Build static GitHub Pages site from stocks_master + lyt data"""
import json, gzip, shutil, os, requests
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
OUT = ROOT / "gh-pages"
DATA = OUT / "data"
CHARTS = OUT / "charts"
STOCK = OUT / "stock"

for d in [OUT, DATA, CHARTS, STOCK]:
    d.mkdir(parents=True, exist_ok=True)

# ======== 1. LOAD SOURCE DATA ========
with open(ROOT / "data/stocks/stocks_master.json","r",encoding="utf-8") as f:
    master = json.load(f)

# Try load lyt data
lyt_scores, lyt_groups, lyt_signals = {}, {}, {}
try:
    r = requests.get("https://raw.githubusercontent.com/treeie2/lyt/main/five_dim_scores.json", timeout=15)
    lyt_scores = r.json()
    r = requests.get("https://raw.githubusercontent.com/treeie2/lyt/main/stock_groups.json", timeout=15)
    lyt_groups = r.json()
    r = requests.get("https://raw.githubusercontent.com/treeie2/lyt/main/daily_signals.json", timeout=15)
    lyt_signals = r.json()
    print(f"lyt: {len(lyt_scores)} scores, {len(lyt_groups)} groups, {lyt_signals.get('total',0)} signals")
except Exception as e:
    print(f"lyt load failed: {e}")

# ======== 2. BUILD STOCK SUMMARY ========
stocks = master.get("stocks", {})
summary = []
detail_files = []

for code, s in stocks.items():
    if not (code.startswith(('00','30','60','68','92'))):
        continue
    
    name = s.get("name","")
    arts = s.get("articles",[])
    concepts = s.get("concepts",[])[:5]
    cb = s.get("core_business",[])[:3]
    ip = s.get("industry_position",[])[:2]
    
    # Get lyt score
    lyt = lyt_scores.get(code,{})
    dims = lyt.get("dims",[])
    
    # Get lyt signals count
    sigs = lyt_signals.get("signals",{}).get(code,[])
    sig_count = len(sigs)
    latest_sig = sigs[0].get("score","") if sigs else ""
    
    # Get latest article date
    dates = [a.get("date","")[:10] for a in arts if a.get("date")]
    latest_date = max(dates) if dates else ""
    
    # Articles count
    mention = s.get("mention_count", 0)
    
    item = {
        "c": code, "n": name, "m": mention, "d": latest_date,
        "t": concepts, "b": cb, "p": ip,
        "sc": sig_count, "ls": latest_sig,
        "dm": dims, "ly": lyt.get("score",0)
    }
    summary.append(item)
    
    # Save detail file (articles stripped of long text)
    detail = {
        "c": code, "n": name, "b": s.get("board",""),
        "i": s.get("industry",""), "m": mention, "d": latest_date,
        "t": s.get("concepts",[]), "pr": s.get("products",[]),
        "cb": s.get("core_business",[]),
        "ip": s.get("industry_position",[]),
        "ch": s.get("chain",[]), "pa": s.get("partners",[]),
        "arts": [{"ti": a.get("title",""), "dt": a.get("date","")[:10],
                  "ac": a.get("accidents",[]), "in": a.get("insights",[]),
                  "km": a.get("key_metrics",[]) } for a in arts[:10]]
    }
    fp = STOCK / f"{code}.json"
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(detail, f, ensure_ascii=False)
    detail_files.append(fp)

# Save summary (sort by mention_count desc)
summary.sort(key=lambda x: (-x["m"], x["c"]))
with gzip.open(DATA / "summary.json.gz", "wt", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False)
print(f"Summary: {len(summary)} stocks")

# ======== 3. BUILD GROUPS ========
groups_list = []

# Merge lyt groups
if isinstance(lyt_groups, list):
    for g in lyt_groups:
        if isinstance(g, dict):
            groups_list.append({
                "id": g.get("id",""), "n": g.get("name",""),
                "d": g.get("description",""), "s": g.get("stocks",[]),
                "c": g.get("color","#3b82f6"), "src": "lyt"
            })

# Merge app_stockapril groups
with open(ROOT / "data/groups/groups.json","r",encoding="utf-8") as f:
    local_groups = json.load(f).get("groups",[])

# Merge hot_topics into groups
with open(ROOT / "data/hot_topics/hot_topics.json","r",encoding="utf-8") as f:
    topics = json.load(f).get("topics",[])
for t in topics:
    groups_list.append({
        "id": t.get("id",""), "n": "🔥 "+t.get("name",""),
        "d": t.get("drivers",""), "s": t.get("stocks",[]),
        "c": "#f59e0b", "src": "topic"
    })

for g in local_groups:
    groups_list.append({
        "id": g.get("id",""), "n": g.get("name",""),
        "d": g.get("description",""), "s": g.get("stocks",[]),
        "c": g.get("color","#3b82f6"), "src": "stockapril"
    })

# Deduplicate by name
seen = set()
unique_groups = []
for g in groups_list:
    if g["n"] not in seen:
        seen.add(g["n"])
        unique_groups.append(g)

with gzip.open(DATA / "groups.json.gz", "wt", encoding="utf-8") as f:
    json.dump(unique_groups, f, ensure_ascii=False)
print(f"Groups: {len(unique_groups)}")

# ======== 4. GENERATE SIGNALS MAP ========
signals_map = lyt_signals.get("signals",{})
with gzip.open(DATA / "signals.json.gz", "wt", encoding="utf-8") as f:
    json.dump(signals_map, f, ensure_ascii=False)
print(f"Signals: {len(signals_map)} stocks")

# ======== 5. COPY LYT CHARTS ========
for i in range(1, 13):
    for code in ["000967","002452","002046","002156","002580","002861","000925",
                 "000519","688689","300440","301265","600719","603010","603061",
                 "600596","688179","300966","600516","300540","600584","002068",
                 "002876","000000"]:
        url = f"https://raw.githubusercontent.com/treeie2/lyt/main/chart_{i:02d}_{code}.html"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                fp = CHARTS / f"chart_{i:02d}_{code}.html"
                open(fp,"w",encoding="utf-8").write(r.text)
                print(f"  chart: chart_{i:02d}_{code}")
        except: pass

print(f"\n[DONE] Static site built in {OUT}")
print(f"  {len(summary)} stocks, {len(unique_groups)} groups")
print(f"  data/summary.json.gz, data/groups.json.gz, data/signals.json.gz")
print(f"  stock/*.json ({len(detail_files)} files)")
