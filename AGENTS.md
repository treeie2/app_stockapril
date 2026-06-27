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
git add data/stocks/stocks_master.json data/stocks/*.json data/groups/groups.json data/hot_topics/
git commit -m "feat: add stocks from YYYY-MM-DD article"
git push origin main

# 如果是分组更新：
git add data/groups/groups.json
git commit -m "feat: update groups - GROUP_NAME"
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

### 分组数据流

```
通达信/同花顺 客户端
    ↓ 导出 .sel / .txt
/tmp/stock_groups/
    ↓ process_groups.py
data/groups/groups.json  ← 前端读取
    ↓ git push
GitHub → ModelScope 自动部署
```

### 方式 A：自动处理（推荐）

从 `/tmp/stock_groups/` 批量处理所有分组文件：

```bash
# 预览（不写入）
python process_groups.py --dry-run

# 正式处理
python process_groups.py

# 处理单个文件
python process_groups.py --file /tmp/stock_groups/THS_7纳米.txt
```

脚本自动完成：名称→代码映射、去重、推送到 GitHub。

### 方式 B：AI 手动创建分组

当用户通过飞书发送「新增分组：XXX」时，AI 直接操作 `groups.json`：

```python
import json, time

g = json.load(open("data/groups/groups.json", "r", encoding="utf-8"))

# 检查重名
if any(grp["name"] == "分组名" for grp in g["groups"]):
    print("分组已存在，跳过")
else:
    g["groups"].append({
        "id": f"group_{int(time.time()*1000)}",
        "name": "分组名",
        "description": "分组描述",
        "color": "#6366f1",
        "icon": "📊",
        "stocks": ["股票名1", "股票名2"],  # 用名称，AI 自动换码
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
        "category": "分类"
    })
    json.dump(g, open("data/groups/groups.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
```

### 分组格式规范

```json
{
  "id": "group_1719000000000_分组名",
  "name": "分组名",
  "description": "简短描述（≤200字）",
  "color": "#3b82f6",
  "icon": "📊",
  "stocks": ["000333", "002475"],  // 6位代码，非名称
  "category": "AI算力链",
  "created_at": "2026-06-27",
  "updated_at": "2026-06-27"
}
```

### category 分类规范

| category | 适用范围 |
|----------|------|
| `AI算力链` | AI芯片、算力租赁、液冷、光模块 |
| `半导体材料` | 硅片、光刻胶、靶材、气体 |
| `封装与PCB` | 先进封装、基板、PCB |
| `元器件` | 电容、电感、连接器、功率器件 |
| `稀有金属` | 锑、铟、钨、稀土 |
| `新能源` | 锂电、光伏、储能 |
| `物理AI与机器人` | 人形机器人、仿真、运动控制 |
| `航天` | 商业航天、SpaceX链 |
| `通讯电子` | 5G、手机、鸿蒙 |
| `华为产业链` | 华为生态相关 |

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

---

## 📋 Group & Hot Topics SKILL（分组 + 热点处理规范）

> 当 AI 收到飞书消息包含「新增分组」「新增热点」「创建题材」等关键词时，按本规范执行。

### 触发词

| 关键词 | 操作 |
|--------|------|
| `新增分组：XXX` | 创建股票分组 |
| `新增热点：XXX` / `新增题材：XXX` | 创建市场热点/题材 |
| `更新分组：XXX` | 追加股票到已有分组 |
| `查询分组` | 列出全部分组 |
| `删除分组：XXX` | 删除指定分组 |

### 分组处理（Group）

#### 输入格式
```
新增分组：7纳米
https://mp.weixin.qq.com/s/xxx
中芯国际, 华虹公司, 北方华创, 中微公司
```

#### AI 执行流程

1. **解析输入** — 提取分组名、文章 URL（如有）、股票列表
2. **查码** — 从 `stocks_master.json` 把股票名称映射为 6 位代码
3. **构建分组 JSON** — 按格式写入 `data/groups/groups.json`
4. **推 GitHub** — `git add data/groups/groups.json && git commit && git push`

#### 分组 JSON 模板

```python
import json, time, os
from datetime import datetime

# 读取现数据
gfile = "data/groups/groups.json"
g = json.load(open(gfile, "r", encoding="utf-8"))

# 智能推断 category
def infer_category(name, desc=""):
    text = name + desc
    if any(k in text for k in ["AI","算力","液冷","光模块","CPO","GPU","服务器"]): return "AI算力链"
    if any(k in text for k in ["半导体","芯片","硅","光刻","靶材","气体","CMP","封测"]): return "半导体材料"
    if any(k in text for k in ["封装","PCB","基板","载板","玻璃"]): return "封装与PCB"
    if any(k in text for k in ["电容","电感","连接器","功率","MLCC","变压器","氮化镓"]): return "元器件"
    if any(k in text for k in ["锂","钴","镍","锑","铟","钨","稀土","钼","铋"]): return "稀有金属"
    if any(k in text for k in ["光伏","储能","氢","电池","磷酸铁"]): return "新能源"
    if any(k in text for k in ["机器人","人形","仿真","具身"]): return "物理AI与机器人"
    if any(k in text for k in ["航天","卫星","SpaceX","低空"]): return "航天"
    if any(k in text for k in ["5G","通讯","手机","鸿蒙","折叠"]): return "通讯电子"
    if any(k in text for k in ["华为","昇腾","鲲鹏"]): return "华为产业链"
    return "产业链/IPO"

# 名称→代码映射
master = json.load(open("data/stocks/stocks_master.json", "r", encoding="utf-8"))
name_to_code = {}
for code, stock in master.get("stocks", {}).items():
    name_to_code[stock["name"]] = code

# 构建新分组
new_group = {
    "id": f"group_{int(time.time()*1000)}_{'分组名'}",
    "name": "分组名",
    "description": "分组描述（≤200字）",
    "color": "#3b82f6",           # 随机选一个 hex 色
    "icon": "📊",
    "stocks": ["000333", "002475"],  # 6位代码
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "updated_at": datetime.now().strftime("%Y-%m-%d"),
    "category": infer_category("分组名", "描述")
}

# 去重检查
existing_names = {grp["name"] for grp in g["groups"]}
if new_group["name"] in existing_names:
    print(f"⚠️ 分组「{new_group['name']}」已存在，追加股票")
    for grp in g["groups"]:
        if grp["name"] == new_group["name"]:
            for code in new_group["stocks"]:
                if code not in grp["stocks"]:
                    grp["stocks"].append(code)
            grp["updated_at"] = datetime.now().strftime("%Y-%m-%d")
else:
    g["groups"].append(new_group)

# 写入
json.dump(g, open(gfile, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

### 热点处理（Hot Topic）

#### 输入格式
```
新增热点：算电协同
AI算力+绿色电力一体化，多用户绿电直连政策发布
协鑫能科, 润泽科技, 晶科科技, 三峡能源
```

#### AI 执行流程

1. **解析** — 热点名 + 驱动逻辑 + 股票列表
2. **查码** — 名称→代码映射
3. **写入** `data/hot_topics/hot_topics.json`
4. **推 GitHub**

#### 热点 JSON 模板

```python
import json, time
from datetime import datetime

hfile = "data/hot_topics/hot_topics.json"
h = json.load(open(hfile, "r", encoding="utf-8"))

new_topic = {
    "id": f"topic_{int(time.time()*1000)}",
    "name": "题材名",
    "drivers": "驱动逻辑/催化剂描述",
    "stocks": [{"code": "000333", "name": "美的集团"}],
    "display": True,
    "created_at": datetime.now().strftime("%Y-%m-%d"),
    "updated_at": datetime.now().strftime("%Y-%m-%d"),
    "category": "分类"
}

# 去重
existing_names = {t["name"] for t in h["topics"]}
if new_topic["name"] not in existing_names:
    h["topics"].append(new_topic)
    json.dump(h, open(hfile, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

### 推 GitHub 统一命令

```bash
cd f:/app_stockapril
git add data/groups/groups.json data/hot_topics/hot_topics.json
git commit -m "feat: add group/hot-topic - XXX"
git push origin main
```

### 飞书汇报格式

```
✅ 分组/热点已创建

📋 类型：分组 / 热点
📛 名称：XXX
📊 股票：N 只（代码1 名称1, 代码2 名称2）
📂 分类：AI算力链
🔄 GitHub: 已推送
🔄 ModelScope: 自动构建中 → https://treeie-aastock.ms.show
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
