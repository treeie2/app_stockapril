# 🚂 Railway 部署 - 个股研究数据库

## ✅ 部署文件已准备

位置：`/home/admin/openclaw/workspace/railway-deploy/`

**文件列表：**
- `main.py` - Flask 应用（简化版，使用示例数据）
- `requirements.txt` - Python 依赖
- `Procfile` - Railway 启动命令
- `.railway.json` - Railway 配置

---

## 📝 部署步骤

### 第 1 步：注册 Railway

**访问：** https://railway.app/

**注册：**
- 用 GitHub 账号登录（推荐）
- 或 Google/邮箱

---

### 第 2 步：创建新项目

1. 点击 **New Project**
2. 选择 **Deploy from GitHub repo**

---

### 第 3 步：连接 GitHub

**选项 A: 直接推送（推荐）**

```bash
cd /home/admin/openclaw/workspace/railway-deploy

# 初始化 Git
git init
git add .
git commit -m "Initial commit - Stock Research DB"

# 创建 GitHub 仓库（在 GitHub 网站）
# 然后推送
git remote add origin https://github.com/YOUR_USERNAME/stock-research.git
git push -u origin main
```

**选项 B: Railway CLI 部署**

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up
```

---

### 第 4 步：在 Railway 配置

1. **Variables** - 无需配置（示例数据）
2. **Settings** - 自动检测 Python
3. **Deploy** - 自动开始部署

---

### 第 5 步：获取域名

部署成功后，Railway 会提供：
```
https://stock-research-production.up.railway.app
```

---

## ✅ 完成！

**访问你的网站：**
- Railway 分配的域名
- 或绑定自定义域名

---

## 💰 费用

- **免费额度**: $5/月
- **实际使用**: 约 $2-3/月（个人使用）
- **超出**: 按量计费

---

## 📊 与本地版本对比

| 功能 | 本地版本 | Railway 版本 |
|------|---------|-------------|
| 数据源 | 本地 JSON 文件 | 示例数据 |
| 股票数量 | 1502 只 | 示例 10 只 |
| 文章数据 | 731 篇 | 无 |
| 搜索功能 | ✅ | ⏳ 待添加 |
| 访问速度 | 本地最快 | 全球 CDN |
| 可用性 | 需保持运行 | 99.9% SLA |

---

## 🔧 后续优化

1. **连接真实数据** - 用 Railway 环境变量配置数据源
2. **添加搜索** - 集成搜索功能
3. **数据库** - 用 Railway PostgreSQL
4. **定时更新** - Railway Cron

---

**需要我帮你推送到 GitHub 吗？** 或者你想手动操作？
