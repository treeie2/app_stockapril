# 🚂 Railway 部署 - 最终方案

## ✅ 项目已准备好

文件位置：`/home/admin/openclaw/workspace/railway-deploy/`

**文件列表：**
- ✅ `main.py` - Flask 应用
- ✅ `requirements.txt` - 依赖
- ✅ `Procfile` - 启动命令
- ✅ `.railway.json` - 配置
- ✅ `README.md` - 说明

---

## 🌐 部署步骤（GitHub 方式）

### 第 1 步：在 GitHub 创建仓库

**访问：** https://github.com/new

- Repository name: `stock-research`
- Public（公开）
- 点击 **Create repository**

---

### 第 2 步：上传文件

**方法 A: 网页上传（最简单）**

1. 创建仓库后，GitHub 会显示 "uploading an existing file"
2. 点击该链接
3. 把以下文件拖进去：
   - `main.py`
   - `requirements.txt`
   - `Procfile`
   - `.railway.json`
4. 点击 **Commit changes**

**方法 B: Git 推送**

```bash
# 在你的电脑
cd railway-deploy
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/treeie2/stock-research.git
git push -u origin main
```

推送时需要：
- Username: `treeie2`
- Password: Personal Access Token

**获取 Token:** https://github.com/settings/tokens/new
- 勾选 `repo` 权限
- 生成后复制

---

### 第 3 步：Railway 连接

**访问：** https://railway.app/

1. 点击 **New Project**
2. 选择 **Deploy from GitHub repo**
3. 选择 `stock-research` 仓库
4. Railway 自动开始部署！

---

### 第 4 步：等待部署

Railway 会：
- 检测 Python 项目
- 安装 `pip install -r requirements.txt`
- 启动 `gunicorn main:app --bind 0.0.0.0:$PORT`

**部署成功后显示：**
```
✅ Generated Domain: stock-research-production.up.railway.app
```

---

## ✅ 完成！

**访问地址：**
```
https://stock-research-production.up.railway.app
```

可以在手机、公司电脑、家里任何地方访问！

---

## 📝 快速清单

- [ ] GitHub 创建仓库 `stock-research`
- [ ] 上传 4 个文件（main.py, requirements.txt, Procfile, .railway.json）
- [ ] Railway 连接 GitHub 仓库
- [ ] 等待部署完成（约 2-3 分钟）
- [ ] 访问分配的域名

---

## 💡 文件位置

服务器路径：
```
/home/admin/openclaw/workspace/railway-deploy/
```

你可以：
1. 用 SCP/SFTP 下载到本地
2. 或在 GitHub 网页手动上传

---

**需要我帮你打包成 ZIP 吗？** 这样下载更方便！
