#!/usr/bin/env python3
"""全量同步 stocks_master.json 到 Firebase Firestore（分批，防超限）"""
import json, time, hashlib, re
from pathlib import Path

TIMEOUT = 60  # 秒
BATCH_SIZE = 100  # 每批100只股票

# ==================== 安装 firebase-admin ====================
# pip install firebase-admin
# =============================================================

import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json"
JSON_PATH = Path(__file__).parent / "data" / "stocks" / "stocks_master.json"

def main():
    print(f"[INFO] 初始化 Firebase...")
    cred = credentials.Certificate(str(CRED_PATH))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    
    print(f"[INFO] 读取 stocks_master.json...")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    stocks = data.get("stocks", {})
    total = len(stocks)
    print(f"[INFO] {total} stocks, estimated writes: ~{total + sum(len(s.get('articles',[])) for s in stocks.values())}")
    
    codes = list(stocks.keys())
    written_stocks = 0
    written_articles = 0
    skipped = 0
    
    for batch_start in range(0, total, BATCH_SIZE):
        batch = codes[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        print(f"\n[BATCH {batch_num}] {batch_start+1}-{min(batch_start+BATCH_SIZE, total)}/{total}")
        
        for code in batch:
            stock = stocks[code]
            name = stock.get("name", "")
            if len(name) < 2:
                continue
            
            # 构建 stock doc
            stock_doc = {
                "code": code,
                "name": name,
                "board": stock.get("board", ""),
                "industry": stock.get("industry", ""),
                "concepts": stock.get("concepts", []),
                "products": _list(stock.get("products", [])),
                "core_business": _list(stock.get("core_business", [])),
                "industry_position": _list(stock.get("industry_position", [])),
                "chain": _list(stock.get("chain", [])),
                "partners": _list(stock.get("partners", [])),
                "mention_count": stock.get("mention_count", 0),
                "last_updated": stock.get("last_updated", ""),
            }
            
            try:
                db.collection("stocks").document(code).set(stock_doc, merge=True)
                written_stocks += 1
            except Exception as e:
                print(f"  [SKIP] {code} {name}: {e}")
                skipped += 1
                time.sleep(2)
                continue
            
            # 写入文章子集合
            for art in stock.get("articles", []):
                source = art.get("source", "")
                if not source:
                    continue
                article_id = hashlib.sha1(source.encode()).hexdigest()[:16]
                
                article_doc = {
                    "title": art.get("title", ""),
                    "date": art.get("date", ""),
                    "source": source,
                    "industry_background": art.get("industry_background", []),
                    "accidents": art.get("accidents", []),
                    "insights": art.get("insights", []),
                    "key_metrics": art.get("key_metrics", []),
                    "target_valuation": art.get("target_valuation", []),
                }
                
                try:
                    db.collection("stocks").document(code)\
                      .collection("articles").document(article_id)\
                      .set(article_doc, merge=True)
                    written_articles += 1
                except Exception as e:
                    print(f"  [SKIP] article {article_id[:8]}: {e}")
                    time.sleep(1)
            
            # 进度打印
            if written_stocks % 50 == 0:
                print(f"  progress: {written_stocks} stocks, {written_articles} articles")
        
        print(f"  batch done. Total: {written_stocks} stocks, {written_articles} articles")
        time.sleep(1)  # 批次间隔
    
    print(f"\n[DONE] {written_stocks} stocks, {written_articles} articles, {skipped} skipped")
    # 关闭连接
    firebase_admin.delete_app(firebase_admin.get_app())


def _list(v):
    if isinstance(v, str):
        return [v] if v.strip() else []
    if isinstance(v, list):
        return v
    return []


if __name__ == "__main__":
    main()
