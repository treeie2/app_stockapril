#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的数据处理流程脚本
从微信文章链接到最终合并到 stocks_master.json
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_stock_mappings():
    """加载股票映射数据"""
    base_dir = Path(__file__).parent
    
    # 加载基础股票列表
    stock_xls = pd.read_excel(base_dir / '.trae/skills/wechat-fetch-research-embedded/assets/全部个股.xls')
    stock_map = {}
    for _, row in stock_xls.iterrows():
        code = str(row['股票代码']).split('.')[0]
        stock_map[code] = row['股票简称']
    
    # 加载行业映射
    industry_df = pd.read_excel(base_dir / 'archived/同花顺行业.xls')
    industry_map = {}
    for _, row in industry_df.iterrows():
        code = str(row['股票代码']).split('.')[0]
        industry_map[code] = row['所属同花顺行业']
    
    # 加载概念映射
    concept_df = pd.read_excel(base_dir / 'archived/所属概念.xls')
    concept_map = {}
    for _, row in concept_df.iterrows():
        code = str(row['股票代码']).split('.')[0]
        concepts = str(row['所属概念']).split(';') if pd.notna(row['所属概念']) else []
        concepts = [c.strip() for c in concepts if c.strip()]
        concept_map[code] = concepts
    
    print(f"✅ 加载股票映射：{len(stock_map)} 只")
    print(f"✅ 加载行业映射：{len(industry_map)} 只")
    print(f"✅ 加载概念映射：{len(concept_map)} 只")
    
    return stock_map, industry_map, concept_map

def create_daily_json(stock_code, stock_info, article_data, output_path):
    """创建日期分片 JSON 文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    daily_data = {
        'date': today,
        'update_count': 1,
        'last_updated': datetime.now().astimezone().isoformat(timespec='seconds'),
        'stocks': {
            stock_code: stock_info
        }
    }
    
    # 确保文章信息正确
    if 'articles' in stock_info:
        for article in stock_info['articles']:
            article.setdefault('date', today)
    
    # 保存
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建日期分片：{output_path}")
    return daily_data

def merge_to_master(daily_json_path, master_json_path):
    """合并日期分片到主数据"""
    # 读取主数据
    with open(master_json_path, 'r', encoding='utf-8') as f:
        master = json.load(f)
    
    # 读取今日数据
    with open(daily_json_path, 'r', encoding='utf-8') as f:
        daily = json.load(f)
    
    merged_count = 0
    for code, stock_data in daily['stocks'].items():
        if code in master['stocks']:
            existing = master['stocks'][code]
            
            # 追加文章（去重）
            titles = [(a['title'], a['source']) for a in existing.get('articles', [])]
            for article in stock_data.get('articles', []):
                if (article['title'], article['source']) not in titles:
                    existing.setdefault('articles', []).append(article)
            
            # 更新计数
            existing['mention_count'] = len(existing['articles'])
            existing['last_updated'] = daily['date']
            
            # 合并产品、概念和个股数据
            if stock_data.get('products'):
                existing_products = set(existing.get('products', []))
                existing_products.update(stock_data['products'])
                existing['products'] = list(existing_products)

            if stock_data.get('concepts'):
                existing_concepts = set(existing.get('concepts', []))
                existing_concepts.update(stock_data['concepts'])
                existing['concepts'] = list(existing_concepts)

            if stock_data.get('core_business'):
                existing_core = set(existing.get('core_business', []))
                existing_core.update(stock_data['core_business'])
                existing['core_business'] = list(existing_core)

            if stock_data.get('industry_position'):
                existing_pos = set(existing.get('industry_position', []))
                existing_pos.update(stock_data['industry_position'])
                existing['industry_position'] = list(existing_pos)

            if stock_data.get('chain'):
                existing_chain = set(existing.get('chain', []))
                existing_chain.update(stock_data['chain'])
                existing['chain'] = list(existing_chain)

            if stock_data.get('partners'):
                existing_partners = set(existing.get('partners', []))
                existing_partners.update(stock_data['partners'])
                existing['partners'] = list(existing_partners)
            
            merged_count += 1
            print(f"✅ 合并 {code} {stock_data['name']}，提及次数：{existing['mention_count']}")
        else:
            # 新股票，直接添加
            master['stocks'][code] = stock_data
            merged_count += 1
            print(f"✅ 新增 {code} {stock_data['name']}")
    
    # 更新时间
    master['last_updated'] = daily['last_updated']
    
    # 保存
    with open(master_json_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 合并完成：{merged_count} 只股票")
    return merged_count

def process_article(url, article_content, stock_code, structured_data):
    """
    处理单篇文章的完整流程

    Args:
        url: 微信文章链接
        article_content: 文章内容文本
        stock_code: 股票代码（6 位数字）
        structured_data: 结构化数据字典，包含：
            - accidents: 催化剂/事件列表
            - insights: 投资洞察列表
            - key_metrics: 关键指标列表
            - target_valuation: 目标估值列表
            - core_business: 核心业务/主要产品列表
            - industry_position: 行业地位/竞争优势列表
            - chain: 产业链位置列表
            - partners: 合作伙伴公司名称列表
    """
    stock_map, industry_map, concept_map = load_stock_mappings()

    if stock_code not in stock_map:
        raise ValueError(f"未找到股票代码 {stock_code}")

    stock_name = stock_map[stock_code]
    industry = industry_map.get(stock_code, '其他')
    concepts = concept_map.get(stock_code, [])

    today = datetime.now().strftime('%Y-%m-%d')
    stock_info = {
        'name': stock_name,
        'code': stock_code,
        'board': 'SH' if stock_code.startswith('6') or stock_code.startswith('9') else 'SZ',
        'industry': industry,
        'concepts': concepts,
        'products': [],
        'core_business': structured_data.get('core_business', []),
        'industry_position': structured_data.get('industry_position', []),
        'chain': structured_data.get('chain', []),
        'partners': structured_data.get('partners', []),
        'mention_count': 1,
        'last_updated': today,
        'articles': [
            {
                'title': f'今天的一些信息整理 {today[5:7]}.{today[8:10]}',
                'date': today,
                'source': url,
                'accidents': structured_data.get('accidents', []),
                'insights': structured_data.get('insights', []),
                'key_metrics': structured_data.get('key_metrics', []),
                'target_valuation': structured_data.get('target_valuation', [])
            }
        ]
    }
    
    # 创建日期分片
    daily_path = f'data/stocks/{today}.json'
    create_daily_json(stock_code, stock_info, None, daily_path)
    
    # 合并到主数据
    master_path = 'data/stocks/stocks_master.json'
    merge_to_master(daily_path, master_path)
    
    print(f"\n✨ 处理完成！")
    print(f"📄 文章：{url}")
    print(f"📊 股票：{stock_code} {stock_name}")
    print(f"📁 分片：{daily_path}")
    print(f"📚 主数据：{master_path}")

# 使用示例
if __name__ == '__main__':
    # 示例：处理中国长城的文章
    process_article(
        url='https://mp.weixin.qq.com/s/hEu1t-SMbV1o-wWArekESg',
        article_content='...',  # 文章内容
        stock_code='000066',
        structured_data={
            'accidents': [
                '2025 年营收 158.09 亿元，同比 +11.31%',
                '推出新一代 8U OAM AI 服务器 GF7290 V5'
            ],
            'insights': [
                '国海计算机认为中国长城能看到翻倍空间',
                '亏损持续收窄，业务结构优化'
            ],
            'key_metrics': [
                '2025 年营收 158.09 亿元，同比 +11.31%',
                '飞腾信息持股比例 28.035%'
            ],
            'target_valuation': [
                '目标市值：先看翻倍 1000 亿元'
            ],
            'core_business': [
                '通用服务器、AI 服务器研发生产',
                '飞腾 CPU 应用',
                '服务器电源'
            ],
            'industry_position': [
                '国产服务器龙头',
                '飞腾信息是国内 Top 级 CPU 厂商',
                '服务器电源市场占有率国内第一、国际前三'
            ],
            'chain': [
                '中游-服务器制造',
                '上游-芯片设计（通过子公司飞腾信息）'
            ],
            'partners': [
                '飞腾信息',
                '华为',
                '海光信息'
            ]
        }
    )
