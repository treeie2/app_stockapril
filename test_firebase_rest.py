"""
测试：使用 REST API 写入虚拟个股数据到 Firebase
"""
import requests
import json
from datetime import datetime

# Firebase 项目配置
PROJECT_ID = "webstock-724"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# 注意：这里需要一个有效的 Firebase ID Token
# 由于安全原因，Web API 写入需要身份验证
# 这里我们创建一个只读的测试来验证数据

def test_firebase_connection():
    """测试 Firebase 连接"""
    print("🔄 测试 Firebase 连接...")
    
    # 尝试读取 stocks 集合
    url = f"{BASE_URL}/stocks"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"✅ 连接成功！当前 stocks 集合有 {len(documents)} 个文档")
            
            if documents:
                print("\n📊 现有股票数据:")
                for doc in documents[:5]:  # 只显示前5个
                    name = doc['name'].split('/')[-1]
                    fields = doc.get('fields', {})
                    stock_name = fields.get('name', {}).get('stringValue', 'N/A')
                    print(f"  • {stock_name} ({name})")
            return True
        elif response.status_code == 403:
            print("⚠️ 访问被拒绝，需要身份验证")
            print("   这是正常的，Firestore 需要身份验证才能读取")
            return False
        else:
            print(f"❌ 连接失败: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False

def create_test_data_json():
    """创建测试数据 JSON 文件，可以手动导入到 Firebase"""
    test_stocks = {
        "000001": {
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
                }
            ],
            "updated_at": datetime.now().isoformat()
        },
        "000858": {
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
        "002594": {
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
                }
            ],
            "updated_at": datetime.now().isoformat()
        },
        "300750": {
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
        "600519": {
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
                }
            ],
            "updated_at": datetime.now().isoformat()
        }
    }
    
    # 保存为 JSON 文件
    output_file = 'test_stocks_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_stocks, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 测试数据已保存到: {output_file}")
    print(f"   包含 {len(test_stocks)} 只虚拟股票")
    
    return test_stocks

if __name__ == "__main__":
    print("=" * 50)
    print("Firebase 测试工具")
    print("=" * 50)
    
    # 测试连接
    test_firebase_connection()
    
    # 创建测试数据
    print("\n" + "=" * 50)
    print("创建测试数据")
    print("=" * 50)
    create_test_data_json()
    
    print("\n" + "=" * 50)
    print("说明")
    print("=" * 50)
    print("""
要将测试数据导入 Firebase，请使用以下方法之一：

方法1: 使用 Firebase Console (推荐)
  1. 访问 https://console.firebase.google.com/
  2. 进入 Firestore Database
  3. 点击 "导入 JSON"
  4. 选择 test_stocks_data.json 文件

方法2: 使用 Python SDK (需要凭证文件)
  1. 从 Firebase Console 下载服务账户密钥
  2. 保存为 firebase-credentials.json
  3. 运行: python test_firebase_write.py

方法3: 使用智能体写入
  1. 让智能体读取 test_stocks_data.json
  2. 调用 agent_stock_writer.py 写入 Firebase
""")
