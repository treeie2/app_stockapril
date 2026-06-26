# Industry Knowledge Skill

从微信文章链接提取行业知识，保存为 Markdown 并上传到 GitHub。

## 触发条件

用户发送微信文章链接（mp.weixin.qq.com/s/...）并要求导入行业知识时触发。

## 完整工作流程

### Step 1: 获取文章内容
使用 `web_fetch` 工具获取文章 URL 的全文内容。

### Step 2: 提取行业分类和知识
AI 从文章中识别并提取每个行业分类的完整内容：

- 行业分类名称（如"光刻胶"、"电子特气"、"CMP抛光材料"）
- 通俗比喻（如"显影液"、"洗涤灵"、"磨刀石"）
- 知识描述（技术原理、趋势、壁垒）
- 主要产品类型和规格参数
- 核心技术和工艺要点
- 相关个股（如有，含代码）

### Step 3: 生成 Markdown 文件

```markdown
# 分类名——芯片的"比喻"

知识描述，包含技术原理和趋势。

## 主要产品类型
| 产品名称 | 规格 | 用途 |
|---------|------|------|
| XXX     | XXX  | XXX  |

## 核心技术
**技术名**: 技术描述

## 相关个股
股票名(股票代码)、股票名(股票代码)
```

### Step 4: 保存到本地
通过脚本保存到 `raw_material/industry/` 目录：

```bash
python .trae/skills/industry-knowledge/scripts/save_knowledge.py "光刻胶" "文件内容..." --push
```

- 不带 `--push`：仅保存到本地
- 带 `--push`：保存后自动执行 git add → commit → push

### Step 5: 推送到 GitHub（可选）
加上 `--push` 参数后，脚本会自动：
```bash
git add raw_material/industry/xxx.md
git commit -m "chore: update industry knowledge"
git push origin main
```

如果 GitHub 推送失败（网络/认证问题），文件仍然已在本地保存，可稍后手动推送。

## 在龙虾（另一台设备）上使用

如果你在另一台设备上使用 CodeBuddy 触发了本 skill：

1. AI 提取知识内容
2. 运行 `python save_knowledge.py "分类" "内容" --push`
3. 文件保存到那台设备的本地仓库
4. 推送到 GitHub（如果那台设备有推送权限）
5. 其他设备 `git pull` 即可同步

## 在 Vercel 上显示

知识文件通过 API 自动显示在：
- 首页 Dashboard → 📚 行业知识库
- `/import` 页面 → 完整知识库管理

Vercel 部署后会自动包含这些文件。
