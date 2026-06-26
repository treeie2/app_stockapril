#!/bin/bash
# 强制触发 Railway 重新部署

echo "🚀 触发 Railway 重新部署..."
echo ""

cd /home/admin/openclaw/workspace/railway-deploy

# 方法 1: 推送空提交触发
echo "📤 推送触发提交..."
git commit --allow-empty -m "chore: trigger redeploy $(date -u)"
git push origin main

echo ""
echo "✅ 已推送到 GitHub"
echo ""
echo "⏳ Railway 将在 1-3 分钟内自动部署"
echo ""
echo "📊 监控部署状态:"
echo "   https://railway.app/dashboard"
echo ""
echo "🌐 访问应用:"
echo "   https://web-production-a1006c.up.railway.app/"
echo ""
