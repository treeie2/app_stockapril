# 🎨 个股研究卡片 UI 2.0 - 完整设计文档

**更新时间**: 2026-03-18  
**版本**: 2.0  
**设计风格**: 赛博朋克科技风 + Tailwind CSS 实用类

---

## 📋 目录

1. [组件概览](#组件概览)
2. [文件结构](#文件结构)
3. [基础卡片 (Base Card)](#基础卡片)
4. [详细卡片 (Detail Card)](#详细卡片)
5. [紧凑卡片 (Compact Card)](#紧凑卡片)
6. [时间轴组件 (Timeline)](#时间轴组件)
7. [使用示例](#使用示例)
8. [配色方案](#配色方案)
9. [动画效果](#动画效果)
10. [响应式适配](#响应式适配)

---

## 📦 组件概览

| 组件类型 | 用途 | 文件 |
|---------|------|------|
| **基础卡片** | 仪表盘、股票列表页 | `stock-card` CSS 类 |
| **详细卡片** | 个股详情页侧边栏 | `stock-detail-card` CSS 类 |
| **紧凑卡片** | 相似度推荐、快速浏览 | `stock-card-compact` CSS 类 |
| **时间轴** | 主题时间轴联动 | `timeline` CSS 类 |

---

## 📁 文件结构

```
railway-deploy/
├── static/
│   └── css/
│       ├── cyber-theme.css      # 原有主题 (保留)
│       └── stock-card.css       # 新增：卡片组件样式
├── templates/
│   ├── components/
│   │   └── stock_card.html      # 新增：卡片模板组件
│   ├── dashboard.html           # 仪表盘 (待更新)
│   ├── stocks.html              # 股票列表 (待更新)
│   ├── stock_detail.html        # 个股详情 (待更新)
│   └── concept_detail.html      # 概念详情 (待更新)
└── STOCK_CARD_UI_2.0.md         # 本文档
```

---

## 🎴 基础卡片 (Base Card)

### 视觉效果
- 渐变顶部光条 (青色 → 紫色 → 青色)
- 悬停时发光 + 上移 4px
- 玻璃态背景 + 网格背景透视
- 圆角 20px

### 结构组成
```
┌─────────────────────────────────┐
│ [代码徽章]          [热度徽章]   │
│ [股票名称]                      │
├─────────────────────────────────┤
│ [核心业务摘要 (可选)]            │
├─────────────────────────────────┤
│ [指标网格]                      │
│ 概念数 | 文章数                 │
│ 市值   | 市盈率 (可选)          │
├─────────────────────────────────┤
│ [概念标签云] (最多 8 个 + 更多)   │
└─────────────────────────────────┘
```

### 热度徽章等级
| 提及次数 | 徽章类型 | 颜色 | 图标 |
|---------|---------|------|------|
| ≥100 | `heat-badge-high` | 粉色渐变 | 🔥 |
| 30-99 | `heat-badge-medium` | 紫色渐变 | ⚡ |
| <30 | `heat-badge-low` | 青色 | 📊 |

### 使用示例 (Jinja2)
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for stock in stocks %}
        {% set card_type = 'base' %}
        {% set stock_data = stock %}
        <div style="--card-index: {{ loop.index0 }}">
            {% include 'components/stock_card.html' %}
        </div>
    {% endfor %}
</div>
```

---

## 📊 详细卡片 (Detail Card)

### 视觉效果
- 顶部 3px 渐变光条 (青 → 紫 → 粉)
- 更深的背景色 (详情页专用)
- 无悬停效果 (静态展示)

### 结构组成
```
┌─────────────────────────────────┐
│ 📊 核心数据                     │
│ [股票名称]                      │
│ [代码徽章]                      │
├─────────────────────────────────┤
│ 当前价格        [实时加载]       │
│ 涨跌幅          [实时加载]       │
│ 总市值          [实时加载]       │
│ 市盈率 (TTM)    [实时加载]       │
├─────────────────────────────────┤
│ [统计信息网格]                  │
│ 提及次数 | 概念数量             │
│ 相关文章 | 板块                 │
├─────────────────────────────────┤
│ 🏷️ 核心概念                     │
│ [标签云 - 最多 12 个]            │
└─────────────────────────────────┘
```

### 使用示例
```html
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- 主内容区 -->
    <div class="lg:col-span-2">
        <!-- 催化剂、洞察等内容 -->
    </div>
    
    <!-- 侧边栏 -->
    <div>
        {% set card_type = 'detail' %}
        {% set stock_data = current_stock %}
        {% include 'components/stock_card.html' %}
        
        <!-- 相似度推荐卡片 -->
        <div style="margin-top: 24px;">
            <div class="detail-card-title">🔗 高度相关标的</div>
            {% for similar in similar_stocks %}
                {% set card_type = 'compact' %}
                {% set stock_data = similar %}
                {% set show_similarity = true %}
                {% include 'components/stock_card.html' %}
            {% endfor %}
        </div>
    </div>
</div>
```

---

## 🔍 紧凑卡片 (Compact Card)

### 视觉效果
- 半透明背景
- 悬停时右移 4px + 高亮边框
- 水平布局 (代码 + 信息 + 相似度)

### 结构组成
```
┌───────────────────────────────────────────────┐
│ [代码] [股票名称]           [相似度%]         │
│        [行业 · 共同概念]                      │
└───────────────────────────────────────────────┘
```

### 使用场景
1. **相似度推荐** - 显示 Jaccard 相似度百分比
2. **快速浏览列表** - 不显示相似度
3. **相关文章提及** - 显示其他股票

### 使用示例
```html
<!-- 相似度推荐 -->
<div class="space-y-3">
    {% for similar in similar_stocks %}
        {% set card_type = 'compact' %}
        {% set stock_data = similar %}
        {% set show_similarity = true %}
        {% include 'components/stock_card.html' %}
    {% endfor %}
</div>
```

---

## 📅 时间轴组件 (Timeline)

### 视觉效果
- 左侧垂直渐变线 (青 → 紫 → 透明)
- 每个节点带发光圆点
- 悬停时右移 4px

### 结构组成
```
│ (圆点) ┌─────────────────────────┐
│        │ 📅 2026-03-15           │
│        │ [标题/内容]             │
│        │ [标签 1] [标签 2]       │
│        └─────────────────────────┘
│
│ (圆点) ┌─────────────────────────┐
│        │ 📅 2026-03-14           │
│        │ [标题/内容]             │
│        └─────────────────────────┘
```

### 使用示例
```html
<div class="card">
    <div class="section-title">📰 主题时间轴</div>
    {% set card_type = 'timeline' %}
    {% set stock_data = current_stock %}
    {% include 'components/stock_card.html' %}
</div>
```

---

## 🎨 配色方案

### 核心变量
```css
:root {
    --primary: #00f0ff;      /* 青色 - 主色调 */
    --secondary: #7b2fff;    /* 紫色 - 次级色 */
    --accent: #ff00ff;       /* 粉色 - 强调色 */
    --bg-dark: #0a0a0f;      /* 深黑 - 页面背景 */
    --bg-card: #12121a;      /* 深灰 - 卡片背景 */
    --bg-glass: rgba(18, 18, 26, 0.8); /* 玻璃态 */
    --border: rgba(0, 240, 255, 0.2);  /* 边框 */
    --text: #e0e0e0;         /* 浅灰 - 主文字 */
    --text-dim: #8888aa;     /* 灰紫 - 次要文字 */
}
```

### 涨跌颜色
```css
.price-up { color: #ff4444; }    /* 上涨 - 红色 */
.price-down { color: #00ff88; }  /* 下跌 - 绿色 */
```

---

## ✨ 动画效果

### 1. 淡入动画 (slideIn)
```css
@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stock-card-animate {
    animation: slideIn 0.5s ease-out;
}
```

### 2. 发光动画 (glow)
```css
@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 240, 255, 0.1); }
    50% { box-shadow: 0 0 30px rgba(0, 240, 255, 0.2); }
}
```

### 3. 交错延迟
```css
.stock-card-stagger-1 { animation-delay: 0.05s; }
.stock-card-stagger-2 { animation-delay: 0.1s; }
.stock-card-stagger-3 { animation-delay: 0.15s; }
/* ... */
```

### 使用方式
```html
{% for stock in stocks %}
    <div class="stock-card stock-card-animate" 
         style="--card-index: {{ loop.index0 }}">
        <!-- 卡片内容 -->
    </div>
{% endfor %}
```

---

## 📱 响应式适配

### 断点
| 断点 | 宽度 | 卡片列数 |
|------|------|---------|
| Mobile | <768px | 1 列 |
| Tablet | 768px-1024px | 2 列 |
| Desktop | >1024px | 3 列 |

### 移动端优化
- 卡片内边距减小 (20px → 16px)
- 股票名称字号减小 (20px → 18px)
- 指标网格保持 2 列
- 概念标签自动换行

### 使用示例
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- 卡片自动响应式布局 -->
</div>
```

---

## 🔧 集成步骤

### 第 1 步：引入 CSS
在模板 `<head>` 中添加：
```html
<link rel="stylesheet" href="/static/css/stock-card.css">
```

### 第 2 步：更新现有模板
**dashboard.html**:
```html
{# 替换原有的统计卡片区域 #}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for stock in top_20 %}
        {% set card_type = 'base' %}
        {% set stock_data = stock %}
        <div style="--card-index: {{ loop.index0 }}">
            {% include 'components/stock_card.html' %}
        </div>
    {% endfor %}
</div>
```

**stock_detail.html**:
```html
{# 在侧边栏添加详细卡片 #}
<div class="lg:col-span-1">
    {% set card_type = 'detail' %}
    {% set stock_data = current_stock %}
    {% include 'components/stock_card.html' %}
</div>
```

### 第 3 步：添加实时行情 (可选)
```javascript
async function fetchMarketData() {
    const codes = document.querySelectorAll('.market-price, .market-change, .market-cap, .market-pe');
    // 调用 API 获取实时数据并更新
}

document.addEventListener('DOMContentLoaded', fetchMarketData);
```

---

## 🎯 后续优化方向

### Phase 1: 相似度推荐 (下一步)
- 在 `main.py` 添加 Jaccard 算法
- 在 `stock_detail` 路由返回相似股票
- 在详情页显示「高度相关标的」紧凑卡片

### Phase 2: 概念矩阵交叉
- 优化 `concept_detail` 路由
- 按行业分组展示股票
- 使用基础卡片展示分组结果

### Phase 3: 时间轴联动
- 优化数据结构 (确保 articles 有日期字段)
- 在详情页添加时间轴组件
- 按日期分组显示 insights

### Phase 4: 交互增强
- 添加搜索功能
- 添加筛选器 (行业/概念/热度)
- 添加深色/浅色模式切换

---

## 📝 注意事项

1. **CSS 加载顺序**: `stock-card.css` 必须在 `cyber-theme.css` 之后加载
2. **组件复用**: 所有卡片都通过 `stock_card.html` 组件渲染，避免重复代码
3. **性能优化**: 大量卡片时使用懒加载或分页
4. **可访问性**: 确保所有交互元素有适当的 ARIA 标签

---

## 🔗 相关文档

- [UI_UPGRADE.md](./UI_UPGRADE.md) - 赛博朋克主题设计
- [README.md](./README.md) - 部署指南
- [main.py](./main.py) - Flask 应用源码

---

**下一步**: 开始实现 **相似度推荐引擎** (Jaccard 算法)
