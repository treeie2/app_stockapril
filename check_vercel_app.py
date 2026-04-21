#!/usr/bin/env python3
"""
诊断 Vercel 应用问题
"""
import requests
import json

def check_vercel():
    """检查 Vercel 应用"""
    base_url = "https://app-stockapril-ashy.vercel.app"
    
    print("🔍 检查 Vercel 应用...\n")
    
    # 1. 检查首页
    print("1️⃣ 检查首页...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   状态码：{response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ 首页可访问")
            # 检查是否包含 002416
            if '002416' in response.text:
                print(f"   ✅ 首页包含 002416")
            else:
                print(f"   ❌ 首页不包含 002416")
        else:
            print(f"   ❌ 首页访问失败")
    except Exception as e:
        print(f"   ❌ 错误：{e}")
    
    # 2. 检查个股页面
    print("\n2️⃣ 检查个股页面...")
    stocks_to_check = ['002416', '301666']
    for code in stocks_to_check:
        url = f"{base_url}/stock/{code}"
        try:
            response = requests.get(url, timeout=10)
            print(f"   {code}: {response.status_code}")
            if response.status_code == 200:
                print(f"      ✅ 页面可访问")
                if '爱施德' in response.text or '力诺药包' in response.text:
                    print(f"      ✅ 包含股票名称")
            elif response.status_code == 404:
                print(f"      ❌ 404 - 股票不存在")
            else:
                print(f"      ❌ 错误：{response.status_code}")
        except Exception as e:
            print(f"      ❌ 错误：{e}")
    
    # 3. 检查 API
    print("\n3️⃣ 检查 API...")
    for code in stocks_to_check:
        url = f"{base_url}/api/stock/{code}"
        try:
            response = requests.get(url, timeout=10)
            print(f"   {code}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ API 可访问")
                print(f"      名称：{data.get('name', 'N/A')}")
            elif response.status_code == 404:
                print(f"      ❌ 404 - 股票不存在")
            else:
                print(f"      ❌ 错误：{response.status_code}")
        except Exception as e:
            print(f"      ❌ 错误：{e}")
    
    # 4. 检查 GitHub 数据
    print("\n4️⃣ 检查 GitHub 数据...")
    github_url = "https://raw.githubusercontent.com/treeie2/app_stockapril/main/data/master/stocks/2026-04-21.json"
    try:
        response = requests.get(github_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('stocks', {})
            print(f"   股票数：{len(stocks)}")
            for code in stocks_to_check:
                if code in stocks:
                    print(f"   ✅ {code} 存在：{stocks[code].get('name', 'N/A')}")
                else:
                    print(f"   ❌ {code} 不存在")
        else:
            print(f"   ❌ GitHub 数据访问失败")
    except Exception as e:
        print(f"   ❌ 错误：{e}")

if __name__ == '__main__':
    check_vercel()
