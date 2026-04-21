#!/usr/bin/env python3
"""
增量同步所有个股数据到 Firebase
只同步新增或更新的股票，避免全量同步
"""
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Firebase 配置
FIREBASE_PROJECT_ID = "stock-research-669e1"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

# 使用 Service Account 认证（需要 credentials 文件）
# 如果没有 credentials，使用匿名访问（需要 Firestore 规则允许）
CREDENTIALS_FILE = Path("secrets/firebase-credentials.json")

def get_access_token():
    """获取 Firebase 访问令牌"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            creds = json.load(f)
        
        # 使用 service account 换取 access token
        token_url = "https://oauth2.googleapis.com/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": create_jwt(creds)
        }
        # 简化：直接返回 token（实际需要 JWT 签名）
        # 这里使用匿名访问
        return None
    return None

def convert_to_firestore(stock, code):
    """将股票数据转换为 Firestore 格式"""
    firestore_data = {
        "fields": {
            "name": {"stringValue": stock.get("name", "")},
            "code": {"stringValue": code},
            "board": {"stringValue": stock.get("board", "")},
            "industry": {"stringValue": stock.get("industry", "")},
            "mention_count": {"integerValue": str(stock.get("mention_count", 0))},
            "updated_at": {"timestampValue": datetime.now().isoformat() + "Z"},
            "last_updated": {"stringValue": stock.get("last_updated", "")}
        }
    }
    
    # 添加可选字段
    optional_fields = {
        "concepts": "arrayValue",
        "products": "arrayValue",
        "core_business": "arrayValue",
        "industry_position": "arrayValue",
        "chain": "arrayValue",
        "partners": "arrayValue"
    }
    
    for field, field_type in optional_fields.items():
        value = stock.get(field, [])
        if value:
            firestore_data["fields"][field] = {
                field_type: {
                    "values": [{"stringValue": v} for v in value]
                }
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
            
            # 添加嵌套数组
            for nested_field in ["accidents", "insights", "key_metrics", "target_valuation", "industry_position", "products", "partners"]:
                nested_value = article.get(nested_field, [])
                if nested_value:
                    article_map["mapValue"]["fields"][nested_field] = {
                        "arrayValue": {
                            "values": [{"stringValue": v} for v in nested_value]
                        }
                    }
            
            article_values.append(article_map)
        
        firestore_data["fields"]["articles"] = {
            "arrayValue": {"values": article_values}
        }
    
    return firestore_data

def sync_incremental(days=30):
    """同步最近 N 天的增量数据"""
    print(f"🚀 增量同步最近 {days} 天数据到 Firebase...\n")
    
    # 获取最近 N 天的日期
    today = datetime.now()
    dates_to_sync = []
    for i in range(days):
        date = today - timedelta(days=i)
        dates_to_sync.append(date.strftime("%Y-%m-%d"))
    
    print(f"📅 同步日期：{dates_to_sync[0]} 到 {dates_to_sync[-1]}\n")
    
    stocks_dir = Path("e:/github/stock-research-backup/data/master/stocks")
    total_success = 0
    total_error = 0
    
    for date in dates_to_sync:
        file_path = stocks_dir / f"{date}.json"
        if not file_path.exists():
            print(f"⏭️  跳过 {date}（文件不存在）")
            continue
        
        print(f"📂 处理 {date}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stocks = data.get('stocks', {})
        if not stocks:
            print(f"  ⏭️  无数据")
            continue
        
        print(f"  📊 {len(stocks)} 只股票")
        
        # 同步每只股票
        for code, stock in stocks.items():
            try:
                doc_url = f"{FIREBASE_BASE_URL}/stocks/{code}"
                firestore_data = convert_to_firestore(stock, code)
                
                # 使用 PATCH 更新（不存在则创建）
                resp = requests.patch(doc_url, json=firestore_data, timeout=10)
                
                if resp.status_code in [200, 201]:
                    total_success += 1
                    print(f"    ✅ {code} {stock.get('name', '')}")
                else:
                    total_error += 1
                    print(f"    ❌ {code}: HTTP {resp.status_code}")
                    
            except Exception as e:
                total_error += 1
                print(f"    ❌ {code}: {str(e)}")
    
    print(f"\n📊 同步完成:")
    print(f"  ✅ 成功：{total_success}")
    print(f"  ❌ 失败：{total_error}")

if __name__ == "__main__":
    # 同步最近 30 天数据
    sync_incremental(days=30)
