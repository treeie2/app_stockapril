# stocks_master.json 使用说明

**文件位置**: `data/stocks/stocks_master.json`
**版本**: v2.3 | **数据量**: 3313 只 A 股 | **更新日期**: 2026-06-04

---

## 1. 整体结构

```json
{
  "version": "2.3",
  "updated_at": "2026-06-04",
  "stocks": {
    "002962": { /* 个股对象 */ },
    "002436": { /* 个股对象 */ },
    // ... 共 3313 只股票，以 6 位股票代码为 key
  }
}
```

顶级字段：
| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | string | 数据格式版本 |
| `updated_at` | string | 整体数据最后更新日期 |
| `stocks` | object | 股票字典，key=6位代码，value=个股对象 |

---

## 2. 个股对象（两层结构）

### 第一层：股票基本信息

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `name` | string | 股票名称 | `"兴森科技"` |
| `code` | string | 6位股票代码 | `"002436"` |
| `board` | string | 上市板块 | `"SH"` 或 `"SZ"` |
| `industry` | string | 行业分类 | `"电子 - 半导体 - 集成电路"` |
| `concepts` | string[] | 概念标签 | `["交换芯片","国产芯片"]` |
| `products` | string[] | 产品列表 | `["交换芯片"]` |
| `core_business` | string[] | 核心业务描述 | `["交换芯片研发与销售"]` |
| `industry_position` | string[] | 行业地位 | `["国产交换芯片龙头"]` |
| `chain` | string[] | 产业链位置 | `["中游 - 芯片设计"]` |
| `partners` | string[] | 合作伙伴/客户 | `["阿里巴巴","字节跳动"]` |
| `mention_count` | number | 被研究文章引用次数 | `2` |
| `last_updated` | string | 该股数据最后更新日期 | `"2026-06-05"` |

### 第二层：文章详情（articles 数组）

```json
"articles": [
  {
    "title": "文章标题",
    "date": "2026-04-21",
    "source": "https://mp.weixin.qq.com/s/xxx",
    "accidents": [
      "事件/催化: Q3业绩下滑",
      "里程碑事件: 新业务进入验证阶段"
    ],
    "insights": [
      "核心投资逻辑: 传统业务承压，新业务带来弹性",
      "产业趋势判断"
    ],
    "key_metrics": [
      "财务指标: 2025Q3营收9.40亿元",
      "关键运营数据"
    ],
    "target_valuation": [
      "目标价/估值: 机构看到XX元"
    ]
  }
]
```

文章字段说明：
| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 文章标题 |
| `date` | string | 文章发布日期 |
| `source` | string | 原文链接（微信文章 URL） |
| `accidents` | string[] | 事件催化/时间节点（发生了什么） |
| `insights` | string[] | 核心投资逻辑/产业判断（为什么重要） |
| `key_metrics` | string[] | 关键财务/运营数据（量化证据） |
| `target_valuation` | string[] | 目标估值/市场预期（价值锚点） |

---

## 3. 快速使用示例

### JavaScript/TypeScript

```javascript
// 获取所有股票列表
const stocks = Object.entries(data.stocks).map(([code, info]) => ({
  code,
  name: info.name,
  board: info.board,
  industry: info.industry,
}));

// 查找某只股票
const stock = data.stocks["002436"];
console.log(`${stock.name} - ${stock.industry}`);

// 获取有研究文章的股票
const researched = Object.values(data.stocks)
  .filter(s => s.articles?.length > 0);

// 获取最近更新的股票（按日期排序）
const recent = Object.values(data.stocks)
  .filter(s => s.last_updated)
  .sort((a, b) => b.last_updated.localeCompare(a.last_updated));
```

### Python

```python
import json

with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取所有股票
for code, stock in data['stocks'].items():
    print(f"{code} {stock['name']} - {stock.get('industry', 'N/A')}")

# 获取某只股票的研究文章
stock = data['stocks']['002436']
for article in stock.get('articles', []):
    print(f"- {article['title']} ({article['date']})")
    print(f"  核心逻辑: {article['insights']}")
```

---

## 4. 数据覆盖统计

| 指标 | 数值 |
|------|------|
| 总股票数 | 3,313 只 |
| 有研究文章 | ~560 只（持续增加） |
| 有行业分类 | ~3,300 只 |
| 有概念标签 | ~2,800 只 |
| 有核心业务描述 | ~500 只 |
| 所有股票均有 name/code/board |

---

## 5. 常见问题

**Q: 如何判断股票是否有研究文章？**
`stock.articles?.length > 0`

**Q: 如何按行业筛选？**
匹配 `industry` 字段，格式为 `"大类 - 中类 - 小类"`，如 `"电子 - 半导体 - 集成电路"`

**Q: `mention_count` 的含义？**
该股票被不同研究文章引用的总次数，>0 表示有相关研究覆盖

**Q: `last_updated` 为空表示什么？**
该股票暂无研究文章覆盖，仅有基础信息（名称、代码、板块）

**Q: 数据更新频率？**
每天不定时更新，通过公众号文章 + 深度研报自动处理入库