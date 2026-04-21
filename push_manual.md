# 手动推送指南（2026-04-21 更新）

由于网络连接问题，可能需要手动执行以下步骤推送更新。

## 完整流程：生成 → 保存 → 推送 → 上线

---

## 场景 1: 推送股票数据（分片模式）

### 步骤 1: 生成和保存数据

**方式 A: 自动完成（推荐）**
```powershell
cd e:/github/stock-research-backup
python scripts/pipeline.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --sync-github
```

**方式 B: 手动分步**
```powershell
# 1. 抓取文章
python scripts/fetch_wechat_via_browser_dom.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --out_text "tmp_article.txt"

# 2. 转换为 raw_material
python scripts/fetch_wechat_to_raw_material.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --out "raw_material/raw_material_2026-04-21.md" `
  --manual_text_file "tmp_article.txt"

# 3. 抽取个股信息
python scripts/extract_stocks_from_raw_material.py `
  --raw "raw_material/raw_material_2026-04-21.md" `
  --stock_xls "./assets/全部个股.xls" `
  --out_json "data/stocks_master_2026-04-21.json"

# 4. 增量合并到分片
python scripts/incremental_update.py `
  --mode merge `
  --json "data/stocks_master_2026-04-21.json"
```

### 步骤 2: 确认数据已生成

```powershell
# 检查分片文件
ls data/master/stocks/2026-04-21.json

# 检查索引文件
cat data/master/stocks_index.json | ConvertFrom-Json | Select-Object -First 10

# 统计股票数量
$stats = Get-Content "data/master/stocks/2026-04-21.json" | ConvertFrom-Json
Write-Host "今日更新：$($stats.update_count) 只股票"
```

### 步骤 3: 推送到 GitHub

**方式 A: 使用同步脚本（推荐）**
```powershell
cd e:/github/stock-research-backup
python scripts/sync_to_github.py --mode shard --base-dir "data/master"
```

**方式 B: 手动 git 操作**
```powershell
# 1. 复制文件到 agent_store
cd e:/github/stock-research-backup
$today = Get-Date -Format "yyyy-MM-dd"
Copy-Item "data/master/stocks/$today.json" "e:/github/agent_store/data/master/stocks/" -Force
Copy-Item "data/master/stocks_index.json" "e:/github/agent_store/data/master/" -Force

# 2. 切换到 agent_store 目录
cd e:/github/agent_store

# 3. 查看更改
git status

# 4. 添加并提交
git add data/master/stocks/*.json data/master/stocks_index.json
git commit -m "Update stock data: $today (+X stocks)"

# 5. 推送到 GitHub
git push github HEAD:main -f
```

### 步骤 4: 验证上线

1. **检查 GitHub 仓库**
   - 访问 https://github.com/treeie2/stock-research
   - 确认最新 commit 已推送

2. **检查 Vercel 部署**
   - 访问 https://vercel.com/dashboard
   - 查看部署状态（应该是 "Ready"）

3. **验证线上数据**
   - 访问线上网站
   - 检查新股票是否已显示

---

## 场景 2: 推送热点数据

### 步骤 1: 添加热点

**方式 A: 直接添加**
```powershell
cd e:/github/stock-research-backup
python add_hot_topic.py "热点名称" "驱动因素描述" "个股 1，个股 2，个股 3"
```

**方式 B: API 提取**
```powershell
$env:DOUBAO_API_TOKEN="your-token"
python call_api_add_hot_topic.py
```

### 步骤 2: 推送到 GitHub

脚本会自动推送，或手动推送：
```powershell
cd e:/github/agent_store
git add data/hot_topics.json
git commit -m "Add hot topic: 热点名称"
git push github HEAD:main -f
```

### 步骤 3: 验证上线

- 访问线上网站
- 检查热点板块是否显示新热点

---

## 常见问题排查

### 问题 1: git push 失败

**错误信息：** "Authentication failed"
**解决方案：**
```powershell
# 使用 Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/treeie2/stock-research.git
git push github HEAD:main -f
```

### 问题 2: 分片文件太大

如果单个分片文件超过 10MB：
```powershell
# 检查文件大小
ls -lh data/master/stocks/*.json

# 压缩数据
python compress_stocks_data.py

# 或者只推送索引文件
git add data/master/stocks_index.json
```

### 问题 3: Vercel 部署失败

**检查步骤：**
1. 访问 https://vercel.com/dashboard
2. 点击失败的部署
3. 查看构建日志
4. 常见错误：
   - JSON 格式错误 → 验证 JSON 格式
   - 文件路径错误 → 检查路径是否正确

### 问题 4: 数据未同步

**检查清单：**
```powershell
# 1. 检查本地文件
ls data/master/stocks/
ls data/master/stocks_index.json

# 2. 检查 agent_store
cd e:/github/agent_store
ls data/master/stocks/

# 3. 检查 GitHub 仓库
# 访问 https://github.com/treeie2/stock-research/tree/main/data/master/stocks

# 4. 检查 Vercel 部署
# 访问 https://vercel.com/dashboard
```

---

## 快速参考命令

### 检查今日更新
```powershell
$today = Get-Date -Format "yyyy-MM-dd"
$stats = Get-Content "data/master/stocks/$today.json" | ConvertFrom-Json
Write-Host "日期：$today"
Write-Host "更新股票数：$($stats.update_count)"
Write-Host "股票代码：$($stocks.stocks.Keys -join ', ')"
```

### 批量推送多天数据
```powershell
# 推送最近 3 天的数据
python scripts/sync_to_github.py --mode shard --base-dir "data/master" --days 3
```

### 验证 JSON 格式
```powershell
# 验证分片文件
Get-Content "data/master/stocks/2026-04-21.json" | ConvertFrom-Json | Out-Null
if ($?) {
  Write-Host "✅ JSON 格式正确"
} else {
  Write-Host "❌ JSON 格式错误"
}
```

---

## 本次更新内容模板

### 新增/更新股票（X 只）

**板块名称（X 只）：**
- 股票名称 (代码) - 目标市值/备注
- ...

### 数据库统计
- 总股票数：XXXX 只
- 今日更新：XX 只
- 最后更新：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

---

## 相关文档

- [PUSH_TO_GITHUB.md](docs/PUSH_TO_GITHUB.md) - GitHub 推送命令详解
- [SYNC_FEATURE.md](docs/SYNC_FEATURE.md) - 数据同步功能
- [DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) - 部署检查清单
