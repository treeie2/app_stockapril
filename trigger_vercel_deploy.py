#!/usr/bin/env python3
"""
触发 Vercel 重新部署
通过调用 Vercel API 触发部署
"""
import os
import requests

def trigger_vercel_deployment():
    """触发 Vercel 部署"""
    print("🚀 触发 Vercel 重新部署...\n")
    
    # Vercel API
    vercel_token = os.environ.get('VERCEL_TOKEN', '')
    project_id = os.environ.get('VERCEL_PROJECT_ID', '')  # Vercel 项目 ID
    
    if not vercel_token:
        print("❌ 未设置 VERCEL_TOKEN 环境变量")
        print("\n请在 Vercel 设置中获取 Token:")
        print("   https://vercel.com/account/tokens")
        print("\n然后设置环境变量:")
        print("   $env:VERCEL_TOKEN = 'your_token_here'")
        return False
    
    if not project_id:
        print("❌ 未设置 VERCEL_PROJECT_ID 环境变量")
        print("\n请获取项目 ID:")
        print("   https://vercel.com/dashboard -> Settings -> Project ID")
        print("\n然后设置环境变量:")
        print("   $env:VERCEL_PROJECT_ID = 'your_project_id'")
        return False
    
    # 调用 Vercel API
    url = f"https://api.vercel.com/v13/deployments?projectId={project_id}"
    headers = {
        "Authorization": f"Bearer {vercel_token}",
        "Content-Type": "application/json"
    }
    data = {
        "projectSettings": {
            "framework": "nextjs"
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 部署触发成功!")
            print(f"   部署 ID: {result.get('id', 'N/A')}")
            print(f"   状态：{result.get('state', 'N/A')}")
            print(f"   URL: {result.get('url', 'N/A')}")
            print("\n📱 访问部署预览:")
            print(f"   https://{result.get('url', 'N/A')}")
            return True
        else:
            print(f"❌ API 调用失败：{response.status_code}")
            print(f"   响应：{response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    trigger_vercel_deployment()
