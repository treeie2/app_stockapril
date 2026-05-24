---
name: "tdx_mark"
description: "Generates Tongdaxin mark.dat files from stocks_master.json research data. Invoke when user asks to generate mark.dat, update TDX labels, or at 7:00 AM daily scheduled task."
---

# tdx_mark — 通达信 mark.dat 自动生成器

## 功能

从 `data/stocks/stocks_master.json` 读取最新的个股研究数据，生成通达信格式的 `mark.dat` 标记文件。

### 核心逻辑

- **有研究数据的股票**（含 `articles` 或 `last_updated`）：替换为投研分析内容（行业地位、核心业务、产业链、合作伙伴、目标估值）
- **没有研究数据的股票**：保留原始通达信概念标签
- **新增股票**：自动追加标记

## 运行方式

### 方式一：自动定时（推荐）

每天早晨 **7:00** 自动运行，生成最新标记文件。

### 方式二：手动触发

在龙虾上输入指令：
```
+tdx_mark
```

## 输入

- 无需额外输入，自动读取 `data/stocks/stocks_master.json`
- 自动参考 `data/stocks/mark.dat` 作为原始标签基础

## 输出

生成到 `.trae/skills/tdx_mark/` 目录：

| 文件 | 说明 |
|------|------|
| `mark_YYYY-MM-DD.dat` | 当前日期的标记文件（GBK编码） |
| `mark_latest.dat` | 最新版本（快捷引用） |

## 文件结构

```
.trae/skills/tdx_mark/
├── SKILL.md                    # 技能定义
├── generate_tdx_mark.py        # 生成脚本
├── mark_2026-05-20.dat         # 每日生成
├── mark_2026-05-21.dat
└── mark_latest.dat             # 最新版本链接
```

## 使用步骤

1. 运行 skill 后，在 `.trae/skills/tdx_mark/` 目录下找到最新生成的 `mark_YYYY-MM-DD.dat`
2. 关闭通达信
3. 将 `mark_YYYY-MM-DD.dat` 复制到通达信 `T0002\mark.dat`
4. 重启通达信即可生效

## 数据字段说明

| 字段 | 显示位置 | 说明 |
|------|---------|------|
| 【行业地位】 | 鼠标悬停 | 个股行业地位与竞争优势 |
| 【核心业务】 | 鼠标悬停 | 主要产品与业务（最多4项） |
| 【产业链】 | 鼠标悬停 | 产业链位置（上/中/下游） |
| 【合作伙伴】 | 鼠标悬停 | 供应链合作伙伴 |
| 【目标估值】 | 鼠标悬停+简标 | 目标市值/空间 |
| 【更新】 | 鼠标悬停 | 数据最后更新日期 |