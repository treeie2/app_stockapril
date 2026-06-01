import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load master
with open('data/stocks/stocks_master.json','r',encoding='utf-8') as f:
    master = json.load(f)

stocks = master.get('stocks', {})

if isinstance(stocks, dict):
    count = len(stocks)
    print(f"📊 Master: {count} 只股票 (字典格式)")
elif isinstance(stocks, list):
    count = len(stocks)
    print(f"📊 Master: {count} 只股票 (列表格式, 已弃用)")
    stocks = {s.get('code','?'): s for s in stocks}
else:
    print(f"❌ 未知格式: {type(stocks)}")
    sys.exit(1)

print(f"📅 更新日期: {master.get('updated_at', 'N/A')}")

# Check article5 stocks
article5_codes = ['603659','600884','300890','835185','300035','001301']
article5_names = ['璞泰来','杉杉股份','翔丰华','贝特瑞','中科电气','尚太科技']
print("\n🔍 文章5 个股校验:")
all_ok = True
for code, name in zip(article5_codes, article5_names):
    s = stocks.get(code)
    if not s:
        print(f"  ❌ {code} {name}: 不存在!")
        all_ok = False
        continue
    issues = []
    if not s.get('core_business'): issues.append('缺core_business')
    if not s.get('industry_position'): issues.append('缺industry_position')
    if not s.get('chain'): issues.append('缺chain')
    if not s.get('articles'): issues.append('缺articles')
    article_count = len(s.get('articles', []))
    last_updated = s.get('last_updated', '')
    concept_count = len(s.get('concepts', []))
    print(f"  {'✅' if not issues else '⚠️'} {code} {name}: articles={article_count}, concepts={concept_count}, updated={last_updated}" + (f" 问题: {', '.join(issues)}" if issues else ""))

# Check groups
print("\n🔍 分组校验:")
with open('data/groups/groups.json', 'r', encoding='utf-8') as f:
    groups = json.load(f)
for g in groups.get('groups', []):
    print(f"  📁 {g['name']}: {len(g.get('stocks',[]))} 只个股 ({', '.join(g.get('stocks',[])[:5])}...)")

# Firestore article subcollection check
print("\n🔍 Firestore 文章子集校验:")
from sync_stocks_to_firebase import get_firebase_app
from firebase_admin import firestore
app = get_firebase_app()
if app:
    db = firestore.client()
    for code in article5_codes:
        doc_ref = db.collection('stocks').document(code)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            article_count = len(data.get('articles', data.get('article_sources', [])))
            articles_ref = doc_ref.collection('articles').list_documents()
            sub_count = len(list(articles_ref))
            print(f"  {'✅' if article_count > 0 else '⚠️'} {code}: doc={article_count} articles, sub={sub_count}")
        else:
            print(f"  ❌ {code}: Firestore 文档不存在!")
else:
    print("  ⚠️ Firebase 不可用，跳过校验")

print("\n✅ 校验完成!" if all_ok else "\n⚠️ 存在部分问题，已标记")