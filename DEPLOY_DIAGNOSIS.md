# Railway 部署问题诊断

**时间**: 2026-03-19 09:50
**问题**: Railway 应用显示旧数据

## 诊断结果

### 1. 本地数据 ✅

```
stocks_master.json: 1.7MB (已更新)
最后修改：2026-03-19 09:35
```

### 2. GitHub 数据 ✅

```
blob size: 1716246 bytes (1.7MB)
提交：a4d6d6f
```

### 3. Railway 状态 ⚠️

```
应用可访问：✅
首页加载：✅
API 端点：✅ (但返回旧数据)
数据加载：❌ (股票不存在)
```

## 可能原因

### 原因 1: Railway 缓存

Railway 可能缓存了旧的数据文件。

**解决方案**:
```bash
# 触发重新部署
git commit --allow-empty -m "chore: force redeploy"
git push
```

### 原因 2: 数据文件未正确加载

检查 `main.py` 中的数据加载逻辑。

**文件路径**:
```python
MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
```

### 原因 3: 部署未完成

Railway 可能还在构建中。

**检查**:
1. Railway Dashboard → Deployments
2. 查看最新部署状态
3. 等待状态变为 `Running`

## 解决方案

### 方案 1: 清除缓存重新部署

```bash
cd /home/admin/openclaw/workspace/railway-deploy

# 修改 .railway.json 禁用缓存
cat > .railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "cache": false
  },
  "deploy": {
    "startCommand": "gunicorn main:app --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

git add .railway.json
git commit -m "chore: disable build cache"
git push
```

### 方案 2: 手动触发 Railway 重新部署

1. 访问：https://railway.app/dashboard
2. 选择项目：`stock-research`
3. 点击 **Deployments**
4. 点击 **Redeploy**

### 方案 3: 检查启动日志

在 Railway Dashboard 中查看日志，确认：
- 数据文件加载成功
- 无错误信息
- 股票数量正确

## 验证步骤

部署完成后：

```bash
# 1. 测试 API
curl "https://web-production-a1006c.up.railway.app/api/stock/002636"

# 预期响应应包含：
# - industry: 电子 - 电子化学品 - 电子化学品Ⅲ
# - concepts: 覆铜板，5G 概念...
# - core_business: 覆铜板研发...
```

## 后续行动

1. ✅ 等待当前部署完成（2-3 分钟）
2. ⏳ 测试 API 端点
3. ⏳ 验证数据正确性
4. ⏳ 如仍失败，手动触发重新部署

---

**最后更新**: 2026-03-19 09:50
