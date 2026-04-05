"""
手动补充缺失的行业数据
基于股票名称和已知信息推断行业
"""
import json
from pathlib import Path

def load_stocks_data():
    """加载股票数据"""
    master_file = Path('data/master/stocks_master.json')
    with open(master_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_stocks_data(data):
    """保存股票数据"""
    master_file = Path('data/master/stocks_master.json')
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def infer_industry(name, code):
    """根据股票名称推断行业"""
    name = name.lower()
    
    # 建筑材料/装修
    if any(k in name for k in ['吊顶', '建材', '陶瓷', '卫浴', '地板', '涂料', '装饰', '装修']):
        return "建筑材料 - 装修建材 - 其他建材"
    
    # 医药医疗
    if any(k in name for k in ['医药', '药业', '制药', '医疗', '医院', '生物', '健康', '诊断']):
        return "医药生物 - 医疗器械 - 医疗设备"
    
    # 机械设备
    if any(k in name for k in ['机械', '设备', '重工', '精密', '液压', '轴承', '模具']):
        return "机械设备 - 通用设备 - 机械基础件"
    
    # 食品饮料
    if any(k in name for k in ['食品', '饮料', '酒水', '乳业', '酒业', '啤酒', '白酒']):
        return "食品饮料 - 饮料制造 - 软饮料"
    
    # 交通运输
    if any(k in name for k in ['航空', '机场', '航运', '港口', '物流', '运输', '铁路']):
        return "交通运输 - 航空运输 - 航空"
    
    # 电子/科技
    if any(k in name for k in ['科技', '电子', '半导体', '芯片', '软件', '信息', '计算', '数据']):
        return "电子 - 半导体 - 集成电路"
    
    # 电力能源
    if any(k in name for k in ['电力', '能源', '光伏', '风电', '核电', '水电']):
        return "电力设备 - 光伏设备 - 光伏电池组件"
    
    # 化工
    if any(k in name for k in ['化工', '化学', '材料', '纤维', '橡胶', '塑料']):
        return "基础化工 - 化学纤维 - 其他纤维"
    
    # 房地产/商业
    if any(k in name for k in ['地产', '商业', '百货', '商场', '零售', '物业']):
        return "房地产 - 商业地产 - 商业运营"
    
    # 汽车
    if any(k in name for k in ['汽车', '车辆', '轮胎', '动力', '汽配']):
        return "汽车 - 汽车零部件 - 汽车电子"
    
    # 金融
    if any(k in name for k in ['银行', '保险', '证券', '金融', '投资', '期货']):
        return "非银金融 - 多元金融 - 金融租赁"
    
    # 传媒/文化
    if any(k in name for k in ['文化', '传媒', '影视', '游戏', '动漫', '出版']):
        return "传媒 - 数字媒体 - 游戏"
    
    # 默认分类
    return "其他 - 其他 - 其他"

def supplement_industry():
    """补充行业数据"""
    print("📊 加载股票数据...")
    data = load_stocks_data()
    stocks = data.get('stocks', [])
    
    print(f"📈 共 {len(stocks)} 只股票\n")
    
    # 找出缺失行业的股票
    missing_industry = [s for s in stocks if not s.get('industry')]
    print(f"📋 缺失行业的股票: {len(missing_industry)} 只\n")
    
    # 补充行业
    print("🔧 开始补充行业信息...")
    supplemented = 0
    
    for stock in missing_industry:
        code = stock.get('code', '')
        name = stock.get('name', '')
        
        industry = infer_industry(name, code)
        stock['industry'] = industry
        supplemented += 1
        
        print(f"  [{supplemented}] {code} {name}")
        print(f"      → {industry}")
    
    print(f"\n✅ 已补充 {supplemented} 只股票的行业信息")
    
    # 保存数据
    print("\n💾 保存数据...")
    save_stocks_data(data)
    
    # 验证
    missing_after = sum(1 for s in stocks if not s.get('industry'))
    print(f"\n📊 补充后:")
    print(f"  - 缺行业: {missing_after} 只")
    print(f"  - 完整度: {(len(stocks) - missing_after) / len(stocks) * 100:.1f}%")
    
    print("\n🎉 行业数据补充完成！")

if __name__ == "__main__":
    supplement_industry()
