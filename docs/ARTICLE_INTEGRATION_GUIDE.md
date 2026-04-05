# 文章识别智能体集成方案

## 架构概览

```
┌─────────────────┐      HTTP API       ┌──────────────────┐
│   智能体Agent    │ ──────────────────> │  文章API服务      │
│  (独立运行)      │   POST /api/article │  (article_api_   │
│                 │      /receive       │   server.py:5001)│
└─────────────────┘                     └────────┬─────────┘
                                                  │
                                                  │ JSON文件
                                                  │ 存储
                                                  ▼
┌─────────────────┐      HTTP API       ┌──────────────────┐
│   主项目Web     │ <────────────────── │  数据同步API      │
│  (main.py:5000) │   GET /api/articles │  (article_importer│
│                 │      /pending       │   .py)           │
└─────────────────┘                     └──────────────────┘
         │
         │ 导入
         ▼
┌──────────────────┐
│ stocks_master.json│
│ (主数据文件)      │
└──────────────────┘
```

## 文件说明

| 文件 | 作用 | 运行端口 |
|------|------|----------|
| `article_api_server.py` | 文章数据接收服务 | 5001 |
| `article_importer.py` | 数据导入器（命令行工具） | - |
| `agent_example.py` | 智能体调用示例 | - |
| `main.py` | 主项目（已添加同步API） | 5000 |

## 快速开始

### 1. 启动文章API服务

```bash
python article_api_server.py
```

服务将运行在 http://localhost:5001

### 2. 智能体发送数据

智能体通过HTTP POST发送识别结果：

```python
import requests

article_data = {
    "article_url": "https://mp.weixin.qq.com/s/...",
    "article_title": "文章标题",
    "article_date": "2026-03-30",
    "source": "wechat",
    "stocks": [
        {
            "name": "汇绿生态",
            "code": "001267",
            "board": "SZ",
            "concepts": ["光模块", "CPO"],
            "articles": [
                {
                    "date": "2026-03-30",
                    "source": "https://...",
                    "insights": ["投资洞察1", "投资洞察2"],
                    "accidents": ["催化剂1"],
                    "key_metrics": ["关键指标1"]
                }
            ]
        }
    ],
    "metadata": {
        "agent_id": "your_agent_id",
        "recognition_confidence": 0.95
    }
}

response = requests.post(
    "http://localhost:5001/api/article/receive",
    json=article_data,
    timeout=30
)
print(response.json())
```

### 3. 导入数据到主项目

**方式一：命令行导入**

```bash
python article_importer.py
```

**方式二：通过主项目API触发**

```bash
curl -X POST http://localhost:5000/api/articles/sync
```

**方式三：在Web界面添加同步按钮**

调用 `/api/articles/sync` 接口

## API端点

### 文章API服务 (端口5001)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/article/receive` | POST | 接收智能体数据 |
| `/api/articles` | GET | 获取文章列表 |
| `/api/articles/pending` | GET | 获取待导入数据 |
| `/api/articles/import` | POST | 标记已导入 |
| `/api/stock/<code>/articles` | GET | 查询股票相关文章 |
| `/api/sync/to-main` | POST | 同步到主项目格式 |

### 主项目新增API (端口5000)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/articles/status` | GET | 检查API服务状态 |
| `/api/articles/sync` | POST | 触发数据同步 |

## 数据格式

### 智能体发送格式

```json
{
  "article_url": "文章链接",
  "article_title": "文章标题",
  "article_date": "2026-03-30",
  "source": "wechat",
  "stocks": [
    {
      "name": "股票名称",
      "code": "股票代码",
      "board": "SZ/SH/BJ",
      "industry": "行业",
      "concepts": ["概念1", "概念2"],
      "products": ["产品1"],
      "core_business": ["核心业务"],
      "industry_position": ["行业地位"],
      "chain": ["产业链位置"],
      "partners": ["合作伙伴"],
      "mention_count": 1,
      "articles": [
        {
          "title": "",
          "date": "2026-03-30",
          "source": "https://...",
          "accidents": ["催化剂"],
          "insights": ["投资洞察"],
          "key_metrics": ["关键指标"],
          "target_valuation": ["目标估值"]
        }
      ]
    }
  ],
  "metadata": {
    "agent_id": "agent_001",
    "recognition_confidence": 0.95
  }
}
```

## 数据存储

文章API服务将数据保存到以下JSON文件：

- `data/articles/articles_db.json` - 所有文章数据
- `data/articles/pending_import.json` - 待导入队列

## 智能体集成示例

参考 `agent_example.py` 文件，包含：

1. 发送文章数据示例
2. 查询文章列表示例
3. 查询股票相关文章示例
4. `StockAnalysisAgent` 类模板

运行示例：

```bash
python agent_example.py
```

## 部署建议

### 本地开发

同时启动两个服务：

```bash
# 终端1：启动文章API服务
python article_api_server.py

# 终端2：启动主项目
python main.py
```

### 生产部署

1. **Railway/云部署**：
   - 文章API服务作为独立服务部署
   - 设置环境变量 `ARTICLE_API_URL` 指向API服务地址

2. **Docker部署**：
   ```yaml
   version: '3'
   services:
     article-api:
       build: .
       command: python article_api_server.py
       ports:
         - "5001:5001"
       volumes:
         - ./data:/app/data
     
     web:
       build: .
       command: python main.py
       ports:
         - "5000:5000"
       environment:
         - ARTICLE_API_URL=http://article-api:5001
       volumes:
         - ./data:/app/data
   ```

## 扩展建议

1. **添加认证**：为API添加API Key验证
2. **数据验证**：使用Pydantic验证输入数据
3. **异步处理**：使用Celery处理大量数据导入
4. **WebSocket**：实时通知主项目有新数据
5. **数据去重**：改进文章去重逻辑（相似度检测）
