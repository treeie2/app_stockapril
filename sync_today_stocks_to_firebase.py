#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将今日更新的个股数据同步到 Firebase (使用 REST API + 服务账号认证)
"""
import json
import requests
from pathlib import Path
from datetime import datetime
import time
import google.auth.transport.requests
from google.oauth2 import service_account

# Firebase 配置
FIREBASE_PROJECT_ID = "webstock-724"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

# 认证配置
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

def get_access_token():
    """获取 Firebase 访问令牌"""
    # 查找服务账号密钥文件
    key_files = [
        Path(__file__).parent / 'serviceAccountKey.json',
        Path(__file__).parent / 'firebase_key.json',
        Path(__file__).parent / '.trae' / 'rules' / 'firebase-credentials.json',
    ]
    
    key_file = None
    for f in key_files:
        if f.exists():
            key_file = f
            break
    
    if not key_file:
        print("❌ 未找到 Firebase 服务账号密钥文件")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(key_file), scopes=SCOPES
        )
        
        # 刷新令牌
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        
        token = credentials.token
        print(f"✅ 获取访问令牌成功 (使用：{key_file.name})")
        return token
    except Exception as e:
        print(f"❌ 获取令牌失败：{e}")
        return None

def article_to_firestore(article: dict) -> dict:
    """将单篇文章转换为 Firestore 格式"""
    firestore_fields = {}
    
    # 字符串字段
    for field in ['title', 'date', 'source', 'insights', 'accident']:
        if field in article and article[field]:
            value = article[field]
            if isinstance(value, str):
                firestore_fields[field] = {"stringValue": value}
    
    # 数组长字段
    for field in ['key_metrics', 'target_valuation']:
        if field in article and article[field]:
            value = article[field]
            if isinstance(value, list):
                firestore_fields[field] = {
                    "arrayValue": {
                        "values": [{"stringValue": str(v)} for v in value]
                    }
                }
    
    return firestore_fields

def merge_articles(existing_articles: list, new_articles: list) -> list:
    """增量合并 articles，按 (source, title) 去重"""
    # 创建现有文章的集合用于去重
    existing_set = set()
    for article in existing_articles:
        source = article.get('source', '')
        title = article.get('title', '')
        existing_set.add((source, title))
    
    # 合并新文章
    merged = existing_articles.copy()
    for article in new_articles:
        source = article.get('source', '')
        title = article.get('title', '')
        if (source, title) not in existing_set:
            merged.append(article)
            existing_set.add((source, title))
    
    return merged

def stock_to_firestore_with_merge(stock: dict, existing_data: dict) -> dict:
    """将股票数据转换为 Firestore 格式，并合并现有数据"""
    firestore_data = {
        "fields": {
            "name": {"stringValue": stock.get("name", "")},
            "code": {"stringValue": stock.get("code", "")},
            "board": {"stringValue": stock.get("board", "")},
            "industry": {"stringValue": stock.get("industry", "")},
            "mention_count": {"integerValue": stock.get("mention_count", 0)},
            "last_updated": {"stringValue": stock.get("last_updated", "")},
            "updated_at": {"timestampValue": datetime.now().isoformat() + "Z"}
        }
    }
    
    # 合并数组字段（包括空数组）
    for field_name in ['concepts', 'products', 'core_business', 'industry_position', 'chain', 'partners']:
        field_value = stock.get(field_name, [])
        firestore_data["fields"][field_name] = {
            "arrayValue": {
                "values": [{"stringValue": str(v)} for v in field_value]
            }
        }
    
    # 添加估值信息
    valuation = stock.get("valuation", {})
    if valuation:
        if valuation.get("target_market_cap"):
            firestore_data["fields"]["target_market_cap"] = {
                "stringValue": valuation.get("target_market_cap", "")
            }
        if valuation.get("target_market_cap_billion"):
            firestore_data["fields"]["target_market_cap_billion"] = {
                "doubleValue": float(valuation.get("target_market_cap_billion", 0))
            }
    
    # 添加 insights
    insights = stock.get("insights", "")
    if insights:
        if isinstance(insights, str):
            firestore_data["fields"]["insights"] = {"stringValue": insights}
        elif isinstance(insights, list):
            firestore_data["fields"]["insights"] = {
                "arrayValue": {
                    "values": [{"stringValue": str(i)} for i in insights]
                }
            }
    
    # 添加 key_metrics
    key_metrics = stock.get("key_metrics", [])
    if key_metrics:
        firestore_data["fields"]["key_metrics"] = {
            "arrayValue": {
                "values": [{"stringValue": str(m)} for m in key_metrics]
            }
        }
    
    # 添加 accident
    accident = stock.get("accident", "")
    if accident:
        firestore_data["fields"]["accident"] = {"stringValue": accident}
    
    # 🔥 关键：增量合并 articles
    new_articles = stock.get("articles", [])
    existing_articles_raw = existing_data.get('articles', {}).get('arrayValue', {}).get('values', [])
    
    # 转换为普通列表
    existing_articles = []
    for article_raw in existing_articles_raw:
        if 'mapValue' in article_raw:
            article_dict = {}
            fields = article_raw['mapValue'].get('fields', {})
            for key, value in fields.items():
                if 'stringValue' in value:
                    article_dict[key] = value['stringValue']
                elif 'arrayValue' in value:
                    arr = value['arrayValue'].get('values', [])
                    article_dict[key] = [v.get('stringValue', '') for v in arr]
            existing_articles.append(article_dict)
    
    # 合并 articles
    merged_articles = merge_articles(existing_articles, new_articles)
    
    if merged_articles:
        firestore_data["fields"]["articles"] = {
            "arrayValue": {
                "values": [
                    {"mapValue": {"fields": article_to_firestore(article)}}
                    for article in merged_articles
                ]
            }
        }
    
    return firestore_data

def sync_stocks_to_firestore(stocks_file: str):
    """同步股票数据到 Firestore"""
    print(f"\n{'='*80}")
    print(f"开始同步股票数据到 Firebase")
    print(f"{'='*80}\n")
    
    # 读取股票数据
    with open(stocks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    update_info = data.get('update_info', {})
    
    print(f"📊 更新信息:")
    print(f"   - 日期：{update_info.get('date', 'N/A')}")
    print(f"   - 来源：{update_info.get('source', 'N/A')}")
    print(f"   - 文章数量：{update_info.get('article_count', 0)}")
    print(f"   - 更新股票：{update_info.get('updated_stocks', 0)}")
    print(f"   - 新增股票：{update_info.get('new_stocks', 0)}")
    print(f"\n")
    
    # 获取访问令牌
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌，终止同步")
        return 0, len(stocks)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 同步每只股票
    success_count = 0
    failed_count = 0
    max_retries = 3
    
    for code, stock in stocks.items():
        stock_name = stock.get('name', 'N/A')
        print(f"同步股票：{code} - {stock_name}")
        
        # 先从 Firebase 读取现有数据
        existing_data = {}
        try:
            resp = requests.get(f"{FIREBASE_BASE_URL}/stocks/{code}", headers=headers, timeout=10)
            if resp.status_code == 200:
                existing_data = resp.json().get('fields', {})
                print(f"  📖 读取到 {len(existing_data.get('articles', {}).get('arrayValue', {}).get('values', []))} 篇现有文章")
        except Exception as e:
            print(f"  ⚠️ 读取现有数据失败：{e}，将使用新数据")
        
        # 转换为 Firestore 格式（合并现有数据）
        firestore_data = stock_to_firestore_with_merge(stock, existing_data)
        
        # 构建文档 URL
        doc_url = f"{FIREBASE_BASE_URL}/stocks/{code}"
        
        # 重试机制
        attempt = 0
        while attempt < max_retries:
            try:
                # 使用 PATCH 方法更新（如果不存在则创建）
                response = requests.patch(
                    doc_url,
                    json=firestore_data,
                    timeout=30,
                    headers=headers
                )
                
                if response.status_code == 200:
                    # 检查合并后的文章数量
                    merged_articles = firestore_data.get('fields', {}).get('articles', {}).get('arrayValue', {}).get('values', [])
                    success_count += 1
                    print(f"  ✅ 成功 (合并后 {len(merged_articles)} 篇文章)")
                    break
                else:
                    print(f"  ⚠️  HTTP {response.status_code}: {response.text[:100]}")
                    attempt += 1
                    if attempt < max_retries:
                        print(f"  重试 {attempt}/{max_retries}...")
                        time.sleep(1)
                    else:
                        failed_count += 1
                        print(f"  ❌ 失败")
                        
            except requests.exceptions.Timeout:
                attempt += 1
                if attempt < max_retries:
                    print(f"  ⏱️  超时，重试 {attempt}/{max_retries}...")
                    time.sleep(1)
                else:
                    failed_count += 1
                    print(f"  ❌ 超时 {max_retries} 次")
                    
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt < max_retries:
                    print(f"  ⚠️  网络错误：{e}，重试 {attempt}/{max_retries}...")
                    time.sleep(1)
                else:
                    failed_count += 1
                    print(f"  ❌ 网络错误：{e}")
    
    print(f"\n{'='*80}")
    print(f"同步完成！")
    print(f"{'='*80}")
    print(f"成功：{success_count} 只")
    print(f"失败：{failed_count} 只")
    print(f"总计：{success_count + failed_count} 只")
    
    if success_count > 0:
        print(f"\n✅ {success_count} 只股票已成功同步到 Firebase")
        print(f"\n下一步：")
        print(f"1. 访问 Vercel 查看更新：https://stock-research20.vercel.app")
        print(f"2. 检查个股页面，例如：https://stock-research20.vercel.app/stock/{list(stocks.keys())[0]}")
    
    return success_count, failed_count

if __name__ == '__main__':
    # 今日更新的股票文件
    today = datetime.now().strftime('%Y-%m-%d')
    stocks_file = Path(__file__).parent / 'data' / f'stocks_master_{today}.json'
    
    if not stocks_file.exists():
        print(f"❌ 文件不存在：{stocks_file}")
        sys.exit(1)
    
    print(f"读取文件：{stocks_file}")
    
    # 同步到 Firebase
    sync_stocks_to_firestore(str(stocks_file))
