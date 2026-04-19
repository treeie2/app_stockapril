#!/usr/bin/env python3
"""
从 raw material 文件中提取重要字段
提取：products、core_business、industry_position、chain、partners、target_valuation
"""
import json
import re
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
RAW_MATERIAL_DIR = Path("e:/github/stock-research-backup/archived/docs/raw_material")


def extract_target_valuation(content):
    """提取目标估值"""
    patterns = [
        r'目标市值[:：]\s*(\d+)\s*亿',
        r'目标[:：]\s*(\d+)\s*亿',
        r'市值[:：]\s*(\d+)\s*亿',
        r'目标价[:：]\s*(\d+)',
        r'目标市值可看(\d+)e',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return f"{match.group(1)}亿"
    return None


def extract_products(content):
    """提取产品信息"""
    products = []
    
    # 产品关键词模式
    patterns = [
        r'产品[:：]([^。\n]+)',
        r'主营[:：]([^。\n]+)',
        r'业务[:：]([^。\n]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # 分割多个产品
            items = re.split(r'[、,，;；]', match)
            for item in items:
                item = item.strip()
                if item and len(item) > 1 and len(item) < 20:
                    products.append(item)
    
    return list(set(products))[:10]  # 去重，最多10个


def extract_core_business(content):
    """提取核心业务"""
    business = []
    
    # 寻找核心业务描述
    patterns = [
        r'核心[:：]([^。\n]+)',
        r'主业[:：]([^。\n]+)',
        r'主要从事([^。]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        business.extend([m.strip() for m in matches if len(m.strip()) > 2])
    
    return business[:5]


def extract_industry_position(content):
    """提取行业地位"""
    positions = []
    
    # 行业地位关键词
    keywords = ['龙头', '第一', '第二', '第三', '领先', '唯一', '核心', '龙头', '领军', '标杆']
    
    lines = content.split('\n')
    for line in lines:
        for keyword in keywords:
            if keyword in line and len(line) < 100:
                # 提取包含关键词的句子
                match = re.search(r'[^。]*' + keyword + r'[^。]*', line)
                if match:
                    pos = match.group(0).strip()
                    if pos and len(pos) > 5:
                        positions.append(pos)
    
    return list(set(positions))[:5]


def extract_chain(content):
    """提取产业链信息"""
    chains = []
    
    # 产业链关键词
    if '产业链' in content:
        matches = re.findall(r'([^。\n]{2,10}产业链)', content)
        chains.extend([m for m in matches if len(m) < 15])
    
    # 上下游
    if '上游' in content or '下游' in content:
        matches = re.findall(r'([^。\n]{2,15}(?:上游|下游)[^。\n]{0,10})', content)
        chains.extend([m.strip() for m in matches if len(m.strip()) > 2])
    
    return list(set(chains))[:5]


def extract_partners(content):
    """提取合作伙伴/客户"""
    partners = []
    
    # 客户/合作伙伴关键词
    patterns = [
        r'客户[:：]([^。\n]+)',
        r'合作伙伴[:：]([^。\n]+)',
        r'已进入([^，。]+)',
        r'与([^，。]{2,10})合作',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # 分割多个合作伙伴
            items = re.split(r'[、,，;；]', match)
            for item in items:
                item = item.strip()
                if item and len(item) > 1 and len(item) < 15:
                    partners.append(item)
    
    return list(set(partners))[:8]


def extract_stock_info_from_content(content, stock_name):
    """从内容中提取股票信息"""
    info = {
        'products': extract_products(content),
        'core_business': extract_core_business(content),
        'industry_position': extract_industry_position(content),
        'chain': extract_chain(content),
        'partners': extract_partners(content),
        'target_valuation': extract_target_valuation(content)
    }
    
    return info


def process_raw_materials():
    """处理所有原材料文件"""
    print("🚀 从原材料文件中提取字段...\n")
    
    # 读取现有数据
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stocks = data.get('stocks', {})
    if isinstance(stocks, list):
        stocks = {s['code']: s for s in stocks}
    
    # 获取所有原材料文件
    raw_files = sorted(RAW_MATERIAL_DIR.glob("*.md"))
    print(f"📁 找到 {len(raw_files)} 个原材料文件\n")
    
    updated_count = 0
    
    for raw_file in raw_files:
        print(f"📄 处理: {raw_file.name}")
        
        with open(raw_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 从文件名提取日期
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', raw_file.name)
        file_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        # 查找股票代码和名称
        stock_pattern = r'###\s*([^\n(]+)\s*\((\d{6})\)'
        matches = list(re.finditer(stock_pattern, content))
        
        print(f"   找到 {len(matches)} 只个股")
        
        for match in matches:
            name = match.group(1).strip()
            code = match.group(2)
            
            if code not in stocks:
                continue
            
            # 获取该股票周围的文本
            start = match.end()
            end = min(len(content), start + 1500)
            # 找到下一个 ### 或文件结束
            next_match = content.find('###', start)
            if next_match > 0 and next_match < end:
                end = next_match
            
            stock_content = content[start:end]
            
            # 提取信息
            info = extract_stock_info_from_content(stock_content, name)
            
            # 更新股票数据
            stock = stocks[code]
            updated = False
            
            # 只更新空字段
            for field, value in info.items():
                if field == 'target_valuation':
                    # 更新到文章的 target_valuation
                    if value and 'articles' in stock and stock['articles']:
                        for article in stock['articles']:
                            if not article.get('target_valuation'):
                                article['target_valuation'] = [value]
                                updated = True
                else:
                    # 更新股票字段
                    current = stock.get(field, [])
                    if not current and value:
                        stock[field] = value
                        updated = True
                    elif current and value:
                        # 合并去重
                        combined = list(set(current + value))
                        if len(combined) > len(current):
                            stock[field] = combined
                            updated = True
            
            if updated:
                updated_count += 1
                print(f"   📝 更新: {name}({code})")
    
    # 保存数据
    data['stocks'] = stocks
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"✅ 处理完成!")
    print(f"   更新股票: {updated_count} 只")
    print(f"   数据库总股票数: {len(stocks)}")


if __name__ == "__main__":
    process_raw_materials()
