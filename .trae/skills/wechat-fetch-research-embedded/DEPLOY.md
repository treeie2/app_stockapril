# WeChat Fetch Research - 服务器部署指南

## 概述

本文档介绍如何在服务器（龙虾/云服务器）上部署 `wechat-fetch-research-embedded` skill。

## 部署方式

### 方式一：Docker Compose（推荐）

#### 1. 准备工作

```bash
# 克隆代码到服务器
git clone <your-repo> /opt/wechat-fetch
cd /opt/wechat-fetch

# 创建必要目录
mkdir -p data raw_material logs secrets

# 准备配置文件
cp .env.example .env
# 编辑 .env 填入你的 API 密钥等配置
nano .env
```

#### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# API 密钥（必填）
PRIMARY_API_KEY=your_volces_api_key
FALLBACK_API_KEY=your_siliconflow_api_key

# GitHub（可选）
GITHUB_TOKEN=ghp_xxx
GITHUB_REPO=username/repo

# 日志级别
LOG_LEVEL=INFO
```

#### 3. 准备 Firebase 凭证

如果你有 Firebase 同步需求：

```bash
# 将 Firebase 凭证文件放入 secrets 目录
cp /path/to/firebase-credentials.json secrets/
```

#### 4. 构建并启动

```bash
# 构建镜像
docker-compose build

# 启动基础服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 5. 运行任务

```bash
# 单次运行（处理一篇文章）
docker-compose run --rm wechat-fetch \
  python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --sync-firestore

# 带 GitHub 同步
docker-compose run --rm wechat-fetch \
  python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --sync-firestore \
  --sync-github
```

### 方式二：使用任务队列（Celery + Redis）

适合需要批量处理大量文章的场景。

```bash
# 启动完整队列服务
docker-compose --profile queue up -d

# 提交任务
python -c "
from tasks import process_article
result = process_article.delay('https://mp.weixin.qq.com/s/...', sync_firestore=True)
print(f'Task ID: {result.id}')
"

# 查看 Flower 监控界面
open http://localhost:5555
```

### 方式三：原生 Python 部署

如果不使用 Docker：

```bash
# 1. 安装 Python 3.11+
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 设置环境变量
export PRIMARY_API_KEY="your_key"
export FALLBACK_API_KEY="your_key"

# 4. 运行
python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..."
```

## 首次运行注意事项

### 微信登录验证

微信公众号有反爬机制，首次运行可能需要手动登录：

```bash
# 使用非 headless 模式（显示浏览器窗口）
docker-compose run --rm -p 5900:5900 wechat-fetch \
  python scripts/pipeline.py \
  --url "https://mp.weixin.qq.com/s/..." \
  --no-headless

# 通过 VNC 连接查看浏览器（密码: 123456）
# 使用 VNC Viewer 连接: localhost:5900
```

完成验证后，登录状态会保存在 `browser_profile` volume 中，后续可以正常使用 headless 模式。

## 目录结构

```
/opt/wechat-fetch/
├── data/                    # 生成的 JSON 数据
├── raw_material/            # 原始文章内容
├── logs/                    # 日志文件
├── secrets/                 # 凭证文件（不要提交到 git）
├── assets/                  # 股票列表等静态资源
├── scripts/                 # Python 脚本
├── docker-compose.yml       # Docker 配置
├── Dockerfile              # 镜像定义
└── .env                    # 环境变量
```

## 常用命令

```bash
# 查看日志
docker-compose logs -f wechat-fetch

# 重启服务
docker-compose restart

# 更新代码后重建
docker-compose down
git pull
docker-compose build
docker-compose up -d

# 清理旧数据（保留最近 7 天）
docker-compose run --rm wechat-fetch \
  python -c "from tasks import cleanup_old_files; cleanup_old_files.delay(7)"

# 进入容器调试
docker-compose exec wechat-fetch bash
```

## 定时任务

使用 cron 设置定时抓取：

```bash
# 编辑 crontab
crontab -e

# 每天 9:30 抓取文章
30 9 * * * cd /opt/wechat-fetch && docker-compose run --rm wechat-fetch python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --sync-firestore >> logs/cron.log 2>&1
```

## 监控与告警

### 日志监控

```bash
# 实时查看错误
docker-compose logs -f wechat-fetch | grep ERROR

# 查看最近 100 行
docker-compose logs --tail=100 wechat-fetch
```

### 健康检查

```bash
# 检查容器状态
docker-compose ps

# 检查磁盘空间
df -h /opt/wechat-fetch
```

## 故障排查

### 问题：Playwright 浏览器启动失败

**解决**：
```bash
# 重新安装浏览器
docker-compose run --rm wechat-fetch playwright install chromium
```

### 问题：API 限流

**解决**：系统会自动切换到备用 API，确保两个 API 密钥都有效。

### 问题：Firebase 同步失败

**解决**：
1. 检查凭证文件路径：`secrets/firebase-credentials.json`
2. 检查文件权限：`chmod 600 secrets/firebase-credentials.json`

### 问题：VNC 连接不上

**解决**：
```bash
# 检查端口映射
docker-compose ps

# 重启服务
docker-compose restart
```

## 安全建议

1. **不要提交凭证到 Git**
   - `secrets/` 目录已加入 `.gitignore`
   - `.env` 文件已加入 `.gitignore`

2. **限制文件权限**
   ```bash
   chmod 600 .env
   chmod 600 secrets/*
   ```

3. **使用非 root 用户运行容器**（可选）
   - 修改 `docker-compose.yml` 添加 `user: "1000:1000"`

4. **定期更换 API 密钥**

## 性能优化

### 调整资源限制

编辑 `docker-compose.yml`：

```yaml
deploy:
  resources:
    limits:
      memory: 8G  # 根据服务器调整
    reservations:
      memory: 2G
```

### 批量处理优化

使用 Celery 并发处理：

```python
from tasks import batch_process

urls = [
    "https://mp.weixin.qq.com/s/...",
    "https://mp.weixin.qq.com/s/...",
    # ...
]

# 批量提交，自动并发处理
batch_process.delay(urls, sync_firestore=True)
```

## 更新维护

```bash
# 备份数据
cp -r data data.backup.$(date +%Y%m%d)

# 更新代码
git pull

# 重建镜像
docker-compose build

# 重启服务
docker-compose up -d

# 验证
docker-compose logs -f
```

## 支持

如有问题，请查看：
- 日志文件：`logs/pipeline.log`
- 原始文档：[SKILL.md](SKILL.md)
- 数据结构规范：[references/数据结构规范_v2.md](references/数据结构规范_v2.md)
