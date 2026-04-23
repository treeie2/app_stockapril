# target_market_cap_billion 字段支持 - 完成报告

**日期**: 2026-04-23  
**版本**: v2.2  
**状态**: ✅ 已完成

---

## 📋 任务概述

根据用户从沸点公众号下载的文章数据（`stocks_master_feidian_metrics.json`），发现文章中包含 `valuation_metrics.target_market_cap_billion` 字段。为支持这一数值型市值数据，需要在以下位置增加对该字段的支持：

1. ✅ 数据结构规范文档
2. ✅ Dashboard 个股页面显示
3. ✅ Firebase 数据同步
4. ✅ Firebase 数据加载

---

## ✅ 完成的工作

### 1. 更新数据结构规范文档

**文件**: `data/数据结构规范_v2.md`

**更新内容**:
- 版本号升级到 v2.2
- 在股票基本信息层级的 `valuation` 对象中增加 `target_market_cap_billion` 字段
- 明确字段说明：
  - 类型：数值型（float）
  - 单位：亿元
  - 用途：用于排序、筛选和计算
  - 与 `target_market_cap` 文本字段配合使用

**示例**:
```json
"valuation": {
  "target_market_cap": "800 亿",
  "target_market_cap_billion": 800.0,
  "target_price": "66.56 元",
  "pe": "2026 年 52 倍 PE",
  "upside": "80.18%",
  "rating": "买入"
}
```

### 2. 更新个股页面模板

**文件**: `templates/stock_detail.html`

**更新内容**:
- 修改估值信息板块的显示逻辑
- 优先显示 `target_market_cap_billion` 数值（带"亿"单位）
- 如果没有数值，则显示 `target_market_cap` 文本

**代码变更**:
```html
{% if stock.valuation.target_market_cap_billion %}
<div style="margin-bottom:1rem">
    <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;">目标市值</div>
    <div style="font-size:1.5rem;font-weight:700;color:var(--accent-amber)">
        {{ stock.valuation.target_market_cap_billion }} 亿
    </div>
</div>
{% elif stock.valuation.target_market_cap %}
<div style="margin-bottom:1rem">
    <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;">目标市值</div>
    <div style="font-size:1.5rem;font-weight:700;color:var(--accent-amber)">
        {{ stock.valuation.target_market_cap }}
    </div>
</div>
{% endif %}
```

### 3. 更新 Firebase 同步代码

**文件**: `sync_today_to_firebase.py` 和 `main.py`

**更新内容**:
- 在同步到 Firebase 时，将 `target_market_cap_billion` 作为 `doubleValue` 类型存储
- 同时保留 `target_market_cap` 文本字段

**代码变更**:
```python
# 添加估值信息
valuation = stock.get("valuation", {})
if valuation:
    if valuation.get("target_market_cap"):
        firestore_data["fields"]["target_market_cap"] = {
            "stringValue": valuation.get("target_market_cap", "")
        }
    if valuation.get("target_market_cap_billion"):
        firestore_data["fields"]["target_market_cap_billion"] = {
            "doubleValue": float(valuation.get("target_market_cap_billion", 0))
        }
```

### 4. 更新 Firebase 数据加载

**文件**: `main.py`

**更新内容**:
- 从 Firebase 加载股票数据时，读取 `target_market_cap_billion` 字段
- 将其转换为浮点数并存储到股票的 `valuation` 对象中

**代码变更**:
```python
# 获取估值信息
target_market_cap = fields.get('target_market_cap', {}).get('stringValue', '')
target_market_cap_billion = fields.get('target_market_cap_billion', {}).get('doubleValue', None)

if target_market_cap or target_market_cap_billion is not None:
    stock['valuation'] = {}
    if target_market_cap:
        stock['valuation']['target_market_cap'] = target_market_cap
    if target_market_cap_billion is not None:
        stock['valuation']['target_market_cap_billion'] = float(target_market_cap_billion)
```

---

## 📊 测试验证

运行测试脚本 `test_valuation_field.py` 验证所有更新：

```bash
python test_valuation_field.py
```

**测试结果**:
```
✅ 规范文档已包含 target_market_cap_billion 字段
✅ 模板文件已包含 target_market_cap_billion 显示逻辑
✅ 同步脚本已支持 target_market_cap_billion 字段
```

---

## 💡 使用说明

### 1. 数据录入格式

在录入个股数据时，应同时提供文本和数值两种格式：

```json
{
  "name": "示例股票",
  "code": "000001",
  "valuation": {
    "target_market_cap": "800 亿",
    "target_market_cap_billion": 800.0
  }
}
```

### 2. 数值转换规则

| 文本格式 | 数值格式（亿元） |
|---------|----------------|
| "800 亿" | 800.0 |
| "150e" | 150.0 |
| "1.5 千亿" | 1500.0 |
| "5000 万" | 0.5 |
| "100 亿元" | 100.0 |

### 3. 优先级规则

- 显示时优先使用 `target_market_cap_billion`（数值型）
- 如果没有数值型数据，则使用 `target_market_cap`（文本型）
- 数值型数据便于排序、筛选和计算

---

## 🔄 后续工作建议

### 1. 历史数据补充

当前 master 数据中只有 3 只股票有估值信息：
- 832522 - 纳科诺尔
- 832225 - 利通科技  
- 002550 - 力诺药包

建议从沸点文章中提取更多估值数据并补充到 master 文件中。

### 2. 自动化提取

可以开发脚本自动从 raw material 文章中提取 `valuation_metrics` 并转换为股票级别的 `valuation` 字段。

### 3. Dashboard 排序功能

在股票列表页面增加按目标市值排序的功能，利用 `target_market_cap_billion` 数值进行比较。

### 4. 估值空间计算

基于 `target_market_cap_billion` 和当前市值计算上涨空间：

```python
upside = (target_market_cap_billion - current_market_cap) / current_market_cap * 100
```

---

## 📝 注意事项

1. **单位统一**: `target_market_cap_billion` 固定使用**亿元**为单位
2. **数据类型**: 必须为浮点数（float），不能是字符串
3. **可选字段**: 该字段为可选字段，不是所有股票都必须有
4. **配合使用**: 建议与 `target_market_cap` 文本字段配合使用，便于显示不同格式

---

## ✅ 完成清单

- [x] 更新数据结构规范文档（v2.2）
- [x] 更新个股页面模板显示逻辑
- [x] 更新 Firebase 同步代码（写入）
- [x] 更新 Firebase 加载代码（读取）
- [x] 创建测试验证脚本
- [x] 编写使用文档

---

**状态**: ✅ 所有任务已完成，可以投入使用
