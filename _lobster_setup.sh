#!/bin/bash
# 龙虾终端 - wechat-fetch-research-embedded skill 一键配置
# 用法: bash _lobster_setup.sh

echo "=== 1. 安装 Python 依赖 ==="
pip install openai playwright requests pandas aiohttp firebase-admin -q
python -m playwright install chromium 2>/dev/null || echo "[WARN] Chromium 安装失败（非致命，可手动抓取）"

echo ""
echo "=== 2. 验证依赖 ==="
python -c "
import openai, requests, pandas; 
try: import aiohttp; print('  aiohttp: OK')
except: print('  aiohttp: MISS (非致命)')
try: import firebase_admin; print('  firebase: OK')
except: print('  firebase: MISS (可选)')
print('  openai/requests/pandas: OK')
"

echo ""
echo "=== 3. 同步最新代码 ==="
cd ~/stock-research-backup 2>/dev/null || cd /home/user/stock-research-backup 2>/dev/null || cd /root/stock-research-backup 2>/dev/null
if [ $? -ne 0 ]; then
    echo "请先 git clone https://github.com/treeie2/app_stockapril.git stock-research-backup"
    exit 1
fi
git pull origin main

echo ""
echo "=== 4. 测试 skill ==="
cd .trae/skills/wechat-fetch-research-embedded
python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/HIQ1qwnjwv6dVb07snn7yg" 2>&1 | head -5

echo ""
echo "=== 配置完成！使用方式 ==="
echo ""
echo "  # 完整流程（抓取+抽取+合并+推送到GitHub）"
echo "  cd .trae/skills/wechat-fetch-research-embedded"
echo "  python scripts/pipeline.py --url '文章URL' --sync-github"
echo ""
echo "  # 或分步执行："
echo "  # 1. 浏览器抓取正文"
echo "  python scripts/fetch_wechat_via_browser_dom.py --url 'URL' --out_text tmp.txt"
echo "  # 2. 落盘 raw_material"
echo "  python scripts/fetch_wechat_to_raw_material.py --url 'URL' --out 'raw_material/raw_material_YYYY-MM-DD.md' --manual_text_file tmp.txt"
echo "  # 3. LLM 抽取个股"
echo "  python scripts/extract_stocks_from_raw_material.py --raw 'raw_material/raw_material_YYYY-MM-DD.md' --stock_xls './assets/全部个股.xls' --out_json 'data/stocks_master_YYYY-MM-DD.json' --mode merge"
echo "  # 4. 合并到主数据"
echo "  python scripts/merge_new_stocks.py"
echo "  # 5. 推送 GitHub"
echo "  git add ../../data/stocks/ && git commit -m 'update' && git push"
