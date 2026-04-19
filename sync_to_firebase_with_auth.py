#!/usr/bin/env python3
"""
使用服务账号凭据同步个股到 Firebase
"""
import json
import requests
import jwt
import time
from pathlib import Path
from datetime import datetime

# 加载服务账号凭据
CREDENTIALS_PATH = Path("e:/github/stock-research-backup/.trae/rules/firebase-credentials.json")

with open(CREDENTIALS_PATH, 'r') as f:
    credentials = json.load(f)

PROJECT_ID = credentials['project_id']
CLIENT_EMAIL = credentials['client_email']
PRIVATE_KEY = credentials['private_key']
TOKEN_URI = credentials['token_uri']

FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def get_access_token():
    """使用服务账号获取 OAuth 2.0 访问令牌"""
    now = int(time.time())
    payload = {
        'iss': CLIENT_EMAIL,
        'sub': CLIENT_EMAIL,
        'scope': 'https://www.googleapis.com/auth/datastore',
        'aud': TOKEN_URI,
        'iat': now,
        'exp': now + 3600
    }
    
    signed_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')
    
    token_data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': signed_jwt
    }
    
    resp = requests.post(TOKEN_URI, data=token_data)
    if resp.status_code == 200:
        return resp.json()['access_token']
    else:
        raise Exception(f"获取令牌失败: {resp.text}")

def sync_stock_to_firebase(code, stock, headers):
    """同步单个个股到 Firebase"""
    doc_url = f"{FIREBASE_BASE_URL}/stocks/{code}"
    
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
    
    # 添加数组字段
    for field_name in ["concepts", "products", "core_business", "industry_position", "chain", "partners"]:
        values = stock.get(field_name, [])
        if values:
            firestore_data["fields"][field_name] = {
                "arrayValue": {"values": [{"stringValue": v} for v in values]}
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
            
            for arr_field in ["accidents", "insights", "key_metrics", "target_valuation", "expected_price", "expected_performance", "market_valuation"]:
                arr_values = article.get(arr_field, [])
                if arr_values:
                    article_map["mapValue"]["fields"][arr_field] = {
                        "arrayValue": {"values": [{"stringValue": v} for v in arr_values]}
                    }
            
            article_values.append(article_map)
        
        firestore_data["fields"]["articles"] = {
            "arrayValue": {"values": article_values}
        }
    
    resp = requests.patch(doc_url, headers=headers, json=firestore_data, timeout=10)
    return resp.status_code in [200, 201]

def sync_today_to_firebase():
    """同步今日数据到 Firebase"""
    print("🚀 使用服务账号同步今日新增个股到 Firebase...\n")
    
    # 获取访问令牌
    print("📋 获取访问令牌...")
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    print("✅ 访问令牌获取成功\n")
    
    # 读取今日数据
    today_file = Path("e:/github/stock-research-backup/data/master/stocks/2026-04-19.json")
    with open(today_file, 'r', encoding='utf-8') as f:
        today_data = json.load(f)
    
    stocks = today_data.get('stocks', {})
    print(f"📊 今日新增 {len(stocks)} 只个股\n")
    
    success_count = 0
    error_count = 0
    errors = []
    
    for code, stock in stocks.items():
        try:
            if sync_stock_to_firebase(code, stock, headers):
                success_count += 1
                print(f"  ✅ {code} {stock.get('name', '')}")
            else:
                error_count += 1
                errors.append(f"{code}: 写入失败")
                print(f"  ❌ {code} {stock.get('name', '')}: 写入失败")
        except Exception as e:
            error_count += 1
            errors.append(f"{code}: {str(e)}")
            print(f"  ❌ {code} {stock.get('name', '')}: {str(e)}")
    
    print(f"\n📊 同步完成:")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {error_count}")
    
    if errors:
        print(f"\n⚠️ 错误详情 (前5个):")
        for err in errors[:5]:
            print(f"    {err}")

if __name__ == "__main__":
    sync_today_to_firebase()
