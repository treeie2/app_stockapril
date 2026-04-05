# 🎨 UI 升级 - 赛博朋克科技风

## 更新时间
2026-03-16 13:42

## 设计理念
- **赛博朋克美学**：深色背景 + 霓虹色点缀
- **科技感**：网格背景、光晕效果、玻璃态导航
- **数据可视化**：清晰的信息层级、模块化布局
- **交互反馈**：悬停效果、动画过渡

## 配色方案

| 角色 | 颜色 | 用途 |
|------|------|------|
| Primary | `#00f0ff` (青色) | 主色调、链接、高亮 |
| Secondary | `#7b2fff` (紫色) | 次级高亮、渐变 |
| Accent | `#ff00ff` (粉色) | 强调色、数据值 |
| Background | `#0a0a0f` (深黑) | 页面背景 |
| Card | `#12121a` (深灰) | 卡片背景 |
| Text | `#e0e0e0` (浅灰) | 主要文字 |
| Text Dim | `#8888aa` (灰紫) | 次要文字 |

## 核心组件

### 1. 动态背景
- **网格效果**：50px 间距的青色细线网格
- **光晕动画**：中心紫色光晕，8 秒脉冲动画

### 2. 玻璃态导航栏
- 毛玻璃效果（backdrop-filter: blur(20px)）
- 悬停下划线动画
- 粘性定位（sticky）

### 3. 科技卡片
- 顶部渐变光条
- 悬停发光效果
- 圆角 16px

### 4. 数据展示
- 等宽字体（JetBrains Mono）
- 渐变色数值
- 大写标签（uppercase）

### 5. 多来源内容块
- 左侧彩色边框
- 序号徽章（渐变背景）
- 悬停高亮效果
- 分隔线渐变

### 6. 概念标签
- 半透明背景
- 悬停发光 + 上移动画
- 主色/次级色两种样式

## 字体
- **标题/数据**：`JetBrains Mono`（等宽科技感）
- **正文**：`Noto Sans SC`（思源黑体）

## 动画效果
- **fade-in**：页面加载淡入
- **stagger-1~4**：交错延迟动画
- **pulse**：背景光晕脉冲
- **hover**：卡片/标签悬停效果

## 响应式
- 移动端适配（Tailwind CSS）
- 卡片网格自动换行
- 导航栏折叠（待实现）

## 文件结构
```
railway-deploy/
├── templates/
│   ├── stock_detail.html    # 股票详情页（已升级）
│   ├── dashboard.html       # 仪表盘（待升级）
│   ├── stocks.html          # 股票列表（待升级）
│   ├── concepts.html        # 概念列表（待升级）
│   ├── concept_detail.html  # 概念详情（待升级）
│   └── search.html          # 搜索页（待升级）
├── static/
│   └── css/
│       └── cyber-theme.css  # 共享主题样式
└── UI_UPGRADE.md            # 本文档
```

## 已完成
- [x] stock_detail.html 全面升级
- [x] 多来源内容格式化显示（催化剂、投资洞察）
- [x] 共享 CSS 主题文件
- [x] 动态背景效果
- [x] 玻璃态导航栏
- [x] 科技卡片组件
- [x] 数据展示组件
- [x] 概念标签样式
- [x] 文章列表样式

## 待完成
- [ ] dashboard.html 升级
- [ ] stocks.html 升级
- [ ] concepts.html 升级
- [ ] concept_detail.html 升级
- [ ] search.html 升级
- [ ] 移动端导航优化
- [ ] 加载动画
- [ ] 深色/浅色模式切换

## 访问
https://web-production-a1006c.up.railway.app

## 技术栈
- Tailwind CSS（实用类优先）
- 自定义 CSS（赛博朋克主题）
- Jinja2 模板（动态内容）
- 原生 JavaScript（最小依赖）
