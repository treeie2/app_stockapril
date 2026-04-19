#!/usr/bin/env python3
"""
测试 Firebase 连接和凭据
"""
import requests
import json
from pathlib import Path

# Firebase 配置
FIREBASE_PROJECT_ID = "stock-research-669e1"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

def test_firebase_connection():
    """测试 Firebase 连接"""
    print("🧪 测试 Firebase 连接...")
    print(f"   项目ID: {FIREBASE_PROJECT_ID}")
    print(f"   API地址: {FIREBASE_BASE_URL}\n")
    
    # 测试1: 获取 stocks 集合列表
    print("📋 测试1: 获取 stocks 集合...")
    try:
        url = f"{FIREBASE_BASE_URL}/stocks"
        resp = requests.get(url, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            documents = data.get('documents', [])
            print(f"   ✅ 连接成功")
            print(f"   📊 返回文档数: {len(documents)}")
            if documents:
                print(f"   📄 第一个文档: {documents[0].get('name', '').split('/')[-1]}")
        elif resp.status_code == 403:
            print(f"   ❌ 403 Forbidden - 权限不足")
            print(f"   💡 可能原因:")
            print(f"      1. Firestore 数据库规则不允许读取")
            print(f"      2. 需要身份验证")
            print(f"      3. API 密钥配置问题")
        elif resp.status_code == 404:
            print(f"   ❌ 404 Not Found - 集合不存在")
        else:
            print(f"   ❌ 错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试2: 尝试获取特定文档
    print("\n📋 测试2: 获取特定文档 (600519 贵州茅台)...")
    try:
        url = f"{FIREBASE_BASE_URL}/stocks/600519"
        resp = requests.get(url, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            fields = data.get('fields', {})
            name = fields.get('name', {}).get('stringValue', 'N/A')
            print(f"   ✅ 文档存在")
            print(f"   📄 名称: {name}")
        elif resp.status_code == 404:
            print(f"   ⚠️ 文档不存在")
        elif resp.status_code == 403:
            print(f"   ❌ 403 Forbidden - 无权限访问")
        else:
            print(f"   ❌ 错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试3: 尝试写入测试数据（会被拒绝，但可以看出权限问题）
    print("\n📋 测试3: 尝试写入测试数据...")
    try:
        test_data = {
            "fields": {
                "name": {"stringValue": "测试股票"},
                "code": {"stringValue": "999999"},
                "test": {"booleanValue": True}
            }
        }
        url = f"{FIREBASE_BASE_URL}/stocks/test_999999"
        resp = requests.patch(url, json=test_data, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code in [200, 201]:
            print(f"   ✅ 写入成功（有写权限）")
        elif resp.status_code == 403:
            print(f"   ❌ 403 Forbidden - 无写权限")
            print(f"   💡 需要检查 Firestore 安全规则")
        else:
            print(f"   ⚠️ 其他错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试4: 检查项目是否存在
    print("\n📋 测试4: 检查项目配置...")
    try:
        # 尝试访问项目信息
        url = f"https://firebase.googleapis.com/v1beta1/projects/{FIREBASE_PROJECT_ID}"
        resp = requests.get(url, timeout=10)
        print(f"   状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ 项目存在")
            print(f"   📄 项目名称: {data.get('displayName', 'N/A')}")
            print(f"   📄 项目状态: {data.get('state', 'N/A')}")
        elif resp.status_code == 403:
            print(f"   ❌ 403 Forbidden - 无法访问项目信息")
            print(f"   💡 可能需要 API 密钥或服务账号")
        elif resp.status_code == 404:
            print(f"   ❌ 404 Not Found - 项目不存在")
        else:
            print(f"   ⚠️ 其他错误: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print("\n" + "="*60)
    print("📊 测试总结:")
    print("="*60)
    print("如果所有测试都返回 403，说明需要:")
    print("  1. 配置 Firestore 安全规则允许读写")
    print("  2. 使用服务账号或 API 密钥进行身份验证")
    print("  3. 检查项目 ID 是否正确")
    print("\nFirestore 安全规则示例:")
    print("""
    rules_version = '2';
    service cloud.firestore {
      match /databases/{database}/documents {
        match /stocks/{stock} {
          allow read, write: if true;  // 开发环境
          // allow read, write: if request.auth != null;  // 生产环境
        }
      }
    }
    """)

if __name__ == "__main__":
    test_firebase_connection()
