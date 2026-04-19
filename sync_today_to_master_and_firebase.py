#!/usr/bin/env python3
"""
同步今日新增个股的详细数据到 stocks_master.json 和 Firebase
"""
import json
import requests
from pathlib import Path
from datetime import datetime

# Firebase 配置
FIREBASE_PROJECT_ID = "stock-research-669e1"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

def sync_to_master():
    """同步今日数据到 stocks_master.json"""
    print("🚀 同步今日新增个股到 stocks_master.json...\n")
    
    # 读取今日数据
    today_file = Path("e:/github/stock-research-backup/data/master/stocks/2026-04-19.json")
    with open(today_file, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    
    today_stocks = today_data.get('stocks', {})
    print(f"📊 今日新增 {len(today_stocks)} 只个股")
    
    # 读取 stocks_master.json
    master_file = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    master_stocks = master_data.get('stocks', {})
    print(f"📊 stocks_master 原有 {len(master_stocks)} 只个股")
    
    # 更新或新增个股
    updated_count = 0
    added_count = 0
    
    for code, stock in today_stocks.items():
        if code in master_stocks:
            # 更新现有个股（保留原有数据，更新今日数据）
            master_stocks[code].update(stock)
            updated_count += 1
            print(f"  🔄 更新: {code} {stock.get('name', '')}")
        else:
            # 新增个股
            master_stocks[code] = stock
            added_count += 1
            print(f"  ➕ 新增: {code} {stock.get('name', '')}")
    
    # 保存回 stocks_master.json
    master_data['stocks'] = master_stocks
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ stocks_master.json 更新完成:")
    print(f"   ➕ 新增: {added_count} 只")
    print(f"   🔄 更新: {updated_count} 只")
    print(f"   📊 总计: {len(master_stocks)} 只")
    
    return today_stocks

def sync_to_firebase(stocks):
    """同步个股到 Firebase"""
    print("\n🚀 同步个股到 Firebase...\n")
    
    success_count = 0
    error_count = 0
    errors = []
    
    for code, stock in stocks.items():
        try:
            # 构建文档路径
            doc_url = f"{FIREBASE_BASE_URL}/stocks/{code}"
            
            # 转换数据为 Firestore 格式
            firestore_data = {
                "fields": {
                    "name": {"stringValue": stock.get("name", "")},
                    "code": {"stringValue": code},
                    "board": {"stringValue": stock.get("board", "")},
                    "industry": {"stringValue": stock.get("industry", "")},
                    "mention_count": {"integerValue": str(stock.get("mention_count", 0))},
                    "updated_at": {"timestampValue": datetime.now().isoformat() + "Z"}
                }
            }
            
            # 添加概念数组
            concepts = stock.get("concepts", [])
            if concepts:
                firestore_data["fields"]["concepts"] = {
                    "arrayValue": {"values": [{"stringValue": c} for c in concepts]}
                }
            
            # 添加产品数组
            products = stock.get("products", [])
            if products:
                firestore_data["fields"]["products"] = {
                    "arrayValue": {"values": [{"stringValue": p} for p in products]}
                }
            
            # 添加核心业务数组
            core_business = stock.get("core_business", [])
            if core_business:
                firestore_data["fields"]["core_business"] = {
                    "arrayValue": {"values": [{"stringValue": cb} for cb in core_business]}
                }
            
            # 添加行业地位数组
            industry_position = stock.get("industry_position", [])
            if industry_position:
                firestore_data["fields"]["industry_position"] = {
                    "arrayValue": {"values": [{"stringValue": ip} for ip in industry_position]}
                }
            
            # 添加产业链数组
            chain = stock.get("chain", [])
            if chain:
                firestore_data["fields"]["chain"] = {
                    "arrayValue": {"values": [{"stringValue": c} for c in chain]}
                }
            
            # 添加合作伙伴数组
            partners = stock.get("partners", [])
            if partners:
                firestore_data["fields"]["partners"] = {
                    "arrayValue": {"values": [{"stringValue": p} for p in partners]}
                }
            
            # 添加文章数组
            articles = stock.get("articles", [])
            if articles:
                article_values = []
                for article in articles:
                    article_map = {
                        "mapValue": {
                            "fields": {
                                "title": {"stringValue": article.get("title", "")},
                                "date": {"stringValue": article.get("date", "")},
                                "source": {"stringValue": article.get("source", "")}
                            }
                        }
                    }
                    
                    # 添加 accidents
                    accidents = article.get("accidents", [])
                    if accidents:
                        article_map["mapValue"]["fields"]["accidents"] = {
                            "arrayValue": {"values": [{"stringValue": a} for a in accidents]}
                        }
                    
                    # 添加 insights
                    insights = article.get("insights", [])
                    if insights:
                        article_map["mapValue"]["fields"]["insights"] = {
                            "arrayValue": {"values": [{"stringValue": i} for i in insights]}
                        }
                    
                    # 添加 key_metrics
                    key_metrics = article.get("key_metrics", [])
                    if key_metrics:
                        article_map["mapValue"]["fields"]["key_metrics"] = {
                            "arrayValue": {"values": [{"stringValue": km} for km in key_metrics]}
                        }
                    
                    article_values.append(article_map)
                
                firestore_data["fields"]["articles"] = {
                    "arrayValue": {"values": article_values}
                }
            
            # 发送到 Firestore
            resp = requests.patch(doc_url, json=firestore_data, timeout=10)
            if resp.status_code in [200, 201]:
                success_count += 1
                print(f"  ✅ {code} {stock.get('name', '')}")
            else:
                error_count += 1
                errors.append(f"{code}: HTTP {resp.status_code}")
                print(f"  ❌ {code} {stock.get('name', '')}: HTTP {resp.status_code}")
                    
        except Exception as e:
            error_count += 1
            errors.append(f"{code}: {str(e)}")
            print(f"  ❌ {code} {stock.get('name', '')}: {str(e)}")
    
    print(f"\n📊 Firebase 同步完成:")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {error_count}")
    
    if errors:
        print(f"\n⚠️ 错误详情 (前5个):")
        for err in errors[:5]:
            print(f"    {err}")

def main():
    """主函数"""
    # 1. 同步到 stocks_master.json
    today_stocks = sync_to_master()
    
    # 2. 同步到 Firebase
    sync_to_firebase(today_stocks)
    
    print("\n✅ 全部同步完成!")

if __name__ == "__main__":
    main()
