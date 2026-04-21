#!/usr/bin/env python3
"""
从 raw_material 文件中提取个股信息并更新到 stocks_master.json
"""
import json
import re
from pathlib import Path
from datetime import datetime
import sys

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent / '.trae' / 'skills' / 'wechat-fetch-research-embedded' / 'scripts'))

RAW_MATERIAL_FILE = Path("e:/github/stock-research-backup/raw_material/raw_material_2026-04-21__1.md")
RAW_MATERIAL_FILE2 = Path("e:/github/stock-research-backup/raw_material/raw_material_2026-04-21__2.md")
MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
TODAY = datetime.now().strftime('%Y-%m-%d')

# 股票名称到代码的映射（从全部个股.xls 中提取的部分）
STOCK_NAME_TO_CODE = {
    '锡业股份': '000960',
    '株冶集团': '600961',
    '豫光金铅': '600531',
    '云南锗业': '002428',
    '博杰股份': '002975',
    '有研新材': '600206',
    '三安光电': '600703',
    '源杰科技': '688498',
    '永鼎股份': '600105',
    '光迅科技': '002281',
    '仕佳光子': '688313',
    '长光华芯': '688048',
    '华工科技': '000988',
    '中际旭创': '300308',
    '新易盛': '300502',
    '天孚通信': '300394',
}

def parse_raw_material(file_path):
    """解析 raw material 文件"""
    if not file_path.exists():
        print(f"❌ 文件不存在：{file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割文章
    articles = []
    article_blocks = re.split(r'## Article\n', content)
    
    for block in article_blocks[1:]:  # 跳过第一个空块
        article = parse_article_block(block)
        if article:
            articles.append(article)
    
    return articles

def parse_article_block(block):
    """解析单个文章块"""
    lines = block.strip().split('\n')
    
    article = {
        'source': '',
        'fetched_at': '',
        'title': '',
        'date': '',
        'content': ''
    }
    
    content_start = False
    content_lines = []
    
    for line in lines:
        if not content_start:
            if line.startswith('source:'):
                article['source'] = line.replace('source:', '').strip()
            elif line.startswith('fetched_at:'):
                article['fetched_at'] = line.replace('fetched_at:', '').strip()
            elif line.startswith('title:'):
                article['title'] = line.replace('title:', '').strip()
            elif line.startswith('date:'):
                article['date'] = line.replace('date:', '').strip()
            else:
                content_start = True
                content_lines.append(line)
        else:
            content_lines.append(line)
    
    article['content'] = '\n'.join(content_lines)
    return article

def extract_stocks_from_article(article):
    """从文章中提取个股信息"""
    content = article['content']
    stocks = []
    
    # 查找股票名称和代码模式
    pattern = r'([^\s(（]+)（(\d{6})）'
    matches = re.findall(pattern, content)
    
    for name, code in matches:
        # 清理名称
        name = name.strip()
        if len(name) >= 2 and len(name) <= 6:
            stocks.append({
                'name': name,
                'code': code,
                'content': extract_stock_content(content, name)
            })
    
    return stocks

def extract_stock_content(full_content, stock_name):
    """提取特定股票的相关内容"""
    # 查找股票名称出现的位置
    pattern = re.escape(stock_name) + r'[（(]?\d{6}[)）]?.*?(?=\n[0-9A-Z]|##|$)'
    matches = re.findall(pattern, full_content, re.DOTALL)
    
    if matches:
        # 返回最相关的一段
        return matches[0][:2000]  # 限制长度
    return ""

def extract_fields(content):
    """从内容中提取字段"""
    fields = {}
    
    # 提取核心业务
    if '核心业务' in content or '主营' in content:
        match = re.search(r'(?:核心业务 | 主营)[:：]([^\n]+)', content)
        if match:
            fields['core_business'] = [match.group(1).strip()]
    
    # 提取行业地位
    if '龙头' in content or '领先' in content or '第一' in content:
        match = re.search(r'([^\n]*(?:龙头 | 领先 | 第一)[^\n]*)', content)
        if match:
            fields['industry_position'] = [match.group(1).strip()[:200]]
    
    # 提取产品
    if '产品' in content:
        match = re.search(r'产品 [^\n]*(?:包括 | 为 | 是)?[:：]?([^\n]+)', content)
        if match:
            fields['products'] = [match.group(1).strip()[:200]]
    
    # 提取目标估值
    match = re.search(r'目标市值 [^\n]*(?:为 | 达 | 看)[:：]?\s*(\d+(?:\.\d+)?)\s*亿', content)
    if match:
        fields['target_valuation'] = [f"目标市值：{match.group(1)}亿"]
    
    return fields

def update_stocks_master(articles):
    """更新 stocks_master.json"""
    # 读取现有数据
    if MASTER_FILE.exists():
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
    else:
        master_data = {'stocks': {}}
    
    stocks = master_data.get('stocks', {})
    updated_count = 0
    
    for article in articles:
        print(f"\n📄 处理文章：{article['title'][:50]}...")
        
        # 提取个股
        stock_mentions = extract_stocks_from_article(article)
        
        for stock_info in stock_mentions:
            code = stock_info['code']
            name = stock_info['name']
            
            print(f"  📈 找到股票：{name} ({code})")
            
            # 提取字段
            fields = extract_fields(stock_info['content'])
            
            # 创建或更新股票记录
            if code not in stocks:
                stocks[code] = {
                    'name': name,
                    'articles': [],
                    'mention_count': 0
                }
            
            # 确保 articles 字段存在
            if 'articles' not in stocks[code]:
                stocks[code]['articles'] = []
            
            # 创建文章记录
            article_record = {
                'source': article['source'],
                'title': article['title'],
                'date': article['date'] or TODAY,
                'fetched_at': article['fetched_at']
            }
            
            # 添加提取的字段
            article_record.update(fields)
            
            # 检查文章是否已存在（去重）
            existing = False
            for existing_article in stocks[code]['articles']:
                if existing_article.get('source') == article['source']:
                    existing = True
                    break
            
            if not existing:
                stocks[code]['articles'].append(article_record)
                stocks[code]['mention_count'] = stocks[code].get('mention_count', 0) + 1
                updated_count += 1
                
                print(f"    ✅ 添加文章记录")
                if fields:
                    print(f"    📊 提取字段：{list(fields.keys())}")
            else:
                print(f"    ⏭️  文章已存在，跳过")
    
    # 保存回文件
    master_data['stocks'] = stocks
    
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！更新了 {updated_count} 只股票")
    return updated_count

def main():
    print("🚀 开始处理 raw_material 文件...\n")
    
    # 解析文章
    articles = []
    for file_path in [RAW_MATERIAL_FILE, RAW_MATERIAL_FILE2]:
        if file_path.exists():
            parsed = parse_raw_material(file_path)
            articles.extend(parsed)
            print(f"✅ 解析文件：{file_path.name} - {len(parsed)} 篇文章")
    
    print(f"\n📚 共找到 {len(articles)} 篇文章")
    
    # 更新 stocks_master.json
    if articles:
        update_stocks_master(articles)
    
    print("\n🎉 处理完成！")

if __name__ == '__main__':
    main()
