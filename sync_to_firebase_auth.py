#!/usr/bin/env python3
"""
增量同步所有个股数据到 Firebase（带认证）
"""
import json
import requests
import time
from pathlib import Path
from datetime import datetime, timedelta

# Firebase 配置
FIREBASE_PROJECT_ID = "webstock-724"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"
CREDENTIALS_FILE = Path(".trae/rules/firebase-credentials.json")

def get_access_token():
    """使用 Service Account 获取访问令牌"""
    with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        creds = json.load(f)
    
    # 创建 JWT（简化版，实际需要签名）
    # 这里使用 Google OAuth2 token endpoint
    token_url = "https://oauth2.googleapis.com/token"
    
    # 使用 private key 创建 JWT assertion
    import jwt
    now = int(time.time())
    payload = {
        "iss": creds["client_email"],
        "sub": creds["client_email"],
        "scope": "https://www.googleapis.com/auth/datastore",
        "aud": token_url,
        "exp": now + 3600,
        "iat": now
    }
    
    # 使用 private key 签名
    assertion = jwt.encode(payload, creds["private_key"], algorithm="RS256")
    
    # 换取 access token
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion
    }
    
    response = requests.post(token_url, data=data, timeout=10)
    response.raise_for_status()
    
    token_data = response.json()
    return token_data["access_token"]

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

def sync_incremental(start_date="2026-04-17", end_date="2026-04-21"):
    """同步指定日期范围的增量数据"""
    print(f"🚀 增量同步 {start_date} 到 {end_date} 数据到 Firebase...\n")
    
    # 获取 access token
    print("🔑 获取访问令牌...")
    try:
        access_token = get_access_token()
        print("✅ 令牌获取成功\n")
    except Exception as e:
        print(f"❌ 令牌获取失败：{e}")
        print("尝试使用匿名访问...\n")
        access_token = None
    
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    # 生成日期范围
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    dates_to_sync = []
    current = start
    while current <= end:
        dates_to_sync.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    
    dates_to_sync.reverse()  # 从新到旧
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
                resp = requests.patch(doc_url, json=firestore_data, headers=headers, timeout=10)
                
                if resp.status_code in [200, 201]:
                    total_success += 1
                    print(f"    ✅ {code} {stock.get('name', '')}")
                else:
                    total_error += 1
                    print(f"    ❌ {code}: HTTP {resp.status_code} - {resp.text[:100]}")
                    
            except Exception as e:
                total_error += 1
                print(f"    ❌ {code}: {str(e)}")
    
    print(f"\n📊 同步完成:")
    print(f"  ✅ 成功：{total_success}")
    print(f"  ❌ 失败：{total_error}")

if __name__ == "__main__":
    # 同步 2026-04-17 到 2026-04-21 的数据
    sync_incremental(start_date="2026-04-17", end_date="2026-04-21")
