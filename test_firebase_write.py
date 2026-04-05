"""
测试：写入虚拟个股数据到 Firebase
"""
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

# 初始化 Firebase
cred = credentials.Certificate('data/firestore_backup/firebase-credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# 创建虚拟测试数据
test_stocks = [
    {
        "code": "000001",
        "name": "平安银行",
        "concepts": ["银行", "金融科技", "粤港澳大湾区"],
        "mention_count": 15,
        "articles": [
            {
                "title": "平安银行2024年业绩分析",
                "source": "证券时报",
                "date": "2024-03-15",
                "insights": [
                    "净利润同比增长12.3%，超出市场预期",
                    "零售业务转型成效显著，AUM突破3万亿"
                ]
            },
            {
                "title": "银行股投资价值分析",
                "source": "中金公司",
                "date": "2024-03-10",
                "insights": [
                    "估值处于历史低位，具备较高安全边际",
                    "股息率超过5%，适合长期配置"
                ]
            }
        ],
        "updated_at": datetime.now().isoformat()
    },
    {
        "code": "000858",
        "name": "五粮液",
        "concepts": ["白酒", "消费", "MSCI中国"],
        "mention_count": 23,
        "articles": [
            {
                "title": "白酒行业深度报告",
                "source": "招商证券",
                "date": "2024-03-12",
                "insights": [
                    "高端白酒需求稳健，五粮液市场份额持续提升",
                    "渠道改革效果显现，经销商信心增强"
                ]
            }
        ],
        "updated_at": datetime.now().isoformat()
    },
    {
        "code": "002594",
        "name": "比亚迪",
        "concepts": ["新能源汽车", "锂电池", "智能驾驶"],
        "mention_count": 45,
        "articles": [
            {
                "title": "比亚迪3月销量创新高",
                "source": "汽车之家",
                "date": "2024-04-02",
                "insights": [
                    "月销量突破30万辆，同比增长46%",
                    "海外市场拓展加速，出口量环比增长25%"
                ]
            },
            {
                "title": "新能源汽车产业链分析",
                "source": "中信证券",
                "date": "2024-03-28",
                "insights": [
                    "垂直整合优势凸显，成本控制能力强",
                    "刀片电池技术领先，安全性获市场认可"
                ]
            },
            {
                "title": "智能驾驶技术进展",
                "source": "华泰证券",
                "date": "2024-03-20",
                "insights": [
                    "DiPilot系统持续迭代，城市NOA功能落地",
                    "智能化转型加速，软件服务收入占比提升"
                ]
            }
        ],
        "updated_at": datetime.now().isoformat()
    },
    {
        "code": "300750",
        "name": "宁德时代",
        "concepts": ["锂电池", "储能", "创业板"],
        "mention_count": 38,
        "articles": [
            {
                "title": "宁德时代2024年一季报前瞻",
                "source": "国泰君安",
                "date": "2024-04-01",
                "insights": [
                    "出货量预计同比增长30%，市场份额保持全球第一",
                    "储能业务快速增长，成为第二增长曲线"
                ]
            }
        ],
        "updated_at": datetime.now().isoformat()
    },
    {
        "code": "600519",
        "name": "贵州茅台",
        "concepts": ["白酒", "消费", "上证50"],
        "mention_count": 52,
        "articles": [
            {
                "title": "茅台批价走势分析",
                "source": "东吴证券",
                "date": "2024-03-25",
                "insights": [
                    "飞天茅台批价企稳回升，渠道库存去化良好",
                    "直销占比提升，吨价有望持续增长"
                ]
            },
            {
                "title": "高端消费复苏跟踪",
                "source": "兴业证券",
                "date": "2024-03-18",
                "insights": [
                    "商务消费场景恢复，高端白酒需求回暖",
                    "茅台1935放量，完善产品矩阵"
                ]
            }
        ],
        "updated_at": datetime.now().isoformat()
    }
]

# 写入 Firebase
print("📝 开始写入虚拟测试数据到 Firebase...")

for stock in test_stocks:
    code = stock["code"]
    doc_ref = db.collection('stocks').document(code)
    doc_ref.set(stock)
    print(f"  ✅ 已写入: {stock['name']} ({code})")

print(f"\n🎉 成功写入 {len(test_stocks)} 只虚拟股票到 Firebase!")
print("\n股票列表:")
for stock in test_stocks:
    print(f"  • {stock['name']} ({stock['code']}) - {stock['mention_count']}次提及")
