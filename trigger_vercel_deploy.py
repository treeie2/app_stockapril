#!/usr/bin/env python3
"""
触发 Vercel 部署
"""
import requests
import json

# Vercel API
VERCEL_API_URL = "https://api.vercel.com/v13/deployments"

# 需要 Vercel Token
# 在 Vercel Dashboard -> Settings -> Tokens 创建
VERCEL_TOKEN = "YOUR_VERCEL_TOKEN"  # 替换为实际 token
TEAM_ID = "YOUR_TEAM_ID"  # 如果有团队
PROJECT_ID = "prj_XXX"  # 项目 ID

def trigger_deploy():
    """触发 Vercel 部署"""
    print("🚀 触发 Vercel 部署...\n")
    
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "project": PROJECT_ID,
        "target": "production",
        "ref": "main"
    }
    
    if TEAM_ID:
        data["teamId"] = TEAM_ID
    
    try:
        response = requests.post(VERCEL_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ 部署已触发!")
        print(f"   部署 ID: {result.get('id')}")
        print(f"   状态：{result.get('state')}")
        print(f"   URL: {result.get('url')}")
        
    except Exception as e:
        print(f"❌ 触发失败：{e}")
        print("\n请手动触发部署:")
        print("1. 访问 https://vercel.com/dashboard")
        print("2. 找到 app-stockapril-ashy 项目")
        print("3. 点击 '...' -> 'Redeploy'")

if __name__ == "__main__":
    trigger_deploy()
