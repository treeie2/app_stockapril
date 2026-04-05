# 🚀 GitHub 推送命令

## 在你的电脑上执行（不是服务器）

---

## 方式 1: 使用 GitHub CLI（最简单）

### 1. 安装 GitHub CLI

**macOS:**
```bash
brew install gh
```

**Windows:**
```bash
winget install GitHub.cli
```

**Linux:**
```bash
sudo apt install gh
```

### 2. 登录 GitHub
```bash
gh auth login
```

### 3. 创建并推送
```bash
cd /path/to/railway-deploy

# 创建仓库
gh repo create stock-research --public --source=. --push
```

**完成！** 🎉

---

## 方式 2: 使用 Personal Access Token

### 1. 创建 Token

访问：https://github.com/settings/tokens/new

- Note: `Railway Deploy`
- Select scopes: **repo** (全选)
- 点击 **Generate token**
- **复制 Token**（只显示一次！）

### 2. 推送代码

```bash
cd /path/to/railway-deploy

git init
git add .
git commit -m "Deploy to Railway"
git branch -M main

# 替换 YOUR_TOKEN 为你的 token
git remote add origin https://YOUR_TOKEN@github.com/treeie2/stock-research.git
git push -u origin main
```

---

## 方式 3: 在 GitHub 网站手动创建

### 1. 创建仓库

访问：https://github.com/new

- Repository name: `stock-research`
- Public 或 Private 都可以
- 点击 **Create repository**

### 2. 按提示推送

GitHub 会显示推送命令，类似：

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/treeie2/stock-research.git
git push -u origin main
```

### 3. 输入密码

推送时会要求输入：
- Username: `treeie2`
- Password: 使用 Personal Access Token（不是 GitHub 密码）

---

## ✅ 推送完成后

1. 访问：https://railway.app/
2. 登录 GitHub
3. New Project → Deploy from GitHub repo
4. 选择 `stock-research`
5. 自动部署！

---

## 📝 快速清单

- [ ] 在 GitHub 创建仓库 `stock-research`
- [ ] 推送代码（3 种方式选 1 个）
- [ ] Railway 连接 GitHub 仓库
- [ ] 等待部署完成
- [ ] 访问分配的域名

---

**推荐方式 1（GitHub CLI）最简单！**
