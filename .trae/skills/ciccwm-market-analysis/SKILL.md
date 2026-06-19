---
name: ciccwm_market_analysis
description: 中金财富市场行情查询与分析，支持沪深A股、北交所、港股、美股的证券详情、资金流向、涨跌幅排行、多日历史行情、个股关联板块。Invoke when user asks for CICCWM/中金财富 stock details, market data, rankings, fund flow, related sectors/blocks, or recent historical market data.
---

# 中金财富市场行情分析

本 skill 通过 `scripts/market_query.py` 调用中金财富通达信行情接口，返回 JSON 行情数据。不要手写 HTTP 请求；优先使用脚本命令行或 Python 函数调用。

## 服务与凭证

- 服务地址: `https://skill.ciccwm.com`
- 业务命令: `SkillTdxQuotationQueryCommon`
- 凭证文件: `~/.config/ciccwm/config.json`
- 凭证字段: `CICCWM_API_KEY`

凭证文件格式:

```json
{
  "CICCWM_API_KEY": "your_api_key_here"
}
```

安全要求:
- 只从配置文件读取密钥，不要在代码、提示词、日志或输出中明文暴露密钥。
- 若缺少凭证，或接口返回 `ret = 5002`，提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills，不要编造密钥。
- 脚本当前会校验 `CICCWM_API_KEY` 是否存在；查询请求本身由脚本封装为 `cmdname/param/entry/tdx_param` 统一接口格式。

## 输入控制

用户请求必须包含明确查询对象或明确市场范围:

| 场景 | 必需信息 |
|------|----------|
| 证券详情 `info` | 证券代码、市场代码 |
| 资金流向 `fund` | 证券代码、市场代码；仅优先用于沪深市场 |
| 涨跌幅排行 `ranking` | 市场/板块代码，可指定返回条数和排序 |
| 历史行情 `history` | 证券代码、市场代码；可指定返回交易日数量 |
| 个股关联板块 `related` | 证券代码、市场代码 |

不要接受纯泛指对象，例如“某只股票”“热门股票”“一些板块”。若用户只给名称未给代码，可以先基于常识映射高置信代码；不确定时要求用户补充代码和市场。

单次调用限制:

| 查询类型 | 单次上限 | 说明 |
|----------|----------|------|
| `info` | 1 只证券 | 脚本只支持单代码 |
| `fund` | 1 只证券 | `--period` 参数存在，但脚本当前请求固定 `Onlytoday=1` |
| `ranking` | 80 条 | `--limit` 超过 80 时脚本会截断为 80；默认返回命名字段对象，`--raw` 返回原始结构 |
| `history` | 1 只证券 | 默认近5个交易日，可用 `--days` 指定数量；默认返回命名字段对象，`--raw` 返回原始结构 |
| `related` | 1 只证券 | 查询个股关联板块 |

## 代码声明

### 市场代码 `--market`

按 `scripts/market_query.py` 中 `SET_CODE_MAP` 使用:

| 市场 | 代码 | 适用 |
|------|------|------|
| 深圳 | `0` | 深市 A 股、深市 ETF 等 |
| 上海 | `1` | 沪市 A 股、沪市 ETF 等 |
| 北交所 | `2` | 北京证券交易所 |
| 港股 | `31` | 香港市场 |
| 美股指数 | `12` | 美股指数（道琼斯、纳斯达克等） |
| 美股 | `74` | 美股个股 |

常用规则:
- `60/68` 开头 A 股通常用上海 `1`。
- `00/30` 开头 A 股通常用深圳 `0`。
- 北交所通常用 `2`。
- 港股按脚本常量用 `31`。
- 美股个股用 `74`，美股指数用 `12`。

### 市场/板块排行代码 `ranking --market`

按 `scripts/market_query.py` 中 `SET_DOMAIN_MAP` 使用:

| 排行范围 | 代码 |
|----------|------|
| 上证A股 | `0` |
| 深证A股 | `2` |
| 北交所 | `12` |
| 沪深A股 | `6` |
| 创业板 | `14` |
| 沪深ETF基金 | `11005` |
| 港股通 | `12006` |

排序参数:
- `--sort_type 1`: 涨幅倒序，查询涨幅榜。
- `--sort_type 0`: 跌幅正序，查询跌幅榜。

### 个股关联板块入参 `related`

`related` 调用 `HQServ.PBXmlBlock`，脚本会按下面结构组装请求:

```json
{
  "Head": {
    "Target": 0
  },
  "Code": "市场代码",
  "Setcode": 证券代码,
  "Blockid": "Stock_GLHQ"
}
```

示例: `related --code 688318 --market 1` 会发送:

```json
{
  "Head": {
    "Target": 0
  },
  "Code": "1",
  "Setcode": 688318,
  "Blockid": "Stock_GLHQ"
}
```

## 调用方式

将 `{baseDir}` 替换为本 skill 目录，即 `ciccwm-market-analysis`。

### 命令行调用

```bash
# 证券详情
python3 {baseDir}/scripts/market_query.py info --code 600519 --market 1

# 今日资金流向
python3 {baseDir}/scripts/market_query.py fund --code 600519 --market 1

# 沪深A股涨幅前10
python3 {baseDir}/scripts/market_query.py ranking --market 6 --limit 10 --sort_type 1

# 沪深A股涨幅前10，返回接口原始 ListHead/ListItem 结构
python3 {baseDir}/scripts/market_query.py ranking --market 6 --limit 10 --sort_type 1 --raw

# 沪深A股跌幅前10
python3 {baseDir}/scripts/market_query.py ranking --market 6 --limit 10 --sort_type 0

# 近5日历史行情
python3 {baseDir}/scripts/market_query.py history --code 600519 --market 1

# 近20日历史行情
python3 {baseDir}/scripts/market_query.py history --code 600519 --market 1 --days 20

# 近5日历史行情，返回接口原始 ListHead/ListItem 结构
python3 {baseDir}/scripts/market_query.py history --code 600519 --market 1 --raw

# 个股关联板块
python3 {baseDir}/scripts/market_query.py related --code 600519 --market 1
```

### Python 函数调用

```python
import sys
sys.path.insert(0, "{baseDir}/scripts")

from market_query import (
    fetch_info,
    fetch_fund_flow,
    fetch_ranking,
    fetch_history,
    fetch_related_blocks,
)

detail = fetch_info("600519", market=1)
fund = fetch_fund_flow("600519", market=1)
ranking = fetch_ranking(market=6, limit=10, sort_type=1)
history = fetch_history("600519", market=1)
history_20d = fetch_history("600519", market=1, days=20)
related = fetch_related_blocks("600519", market=1)
```

## 输出控制

脚本输出为 UTF-8 JSON:

```bash
python3 {baseDir}/scripts/market_query.py info --code 600519 --market 1
```

处理输出时:
- 保留原始 JSON 中的关键字段，不要臆造缺失字段。
- `history` 和 `ranking` 默认已将接口的 `ListHead.ItemHead + ListItem[].Item` 位置数组转为 `items` 对象数组。
- 当需要排查原始接口字段或验证字段顺序时，对 `history` / `ranking` 使用 `--raw`。
- 面向用户回答时优先提取证券名称、代码、市场、价格、涨跌幅、成交额、成交量、时间、板块名称等可识别字段。
- 如果接口返回空数据、错误状态或字段含义不明确，明确说明“接口未返回可解析字段”，并附上关键原始字段摘要。
- 多只证券查询时逐只调用脚本，最终合并为表格；若某只失败，在结果中单独标注失败原因。
- 涉及实时行情时说明时效: 交易时段通常为最新行情，非交易时段可能为最近交易日或延迟数据。

`history` 默认输出示例:

```json
{
  "code": "300750",
  "market": 0,
  "days": 5,
  "period": 4,
  "items": [
    {
      "date": "20260513",
      "open": 431.01001,
      "high": 436.579987,
      "low": 427.079987,
      "close": 434.049988,
      "amount": 13668347904,
      "volume": 31685824
    }
  ]
}
```

`ranking` 默认输出示例:

```json
{
  "market": 6,
  "limit": 10,
  "sort_type": 1,
  "sort_name": "涨幅倒序",
  "total": 5208,
  "items": [
    {
      "code": "601138",
      "market": "1",
      "name": "工业富联",
      "previous_close": 64.4,
      "current_price": 70.84,
      "amount": 28051300352
    }
  ]
}
```

## 常见任务映射

| 用户意图 | 使用命令 |
|----------|----------|
| “查贵州茅台详情/基本信息/行情” | `info --code 600519 --market 1` |
| “查宁德时代资金流向” | `fund --code 300750 --market 0` |
| “今天沪深A股涨幅榜前20” | `ranking --market 6 --limit 20 --sort_type 1` |
| “创业板跌幅榜前10” | `ranking --market 14 --limit 10 --sort_type 0` |
| “查腾讯控股近5日走势” | `history --code 00700 --market -1` |
| “查宁德时代近20日历史行情” | `history --code 300750 --market 0 --days 20` |
| “查宁德时代关联板块/所属板块” | `related --code 300750 --market 0` |

## 失败处理

- `配置文件不存在`、`缺少 CICCWM_API_KEY` 或接口返回 `ret = 5002`: 提示用户前往 `https://web.ciccwm.com/zzt/app/skills-center/#/` 重新安装 skills。
- JSON 解析失败或网络失败: 简要说明接口调用失败，并保留脚本返回的错误信息。
- 用户要求超过脚本能力，例如“分时行情”或“批量行情”: 说明脚本当前不提供分时方法，且单次只支持单只证券；多只证券可逐只调用并合并结果。
