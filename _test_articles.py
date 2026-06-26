import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.load(open("data/stocks/stocks_master.json", "r", encoding="utf-8"))
codes = [
    "300218","000050","300054","003037","300964","300260",
    "000620","001298","300345","301348","300436","301236",
    "300976","301078","301349","301468","002383","002179",
    "000333","301449","000725","301499","000422","002388",
    "000089","002351","300286","301156","300445","002479",
    "002404","002430","301321","301367","300806","300481",
    "000543","301595"
]

missing = []
exist = []
for c in codes:
    if c in d["stocks"]:
        s = d["stocks"][c]
        exist.append(f"{c} {s['name']} ({len(s.get('articles',[]))} arts)")
    else:
        missing.append(c)

print(f"=== Exist ({len(exist)}) ===")
for e in exist:
    print(f"  {e}")
    
print(f"\n=== Missing ({len(missing)}) ===")
for m in missing:
    print(f"  {m}")
