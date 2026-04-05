# 🚨 Railway 核弹级修复方案

**时间**: 2026-03-20 19:38
**状态**: ❌ Railway 顽固使用旧代码（1455 只股票）

---

## 🔍 问题确认

### GitHub 最新代码（正确）
```bash
✅ main.py 读取 stocks_master.json.gz
✅ 数据：1853 只股票
✅ 长江电力存在
```

### Railway 部署日志（错误）
```
❌ 19:33:09 启动
❌ 加载 1455 只股票
❌ 完全无视 GitHub 最新提交
```

---

## 💣 根本原因

**Railway 构建缓存污染**

Railway 可能：
1. 缓存了旧的 Docker 镜像
2. Git 连接失效但未断开
3. 构建钩子未触发
4. 环境变量指向旧分支

---

## ☢️ 核弹级解决方案（按顺序执行）

### 步骤 1: 完全断开 Git 连接

1. Railway 控制台 → 项目 `stock-research`
2. Settings → Git
3. **点击 "Disconnect"**
4. 确认断开

### 步骤 2: 清理 Railway 缓存

1. Settings → "Danger Zone"
2. **点击 "Delete Project"**（删除项目）
3. 确认删除

### 步骤 3: 重新创建项目

1. Railway 控制台 → **"New Project"**
2. **"Deploy from GitHub repo"**
3. 选择 `treeie2/stock-research`
4. 确认分支是 `main`
5. 点击 **"Connect and Deploy"**

### 步骤 4: 验证部署

等待 5-10 分钟部署完成后：

```bash
# 测试长江电力
curl -s "https://web-production-a1006c.up.railway.app/api/stock/600900"

# 应该返回股票数据，不是"股票不存在"
```

---

## 🎯 备选方案（如果不删除项目）

### 方案 A: 强制重新构建

1. Railway 控制台 → Deployments
2. 找到最新部署
3. 点击 "..." → **"Rebuild"**
4. 勾选 **"No cache"**（如果有）

### 方案 B: 修改环境变量触发重建

1. Settings → Variables
2. 添加新变量：`BUILD_NUMBER=202603201938`
3. 保存 → 自动触发重新部署

### 方案 C: 修改 Procfile 触发重建

```bash
# 修改 Procfile
echo "web: gunicorn main:app --bind 0.0.0.0:$PORT --reload" > Procfile
git add Procfile
git commit -m "chore: 强制重新构建"
git push
```

---

## ⚠️ 删除项目前确认

删除项目会：
- ✅ 保留 GitHub 代码（不受影响）
- ✅ 保留 Railway 域名（可以重新绑定）
- ❌ 丢失部署历史
- ❌ 丢失环境变量（如果有）

**如果你有重要环境变量，请先记录！**

---

## 📋 当前提交状态

```
✅ 5549b62 fix: 恢复 stocks_master.json 到部署包
✅ 1bcb382 docs: 添加 Railway 紧急修复方案
✅ fb2273e chore: 强制重新构建版本号
```

GitHub 代码 100% 正确，问题在 Railway 端。

---

## 🎯 推荐行动

**立即执行"步骤 1-3"：删除并重新创建项目**

这是最彻底的解决方案，保证拉取最新代码。

预计时间：10-15 分钟

---

**紧急程度**: 🔴🔴🔴 最高
**影响**: 所有新功能不可用
**建议**: 立即执行核弹方案
