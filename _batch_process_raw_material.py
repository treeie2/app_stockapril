"""
批量处理所有 raw_material 文件，提取个股结构化信息
按照数据结构说明 v3.0 的规范处理
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

RAW_MATERIAL_DIR = Path("raw_material")
OUTPUT_DIR = Path("data/stocks")
MASTER_FILE = OUTPUT_DIR / "stocks_master.json"
STOCK_XLS = Path(".trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls")

# 提取脚本路径
EXTRACT_SCRIPT = Path(".trae/skills/wechat-fetch-research-embedded/scripts/extract_stocks_from_raw_material.py")


def load_existing_stocks():
    """加载现有的 stocks_master.json"""
    if MASTER_FILE.exists():
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"stocks": {}}


def process_raw_material(raw_file):
    """处理单个 raw_material 文件"""
    print(f"\n📄 处理：{raw_file.name}")
    
    # 提取日期（从文件名）
    date_str = raw_file.stem.replace('raw_material_', '').replace('_', '-')
    if len(date_str) > 10:
        date_str = date_str[:10]  # 截取前 10 个字符，如 2026-05-19
    
    # 输出文件
    output_json = OUTPUT_DIR / f"stocks_master_{date_str}.json"
    
    # 运行提取脚本
    cmd = [
        "python", str(EXTRACT_SCRIPT),
        "--raw", str(raw_file),
        "--stock_xls", str(STOCK_XLS),
        "--out_json", str(output_json),
        "--mode", "merge"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print(f"   ✅ 提取完成，输出：{output_json.name}")
            return output_json
        else:
            stderr_msg = result.stderr[:200] if result.stderr else "未知错误"
            print(f"   ❌ 提取失败：{stderr_msg}")
            return None
    except Exception as e:
        print(f"   ❌ 执行错误：{e}")
        return None


def merge_to_master(extracted_file, master_data):
    """将提取的数据合并到 master"""
    if not extracted_file or not extracted_file.exists():
        return 0
    
    try:
        with open(extracted_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        new_stocks = new_data.get('stocks', {})
        if isinstance(new_stocks, list):
            # 如果是列表，转换为字典
            new_stocks = {s.get('code', str(i)): s for i, s in enumerate(new_stocks)}
        
        master_stocks = master_data.get('stocks', {})
        merged_count = 0
        
        for code, stock in new_stocks.items():
            if code in master_stocks:
                # 合并文章
                existing_articles = master_stocks[code].get('articles', [])
                new_articles = stock.get('articles', [])
                
                # 去重（按 source）
                existing_sources = {a.get('source') for a in existing_articles}
                for article in new_articles:
                    if article.get('source') not in existing_sources:
                        existing_articles.append(article)
                
                # 更新第一层信息（如果有）
                for field in ['products', 'core_business', 'industry_position', 'chain', 'partners', 'concepts']:
                    if field in stock and stock[field]:
                        master_stocks[code][field] = stock[field]
                
                master_stocks[code]['articles'] = existing_articles
                master_stocks[code]['mention_count'] = len(master_stocks[code]['articles'])
            else:
                # 新股票
                master_stocks[code] = stock
            
            merged_count += 1
        
        master_data['stocks'] = master_stocks
        return merged_count
    
    except Exception as e:
        print(f"   ❌ 合并失败：{e}")
        return 0


def main():
    print("=" * 80)
    print("🔍 批量处理 raw_material 文件")
    print("=" * 80)
    
    # 获取所有 raw_material 文件
    raw_files = sorted(RAW_MATERIAL_DIR.glob("raw_material_*.md"), reverse=True)
    print(f"\n📂 找到 {len(raw_files)} 个 raw_material 文件")
    
    # 加载现有数据
    print("\n📂 加载 stocks_master.json...")
    master_data = load_existing_stocks()
    print(f"   现有股票：{len(master_data.get('stocks', {}))} 只")
    
    # 逐个处理
    total_merged = 0
    for raw_file in raw_files:
        # 提取
        extracted_file = process_raw_material(raw_file)
        
        # 合并
        if extracted_file:
            merged = merge_to_master(extracted_file, master_data)
            total_merged += merged
            print(f"   📦 合并了 {merged} 只股票")
    
    # 保存
    print("\n💾 保存更新后的 stocks_master.json...")
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    # 统计
    print("\n" + "=" * 80)
    print("📊 处理结果:")
    print(f"   处理文件数：{len(raw_files)}")
    print(f"   合并股票数：{total_merged}")
    print(f"   总股票数：{len(master_data.get('stocks', {}))}")
    
    # 统计第一层信息完整度
    stocks = master_data.get('stocks', {})
    complete = sum(1 for s in stocks.values() if s.get('products') and s.get('core_business') and s.get('industry_position'))
    print(f"   完整第一层信息：{complete} 只 ({complete/len(stocks)*100:.1f}%)")
    print("\n✅ 完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
