# AGENTS.md — 龙虾（Lobster）AI 执行规范

> 云端投研助手。通过飞书接收微信文章链接，自动提取个股数据并更新数据库。

## 核心职责

1. **接收飞书消息** → 解析微信文章 URL
2. **抓取文章正文** → 使用 `web_fetch` 工具
3. **提取个股数据** → LLM 结构化提取 → 合并到 `stocks_master.json`
4. **推送数据上线** → GitHub + Supabase + ModelScope

## 执行流程

### 输入端：飞书消息格式

```
新增个股：https://mp.weixin.qq.com/s/xxx
新增分组：分组名
https://mp.weixin.qq.com/s/yyy
```

### Step 0：解析输入

从飞书消息中提取：
- 微信文章 URL（`mp.weixin.qq.com/s/*`）
- 分组名称（如有）
- 操作类型（新增/更新/查询）

### Step 1：抓取文章

```
使用 web_fetch 工具：
- URL: 用户提供的微信文章链接
- fetchInfo: "完整获取文章全部内容，提取所有个股名称、代码、核心业务、行业地位、估值数据"
```

### Step 2：查码确认

从 `data/stocks/stocks_master.json` 查找每个个股的代码：
```python
import json
d = json.load(open("data/stocks/stocks_master.json", "r", encoding="utf-8"))
for name in ["美的集团", "鼎龙股份", ...]:
    for code, s in d["stocks"].items():
        if s["name"] == name:
            print(f"{code}: {name}")
```

缺失代码则从 `archived/全部个股.xls` 查找。

### Step 3：数据写入

AI 直接编写 Python 脚本完成三件事：
1. 为现有个股追加 article
2. 为缺失个股创建新条目
3. 合并到 `stocks_master.json`

**article 最小结构**：
```json
{
  "title": "文章标题",
  "source": "https://mp.weixin.qq.com/s/xxx",
  "date": "2026-06-25",
  "type": "机构调研",
  "author": "作者",
  "notes": ["关键数据摘要"]
}
```

**去重规则**：按 `(source, title)` 双键去重，已存在则跳过。

### Step 4：同步上线

#### 4A. 推 GitHub
```bash
cd f:/app_stockapril
git add data/stocks/stocks_master.json data/stocks/*.json data/groups/ data/hot_topics/
git commit -m "feat: add stocks from YYYY-MM-DD article"
git push origin main
```

#### 4B. 同步 Supabase（可选）
```bash
python sync_to_supabase.py
# 或 HTTP API 直接 upsert
```

#### 4C. 同步 ModelScope（可选）
```bash
cd f:/aastock
git pull origin master
cp f:/app_stockapril/data/stocks/stocks_master.json data/stocks/
git add -A && git commit -m "sync: YYYY-MM-DD" && git push origin master
```

### Step 5：汇报结果

飞书回复格式：
```
✅ 已完成

📊 本次处理：
- 文章：标题名（来源URL）
- 新增：N只（代码1 名称1, 代码2 名称2）
- 更新：M只（名称3 +1篇, 名称4 +1篇）
- 缺失：K只（名称5, 名称6）

🔄 GitHub: 已推送
🔄 ModelScope: 待构建
```

## 分组管理

### 创建分组
```python
# 读取 groups.json
g = json.load(open("data/groups/groups.json", "r", encoding="utf-8"))
g["groups"].append({
    "name": "分组名",
    "description": "描述",
    "stocks": ["股票名1", "股票名2", ...],
    "source": "来源",
    "color": "#6366f1"
})
json.dump(g, open("data/groups/groups.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

### 补充分组内容
从微信文章提取的个股，自动归属到对应分组。

## 热门题材

```python
t = json.load(open("data/hot_topics/hot_topics.json", "r", encoding="utf-8"))
t["topics"].append({
    "name": "题材名",
    "description": "描述",
    "stocks": [{"code": "000333", "name": "美的集团"}],
    "category": "分类"
})
```

## 错误处理

| 场景 | 处理 |
|------|------|
| JSON 文件损坏 | `git checkout HEAD -- data/stocks/stocks_master.json` |
| 文章无法抓取 | 尝试浏览器 UA / 通知用户手动提供正文 |
| 股票代码找不到 | 记录缺失列表，提示用户手动补充 |
| Git push 失败 | 重试 3 次，仍失败则通知用户检查网络 |
| LFS 指针未拉取 | `git lfs pull` |

## 注意事项

1. **去重优先**：每次处理前检查 `(source, title)` 是否已存在
2. **mention_count 同步**：新增文章后必须 `mention_count = len(articles)`
3. **last_updated 更新**：包含最新文章日期
4. **set 字段合并**：products/core_business/industry_position/chain/partners 使用 set 去重合并
5. **日期格式**：统一 `YYYY-MM-DD`
6. **不要暴露 token**：所有 API key/token 从配置文件或环境变量读取
7. **清理临时文件**：处理完成后删除临时 Python 脚本
