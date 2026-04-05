# Railway 部署检查清单

**时间**: 2026-03-19 09:43
**触发提交**: 653fe11

## ✅ 已完成

### 1. 数据验证

```bash
✅ stocks_master.json 已更新
- 金安国纪 (002636) 数据正确:
  - 行业：电子 - 电子化学品 - 电子化学品Ⅲ
  - 概念：覆铜板，5G 概念，新能源汽车，华为概念，集成电路
  - 核心业务：覆铜板研发、生产和销售
  - 主要产品：覆铜板，粘结片，半固化片，铝基覆铜板
  - 行业地位：国内覆铜板行业龙头，全球市场份额领先
```

### 2. Git 推送

```bash
✅ 已推送到 GitHub
提交：653fe11 - chore: trigger redeploy
仓库：https://github.com/treeie2/stock-research
```

### 3. Railway 触发

```bash
✅ 已推送触发提交
✅ Railway 应自动检测并部署
```

## ⏳ 等待部署

**预计时间**: 1-3 分钟

### 监控步骤

#### 1. 检查 GitHub Actions
访问：https://github.com/treeie2/stock-research/actions
- 查看最新的推送
- 确认无错误

#### 2. 检查 Railway Dashboard
访问：https://railway.app/dashboard
- 选择项目：`stock-research`
- 查看 **Deployments** 标签
- 状态应从 `Building` → `Deploying` → `Running`

#### 3. 查看部署日志
在 Railway Dashboard 中：
- 点击 **Deployments** → 最新部署
- 查看 **Logs**
- 确认无错误信息

#### 4. 验证应用
部署完成后访问：
```
https://web-production-a1006c.up.railway.app/
```

## 🔍 验证数据

### 方法 1: 浏览器访问

访问首页，搜索 `002636` 或 `金安国纪`

### 方法 2: API 测试

```bash
curl "https://web-production-a1006c.up.railway.app/api/stocks/002636"
```

**预期响应**:
```json
{
  "code": "002636",
  "name": "金安国纪",
  "industry": "电子 - 电子化学品 - 电子化学品Ⅲ",
  "concepts": ["覆铜板", "5G 概念", "新能源汽车", "华为概念", "集成电路"],
  "core_business": ["覆铜板研发、生产和销售"],
  "products": ["覆铜板", "粘结片", "半固化片", "铝基覆铜板"],
  "industry_position": ["国内覆铜板行业龙头", "全球市场份额领先"]
}
```

### 方法 3: 检查首页显示

访问：`https://web-production-a1006c.up.railway.app/`

**预期**:
- 金安国纪应显示在第 1 位（最新文章日期 2026-03-19）
- 显示行业：电子 - 电子化学品 - 电子化学品Ⅲ
- 显示概念：覆铜板，5G 概念，新能源汽车...
- 显示核心业务：覆铜板研发、生产和销售
- 显示主要产品：覆铜板，粘结片，半固化片...

## ⚠️ 故障排除

### 问题 1: Railway 未自动部署

**解决方案**:
1. 访问 Railway Dashboard
2. 点击 **Deployments**
3. 手动点击 **Redeploy**

### 问题 2: 部署失败

**检查日志**:
```
Railway Dashboard → Deployments → 最新部署 → Logs
```

**常见错误**:
- 依赖安装失败 → 检查 `requirements.txt`
- 启动命令失败 → 检查 `.railway.json`
- 端口绑定失败 → 检查 `main.py`

### 问题 3: 数据未更新

**可能原因**:
- Railway 缓存
- 数据文件路径错误

**解决方案**:
1. Railway Dashboard → **Redeploy**
2. 检查日志中的文件加载信息
3. 确认数据文件在 Git 中：
   ```bash
   git ls-files data/master/stocks_master.json
   ```

### 问题 4: 应用返回 404/502

**解决方案**:
1. 等待 2-3 分钟（部署需要时间）
2. 检查 Railway 日志
3. 确认 `main.py` 能正常启动

## 📊 部署时间线

```
09:35 - 数据更新完成
09:35 - Git 推送完成
09:43 - 触发重新部署提交
09:44 - ⏳ 等待 Railway 部署
09:47 - 预计部署完成
```

## 🎯 成功标准

- [ ] Railway 显示 `Running` 状态
- [ ] 访问首页无错误
- [ ] 搜索 `002636` 显示正确数据
- [ ] 行业、概念、核心业务等字段正确显示
- [ ] 多篇文章正确显示

## 🔗 相关链接

- **GitHub**: https://github.com/treeie2/stock-research
- **Railway Dashboard**: https://railway.app/dashboard
- **应用 URL**: https://web-production-a1006c.up.railway.app/
- **最新提交**: https://github.com/treeie2/stock-research/commit/653fe11

---

**最后更新**: 2026-03-19 09:43
