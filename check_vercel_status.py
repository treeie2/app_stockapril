#!/usr/bin/env python3
"""
检查 Vercel 网站状态
"""
import requests

# 测试主页
url = 'https://app-stockapril.vercel.app/'

print("📥 正在测试 Vercel 主页...")
print(f"URL: {url}\n")

try:
    response = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    
    print(f"状态码：{response.status_code}")
    print(f"\n响应内容（前 2000 字符）:")
    print(response.text[:2000])
    
except requests.exceptions.Timeout:
    print("❌ 连接超时！Vercel 服务可能未响应")
except Exception as e:
    print(f"❌ 错误：{e}")
