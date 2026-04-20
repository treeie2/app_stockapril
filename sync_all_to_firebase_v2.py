#!/usr/bin/env python3
"""
同步所有股票数据到 Firebase - 改进版（带重试和批量处理）
"""
import json
import requests
import jwt
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 加载服务账号凭据
CREDENTIALS_PATH = Path("e:/github/stock-research-backup/.trae/rules/firebase-credentials.json")

with open(CREDENTIALS_PATH, 'r') as f:
    credentials = json.load(f)

PROJECT_ID = credentials['project_id']
CLIENT_EMAIL = credentials['client_email']
PRIVATE_KEY = credentials['private_key']
TOKEN_URI = credentials['token_uri']

FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# 线程本地存储
tls = threading.local()

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

def get_headers():
    """获取当前线程的请求头"""
    if not hasattr(tls, 'headers') or not tls.headers:
        access_token = get_access_token()
        tls.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    return tls.headers

def sync_stock_to_firebase(code, stock, max_retries=3):
    """同步单个个股到 Firebase（带重试）"""
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
    
    # 添加文章数组（限制数量以避免请求过大）
    articles = stock.get("articles", [])[:5]  # 只同步前5篇文章
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
                        "arrayValue": {"values": [{"stringValue": v} for v in arr_values[:3]]}  # 限制数组长度
                    }
            
            article_values.append(article_map)
        
        firestore_data["fields"]["articles"] = {
            "arrayValue": {"values": article_values}
        }
    
    # 重试机制
    for attempt in range(max_retries):
        try:
            resp = requests.patch(
                doc_url, 
                headers=get_headers(), 
                json=firestore_data,
                timeout=30
            )
            if resp.status_code in [200, 201]:
                return True, None
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text[:100]}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                return False, error_msg
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                # 重置 headers 以获取新令牌
                if hasattr(tls, 'headers'):
                    delattr(tls, 'headers')
                continue
            return False, str(e)[:100]
    
    return False, "Max retries exceeded"

def sync_batch(stock_batch, batch_num, total_batches):
    """同步一批股票"""
    success_count = 0
    error_count = 0
    
    for i, (code, stock) in enumerate(stock_batch):
        success, error = sync_stock_to_firebase(code, stock)
        global_idx = (batch_num - 1) * len(stock_batch) + i + 1
        
        if success:
            success_count += 1
            print(f"✅ [{global_idx}] 同步成功: {code} {stock.get('name', '')}")
        else:
            error_count += 1
            print(f"❌ [{global_idx}] 同步失败: {code} - {error}")
        
        # 每同步一个后暂停一下，避免请求过快
        time.sleep(0.5)
    
    return success_count, error_count

def main():
    print("🚀 开始同步所有股票到 Firebase...\n")
    
    # 读取 stocks_master.json
    master_file = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
    with open(master_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    total = len(stocks)
    print(f"📊 共有 {total} 只股票需要同步\n")
    
    # 分批处理
    batch_size = 50
    stock_items = list(stocks.items())
    batches = [stock_items[i:i+batch_size] for i in range(0, len(stock_items), batch_size)]
    
    print(f"📦 分为 {len(batches)} 批，每批 {batch_size} 只\n")
    
    total_success = 0
    total_error = 0
    
    for batch_num, batch in enumerate(batches, 1):
        print(f"\n📦 处理第 {batch_num}/{len(batches)} 批 ({len(batch)} 只)...")
        success, error = sync_batch(batch, batch_num, len(batches))
        total_success += success
        total_error += error
        
        # 每批之间暂停更长时间
        if batch_num < len(batches):
            print(f"⏳ 批次间暂停 5 秒...")
            time.sleep(5)
    
    print(f"\n🎉 同步完成！")
    print(f"   ✅ 成功: {total_success}")
    print(f"   ❌ 失败: {total_error}")
    print(f"   📊 总计: {total}")

if __name__ == '__main__':
    main()
