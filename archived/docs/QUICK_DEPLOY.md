# 🚂 Railway 快速部署 - 浏览器方式

## ✅ CLI 已安装

Railway CLI 已安装完成，但需要浏览器授权。

---

## 🌐 方式 1: 浏览器授权（推荐）

### 第 1 步：打开授权链接

**在浏览器访问：**
```
https://railway.app/login
```

### 第 2 步：登录

- GitHub 账号（推荐）
- Google 账号
- 邮箱

### 第 3 步：返回终端

登录后，在终端执行：
```bash
cd /home/admin/openclaw/workspace/railway-deploy
railway init
railway up
```

---

## 🚀 方式 2: GitHub 推送（无需 CLI）

### 第 1 步：创建 GitHub 仓库

1. 访问：https://github.com/new
2. 仓库名：`stock-research`
3. 公开/私有都可以
4. 点击 **Create repository**

### 第 2 步：推送代码

```bash
cd /home/admin/openclaw/workspace/railway-deploy

git init
git add .
git commit -m "Deploy to Railway"

# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/stock-research.git
git branch -M main
git push -u origin main
```

### 第 3 步：Railway 连接

1. 访问：https://railway.app/
2. 登录（用 GitHub）
3. 点击 **New Project**
4. 选择 **Deploy from GitHub repo**
5. 选择 `stock-research` 仓库
6. 点击 **Deploy**

### 第 4 步：等待部署

Railway 会自动：
- 检测 Python 项目
- 安装依赖
- 启动应用

**部署成功后会提供域名：**
```
https://stock-research-production.up.railway.app
```

---

## 💡 推荐：方式 2（GitHub 推送）

**优点：**
- ✅ 无需 CLI 授权
- ✅ 代码有版本控制
- ✅ 后续更新只需 `git push`
- ✅ Railway 自动重新部署

---

## 📝 快速执行清单

### 方式 2（GitHub）

- [ ] 在 GitHub 创建仓库 `stock-research`
- [ ] 复制仓库 URL（如：https://github.com/yourname/stock-research.git）
- [ ] 在终端执行推送命令
- [ ] Railway 连接 GitHub 仓库
- [ ] 等待部署完成
- [ ] 访问分配的域名

---

**你想用哪种方式？**
1. 浏览器登录 Railway（我提供链接）
2. GitHub 推送（给我你的 GitHub 用户名，我帮你准备命令）
