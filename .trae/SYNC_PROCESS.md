 # 数据同步流程说明

## 📊 数据架构

### 存储位置

```
e:\github\stock-research-backup/
├── data/
│   ├── master/
│   │   ├── stocks_master.json          # 主文件（完整数据）
│   │   ├── stocks_index.json           # 索引文件
│   │   └── stocks/
│   │       ├── 2026-04-21.json        # 按日期分片
│   │       ├── 2026-04-19.json
│   │       └── ...
│   └── hot_topics.json                 # 热点数据
```

### 同步到 GitHub 的流程

数据通过 **agent_store** 仓库同步到 GitHub，然后 Vercel 自动部署：

```
stock-research-backup (本地)
    ↓ (复制文件)
agent_store (本地)
    ↓ (git push)
GitHub: treeie2/models_app
    ↓ (自动部署)
Vercel: https://app-stockapril.vercel.app
```

## 🔄 完整同步流程

### 方式 1：手动同步（推荐）

#### Step 1: 合并到主文件
```powershell
cd e:/github/stock-research-backup
python merge_today_to_master.py
```

这会将 `data/master/stocks/2026-04-21.json` 的数据合并到 `stocks_master.json`。

#### Step 2: 同步到 agent_store
```powershell
cd e:/github/stock-research-backup
python sync_all_to_github.py
```

这会：
1. 复制所有分片文件到 `agent_store`
2. 复制 `stocks_master.json`
3. 复制 `stocks_index.json`
4. 复制 `hot_topics.json`
5. 执行 git add/commit/push

#### Step 3: 验证部署

访问 Vercel 查看部署状态：
- https://vercel.com/dashboard

验证线上数据：
- https://app-stockapril.vercel.app

### 方式 2：使用 Pipeline（自动化）

如果你使用 wechat-fetch-research-embedded skill：

```powershell
python scripts/pipeline.py `
  --url "https://mp.weixin.qq.com/s/..." `
  --sync-github
```

这会自动完成：
1. 抓取公众号文章
2. 抽取个股信息
3. 保存到分片文件
4. 更新索引
5. 同步到 GitHub

## 📝 关键文件说明

### 1. stocks_master.json
- **作用**：完整的股票数据库
- **格式**：`{"stocks": {code: data}}`
- **同步方式**：通过 `sync_all_to_github.py` 复制

### 2. stocks_index.json
- **作用**：股票代码索引，记录每只股票所在的分片文件
- **格式**：
```json
{
  "version": "2.0",
  "last_updated": "2026-04-21",
  "total_stocks": 3166,
  "stocks": {
    "300433": {
      "name": "蓝思科技",
      "last_updated": "2026-04-21",
      "file": "2026-04-21.json"
    }
  }
}
```

### 3. stocks/YYYY-MM-DD.json
- **作用**：按日期分片存储当日更新的股票
- **格式**：
```json
{
  "date": "2026-04-21",
  "update_count": 9,
  "stocks": {
    "300433": { ... },
    "002600": { ... }
  }
}
```

### 4. hot_topics.json
- **作用**：热点板块数据
- **格式**：
```json
{
  "topics": [
    {
      "id": "topic_20260421214335",
      "name": "荣耀机器人 IPO",
      "drivers": "荣耀机器人半马 50 分 26 秒破人类纪录，启动 A 股 IPO，9 大影子股受益",
      "stocks": ["爱施德", "天音控股", ...]
    }
  ]
}
```

## 🎯 本次更新说明

### 2026-04-21 更新内容

1. **荣耀机器人 IPO 影子股（9 只）**
   - 002475 立讯精密
   - 002138 顺络电子
   - 300433 蓝思科技
   - 002600 领益智造
   - 688322 奥比中光
   - 300602 飞荣达
   - 300136 信维通信
   - 300115 长盈精密
   - 002440 安洁科技

2. **修复 002201 股票名称**
   - 原名称：航空航天（错误）
   - 新名称：正威新材（正确）

3. **更新 hot_topics.json**
   - 荣耀机器人 IPO 影子股从 6 只增加到 9 只
   - 格式从逗号分隔改为数组格式

## 🛠️ 常用脚本

### merge_today_to_master.py
将当天分片数据合并到 stocks_master.json

### sync_all_to_github.py
同步所有数据到 agent_store 并推送到 GitHub

### update_index_and_fix.py
更新索引文件并修复股票名称问题

### verify_fixes.py
验证所有修复是否成功

## 📦 数据流向总结

```
微信公众号文章
    ↓ (fetch_wechat_via_browser_dom.py)
raw_material/raw_material_2026-04-21.md
    ↓ (extract_stocks_from_raw_material.py)
data/stocks_master_2026-04-21.json（中间产物）
    ↓ (incremental_update.py)
data/master/stocks/2026-04-21.json（分片）
data/master/stocks_index.json（索引）
    ↓ (merge_today_to_master.py)
data/master/stocks_master.json（主文件）
    ↓ (sync_all_to_github.py)
agent_store/data/master/
    ↓ (git push)
GitHub: treeie2/models_app
    ↓ (自动部署)
Vercel: app-stockapril.vercel.app
```

## ✅ 验证清单

同步完成后，请验证：

- [ ] stocks_master.json 包含最新数据
- [ ] stocks_index.json 已更新
- [ ] 分片文件已创建（2026-04-21.json）
- [ ] hot_topics.json 已更新
- [ ] agent_store 已同步
- [ ] GitHub 已推送
- [ ] Vercel 部署成功
- [ ] 网页显示正确

## 🔗 相关资源

- GitHub 仓库：https://github.com/treeie2/models_app
- Vercel 部署：https://vercel.com/dashboard
- 线上网站：https://app-stockapril.vercel.app
