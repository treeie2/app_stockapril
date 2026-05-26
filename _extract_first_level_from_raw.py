"""
从 raw_material 的完整数据中提取第一层信息，补充到 stocks_master.json
数据源：raw_material/stocks_from_raw_materials_complete_2026-04-23.json
"""
import json
from pathlib import Path

MASTER_FILE = Path("data/stocks/stocks_master.json")
RAW_MATERIAL_FILE = Path("raw_material/stocks_from_raw_materials_complete_2026-04-23.json")

# 第一层字段列表
FIRST_LEVEL_FIELDS = [
    "products", "core_business", "industry_position", 
    "chain", "partners", "industry", "concepts"
]


def load_json_file(file_path):
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_stock_in_raw_material(code, name, raw_materials_list):
    """在 raw_material 列表中查找对应的股票"""
    for stock in raw_materials_list:
        # 优先匹配 code
        if code and stock.get('code') == code:
            return stock
        # 其次匹配 name
        if name and stock.get('name') == name:
            return stock
    return None


def merge_first_level_info(master_stock, raw_stock):
    """从 raw_stock 补充 master_stock 的第一层信息"""
    updated = False
    updated_fields = []
    
    for field in FIRST_LEVEL_FIELDS:
        # 如果 master 中该字段为空或不存在，且 raw 中有值
        if (field not in master_stock or not master_stock[field]) and \
           (field in raw_stock and raw_stock[field]):
            master_stock[field] = raw_stock[field]
            updated = True
            updated_fields.append(field)
    
    return updated, updated_fields


def main():
    print("🔍 从 raw_material 提取第一层信息补充到 stocks_master.json")
    print("=" * 60)
    
    # 加载 stocks_master.json
    print("\n📂 加载 stocks_master.json...")
    master_data = load_json_file(MASTER_FILE)
    master_stocks = master_data.get('stocks', {})
    print(f"   总计：{len(master_stocks)} 只股票")
    
    # 统计缺少第一层信息的股票
    missing_stocks = []
    for code, stock in master_stocks.items():
        if not (stock.get('products') and stock.get('core_business') and stock.get('industry_position')):
            missing_stocks.append((code, stock))
    
    print(f"   缺少第一层信息：{len(missing_stocks)} 只")
    
    # 加载 raw_material 完整数据
    print("\n📂 加载 raw_material 完整数据...")
    raw_data = load_json_file(RAW_MATERIAL_FILE)
    raw_materials = raw_data.get('stocks', [])
    print(f"   总计：{len(raw_materials)} 只股票")
    
    # 统计 raw_material 中有完整第一层信息的股票
    complete_in_raw = sum(1 for s in raw_materials if s.get('products') and s.get('core_business') and s.get('industry_position'))
    print(f"   完整第一层信息：{complete_in_raw} 只 ({complete_in_raw/len(raw_materials)*100:.1f}%)")
    
    # 检查并补充缺失信息
    print("\n🔍 检查并补充缺失信息...")
    updated_count = 0
    
    for code, stock in missing_stocks:
        name = stock.get('name', '')
        
        # 在 raw_material 中查找
        raw_stock = find_stock_in_raw_material(code, name, raw_materials)
        
        if raw_stock:
            # 补充第一层信息
            updated, updated_fields = merge_first_level_info(stock, raw_stock)
            if updated:
                updated_count += 1
                print(f"   ✅ {code} {name}: 补充了 {updated_fields}")
    
    # 保存更新后的文件
    print("\n💾 保存更新后的 stocks_master.json...")
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    # 重新统计
    complete_count = sum(1 for s in master_stocks.values() if s.get('products') and s.get('core_business') and s.get('industry_position'))
    partial_count = sum(1 for s in master_stocks.values() if (s.get('products') or s.get('core_business') or s.get('industry_position')) and not (s.get('products') and s.get('core_business') and s.get('industry_position')))
    empty_count = sum(1 for s in master_stocks.values() if not s.get('products') and not s.get('core_business') and not s.get('industry_position'))
    
    print("\n" + "=" * 60)
    print("📊 更新后统计:")
    print(f"   总股票数：{len(master_stocks)}")
    print(f"   ✅ 完整第一层信息：{complete_count} ({complete_count/len(master_stocks)*100:.1f}%)")
    print(f"   ⚠️  部分第一层信息：{partial_count} ({partial_count/len(master_stocks)*100:.1f}%)")
    print(f"   ❌ 无第一层信息：{empty_count} ({empty_count/len(master_stocks)*100:.1f}%)")
    print(f"\n   本次更新：{updated_count} 只股票")
    print("\n✅ 完成!")


if __name__ == "__main__":
    main()
