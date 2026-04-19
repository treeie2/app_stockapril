#!/usr/bin/env python3
"""
检查 Vercel 上实际返回的数据
"""
import urllib.request
import json

# 尝试访问 Vercel 的 API
url = "https://modelsapp-git-main-shermanns-projects.vercel.app/api/stock/688518"

try:
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        content = response.read().decode('utf-8')
        
        # 检查是否是 HTML 页面（登录页）
        if '<!DOCTYPE html>' in content or '<html>' in content:
            print("⚠️ 返回的是 HTML 页面，不是 JSON 数据")
            print("   可能需要登录 Vercel 才能访问")
        else:
            try:
                data = json.loads(content)
                print("✅ 成功获取 JSON 数据")
                print(f"   数据类型: {type(data)}")
                if isinstance(data, dict):
                    print(f"   字段: {list(data.keys())}")
                    if 'name' in data:
                        print(f"   名称: {data['name']}")
                    if 'articles' in data:
                        print(f"   文章数: {len(data['articles'])}")
            except:
                print("❌ 返回的不是有效 JSON")
                print(f"   内容预览: {content[:200]}")
                
except Exception as e:
    print(f"❌ 请求失败: {e}")
