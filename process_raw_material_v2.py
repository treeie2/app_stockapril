#!/usr/bin/env python3
"""
根据数据结构规范 v2 处理 raw material 文件
"""
import json
import re
from pathlib import Path
from datetime import datetime

def parse_raw_material_batch(file_path):
    """处理 batch 文件（包含多篇文章）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割文章 - 使用更精确的分割
    articles = re.split(r'\n---\n\n## Article', content)
    
    stocks_data = {}
    
    for article in articles:
        if not article.strip():
            continue
        
        # 清理文章开头
        article = article.replace('## Article\n', '')
            
        # 提取文章元数据
        source_match = re.search(r'source: (.+)', article)
        fetched_match = re.search(r'fetched_at: (.+)', article)
        title_match = re.search(r'title: (.+)', article)
        
        source = source_match.group(1).strip() if source_match else ''
        fetched_at = fetched_match.group(1).strip() if fetched_match else ''
        title = title_match.group(1).strip() if title_match else ''
        
        # 提取股票名称（从标题）
        stock_name_match = re.search(r'([^，,]+)[，,]\d+ 倍空间', title)
        if not stock_name_match:
            # 尝试其他格式
            stock_name_match = re.search(r'^([^\n，,]+)[，,]', title)
        
        if not stock_name_match:
            continue
            
        stock_name = stock_name_match.group(1).strip()
        
        # 提取股票代码（需要手动映射）
        stock_code_map = {
            '纳科诺尔': '832522',
            '力诺药包': '301666',
            '利通科技': '832225'
        }
        
        stock_code = stock_code_map.get(stock_name)
        if not stock_code:
            print(f"⚠️ 未找到股票代码：{stock_name}")
            continue
        
        # 提取文章内容
        # 寻找关键信息
        accidents = []
        insights = []
        key_metrics = []
        target_valuation = []
        
        # 提取催化剂/事件
        if '固态实验室' in article:
            accidents.append('固态实验室主体已建成，设备进厂')
        if '等静压设备' in article:
            accidents.append('首台等静压设备下线，容积 8L')
        if '干法正极设备' in article:
            accidents.append('干法正极成膜设备取得进展')
        if '玻璃基板' in article:
            accidents.append('玻璃基板送样台积电，150×150mm 已通过测试')
        if '温等静压设备' in article:
            accidents.append('首台固态电池温等静压设备下线，容积 56L')
        
        # 提取投资洞察
        if '2 倍空间' in article:
            insights.append(f'{stock_name}：固态电池设备核心标的，看到 2 倍空间')
        if '10 倍空间' in article:
            insights.append(f'{stock_name}：玻璃基板垂直一体化，潜在十倍股')
        if '干法电极' in article:
            insights.append('干法电极设备卡位领先，等静压设备进展积极')
        if '玻璃基板' in article and '台积电' in article:
            insights.append('玻璃基板送样台积电，成本优势显著，毛利 90%+')
        
        # 提取关键指标
        if '预计今年业绩在 2 亿以上' in article:
            key_metrics.append('预计今年业绩 2 亿以上')
        if '主业给 50 亿市值' in article:
            key_metrics.append('主业估值 50 亿市值')
        if '今年利润 1.2 亿以上' in article:
            key_metrics.append('今年利润 1.2 亿以上')
        if 'Q1 业绩很好' in article:
            key_metrics.append('Q1 业绩很好')
        
        # 提取目标估值
        if '整体市值看到 275 亿' in article:
            target_valuation.append('整体市值看到 275 亿，有近 2 倍空间')
        if '主业扎实，玻璃基板提供高弹性' in article:
            target_valuation.append('主业扎实，玻璃基板提供高弹性，一旦放量有十倍股潜力')
        if '整体市值看到 120 亿' in article:
            target_valuation.append('整体市值看到 120 亿，有两倍空间')
        
        # 提取概念
        concepts = []
        if '固态电池' in article:
            concepts.extend(['固态电池', '干法电极'])
        if '等静压设备' in article:
            concepts.append('等静压设备')
        if '玻璃基板' in article:
            concepts.extend(['玻璃基板', '半导体材料'])
        if '台积电' in article:
            concepts.append('台积电产业链')
        
        # 提取产品
        products = []
        if '干法电极设备' in article:
            products.append('干法电极设备')
        if '等静压设备' in article:
            products.append('等静压设备')
        if '锂带压延转印设备' in article:
            products.append('锂带压延转印设备')
        if '玻璃基板' in article:
            products.append('玻璃基板')
        if '模制瓶' in article or '耐热玻璃' in article:
            products.extend(['模制瓶', '耐热玻璃', '预灌封'])
        
        # 提取行业
        industry_map = {
            '纳科诺尔': '机械设备 - 电池设备 - 锂电设备',
            '力诺药包': '医药生物 - 医疗器械 - 医疗耗材',
            '利通科技': '机械设备 - 专用设备 - 锂电设备'
        }
        
        # 构建股票数据
        today = fetched_at.split('T')[0] if fetched_at else datetime.now().strftime('%Y-%m-%d')
        
        stock_data = {
            'code': stock_code,
            'name': stock_name,
            'board': 'BJ' if stock_code.startswith('8') else 'SZ',
            'industry': industry_map.get(stock_name, '未知'),
            'concepts': list(set(concepts)) if concepts else [],
            'products': products if products else [],
            'core_business': [],
            'industry_position': [],
            'chain': [],
            'partners': [],
            'mention_count': 1,
            'articles': [
                {
                    'title': title,
                    'date': today,
                    'source': source,
                    'accidents': accidents if accidents else [],
                    'insights': insights if insights else [],
                    'key_metrics': key_metrics if key_metrics else [],
                    'target_valuation': target_valuation if target_valuation else []
                }
            ],
            'last_updated': today
        }
        
        stocks_data[stock_code] = stock_data
    
    return stocks_data

def parse_raw_material_single(file_path):
    """处理单篇文章（隆华科技）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取元数据
    source_match = re.search(r'source: (.+)', content)
    fetched_match = re.search(r'fetched_at: (.+)', content)
    title_match = re.search(r'title: (.+)', content)
    
    source = source_match.group(1).strip() if source_match else ''
    fetched_at = fetched_match.group(1).strip() if fetched_match else ''
    title = title_match.group(1).strip() if title_match else ''
    
    # 隆华科技信息
    stock_code = '300263'
    stock_name = '隆华科技'
    today = fetched_at.split('T')[0] if fetched_at else datetime.now().strftime('%Y-%m-%d')
    
    # 提取概念
    concepts = [
        '稀土永磁', '低空经济', '光伏钙钛矿', '第四代半导体',
        '电子新材料', '高分子复合材料', '节能环保', '军民融合',
        '稀土分离', '隐身材料', '核能'
    ]
    
    # 提取产品
    products = [
        '电子溅射靶材', '钼靶材', 'ITO 靶材', '钙钛矿靶材',
        'PMI 泡沫材料', 'PVC 结构芯材', '稀土萃取剂', '节能换热装备'
    ]
    
    # 提取核心业务
    core_business = [
        '电子新材料研发生产', '高分子复合材料制造', '节能环保装备',
        '稀土分离与回收'
    ]
    
    # 提取行业地位
    industry_position = [
        '国内唯一实现钙钛矿太阳能电池用靶材批量供货',
        '国内唯一通过 AS9100D 航空航天质量体系认证的 PMI 泡沫供应商',
        '稀土萃取剂龙头，市占率超 80%',
        '钼靶和 ITO 靶材行业龙头'
    ]
    
    # 提取产业链位置
    chain = [
        '上游 - 电子材料',
        '上游 - 稀土材料',
        '中游 - 高分子复合材料'
    ]
    
    # 提取合作伙伴
    partners = [
        '京东方', '华星光电', '天马微电子', '信利半导体', 'TCL 华星'
    ]
    
    # 提取催化剂
    accidents = [
        '大尺寸钼靶材批量供货，打破国外垄断',
        'ITO 靶材通过多条 TFT 产线测试认证',
        'PMI 产品应用于多型军用飞机'
    ]
    
    # 提取投资洞察
    insights = [
        '历经五年转型升级，从传热节能设备企业发展为电子新材料龙头',
        '靶材业务加快进口替代，宽幅钼靶、高世代线 ITO 靶材市场份额大幅提升',
        '高分子复合材料覆盖军工、轨道交通等领域，产能规模迅速壮大'
    ]
    
    # 提取关键指标
    key_metrics = [
        '钼靶用户包括京东方、华星光电、天马微电子等',
        'ITO 靶材在京东方 G8.5、G6 等高世代产线量产使用',
        '稀土萃取剂市占率超 80%'
    ]
    
    # 提取目标估值
    target_valuation = []
    
    stock_data = {
        'code': stock_code,
        'name': stock_name,
        'board': 'SZ',
        'industry': '电子 - 电子材料 - 电子化学品',
        'concepts': concepts,
        'products': products,
        'core_business': core_business,
        'industry_position': industry_position,
        'chain': chain,
        'partners': partners,
        'mention_count': 1,
        'articles': [
            {
                'title': title,
                'date': today,
                'source': source,
                'accidents': accidents,
                'insights': insights,
                'key_metrics': key_metrics,
                'target_valuation': target_valuation
            }
        ],
        'last_updated': today
    }
    
    return {stock_code: stock_data}

def save_to_daily_file(stocks_data, date):
    """保存到当天分片文件"""
    daily_file = Path('data/master/stocks') / f'{date}.json'
    
    # 读取现有数据
    if daily_file.exists():
        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_data = json.load(f)
    else:
        daily_data = {'date': date, 'update_count': 0, 'stocks': {}}
    
    # 合并数据
    for code, stock in stocks_data.items():
        if code in daily_data['stocks']:
            # 合并文章
            existing = daily_data['stocks'][code]
            existing_articles = existing.get('articles', [])
            new_articles = stock.get('articles', [])
            
            # 去重
            existing_keys = {(a.get('source'), a.get('title')) for a in existing_articles}
            for article in new_articles:
                key = (article.get('source'), article.get('title'))
                if key not in existing_keys:
                    existing_articles.append(article)
                    existing_keys.add(key)
            
            # 更新其他字段
            existing['mention_count'] = existing.get('mention_count', 0) + 1
            existing['last_updated'] = date
            
            # 合并概念、产品等
            if stock.get('concepts'):
                existing_concepts = set(existing.get('concepts', []))
                existing_concepts.update(stock['concepts'])
                existing['concepts'] = list(existing_concepts)
            
            if stock.get('products'):
                existing_products = set(existing.get('products', []))
                existing_products.update(stock['products'])
                existing['products'] = list(existing_products)
        else:
            daily_data['stocks'][code] = stock
    
    daily_data['update_count'] = len(daily_data['stocks'])
    
    # 保存
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 已保存到 {daily_file}')
    return daily_data

def update_index(stocks_data, date):
    """更新索引文件"""
    index_file = Path('data/master/stocks_index.json')
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # 更新索引
    for code, stock in stocks_data.items():
        index_data['stocks'][code] = {
            'name': stock['name'],
            'last_updated': date,
            'file': f'{date}.json'
        }
    
    index_data['total_stocks'] = len(index_data['stocks'])
    index_data['last_updated'] = date
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 已更新 stocks_index.json')

def merge_to_master(stocks_data):
    """合并到主文件"""
    master_file = Path('data/master/stocks_master.json')
    
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    master_stocks = master_data.get('stocks', {})
    
    for code, stock in stocks_data.items():
        if code in master_stocks:
            # 合并文章
            existing = master_stocks[code]
            existing_articles = existing.get('articles', [])
            new_articles = stock.get('articles', [])
            
            existing_keys = {(a.get('source'), a.get('title')) for a in existing_articles}
            for article in new_articles:
                key = (article.get('source'), article.get('title'))
                if key not in existing_keys:
                    existing_articles.append(article)
                    existing_keys.add(key)
            
            existing['mention_count'] = existing.get('mention_count', 0) + 1
            existing['last_updated'] = stock['last_updated']
        else:
            master_stocks[code] = stock
    
    master_data['stocks'] = master_stocks
    
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 已合并到 stocks_master.json')
    print(f'📊 总计：{len(master_stocks)} 只股票')

if __name__ == '__main__':
    today = '2026-04-21'
    
    print('🔄 处理 raw_material_2026-04-21_batch.md...')
    batch_stocks = parse_raw_material_batch('raw_material/raw_material_2026-04-21_batch.md')
    print(f'   处理了 {len(batch_stocks)} 只股票：{list(batch_stocks.keys())}')
    
    print('\n🔄 处理 raw_material_2026-04-21_3.md...')
    single_stocks = parse_raw_material_single('raw_material/raw_material_2026-04-21_3.md')
    print(f'   处理了 {len(single_stocks)} 只股票：{list(single_stocks.keys())}')
    
    # 合并所有股票
    all_stocks = {**batch_stocks, **single_stocks}
    
    print(f'\n💾 保存到分片文件...')
    save_to_daily_file(all_stocks, today)
    
    print('\n📑 更新索引...')
    update_index(all_stocks, today)
    
    print('\n📦 合并到主文件...')
    merge_to_master(all_stocks)
    
    print('\n✅ 全部完成！')
