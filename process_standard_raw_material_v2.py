#!/usr/bin/env python3
"""
从标准化 raw_material 文件中提取完整的个股信息并更新到 stocks_master.json
包含：核心业务、行业地位、产业链位置、概念、目标估值等
"""
import json
import re
from pathlib import Path
from datetime import datetime

RAW_MATERIAL_FILE = Path("e:/github/stock-research-backup/raw_material/raw_material_2026-04-21.md")
MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
TODAY = datetime.now().strftime('%Y-%m-%d')

def parse_standard_raw_material(file_path):
    """解析标准化的 raw_material 文件"""
    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割成不同的文章部分
    articles = []
    article_sections = re.split(r'\n---\n', content)
    
    for section in article_sections[1:]:  # 跳过第一个标题部分
        if '# ' in section:
            article = parse_article_section(section)
            if article:
                articles.append(article)
    
    return articles

def parse_article_section(section):
    """解析单个文章部分"""
    lines = section.strip().split('\n')
    
    article = {
        'title': '',
        'source': '',
        'date': '',
        'stocks': [],
        'concepts': [],
        'chain_positions': []
    }
    
    # 提取标题
    title_match = re.search(r'^# (.+)$', section, re.MULTILINE)
    if title_match:
        article['title'] = title_match.group(1).strip()
    
    # 提取来源和日期
    source_match = re.search(r'\*\*来源\*\*: (.+)$', section, re.MULTILINE)
    if source_match:
        article['source'] = source_match.group(1).strip()
    
    date_match = re.search(r'\*\*文章日期\*\*: (.+)$', section, re.MULTILINE)
    if date_match:
        article['date'] = date_match.group(1).strip()
    
    # 提取个股信息
    article['stocks'] = extract_stocks_from_section(section)
    
    # 提取核心概念
    concepts_match = re.search(r'### 核心概念\n(.*?)(?=\n### |\Z)', section, re.DOTALL)
    if concepts_match:
        concepts_content = concepts_match.group(1)
        article['concepts'] = [line.strip().lstrip('- ').strip() for line in concepts_content.split('\n') if line.strip() and not line.strip().startswith('###')]
    
    # 提取产业链位置
    chain_match = re.search(r'### 产业链位置\n(.*?)(?=\n### |\Z)', section, re.DOTALL)
    if chain_match:
        chain_content = chain_match.group(1)
        article['chain_positions'] = [line.strip().lstrip('- ').strip() for line in chain_content.split('\n') if line.strip() and not line.strip().startswith('###')]
    
    return article

def extract_stocks_from_section(section):
    """从文章部分提取个股信息"""
    stocks = []
    
    # 查找个股部分
    stocks_section_match = re.search(r'### 涉及个股\n(.*?)(?=\n### |\Z)', section, re.DOTALL)
    if not stocks_section_match:
        return stocks
    
    stocks_content = stocks_section_match.group(1)
    
    # 匹配个股条目：1. **股票名称** (代码。交易所)
    stock_pattern = r'\d+\. \*\*([^*]+)\*\* \((\d{6})\.(SZ|SH)\)'
    matches = re.findall(stock_pattern, stocks_content)
    
    for match in matches:
        name, code, board = match
        stock_info = {
            'name': name.strip(),
            'code': code,
            'board': board,
            'core_business': [],
            'industry_position': [],
            'chain': [],
            'target_valuation': ''
        }
        
        # 查找该股票的详细信息
        stock_start = stocks_content.find(match[0])
        if stock_start != -1:
            # 找到下一个股票条目的位置
            next_stock = re.search(r'\n\d+\. \*\*', stocks_content[stock_start + len(match[0]):])
            if next_stock:
                stock_detail = stocks_content[stock_start:stock_start + len(match[0]) + next_stock.start()]
            else:
                stock_detail = stocks_content[stock_start:]
            
            # 提取核心业务
            business_match = re.search(r'- 核心业务：(.+?)(?=\n|$)', stock_detail)
            if business_match:
                business_str = business_match.group(1).strip()
                # 分割多个业务
                stock_info['core_business'] = [b.strip() for b in business_str.split('、')]
            
            # 提取行业地位
            position_match = re.search(r'- 行业地位：(.+?)(?=\n|$)', stock_detail)
            if position_match:
                position_str = position_match.group(1).strip()
                stock_info['industry_position'] = [position_str]
            
            # 提取产业链位置
            chain_match = re.search(r'- 产业链位置：(.+?)(?=\n|$)', stock_detail)
            if chain_match:
                chain_str = chain_match.group(1).strip()
                # 分割多个位置
                stock_info['chain'] = [c.strip() for c in chain_str.split('、')]
            
            # 提取目标估值
            target_match = re.search(r'- 目标估值：(.+?)(?=\n|$)', stock_detail)
            if target_match:
                stock_info['target_valuation'] = target_match.group(1).strip()
        
        stocks.append(stock_info)
    
    return stocks

def update_stocks_master(articles):
    """更新 stocks_master.json"""
    if not MASTER_FILE.exists():
        print(f"❌ 主数据文件不存在：{MASTER_FILE}")
        return
    
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        stocks_master = json.load(f)
    
    updated_count = 0
    
    for article in articles:
        print(f"\n📄 处理文章：{article['title'][:50]}...")
        
        for stock in article['stocks']:
            code = stock['code']
            name = stock['name']
            
            # 确保股票存在
            if code not in stocks_master:
                stocks_master[code] = {
                    'name': name,
                    'code': code,
                    'board': stock['board'],
                    'industry': '',
                    'concepts': [],
                    'products': [],
                    'core_business': [],
                    'industry_position': [],
                    'chain': [],
                    'partners': [],
                    'mention_count': 0,
                    'articles': []
                }
            
            # 更新基本信息
            stocks_master[code]['name'] = name
            stocks_master[code]['board'] = stock['board']
            
            # 更新核心业务
            if stock['core_business']:
                for business in stock['core_business']:
                    if business not in stocks_master[code].get('core_business', []):
                        if 'core_business' not in stocks_master[code]:
                            stocks_master[code]['core_business'] = []
                        stocks_master[code]['core_business'].append(business)
            
            # 更新行业地位
            if stock['industry_position']:
                for position in stock['industry_position']:
                    if position not in stocks_master[code].get('industry_position', []):
                        if 'industry_position' not in stocks_master[code]:
                            stocks_master[code]['industry_position'] = []
                        stocks_master[code]['industry_position'].append(position)
            
            # 更新产业链位置
            if stock['chain']:
                for chain_item in stock['chain']:
                    if chain_item not in stocks_master[code].get('chain', []):
                        if 'chain' not in stocks_master[code]:
                            stocks_master[code]['chain'] = []
                        stocks_master[code]['chain'].append(chain_item)
            
            # 添加文章概念
            if article['concepts']:
                for concept in article['concepts']:
                    if concept not in stocks_master[code].get('concepts', []):
                        if 'concepts' not in stocks_master[code]:
                            stocks_master[code]['concepts'] = []
                        stocks_master[code]['concepts'].append(concept)
            
            # 检查文章是否已存在
            article_exists = False
            for existing_article in stocks_master[code].get('articles', []):
                if (existing_article.get('title') == article['title'] and 
                    existing_article.get('source') == article['source']):
                    article_exists = True
                    # 更新现有文章的目标估值
                    if stock['target_valuation']:
                        if 'target_valuation' not in existing_article:
                            existing_article['target_valuation'] = []
                        if stock['target_valuation'] not in existing_article['target_valuation']:
                            existing_article['target_valuation'].append(stock['target_valuation'])
                    break
            
            if not article_exists:
                # 添加新文章
                new_article = {
                    'title': article['title'],
                    'date': article['date'] or TODAY,
                    'source': article['source'],
                    'accidents': [],
                    'insights': [],
                    'key_metrics': [],
                    'target_valuation': [stock['target_valuation']] if stock['target_valuation'] else [],
                    'content': '',
                    'analysis': '',
                    'summary': ''
                }
                
                if 'articles' not in stocks_master[code]:
                    stocks_master[code]['articles'] = []
                
                stocks_master[code]['articles'].append(new_article)
                stocks_master[code]['mention_count'] = stocks_master[code].get('mention_count', 0) + 1
            
            updated_count += 1
            print(f"  ✅ 更新：{name} ({code})")
            if stock['core_business']:
                print(f"     核心业务：{', '.join(stock['core_business'])}")
            if stock['industry_position']:
                print(f"     行业地位：{', '.join(stock['industry_position'])}")
            if stock['chain']:
                print(f"     产业链位置：{', '.join(stock['chain'])}")
            if stock['target_valuation']:
                print(f"     目标估值：{stock['target_valuation']}")
    
    # 保存更新后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！更新了 {updated_count} 只股票")
    return updated_count

def main():
    print("🚀 开始处理标准化 raw_material 文件，提取完整信息...\n")
    
    # 解析 raw_material 文件
    articles = parse_standard_raw_material(RAW_MATERIAL_FILE)
    
    if not articles:
        print("❌ 未找到任何文章")
        return
    
    print(f"📚 共找到 {len(articles)} 篇文章\n")
    
    # 更新 stocks_master.json
    update_stocks_master(articles)
    
    print("\n🎉 处理完成！")

if __name__ == '__main__':
    main()
