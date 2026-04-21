#!/usr/bin/env python3
"""
检查 Vercel API 状态
"""
import requests

# 测试 Vercel API
url = 'https://app-stockapril.vercel.app/api/stocks?limit=5&offset=0'

print("📥 正在测试 Vercel API...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, timeout=30)
    
    print(f"状态码：{response.status_code}")
    print(f"响应头：{dict(response.headers)}")
    print(f"\n响应内容（前 1000 字符）:")
    print(response.text[:1000])
    
except Exception as e:
    print(f"❌ 错误：{e}")
