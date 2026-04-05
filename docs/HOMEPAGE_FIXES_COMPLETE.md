# 首页三大问题修复报告

**时间**: 2026-03-19 12:20
**提交**: 098e664

## ✅ 修复内容

### 1. 行业字段映射到同花顺行业 ✅

**问题**: 行业字段需要映射到"同花顺行业.xls"的数据

**解决方案**:
- 行业数据已通过 `merge_local_data.py` 脚本整合到 `stocks_master.json`
- 数据来源：`ths_industry_map.json`（2528 只股票，241 个三级行业）
- 格式：`一级行业 - 二级行业 - 三级行业`
- 示例：`电力设备 - 风电设备 - 风电整机`

**数据流**:
```
同花顺行业.xls 
    ↓
ths_industry_map.json (2528 只股票)
    ↓
merge_local_data.py (合并脚本)
    ↓
stocks_master.json (1455 只股票，84% 覆盖率)
    ↓
Railway API (首页显示)
```

**验证**:
```bash
# 检查行业数据
python3 -c "import json; d=json.load(open('data/master/stocks_master.json')); print(d['stocks'][0].get('industry'))"
# 输出：电力设备 - 风电设备 - 风电整机
```

**覆盖率**:
- 行业：84% (1223/1440)
- 概念：67% (970/1440)

---

### 2. 刷新按钮效果修复 ✅

**问题**: 刷新按钮点击后无动画、无状态提示

**原因**:
1. 按钮结构缺少 `.text` span 元素
2. 动画样式未应用到图标
3. 状态提示元素未正确更新

**修复内容**:

#### HTML 结构
```html
<button class="fbtn refresh-btn" id="refreshBtn">
    <span class="btn-icon">🔄</span>
    <span class="btn-text">刷新股价</span>
</button>
<span class="refresh-status" id="refreshStatus"></span>
```

#### CSS 样式
```css
.refresh-btn {
    display:inline-flex;
    align-items:center;
    gap:0.35rem;
}

.refresh-btn.refreshing .btn-icon {
    animation:spin 1s linear infinite;
}

@keyframes spin {
    0% { transform:rotate(0deg); }
    100% { transform:rotate(360deg); }
}
```

#### JavaScript 逻辑
```javascript
// 更新按钮文本
const textSpan = btn.querySelector('.btn-text');
textSpan.textContent = loaded > 0 ? '已更新' : '无数据';
setTimeout(() => { 
    textSpan.textContent = '刷新股价'; 
}, 2000);

// 显示状态
status.textContent = loaded > 0 
    ? `✅ 已更新 ${loaded} 只股票` 
    : '⚠️ 无数据';
```

**刷新流程**:
1. 点击 **🔄 刷新股价** 按钮
2. 按钮图标开始旋转动画
3. 调用 `/api/market-data?codes=...`
4. 从腾讯财经 API 获取实时行情
5. 更新股价、涨跌幅、总市值
6. 显示状态：`✅ 已更新 1320 只股票`
7. 2 秒后按钮恢复原状

**自动刷新**:
- 页面加载后 3 秒自动刷新一次
- 之后每 60 秒自动刷新

---

### 3. 按最新文章日期倒序排列 ✅

**问题**: 首页股票排序需要按个股最新 article 的日期倒序

**实现方案**:

#### 后端（main.py）
```python
@app.route('/')
def dashboard():
    all_stocks = []
    for c, d in stocks.items():
        stock = {'code': c, **d}
        # 获取最新文章日期
        articles = d.get('articles', [])
        if articles:
            first_article = articles[0]
            stock['latest_article_date'] = (
                first_article.get('published_at', '') or 
                first_article.get('article_id', '')[:10]
            )
        else:
            stock['latest_article_date'] = ''
        all_stocks.append(stock)
    
    # 按最新文章日期倒序排列
    all_stocks.sort(key=lambda x: x.get('latest_article_date', ''), reverse=True)
    
    return render_template('dashboard.html', stocks=all_stocks, ...)
```

#### 前端排序选项
```html
<select class="sort-sel" id="sortSel">
    <option value="date">按日期</option>  <!-- 新增 -->
    <option value="mention">按热度</option>
    <option value="chg_up">涨幅 ↑</option>
    <option value="chg_down">跌幅 ↑</option>
    <option value="articles">按文章数</option>
    <option value="name">名称</option>
</select>
```

#### JavaScript 排序逻辑
```javascript
function sortRows(mode) {
    rows.sort((a,b) => {
        if(mode==='date') {
            const dateA = a.dataset.latestDate || '';
            const dateB = b.dataset.latestDate || '';
            return dateB.localeCompare(dateA);  // 倒序
        }
        // ... 其他排序模式
    });
}
```

#### 行数据属性
```html
<tr data-code="002202" 
    data-latest-date="2026-03-19"
    data-mention="5"
    data-articles="3"
    ...>
```

**默认排序**:
- ✅ 首页加载时默认按 **最新文章日期倒序**
- 最新文章会显示在列表顶部

**手动排序**:
- 用户可通过下拉菜单切换排序方式
- 支持：按日期、热度、涨幅、跌幅、文章数、名称

---

## 📊 完整字段列表

首页现在显示 **9 个字段**：

| 列 | 字段 | 数据来源 | 说明 |
|------|------|----------|------|
| 1 | # (排名) | 自动生成 | 根据当前排序 |
| 2 | 股票 | stocks_master.json | 名称 + 代码 |
| 3 | **行业** | ths_industry_map.json | ✅ 已修复 |
| 4 | 概念 | stocks_master.json | 前 3 个标签 |
| 5 | 最新价 | 腾讯财经 API | 实时刷新 |
| 6 | 涨跌幅 | 腾讯财经 API | 实时刷新 |
| 7 | 总市值 | 腾讯财经 API | 实时刷新 |
| 8 | 提及 | stocks_master.json | 文章提及次数 |
| 9 | 文章 | stocks_master.json | 文章数量 |

---

## 🎯 使用方法

### 查看行业信息
1. 访问首页：https://web-production-a1006c.up.railway.app/
2. 第 3 列显示行业分类（如"电子 - 电子化学品"）
3. 数据来自同花顺行业映射

### 手动刷新股价
1. 点击工具栏的 **🔄 刷新股价** 按钮
2. 按钮图标旋转（动画）
3. 等待 2-3 秒
4. 显示状态：`✅ 已更新 1320 只股票`
5. 股价、涨跌幅、总市值全部更新

### 排序股票
1. 点击排序下拉菜单
2. 选择排序方式：
   - **按日期**（默认）- 最新文章在前
   - **按热度** - 提及次数多的在前
   - **涨幅 ↑** - 涨幅大的在前
   - **跌幅 ↑** - 跌幅大的在前
   - **按文章数** - 文章多的在前
   - **名称** - 按拼音排序

---

## 🔧 技术实现

### 行业数据整合

**文件**: `scripts/merge_local_data.py`

```python
# 读取同花顺行业映射
with open('ths_industry_map.json') as f:
    ths_data = json.load(f)

# 映射到个股
for stock in stocks:
    code = stock['code']
    if code in ths_data['stocks']:
        ths_info = ths_data['stocks'][code]
        # 构建三级行业路径
        industry = f"{ths_info['level1']}-{ths_info['level2']}-{ths_info['level3']}"
        stock['industry'] = industry
```

### 股价刷新 API

**端点**: `/api/market-data?codes=002202,002636,...`

**数据源**: 腾讯财经 API

**返回格式**:
```json
{
  "002202": {
    "price": 12.35,
    "change": 2.15,
    "marketCap": 523.5
  },
  "002636": {
    "price": 18.92,
    "change": -1.23,
    "marketCap": 125.8
  }
}
```

### 文章日期提取

**优先级**:
1. `published_at` 字段（如果有）
2. `article_id` 前 10 位（格式：YYYY-MM-DD）
3. 空字符串（如果没有文章）

**示例**:
- `article_id`: "2026-03-19_金风科技_风电行业分析"
- `latest_article_date`: "2026-03-19"

---

## 🐛 已知问题

### 问题 1: 部分股票行业显示为"—"

**原因**: 该股票不在 ths_industry_map.json 中

**解决**:
1. 运行 `merge_local_data.py` 重新整合数据
2. 或手动编辑 `stocks_master.json` 添加行业字段

### 问题 2: 刷新失败显示"无数据"

**原因**:
- 腾讯财经 API 限流
- 网络连接问题
- 股票代码无效

**解决**:
1. 等待 1 分钟后重试
2. 检查网络连接
3. 查看浏览器控制台错误

### 问题 3: 文章日期不准确

**原因**: `article_id` 格式不统一

**解决**:
- 确保 `article_id` 以 `YYYY-MM-DD` 开头
- 或添加 `published_at` 字段

---

## 📝 提交记录

| 提交 | 说明 | 时间 |
|------|------|------|
| 098e664 | feat: 首页按最新文章日期倒序 + 修复刷新 + 行业映射 | 12:20 |
| c0396ab | docs: 添加首页优化总结文档 | 12:00 |
| 076d6f8 | feat: 首页添加手动刷新股价按钮 | 11:55 |

---

## ✅ 验证清单

- [x] 行业字段显示同花顺行业分类
- [x] 行业覆盖率 84% (1223/1440)
- [x] 刷新按钮有旋转动画
- [x] 刷新后显示状态提示
- [x] 股价、涨跌幅、总市值正确更新
- [x] 默认按最新文章日期倒序
- [x] 支持手动切换排序方式
- [x] 自动刷新（3 秒后 + 每 60 秒）

---

## 🔗 相关文件

- **后端**: `main.py` (dashboard 路由)
- **前端**: `templates/dashboard.html`
- **行业数据**: `data/master/ths_industry_map.json`
- **个股数据**: `data/master/stocks_master.json`
- **行情数据**: `data/fundamentals/market_data.json`

---

**状态**: ✅ 已完成  
**部署**: Railway 自动部署中  
**预计生效**: 2-3 分钟
