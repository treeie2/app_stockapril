#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比 Firebase stocks 集合 与 本地 stocks_master.json 的内容差异"""
import os, json, sys
from datetime import datetime
os.environ["NO_PROXY"] = "*"

MASTER_FILE = "data/stocks/stocks_master.json"

def load_local_master():
    with open(MASTER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("=" * 70)
    print("📊 Firebase vs stocks_master.json 对比报告")
    print(f"⏱  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ====== 1. 本地 stocks_master.json ======
    print("\n📁 [本地] stocks_master.json")
    print("-" * 40)
    master = load_local_master()
    master_stocks = master.get("stocks", {})
    master_codes = set(master_stocks.keys())
    print(f"   版本: {master.get('version', '?')}")
    print(f"   更新: {master.get('updated_at', '?')}")
    print(f"   股票总数: {len(master_codes)}")

    # 统计字段覆盖情况
    master_with_articles = sum(1 for s in master_stocks.values() if s.get('articles'))
    master_with_lastupd = sum(1 for s in master_stocks.values() if s.get('last_updated'))
    master_with_industry = sum(1 for s in master_stocks.values() if s.get('industry_position'))
    master_with_corebiz = sum(1 for s in master_stocks.values() if s.get('core_business'))
    master_with_products = sum(1 for s in master_stocks.values() if s.get('products'))
    master_with_chain = sum(1 for s in master_stocks.values() if s.get('chain'))
    master_with_partners = sum(1 for s in master_stocks.values() if s.get('partners'))
    master_with_valuation = sum(1 for s in master_stocks.values() if s.get('valuation') or s.get('target_market_cap'))
    master_with_concepts = sum(1 for s in master_stocks.values() if s.get('concepts'))
    master_with_insights = sum(1 for s in master_stocks.values() if s.get('insights'))

    print(f"\n   📋 字段覆盖情况:")
    print(f"      articles (文章):       {master_with_articles:>5d} / {len(master_codes)}")
    print(f"      last_updated (更新):   {master_with_lastupd:>5d} / {len(master_codes)}")
    print(f"      industry_position (行业): {master_with_industry:>5d} / {len(master_codes)}")
    print(f"      core_business (业务):  {master_with_corebiz:>5d} / {len(master_codes)}")
    print(f"      products (产品):       {master_with_products:>5d} / {len(master_codes)}")
    print(f"      chain (产业链):        {master_with_chain:>5d} / {len(master_codes)}")
    print(f"      partners (伙伴):       {master_with_partners:>5d} / {len(master_codes)}")
    print(f"      valuation (估值):      {master_with_valuation:>5d} / {len(master_codes)}")
    print(f"      concepts (概念):       {master_with_concepts:>5d} / {len(master_codes)}")
    print(f"      insights (洞见):       {master_with_insights:>5d} / {len(master_codes)}")

    # 统计板块分布
    board_dist = {}
    for s in master_stocks.values():
        b = s.get('board', 'unknown')
        board_dist[b] = board_dist.get(b, 0) + 1
    print(f"\n   板块分布:")
    for b, c in sorted(board_dist.items(), key=lambda x: -x[1]):
        print(f"      {b}: {c}")

    # ====== 2. Firebase ======
    print("\n\n🔥 [Firebase] stocks 集合")
    print("-" * 40)
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        from pathlib import Path
        
        key_files = [
            Path(__file__).parent / "api" / "firebase-credentials.json",
            Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
        ]
        key_file = None
        for f in key_files:
            if f.exists():
                key_file = str(f)
                break
        if not key_file:
            print("    ❌ 未找到 Firebase 密钥文件")
            return

        cred = credentials.Certificate(key_file)
        app = firebase_admin.initialize_app(cred, {'projectId': 'webstock-724'})
        db = firestore.client()

        # 拉取所有 stocks 文档
        stocks_ref = db.collection('stocks')
        docs = list(stocks_ref.get())
        fb_total = len(docs)

        fb_codes = set()
        fb_with_articles = 0
        fb_with_lastupd = 0
        fb_with_industry = 0
        fb_with_corebiz = 0
        fb_with_products = 0
        fb_with_valuation = 0
        fb_with_concepts = 0
        fb_with_name = 0
        fb_names = {}

        for doc in docs:
            code = doc.id
            fb_codes.add(code)
            data = doc.to_dict()
            if data.get('name'):
                fb_with_name += 1
                fb_names[code] = data.get('name')
            if data.get('articles'):
                fb_with_articles += 1
            if data.get('last_updated'):
                fb_with_lastupd += 1
            if data.get('industry_position'):
                fb_with_industry += 1
            if data.get('core_business'):
                fb_with_corebiz += 1
            if data.get('products'):
                fb_with_products += 1
            if data.get('valuation') or data.get('target_market_cap'):
                fb_with_valuation += 1
            if data.get('concepts'):
                fb_with_concepts += 1

        print(f"   股票总数: {fb_total}")
        print(f"\n   字段覆盖情况:")
        print(f"      name (名称):          {fb_with_name:>5d} / {fb_total}")
        print(f"      articles (文章):       {fb_with_articles:>5d} / {fb_total}")
        print(f"      last_updated (更新):   {fb_with_lastupd:>5d} / {fb_total}")
        print(f"      industry_position (行业): {fb_with_industry:>5d} / {fb_total}")
        print(f"      core_business (业务):  {fb_with_corebiz:>5d} / {fb_total}")
        print(f"      products (产品):       {fb_with_products:>5d} / {fb_total}")
        print(f"      valuation (估值):      {fb_with_valuation:>5d} / {fb_total}")
        print(f"      concepts (概念):       {fb_with_concepts:>5d} / {fb_total}")

    except Exception as e:
        print(f"    ❌ Firebase 连接失败: {e}")
        import traceback; traceback.print_exc()
        return

    # ====== 3. 交叉对比 ======
    print("\n\n🔄 交叉对比")
    print("=" * 40)

    both = master_codes & fb_codes
    only_master = master_codes - fb_codes
    only_firebase = fb_codes - master_codes

    print(f"\n   两边都有:     {len(both)} 只")
    print(f"   仅在本地:     {len(only_master)} 只")
    print(f"   仅在 Firebase: {len(only_firebase)} 只")

    if only_master:
        print(f"\n   📋 仅在本地 stocks_master.json 的股票 (前20):")
        for code in sorted(only_master)[:20]:
            s = master_stocks[code]
            print(f"      {code} {s.get('name','?')} (研究:{'✅' if s.get('articles') else '❌'})")
        if len(only_master) > 20:
            print(f"      ... 共 {len(only_master)} 只")

    if only_firebase:
        print(f"\n   📋 仅在 Firebase 的股票 (前20):")
        count = 0
        for code in sorted(only_firebase)[:20]:
            name = fb_names.get(code, '?')
            print(f"      {code} {name}")
        if len(only_firebase) > 20:
            print(f"      ... 共 {len(only_firebase)} 只")

    # ====== 4. 研究数据深度对比 (仅两边都有的) ======
    print(f"\n\n🔬 深度对比 (两边都有的 {len(both)} 只)")
    print("=" * 40)

    # 对比有研究数据的数量
    master_research_codes = {c for c in master_codes if master_stocks[c].get('articles') or master_stocks[c].get('last_updated')}
    fb_research_codes = set()
    for doc in docs:
        if doc.id in both:
            data = doc.to_dict()
            if data.get('articles') or data.get('last_updated'):
                fb_research_codes.add(doc.id)

    both_research = master_research_codes & fb_research_codes
    only_master_research = master_research_codes - fb_research_codes
    only_fb_research = fb_research_codes - master_research_codes

    print(f"\n   两边都有研究数据:   {len(both_research)} 只")
    print(f"   仅本地有研究:       {len(only_master_research)} 只")
    print(f"   仅 Firebase 有研究: {len(only_fb_research)} 只")

    if only_master_research:
        print(f"\n   仅本地有研究数据的股票 (前10):")
        for code in sorted(only_master_research)[:10]:
            s = master_stocks[code]
            print(f"      {code} {s.get('name','?')} [更新:{s.get('last_updated','?')}]")

    # ====== 5. 名称一致性检查 ======
    print(f"\n\n🏷 名称一致性检查")
    print("=" * 40)
    name_mismatch = []
    for code in both:
        local_name = master_stocks[code].get('name', '')
        fb_name = fb_names.get(code, '')
        if local_name and fb_name and local_name != fb_name:
            name_mismatch.append((code, local_name, fb_name))
    print(f"   名称一致: {len(both) - len(name_mismatch)} 只")
    print(f"   名称不一致: {len(name_mismatch)} 只")
    if name_mismatch:
        print(f"\n   名称不一致列表 (前10):")
        for code, ln, fn in name_mismatch[:10]:
            print(f"      {code}: 本地='{ln}'  vs  Firebase='{fn}'")

    # ====== 6. 摘要 ======
    print("\n\n" + "=" * 70)
    print("📋 对比摘要")
    print("=" * 70)
    print(f"""
    ┌──────────────────────┬────────────┬────────────┬──────────┐
    │       指标           │ 本地 Master │ Firebase   │ 差异     │
    ├──────────────────────┼────────────┼────────────┼──────────┤
    │ 股票总数             │ {len(master_codes):>9} │ {fb_total:>9} │ {fb_total-len(master_codes):>+8} │
    │ 有研究数据的股票      │ {len(master_research_codes):>9} │ {len(fb_research_codes):>9} │ {len(fb_research_codes)-len(master_research_codes):>+8} │
    │ 有名称的股票          │ {len(master_codes):>9} │ {fb_with_name:>9} │ {fb_with_name-len(master_codes):>+8} │
    │ 有行业地位            │ {master_with_industry:>9} │ {fb_with_industry:>9} │ {fb_with_industry-master_with_industry:>+8} │
    │ 有核心业务            │ {master_with_corebiz:>9} │ {fb_with_corebiz:>9} │ {fb_with_corebiz-master_with_corebiz:>+8} │
    │ 有产品               │ {master_with_products:>9} │ {fb_with_products:>9} │ {fb_with_products-master_with_products:>+8} │
    │ 有估值               │ {master_with_valuation:>9} │ {fb_with_valuation:>9} │ {fb_with_valuation-master_with_valuation:>+8} │
    │ 有概念               │ {master_with_concepts:>9} │ {fb_with_concepts:>9} │ {fb_with_concepts-master_with_concepts:>+8} │
    └──────────────────────┴────────────┴────────────┴──────────┘
    """)
    print(f"   两边共有: {len(both)} 只")
    print(f"   仅本地有: {len(only_master)} 只")
    print(f"   仅 Firebase 有: {len(only_firebase)} 只")

if __name__ == "__main__":
    main()