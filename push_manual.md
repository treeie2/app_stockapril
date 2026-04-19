# 手动推送指南

由于网络连接问题，请手动执行以下步骤推送更新：

## 步骤

1. **打开终端**，切换到 agent_store 目录：
   ```powershell
   cd e:/github/agent_store
   ```

2. **确认数据已同步**：
   ```powershell
   git status
   ```
   应该能看到 `data/master/stocks_master.json` 有修改

3. **添加并提交**：
   ```powershell
   git add -A
   git commit -m "添加嘉元科技等9只股票数据，更新铜箔和算力板块"
   ```

4. **推送到 GitHub**：
   ```powershell
   git push github HEAD:main -f
   ```

5. **等待 Vercel 部署**：
   - 访问 https://vercel.com/dashboard
   - 查看部署状态

## 本次更新内容

### 新增/更新股票（9只）

**铜箔板块（5只）：**
- 德福科技(301511) - 目标市值400亿
- 诺德股份(600110) - 目标市值300亿
- 铜冠铜箔(301217) - 目标市值450亿+
- 中一科技(301150) - 目标市值200亿
- 海亮股份(002203) - 目标市值450亿

**算力/NCP渠道（4只）：**
- 伟测科技(688372) - 算力芯片测试
- 利通电子(603629) - 目标市值380亿
- 盈峰环境(000967) - 目标市值500亿
- 行云科技(300467) - 目标市值272亿

### 数据库统计
- 总股票数：3155只
- 最后更新：$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
