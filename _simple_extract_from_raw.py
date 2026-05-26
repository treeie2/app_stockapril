"""
直接从 raw_material 文件中提取个股第一层信息
不依赖 LLM，基于规则和现有股票映射
"""
import json
import re
from pathlib import Path

RAW_MATERIAL_DIR = Path("raw_material")
MASTER_FILE = Path("data/stocks/stocks_master.json")
STOCK_INDEX_FILE = Path("data/stocks/stocks_index.json")


def load_stock_index():
    """加载股票索引"""
    if not STOCK_INDEX_FILE.exists():
        return {}, {}
    
    with open(STOCK_INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks_dict = data.get('stocks', {})
    code_to_name = {code: info['name'] for code, info in stocks_dict.items()}
    name_to_code = {info['name']: code for code, info in stocks_dict.items()}
    return code_to_name, name_to_code


def parse_raw_material(file_path):
    """解析 raw_material 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    articles = []
    current_article = {}
    
    for line in content.split('\n'):
        if line.startswith('## Article'):
            if current_article:
                articles.append(current_article)
            current_article = {'content': ''}
        elif line.startswith('source:'):
            current_article['source'] = line.split(':', 1)[1].strip()
        elif line.startswith('fetched_at:'):
            current_article['date'] = line.split(':', 1)[1].strip()[:10]
        elif line.startswith('title:'):
            current_article['title'] = line.split(':', 1)[1].strip()
        elif current_article:
            current_article['content'] += line + '\n'
    
    if current_article:
        articles.append(current_article)
    
    return articles


def extract_stock_info_from_content(content, code_to_name, name_to_code):
    """从内容中提取股票信息和第一层数据"""
    stocks_found = {}
    
    # 提取股票代码和名称（通过索引匹配）
    for code, name in code_to_name.items():
        if code in content or name in content:
            stocks_found[code] = {'code': code, 'name': name, 'mentioned': True}
    
    # 如果没有找到，尝试通过名称匹配
    for name, code in name_to_code.items():
        if name in content and code not in stocks_found:
            stocks_found[code] = {'code': code, 'name': name, 'mentioned': True}
    
    return list(stocks_found.values())


def extract_first_level_info(content):
    """从内容中提取第一层信息（简单规则提取）"""
    info = {
        'products': [],
        'core_business': [],
        'industry_position': [],
        'chain': [],
        'partners': []
    }
    
    # 提取产品（简单规则：包含"产品"、"设备"、"材料"等关键词的句子）
    product_keywords = ['产品', '设备', '材料', '系统', '解决方案']
    for line in content.split('\n'):
        for keyword in product_keywords:
            if keyword in line and len(line) < 200:
                # 简化提取
                if '专注于' in line or '主要从事' in line or '核心产品' in line:
                    info['products'].append(line.strip()[:100])
                    break
    
    # 提取核心业务
    biz_keywords = ['专注于', '主要从事', '核心业务', '主营业务']
    for line in content.split('\n'):
        for keyword in biz_keywords:
            if keyword in line and len(line) < 200:
                info['core_business'].append(line.strip()[:100])
                break
    
    # 提取行业地位
    position_keywords = ['龙头', '领先', '第一', '核心', '头部', '少数', '率先']
    for line in content.split('\n'):
        for keyword in position_keywords:
            if keyword in line and len(line) < 200:
                info['industry_position'].append(line.strip()[:100])
                break
    
    # 提取合作伙伴
    partner_keywords = ['客户', '合作', '供应链', '服务于']
    for line in content.split('\n'):
        for keyword in partner_keywords:
            if keyword in line and ('包括' in line or '有' in line) and len(line) < 200:
                info['partners'].append(line.strip()[:100])
                break
    
    # 去重
    for key in info:
        info[key] = list(set(info[key]))[:3]  # 每个字段最多 3 个
    
    return info


def main():
    print("=" * 80)
    print("🔍 直接从 raw_material 提取第一层信息")
    print("=" * 80)
    
    # 加载股票索引
    print("\n📂 加载股票索引...")
    code_to_name, name_to_code = load_stock_index()
    print(f"   已加载 {len(code_to_name)} 只股票")
    
    # 获取所有 raw_material 文件
    raw_files = sorted(RAW_MATERIAL_DIR.glob("raw_material_*.md"), reverse=True)
    print(f"\n📂 找到 {len(raw_files)} 个 raw_material 文件")
    
    # 加载现有 master 数据
    print("\n📂 加载 stocks_master.json...")
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    master_stocks = master_data.get('stocks', {})
    print(f"   现有股票：{len(master_stocks)} 只")
    
    # 处理每个文件
    total_stocks = 0
    total_articles = 0
    
    for raw_file in raw_files:
        print(f"\n📄 处理：{raw_file.name}")
        
        articles = parse_raw_material(raw_file)
        print(f"   找到 {len(articles)} 篇文章")
        
        for article in articles:
            content = article.get('content', '')
            source = article.get('source', '')
            date = article.get('date', '')
            title = article.get('title', '')
            
            # 提取提到的股票
            stocks = extract_stock_info_from_content(content, code_to_name, name_to_code)
            
            for stock in stocks:
                code = stock['code']
                
                # 如果股票不在 master 中，跳过
                if code not in master_stocks:
                    continue
                
                # 添加文章
                if 'articles' not in master_stocks[code]:
                    master_stocks[code]['articles'] = []
                
                # 检查文章是否已存在
                existing_sources = {a.get('source') for a in master_stocks[code]['articles']}
                if source not in existing_sources:
                    article_data = {
                        'title': title,
                        'date': date,
                        'source': source,
                        'accidents': [],
                        'insights': [],
                        'key_metrics': [],
                        'target_valuation': []
                    }
                    master_stocks[code]['articles'].append(article_data)
                    master_stocks[code]['mention_count'] = len(master_stocks[code]['articles'])
                    
                    # 提取第一层信息
                    first_level = extract_first_level_info(content)
                    
                    # 补充第一层信息
                    for field in ['products', 'core_business', 'industry_position', 'chain', 'partners']:
                        if first_level[field] and (field not in master_stocks[code] or not master_stocks[code][field]):
                            master_stocks[code][field] = first_level[field]
                    
                    total_articles += 1
                    print(f"      ✅ {code} {stock['name']}: 添加文章，补充第一层信息")
    
    # 保存
    print("\n💾 保存更新后的 stocks_master.json...")
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    # 统计
    stocks = master_data.get('stocks', {})
    complete = sum(1 for s in stocks.values() if s.get('products') and s.get('core_business') and s.get('industry_position'))
    
    print("\n" + "=" * 80)
    print("📊 处理结果:")
    print(f"   处理文件数：{len(raw_files)}")
    print(f"   添加文章数：{total_articles}")
    print(f"   总股票数：{len(stocks)}")
    print(f"   完整第一层信息：{complete} 只 ({complete/len(stocks)*100:.1f}%)")
    print("\n✅ 完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
