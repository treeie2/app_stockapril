#!/usr/bin/env python3
"""
从今天生成的标准化 raw_material 文件中提取个股信息并更新到 stocks_master.json
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
        'stocks': []
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
    
    return article

def extract_stocks_from_section(section):
    """从文章部分提取个股信息"""
    stocks = []
    
    # 查找个股部分
    stocks_section_match = re.search(r'### 涉及个股\n(.*?)(?=\n### |\Z)', section, re.DOTALL)
    if not stocks_section_match:
        return stocks
    
    stocks_content = stocks_section_match.group(1)
    
    # 匹配个股条目：1. **股票名称** (代码.交易所)
    stock_pattern = r'\d+\. \*\*([^*]+)\*\* \((\d{6})\.(SZ|SH)\)'
    matches = re.findall(stock_pattern, stocks_content)
    
    for match in matches:
        name, code, board = match
        stock_info = {
            'name': name.strip(),
            'code': code,
            'board': board,
            'core_layout': '',
            'latest_progress': '',
            'target_valuation': ''
        }
        
        # 查找该股票的详细信息（从当前行到下一个股票条目）
        stock_start = stocks_content.find(match[0])
        if stock_start != -1:
            # 找到下一个股票条目的位置
            next_stock = re.search(r'\n\d+\. \*\*', stocks_content[stock_start + len(match[0]):])
            if next_stock:
                stock_detail = stocks_content[stock_start:stock_start + len(match[0]) + next_stock.start()]
            else:
                stock_detail = stocks_content[stock_start:]
            
            # 提取核心布局
            layout_match = re.search(r'- 核心布局：(.+?)(?=\n|$)', stock_detail)
            if layout_match:
                stock_info['core_layout'] = layout_match.group(1).strip()
            
            # 提取最新进展
            progress_match = re.search(r'- 最新进展：(.+?)(?=\n|$)', stock_detail)
            if progress_match:
                stock_info['latest_progress'] = progress_match.group(1).strip()
            
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
            
            # 检查文章是否已存在
            article_exists = False
            for existing_article in stocks_master[code].get('articles', []):
                if (existing_article.get('title') == article['title'] and 
                    existing_article.get('source') == article['source']):
                    article_exists = True
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
                    'content': f"{stock['core_layout']}\n{stock['latest_progress']}".strip(),
                    'analysis': '',
                    'summary': ''
                }
                
                if 'articles' not in stocks_master[code]:
                    stocks_master[code]['articles'] = []
                
                stocks_master[code]['articles'].append(new_article)
                stocks_master[code]['mention_count'] = stocks_master[code].get('mention_count', 0) + 1
                updated_count += 1
                
                print(f"  ✅ 更新：{name} ({code})")
    
    # 保存更新后的数据
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(stocks_master, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！更新了 {updated_count} 只股票")
    return updated_count

def main():
    print("🚀 开始处理标准化 raw_material 文件...\n")
    
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
