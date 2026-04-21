# Vercel 部署问题解决指南

## 问题现状

- ✅ **GitHub 仓库数据已更新**
  - 最新提交：`7435718` - 同步所有分片数据：8 个文件，3164 只个股
  - 包含 002416 爱施德、301666 力诺药包等新股数据
  
- ❌ **Vercel 应用未自动重新部署**
  - 网站仍显示旧数据（2026-04-19）
  - 访问 https://app-stockapril.vercel.app/stock/002416 无法打开

## 解决方案

### 方案 1：手动触发 Vercel 部署（推荐 - 立即生效）

1. **访问 Vercel Dashboard**
   - 打开：https://vercel.com/dashboard

2. **找到项目**
   - 找到 `app-stockapril` 项目

3. **点击 Redeploy**
   - 点击项目卡片
   - 点击右上角 "..." 菜单
   - 选择 "Redeploy"
   - 确认部署

4. **等待部署完成**
   - 部署通常需要 1-3 分钟
   - 部署完成后，网站会自动更新到最新数据

### 方案 2：配置自动部署（一劳永逸）

已创建 GitHub Actions workflow 文件：`.github/workflows/trigger-vercel.yml`

**需要在 Vercel 设置中获取：**

1. **获取 Vercel Token**
   - 访问：https://vercel.com/account/tokens
   - 创建新的 Token
   - 复制 Token

2. **获取 Project ID**
   - 访问：https://vercel.com/dashboard
   - 点击 `app-stockapril` 项目
   - Settings -> General -> Project ID
   - 复制 Project ID

3. **添加到 GitHub Secrets**
   - 访问：https://github.com/treeie2/app_stockapril/settings/secrets/actions
   - 添加两个 secrets：
     - `VERCEL_TOKEN`: 你的 Vercel Token
     - `VERCEL_PROJECT_ID`: 你的 Project ID

4. **推送触发部署**
   - 每次推送到 main 分支时自动触发部署

### 方案 3：使用本地脚本触发

```powershell
# 设置环境变量
$env:VERCEL_TOKEN = "your_token_here"
$env:VERCEL_PROJECT_ID = "your_project_id"

# 运行脚本
python trigger_vercel_deploy.py
```

## 验证部署成功

部署完成后，访问：
- https://app-stockapril.vercel.app/stock/002416 - 爱施德
- https://app-stockapril.vercel.app/stock/301666 - 力诺药包

应该能看到完整的股票信息。

## Git 推送问题

当前本地有 2 个提交未推送：
- `85f12bf` - 添加 GitHub Actions 自动触发 Vercel 部署
- `94abd88` - 更新股票数据：8 个分片文件，3169 只个股

推送被拒绝可能是因为：
1. 仓库大小限制（105MB 超过 LFS 限制）
2. 分支保护规则

**建议**：先手动触发 Vercel 部署，确保网站能访问，再解决 Git 推送问题。

## 快速解决步骤

1. **立即访问**：https://vercel.com/dashboard
2. **点击** `app-stockapril` 项目
3. **点击** "Redeploy" 按钮
4. **等待** 2-3 分钟
5. **访问**：https://app-stockapril.vercel.app/stock/002416

完成！✅
