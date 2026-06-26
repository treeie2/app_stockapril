# BOOTSTRAP.md — 龙虾（Lobster）环境初始化指南

> 将 `app_stockapril` 项目部署到云端龙虾服务器，使其能接收飞书消息并自动处理微信文章。

## 1. 环境要求

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 脚本执行 |
| Git | 2.40+ | 代码同步 |
| Node.js | 20+ | 飞书 SDK（可选） |
| pip | 最新 | 依赖安装 |

## 2. 首次部署

### 2.1 克隆仓库

```bash
git clone https://github.com/treeie2/app_stockapril.git
cd app_stockapril
```

### 2.2 处理 LFS 大文件

```bash
git lfs install
git lfs pull
```

### 2.3 安装 Python 依赖

```bash
pip install -r requirements.txt
pip install gunicorn openai pandas openpyxl xlsxwriter supabase
```

### 2.4 验证核心数据文件

```bash
python -c "
import json, os
f = 'data/stocks/stocks_master.json'
if os.path.getsize(f) > 1000000:
    d = json.load(open(f, 'r', encoding='utf-8'))
    print(f'OK: {len(d[\"stocks\"])} stocks')
else:
    print('ERROR: stocks_master.json is too small (LFS pointer?)')
"
```

如果文件过小（< 1MB），说明 LFS 未拉取成功：
```bash
git checkout HEAD -- data/stocks/stocks_master.json
git lfs pull
```

### 2.5 配置 SSH（GitHub 推送）

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "lobster@stock" -f ~/.ssh/github_lobster

# 配置 SSH（走 443 端口绕过防火墙）
cat >> ~/.ssh/config << EOF
Host github.com
  HostName ssh.github.com
  Port 443
  IdentityFile ~/.ssh/github_lobster
  StrictHostKeyChecking no
EOF

# 测试连接
ssh -T git@github.com
# 应输出: Hi treeie2! You've successfully authenticated...
```

将 `~/.ssh/github_lobster.pub` 添加到 https://github.com/settings/keys

### 2.6 配置 Git

```bash
git config --global user.email "lobster@stock"
git config --global user.name "Lobster AI"
```

## 3. 数据同步

### 3.1 拉取 GitHub 最新数据（每日）

```bash
cd f:/app_stockapril
git pull origin main
# 如果 pull 失败，强制重置：
# git fetch origin main && git reset --hard origin/main && git lfs pull
```

### 3.2 JSON 修复（启动前检查）

```python
# 如果 stocks_master.json 损坏（LFS 冲突等）
import json
try:
    json.load(open("data/stocks/stocks_master.json", "r", encoding="utf-8"))
except:
    import subprocess
    subprocess.run(["git", "checkout", "HEAD", "--", "data/stocks/stocks_master.json"])
    subprocess.run(["git", "lfs", "pull"])
```

## 4. 项目文件结构

```
app_stockapril/
├── main.py                     # Flask 应用（本地/Vercel/ModelScope）
├── requirements.txt            # Python 依赖
├── AGENTS.md                   # AI 执行规范
├── BOOTSTRAP.md                # 本文件
├── supabase_config.json        # Supabase 凭证
├── data/
│   ├── stocks/
│   │   ├── stocks_master.json  # 主数据库（3545+ stocks）
│   │   ├── stocks_master.json.gz
│   │   ├── stocks_index.json
│   │   └── YYYY-MM-DD.json     # 日期分片
│   ├── groups/
│   │   └── groups.json         # 分组数据
│   └── hot_topics/
│       └── hot_topics.json     # 热门题材
├── .trae/skills/
│   └── wechat-fetch-research-embedded/
│       ├── SKILL.md            # Skill 说明
│       ├── config.json         # LLM 配置
│       ├── scripts/            # 核心脚本
│       └── assets/             # 股票列表（xls）
└── archived/
    └── 全部个股.xls            # 完整股票列表
```

## 5. 快捷命令（龙虾专用）

### 处理单篇文章
```bash
cd f:/app_stockapril && python -c "
# 你的 AI 生成的处理脚本
# AGENTS.md 里定义了完整流程
"
```

### 推送到 GitHub
```bash
cd f:/app_stockapril && \
git add data/stocks/stocks_master.json && \
git commit -m 'feat: update from lobster' && \
git push origin main
```

### 拉取最新数据
```bash
cd f:/app_stockapril && git pull origin main && git lfs pull
```

### 健康检查
```bash
cd f:/app_stockapril && python -c "
import json, os
p = 'data/stocks/stocks_master.json'
d = json.load(open(p, 'r', encoding='utf-8'))
print(f'Stocks: {len(d[\"stocks\"])}')
print(f'Updated: {d.get(\"updated_at\", \"?\")}')
# 检查最近更新的股票
from datetime import datetime, timedelta
recent = datetime.now() - timedelta(days=7)
count = 0
for c, s in d['stocks'].items():
    lu = s.get('last_updated', '')
    if lu >= recent.strftime('%Y-%m-%d'):
        count += 1
print(f'Recent (7d): {count}')
"
```

## 6. 故障恢复

| 问题 | 解决方案 |
|------|---------|
| `stocks_master.json` 为空 | `git lfs pull` |
| Git push 失败 | 检查 SSH config → 走 443 端口 |
| LLM API 调用失败 | 检查 `config.json` 中的 api_key |
| 依赖缺失 | `pip install -r requirements.txt` |
| 端口冲突 | Flask 默认 7860，可改 `PORT` 环境变量 |
| LFS 文件损坏 | `git checkout HEAD -- data/stocks/stocks_master.json` |
