#!/usr/bin/env python3
"""
使用服务账号凭据测试 Firebase 连接
"""
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import jwt

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
    import time
    
    now = int(time.time())
    payload = {
        'iss': CLIENT_EMAIL,
        'sub': CLIENT_EMAIL,
        'scope': 'https://www.googleapis.com/auth/datastore',
        'aud': TOKEN_URI,
        'iat': now,
        'exp': now + 3600
    }
    
    # 使用 PyJWT 签名
    signed_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256')
    
    # 请求访问令牌
    token_data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': signed_jwt
    }
    
    resp = requests.post(TOKEN_URI, data=token_data)
    if resp.status_code == 200:
        return resp.json()['access_token']
    else:
        print(f"获取令牌失败: {resp.status_code}")
        print(resp.text)
        return None

def test_firebase_with_auth():
    """使用身份验证测试 Firebase"""
    print("🧪 使用服务账号测试 Firebase 连接...")
    print(f"   项目ID: {PROJECT_ID}")
    print(f"   服务账号: {CLIENT_EMAIL}\n")
    
    # 获取访问令牌
    print("📋 获取访问令牌...")
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return
    print("✅ 访问令牌获取成功\n")
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # 测试1: 获取 stocks 集合
    print("📋 测试1: 获取 stocks 集合...")
    try:
        url = f"{FIREBASE_BASE_URL}/stocks"
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            documents = data.get('documents', [])
            print(f"   ✅ 连接成功")
            print(f"   📊 返回文档数: {len(documents)}")
            if documents:
                print(f"   📄 第一个文档: {documents[0].get('name', '').split('/')[-1]}")
        else:
            print(f"   ❌ 错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试2: 获取特定文档
    print("\n📋 测试2: 获取特定文档...")
    try:
        url = f"{FIREBASE_BASE_URL}/stocks/300750"
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            fields = data.get('fields', {})
            name = fields.get('name', {}).get('stringValue', 'N/A')
            print(f"   ✅ 文档存在")
            print(f"   📄 名称: {name}")
        elif resp.status_code == 404:
            print(f"   ⚠️ 文档不存在")
        else:
            print(f"   ❌ 错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试3: 写入测试数据
    print("\n📋 测试3: 写入测试数据...")
    try:
        test_data = {
            "fields": {
                "name": {"stringValue": "测试股票"},
                "code": {"stringValue": "999999"},
                "test": {"booleanValue": True},
                "updated_at": {"timestampValue": datetime.now().isoformat() + "Z"}
            }
        }
        url = f"{FIREBASE_BASE_URL}/stocks/test_999999"
        resp = requests.patch(url, headers=headers, json=test_data, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code in [200, 201]:
            print(f"   ✅ 写入成功（有写权限）")
            # 清理测试数据
            requests.delete(url, headers=headers)
            print(f"   🗑️ 测试数据已清理")
        else:
            print(f"   ❌ 错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print("\n" + "="*60)
    print("📊 测试完成!")
    print("="*60)

if __name__ == "__main__":
    test_firebase_with_auth()
