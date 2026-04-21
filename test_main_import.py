#!/usr/bin/env python3
"""
测试 main.py 能否正常导入
"""
import sys
import os

# 模拟 Vercel 环境
os.environ['VERCEL'] = '1'

print("🔍 测试导入 main 模块...")

try:
    # 尝试导入 main 模块
    import main
    print("✅ main 模块导入成功")
    
    # 尝试加载数据
    print("\n📋 测试数据加载...")
    main.load_all_data()
    print(f"✅ 数据加载成功：{len(main.stocks)} 只股票")
    
except Exception as e:
    print(f"❌ 错误：{e}")
    import traceback
    traceback.print_exc()
