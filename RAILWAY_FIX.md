# Railway 部署修复方案

**时间**: 2026-03-20 18:43
**问题**: Railway 部署不完整，API 超时，首页加载失败

---

## 🐛 症状

1. ✅ GitHub 数据正确（1853 只股票，有长江电力）
2. ✅ 本地数据正确
3. ❌ Railway API 超时（`/api/stock/600900`）
4. ❌ 首页加载超时
5. ✅ 搜索页面能访问（`/search`）

---

## 🔍 可能原因

### 1. Railway 构建失败
- 数据文件太大（2.3MB）
- 构建超时
- 内存不足

### 2. 路由问题
- main.py 启动失败
- gunicorn worker 崩溃
- 端口绑定问题

### 3. 缓存问题
- Railway CDN 缓存旧版本
- 浏览器缓存

---

## 🔧 解决方案

### 方案 1: 检查 Railway 控制台日志
1. 访问 https://railway.app/
2. 找到项目 `stock-research`
3. 查看 "Deployments" 标签
4. 检查最新部署是否成功
5. 查看 "View Logs" 找错误信息

### 方案 2: 手动重启部署
1. Railway 控制台 → "Deploy" → "Restart"
2. 等待 5-10 分钟
3. 测试 API

### 方案 3: 压缩数据文件
如果数据文件太大导致构建失败：
```bash
# 压缩 master.json
gzip -k data/master/stocks_master.json
# 修改 main.py 读取 .gz 文件
```

### 方案 4: 检查 main.py 启动
查看日志中是否有：
- `ModuleNotFoundError`
- `JSONDecodeError`
- `Port already in use`
- `Worker timeout`

---

## 📋 验证步骤

部署成功后验证：

```bash
# 1. 测试首页
curl -s "https://web-production-a1006c.up.railway.app/" | grep -o "1853"

# 2. 测试 API
curl -s "https://web-production-a1006c.up.railway.app/api/stock/600900" | grep "长江电力"

# 3. 测试搜索
curl -s "https://web-production-a1006c.up.railway.app/search" | grep "全文搜索"
```

---

## ⚠️ 紧急方案

如果 Railway 持续失败：

### 临时方案 1: 使用备用域名
检查是否有其他 Railway 部署 URL

### 临时方案 2: 本地测试
```bash
cd ~/openclaw/workspace/railway-deploy
python3 main.py
# 访问 http://localhost:5000
```

### 临时方案 3: 切换到其他部署平台
- Vercel
- Render
- Fly.io

---

**下一步**: 需要访问 Railway 控制台查看部署日志
