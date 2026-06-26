#!/usr/bin/env python3
"""
Vercel Serverless Function 入口 v3
"""
import sys
import os

print("[Vercel] Starting v7 - GitHub raw priority, Supabase fallback", flush=True)

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入主应用
from main import app

# Vercel 需要这个 handler
handler = app
