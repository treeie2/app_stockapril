"""
从 raw_material 补充 stocks_master.json 缺失的第一层信息
"""
import json
from pathlib import Path

MASTER_FILE = Path("data/stocks/stocks_master.json")
RAW_MATERIAL_DIR = Path("raw_material")

# 第一层字段列表
FIRST_LEVEL_FIELDS = [
    "name", "code", "board", "industry", "concepts", "products",
    "core_business", "industry_position", "chain", "partners",
    "mention_count", "articles", "valuation", "last_updated", "updated_at"
]


def load_json_file(file_path):
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_stock_in_raw_material(code, name, raw_materials):
    """在 raw_material 中查找对应的股票"""
    for stock in raw_materials:
        # 优先匹配 code
        if code and stock.get('code') == code:
            return stock
        # 其次匹配 name
        if name and stock.get('name') == name:
            return stock
    return None


def merge_stock_info(master_stock, raw_stock):
    """从 raw_stock 补充 master_stock 缺失的字段"""
    updated = False
    for field in FIRST_LEVEL_FIELDS:
        # 跳过 articles 和 valuation，这些需要特殊处理
        if field in ['articles', 'valuation']:
            continue
            
        # 如果 master 中该字段为空或不存在，从 raw 补充
        if field not in master_stock or not master_stock[field]:
            if field in raw_stock and raw_stock[field]:
                master_stock[field] = raw_stock[field]
                updated = True
    
    # 特殊处理 articles：合并而不是替换
    if raw_stock.get('articles'):
        master_articles = master_stock.get('articles', [])
        raw_articles = raw_stock.get('articles', [])
        
        # 创建一个集合来追踪已有的文章（按 title+date）
        existing_keys = {(a.get('title', ''), a.get('date', '')) for a in master_articles}
        
        # 添加 raw 中新的文章
        for article in raw_articles:
            key = (article.get('title', ''), article.get('date', ''))
            if key not in existing_keys:
                master_articles.append(article)
                updated = True
        
        if master_articles:
            master_stock['articles'] = master_articles
    
    # 特殊处理 valuation：合并
    if raw_stock.get('valuation'):
        if 'valuation' not in master_stock:
            master_stock['valuation'] = {}
        master_stock['valuation'].update(raw_stock['valuation'])
        updated = True
    
    return updated


def main():
    print("🔍 从 raw_material 补充 stocks_master.json 缺失信息")
    print("=" * 60)
    
    # 加载 stocks_master.json
    print("\n📂 加载 stocks_master.json...")
    master_data = load_json_file(MASTER_FILE)
    master_stocks = master_data.get('stocks', {})
    print(f"   总计：{len(master_stocks)} 只股票")
    
    # 加载所有 raw_material 文件
    raw_materials = []
    print("\n📂 加载 raw_material 文件...")
    
    for json_file in RAW_MATERIAL_DIR.glob("*.json"):
        if 'stocks_from_raw_materials' in str(json_file) or 'stocks_master' in str(json_file):
            print(f"   读取：{json_file.name}")
            try:
                data = load_json_file(json_file)
                if 'stocks' in data:
                    stocks_list = data['stocks']
                    if isinstance(stocks_list, list):
                        raw_materials.extend(stocks_list)
                    elif isinstance(stocks_list, dict):
                        raw_materials.extend(stocks_list.values())
            except Exception as e:
                print(f"   ⚠️ 读取失败：{e}")
    
    print(f"   总计：{len(raw_materials)} 条 raw_material 记录")
    
    # 检查并补充缺失信息
    print("\n🔍 检查并补充缺失信息...")
    updated_count = 0
    checked_count = 0
    
    for code, stock in master_stocks.items():
        name = stock.get('name', '')
        
        # 检查是否缺少关键的第一层信息
        missing_fields = []
        for field in ['products', 'core_business', 'industry_position', 'chain', 'partners']:
            if field not in stock or not stock[field]:
                missing_fields.append(field)
        
        if missing_fields:
            checked_count += 1
            
            # 在 raw_material 中查找
            raw_stock = find_stock_in_raw_material(code, name, raw_materials)
            
            if raw_stock:
                # 补充缺失信息
                if merge_stock_info(stock, raw_stock):
                    updated_count += 1
                    print(f"   ✅ {code} {name}: 补充了 {missing_fields}")
    
    # 保存更新后的文件
    print("\n💾 保存更新后的 stocks_master.json...")
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("📊 统计结果:")
    print(f"   检查股票数：{checked_count} 只（缺少第一层信息的）")
    print(f"   更新股票数：{updated_count} 只")
    print(f"   更新率：{updated_count / checked_count * 100:.1f}%" if checked_count > 0 else "   无需更新")
    print("\n✅ 完成!")


if __name__ == "__main__":
    main()
