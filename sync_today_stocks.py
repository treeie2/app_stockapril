#!/usr/bin/env python3
"""
快速同步今天更新的股票到 Firebase
"""
import json
import requests
from pathlib import Path
import time

# Firebase 配置
FIREBASE_CREDENTIALS = Path("e:/github/stock-research-backup/.trae/rules/firebase-credentials.json")
PROJECT_ID = "app-stockapril"

# 今天更新的股票代码
TODAY_STOCKS = [
    '002046',  # 国机精工
    '603019',  # 中科曙光
    '000977',  # 浪潮信息
    '603118',  # 共进股份
    '000960',  # 锡业股份
    '600961',  # 株冶集团
    '600531',  # 豫光金铅
    '002428',  # 云南锗业
    '002975',  # 博杰股份
    '600206',  # 有研新材
    '600703',  # 三安光电
    '688498',  # 源杰科技
    '600105',  # 永鼎股份
    '688048',  # 长光华芯
    '002023',  # 海特高新
    '688313',  # 仕佳光子
    '002281',  # 光迅科技
    '000988',  # 华工科技
    '002725',  # 跃岭股份
    '300316',  # 晶盛机电
    '002371',  # 北方华创
    '603005',  # 晶方科技
]

def get_firebase_token():
    """获取 Firebase 访问令牌"""
    import json
    with open(FIREBASE_CREDENTIALS, 'r', encoding='utf-8') as f:
        creds = json.load(f)
    
    # 使用 service account 获取 access token
    token_url = "https://oauth2.googleapis.com/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": create_jwt(creds)
    }
    
    # 简化：直接从 credentials 获取项目信息
    return None  # 使用简化方式

def sync_stock(code, stock_data):
    """同步单个股票到 Firebase"""
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
    doc_url = f"{base_url}/stocks/{code}"
    
    # 准备数据
    document = {
        'fields': {
            'name': {'stringValue': stock_data.get('name', '')},
            'code': {'stringValue': code},
            'board': {'stringValue': stock_data.get('board', '')},
            'industry': {'stringValue': stock_data.get('industry', '')},
            'concepts': {'arrayValue': {'values': [{'stringValue': c} for c in stock_data.get('concepts', [])]}},
            'mentionCount': {'integerValue': stock_data.get('mention_count', 0)},
            'articles': {'arrayValue': {'values': []}}
        }
    }
    
    # 添加文章
    for article in stock_data.get('articles', []):
        article_field = {
            'mapValue': {
                'fields': {
                    'title': {'stringValue': article.get('title', '')},
                    'date': {'stringValue': article.get('date', '')},
                    'source': {'stringValue': article.get('source', '')},
                    'content': {'stringValue': article.get('content', '')},
                    'targetValuation': {'arrayValue': {'values': [{'stringValue': v} for v in article.get('target_valuation', [])]}},
                }
            }
        }
        document['fields']['articles']['arrayValue']['values'].append(article_field)
    
    try:
        resp = requests.patch(doc_url, json=document, timeout=30)
        if resp.status_code == 200:
            print(f"✅ [{code}] {stock_data.get('name', '')} 同步成功")
            return True
        else:
            print(f"❌ [{code}] 同步失败：{resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ [{code}] 同步异常：{e}")
        return False

def main():
    print("🚀 开始快速同步今日更新股票到 Firebase...\n")
    
    # 读取 stocks_master.json
    master_file = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
    with open(master_file, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    success_count = 0
    fail_count = 0
    
    for code in TODAY_STOCKS:
        if code in stocks_master:
            stock_data = stocks_master[code]
            if sync_stock(code, stock_data):
                success_count += 1
            else:
                fail_count += 1
            time.sleep(0.5)  # 避免请求过快
        else:
            print(f"⚠️  [{code}] 未在 stocks_master.json 中找到")
    
    print(f"\n✅ 完成！成功：{success_count}, 失败：{fail_count}")

if __name__ == '__main__':
    main()
