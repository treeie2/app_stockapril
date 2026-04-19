#!/usr/bin/env python3
"""
同步所有股票数据到 Firebase
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
    
    # 添加估值信息
    valuation = stock.get("valuation", {})
    if valuation:
        valuation_fields = {}
        for k, v in valuation.items():
            if v is not None:
                valuation_fields[k] = {"stringValue": str(v)}
        if valuation_fields:
            firestore_data["fields"]["valuation"] = {"mapValue": {"fields": valuation_fields}}
    
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
            
            for arr_field in ["accidents", "insights", "key_metrics", "target_valuation"]:
                arr_values = article.get(arr_field, [])
                if arr_values:
                    article_map["mapValue"]["fields"][arr_field] = {
                        "arrayValue": {"values": [{"stringValue": v} for v in arr_values]}
                    }
            
            article_values.append(article_map)
        
        firestore_data["fields"]["articles"] = {
            "arrayValue": {"values": article_values}
        }
    
    resp = requests.patch(doc_url, headers=headers, json=firestore_data)
    return resp.status_code in [200, 201]

def main():
    print("🚀 开始同步所有股票到 Firebase...\n")
    
    # 获取访问令牌
    print("🔑 获取 Firebase 访问令牌...")
    try:
        access_token = get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        print("✅ 获取令牌成功\n")
    except Exception as e:
        print(f"❌ 获取令牌失败: {e}")
        return
    
    # 读取 stocks_master.json
    master_file = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    print(f"📊 共有 {len(stocks)} 只股票需要同步\n")
    
    # 同步到 Firebase
    success_count = 0
    error_count = 0
    
    for i, (code, stock) in enumerate(stocks.items(), 1):
        try:
            if sync_stock_to_firebase(code, stock, headers):
                success_count += 1
                print(f"✅ [{i}/{len(stocks)}] 同步成功: {code} {stock.get('name', '')}")
            else:
                error_count += 1
                print(f"❌ [{i}/{len(stocks)}] 同步失败: {code}")
        except Exception as e:
            error_count += 1
            print(f"❌ [{i}/{len(stocks)}] 同步异常: {code} - {e}")
    
    print(f"\n🎉 同步完成！成功: {success_count}, 失败: {error_count}")

if __name__ == '__main__':
    main()
