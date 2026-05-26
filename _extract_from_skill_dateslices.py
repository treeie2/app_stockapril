"""
从 wechat-fetch-research-embedded 的日期分片文件中提取第一层信息
补充到 stocks_master.json 中缺失的股票
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path("data/stocks/stocks_master.json")
SKILL_DATA_DIR = Path(".trae/skills/wechat-fetch-research-embedded/data/master/stocks")

# 第一层字段列表
FIRST_LEVEL_FIELDS = [
    "products", "core_business", "industry_position", 
    "chain", "partners", "industry", "concepts"
]


def load_json_file(file_path):
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def merge_first_level_info(master_stock, skill_stock):
    """从 skill_stock 补充 master_stock 的第一层信息"""
    updated = False
    updated_fields = []
    
    for field in FIRST_LEVEL_FIELDS:
        # 如果 master 中该字段为空或不存在，且 skill 中有值
        if (field not in master_stock or not master_stock[field]) and \
           (field in skill_stock and skill_stock[field]):
            master_stock[field] = skill_stock[field]
            updated = True
            updated_fields.append(field)
    
    return updated, updated_fields


def main():
    print("🔍 从 skill 日期分片文件提取第一层信息")
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
    
    # 加载所有日期分片文件
    print("\n📂 加载 skill 日期分片文件...")
    all_skill_stocks = {}
    
    json_files = sorted(SKILL_DATA_DIR.glob("*.json"), reverse=True)
    for json_file in json_files:
        print(f"   读取：{json_file.name}")
        try:
            data = load_json_file(json_file)
            stocks = data.get('stocks', {})
            if isinstance(stocks, dict):
                for code, stock in stocks.items():
                    # 只保留有第一层信息的股票
                    if stock.get('products') or stock.get('core_business') or stock.get('industry_position'):
                        if code not in all_skill_stocks:
                            all_skill_stocks[code] = stock
        except Exception as e:
            print(f"   ⚠️ 读取失败：{e}")
    
    print(f"   有第一层信息的股票：{len(all_skill_stocks)} 只")
    
    # 检查并补充缺失信息
    print("\n🔍 检查并补充缺失信息...")
    updated_count = 0
    
    for code, stock in missing_stocks:
        # 在 skill 数据中查找
        if code in all_skill_stocks:
            skill_stock = all_skill_stocks[code]
            # 补充第一层信息
            updated, updated_fields = merge_first_level_info(stock, skill_stock)
            if updated:
                updated_count += 1
                print(f"   ✅ {code} {stock.get('name', '')}: 补充了 {updated_fields}")
    
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
