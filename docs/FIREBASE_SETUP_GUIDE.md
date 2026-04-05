# Firebase Firestore 集成指南

## 方案概述

使用 **Firebase Firestore** 作为云端JSON数据库，实现智能体和stock-research之间的数据同步。

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   智能体Agent    │  ───>   │  Firebase        │  ───>   │  stock-research │
│  (本地Python)    │  写入   │  Firestore       │  读取   │  (Web项目)      │
│                 │         │  (云端JSON数据库)  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

## 为什么选择 Firestore？

| 特性 | 说明 |
|------|------|
| **免费额度** | 每天5万次读取、2万次写入、1GB存储 |
| **JSON原生** | 完美支持JSON数据结构 |
| **实时同步** | 支持实时监听数据变化 |
| **Python SDK** | 完善的Python支持 |
| **全球CDN** | 访问速度快 |
| **安全可靠** | Google基础设施 |

## 快速开始

### 1. 创建Firebase项目

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 点击 "创建项目"
3. 输入项目名称（如 `stock-research-db`）
4. 按提示完成创建

### 2. 创建Firestore数据库

1. 在Firebase控制台，点击左侧 "Firestore Database"
2. 点击 "创建数据库"
3. 选择 "以测试模式开始"（方便开发，后续可调整安全规则）
4. 选择数据中心位置（推荐 `asia-east1` 台湾）
5. 点击 "启用"

### 3. 获取服务账号密钥

1. 点击左上角齿轮图标 → "项目设置"
2. 选择 "服务账号" 标签
3. 点击 "生成新的私钥"
4. 下载JSON文件，重命名为 `firebase-credentials.json`
5. 将文件放到项目根目录

### 4. 安装依赖

```bash
pip install firebase-admin
```

添加到 requirements.txt：
```
firebase-admin==6.5.0
```

## 使用说明

### 智能体写入数据

```python
from agent_firestore_writer import AgentFirestoreWriter

# 初始化写入器
writer = AgentFirestoreWriter('firebase-credentials.json')

# 写入文章分析结果
doc_id = writer.write_article_analysis(
    article_url="https://mp.weixin.qq.com/s/...",
    article_title="光模块行业深度分析",
    article_date="2026-03-30",
    stocks=[
        {
            "name": "中际旭创",
            "code": "300308",
            "board": "SZ",
            "concepts": ["光模块", "CPO"],
            "articles": [{
                "date": "2026-03-30",
                "source": "https://mp.weixin.qq.com/s/...",
                "insights": ["全球光模块龙头"],
                "accidents": ["AI算力需求爆发"],
                "key_metrics": ["25年预期净利超60亿"]
            }]
        }
    ],
    metadata={"agent_id": "stock_analyzer_v1"}
)

print(f"写入成功，文档ID: {doc_id}")
```

### stock-research同步数据

```bash
# 查看同步状态
python sync_from_firestore.py --status

# 预览待同步文章
python sync_from_firestore.py --preview

# 执行同步
python sync_from_firestore.py --sync

# 自动确认同步（不提示）
python sync_from_firestore.py --sync --yes

# 全量同步（包括已同步的）
python sync_from_firestore.py --full
```

Python代码方式：

```python
from sync_from_firestore import FirestoreSyncManager

# 初始化同步管理器
sync = FirestoreSyncManager('firebase-credentials.json')

# 同步待处理文章
stats = sync.sync_pending_articles()
print(f"同步完成: {stats}")
```

### 在Web界面添加同步按钮

修改 `main.py`，添加同步API：

```python
@app.route('/api/sync/firestore', methods=['POST'])
def sync_from_firestore():
    """从Firestore同步数据"""
    try:
        from sync_from_firestore import FirestoreSyncManager
        sync = FirestoreSyncManager()
        stats = sync.sync_pending_articles(auto_confirm=True)
        return jsonify({
            'success': True,
            'message': '同步完成',
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

前端添加按钮调用此API即可。

## 文件说明

| 文件 | 作用 | 使用方 |
|------|------|--------|
| `firestore_db.py` | Firestore数据库核心模块 | 双方共用 |
| `agent_firestore_writer.py` | 智能体写入工具 | 智能体 |
| `sync_from_firestore.py` | 数据同步工具 | stock-research |
| `firebase-credentials.json` | Firebase密钥（需自行创建） | 双方共用 |

## 数据结构

Firestore中的文档结构：

```
collections/
├── articles/           # 文章集合
│   ├── {doc_id}/      # 文章文档
│   │   ├── article_url: string
│   │   ├── article_title: string
│   │   ├── article_date: string
│   │   ├── source: string
│   │   ├── stocks: array
│   │   ├── metadata: map
│   │   ├── sync_status: string (pending/synced/failed)
│   │   ├── created_at: timestamp
│   │   └── synced_at: timestamp
│   └── ...
│
└── stocks/            # 股票集合（可选）
    ├── {code}/
    │   └── ...
    └── ...
```

## 安全规则配置

生产环境建议配置安全规则：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 文章集合
    match /articles/{articleId} {
      allow read: if true;  // 允许读取
      allow create: if request.auth != null;  // 需要认证才能写入
      allow update: if request.auth != null;
      allow delete: if false;  // 禁止删除
    }
    
    // 股票集合
    match /stocks/{stockId} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## 费用估算

Firestore免费额度：
- 读取：5万次/天
- 写入：2万次/天
- 删除：2万次/天
- 存储：1GB

对于个人使用完全免费。超出后：
- 读取：$0.06/10万次
- 写入：$0.18/10万次

## 常见问题

### Q: 凭证文件放在哪里安全？
A: 
- 本地开发：放在项目根目录，添加到 `.gitignore`
- 生产环境：使用环境变量，不要提交到Git

### Q: 智能体和stock-research可以用同一凭证吗？
A: 可以，建议创建同一个服务账号，双方使用相同凭证文件

### Q: 数据会实时同步吗？
A: Firestore支持实时监听，但当前实现是轮询模式。如需实时同步，可使用Firestore的`on_snapshot`功能

### Q: 可以离线使用吗？
A: 可以，`sync_from_firestore.py`会自动创建本地备份（`data/firestore_backup/`）

## 扩展功能

1. **实时同步**：使用Firestore的实时监听功能
2. **数据验证**：添加输入数据验证
3. **版本控制**：记录数据修改历史
4. **多智能体支持**：区分不同智能体的数据
5. **数据清理**：自动清理过期数据

## 参考链接

- [Firebase Console](https://console.firebase.google.com/)
- [Firestore文档](https://firebase.google.com/docs/firestore)
- [Python SDK文档](https://firebase.google.com/docs/reference/admin/python)
