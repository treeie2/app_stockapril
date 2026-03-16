#!/usr/bin/env python3
"""
从 company_mentions.json 生成 search_index_full.json.gz
用于 Railway 前端展示
"""
import json
import gzip
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / 'data' / 'sentiment'
MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
SENTIMENT_FILE = DATA_DIR / 'company_mentions.json'
OUTPUT_FILE = DATA_DIR / 'search_index_full.json.gz'

def clean_text(text: str) -> str:
    """清理文本中的 Markdown/HTML 格式"""
    if not text:
        return ""
    
    import re
    # 移除 [cite: x, y] 引用标记
    text = re.sub(r'\[cite:\s*\d+(?:,\s*\d+)*\]', '', text)
    # 移除 Markdown 链接 [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # 移除图片链接
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    # 移除裸 URL
    text = re.sub(r'https?://[^\s\]\)]+', '', text)
    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 移除多余空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    print("=" * 70)
    print("📊 生成 Railway 搜索索引")
    print("=" * 70)
    
    # 1. 加载股票主数据
    print("\n📄 加载 stocks_master.json")
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    stocks_dict = {}
    for stock in master_data.get('stocks', []):
        code = stock['code']
        llm = stock.get('llm_summary', {})
        stocks_dict[code] = {
            'name': stock['name'],
            'board': stock.get('market', ''),
            'mention_count': stock.get('mention_count', 0),
            'concepts': stock.get('concept_tags', []),
            'industries': [stock.get('industry_sw', ''), stock.get('industry_citic', '')],
            'products': llm.get('products', []),
            'core_business': clean_text(llm.get('core_business', '')),
            'industry_position': clean_text(llm.get('industry_position', '')),
            'partners': llm.get('partners', []),
            'accident': clean_text(llm.get('accident', '')),
            'articles': []
        }
    
    print(f"  ✅ 加载 {len(stocks_dict)} 只股票")
    
    # 2. 加载情绪数据（提及记录）
    print("\n📄 加载 company_mentions.json")
    with open(SENTIMENT_FILE, 'r', encoding='utf-8') as f:
        sentiment_data = json.load(f)
    
    # 按股票代码分组提及记录
    mentions_by_code = defaultdict(list)
    for mention in sentiment_data.get('mentions', []):
        code = mention['code']
        article_id = f"{code}_{mention.get('article_url', '')}"
        
        # 检查是否已存在（去重）
        exists = any(a.get('article_id') == article_id for a in mentions_by_code[code])
        if not exists:
            article = {
                'article_id': article_id,
                'article_title': clean_text(mention.get('article_title', '')),
                'article_url': mention.get('article_url', ''),
                'date': mention.get('date', ''),
                'source': mention.get('source', ''),
                'context': clean_text(mention.get('context', '')),
                'accident': clean_text(mention.get('accident', '')),
                'industry_position': clean_text(mention.get('industry_position', '')),
                'products': mention.get('products', []),
                'partners': mention.get('partners', [])
            }
            mentions_by_code[code].append(article)
    
    # 合并到股票数据
    for code, articles in mentions_by_code.items():
        if code in stocks_dict:
            stocks_dict[code]['articles'] = articles
            # 更新提及数
            stocks_dict[code]['mention_count'] = len(articles)
    
    total_articles = sum(len(s['articles']) for s in stocks_dict.values())
    print(f"  ✅ 加载 {len(sentiment_data.get('mentions', []))} 条提及")
    print(f"  ✅ 去重后 {total_articles} 篇文章")
    
    # 3. 生成概念索引
    print("\n📄 生成概念索引")
    concepts = defaultdict(list)
    for code, stock in stocks_dict.items():
        for concept in stock.get('concepts', []):
            concepts[concept].append(code)
    
    print(f"  ✅ 生成 {len(concepts)} 个概念")
    
    # 4. 生成 detail_texts（用于详情页展示）
    for code, stock in stocks_dict.items():
        detail_texts = []
        
        # 核心业务
        if stock['core_business']:
            detail_texts.append(f"核心业务：{stock['core_business']}")
        
        # 行业地位
        if stock['industry_position']:
            detail_texts.append(f"行业地位：{stock['industry_position']}")
        
        # 催化剂
        if stock['accident']:
            detail_texts.append(f"催化剂：{stock['accident']}")
        
        # 合作伙伴
        if stock['partners']:
            detail_texts.append(f"合作伙伴：{', '.join(stock['partners'])}")
        
        stock['detail_texts'] = detail_texts
    
    # 5. 输出
    print("\n📄 生成索引文件")
    output_data = {
        'version': '2.0',
        'update_time': Path(SENTIMENT_FILE).stat().st_mtime,
        'stocks': stocks_dict,
        'concepts': dict(concepts)
    }
    
    with gzip.open(OUTPUT_FILE, 'wt', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 保存到：{OUTPUT_FILE}")
    print(f"  📊 文件大小：{OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    # 6. 推送到 Railway
    print("\n🚀 推送到 Railway")
    import subprocess
    import os
    
    os.chdir(Path(__file__).parent)
    
    subprocess.run(["git", "config", "user.email", "18901700722@163.com"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "ShermanXue"], check=True, capture_output=True)
    
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        print("  ⚠️ 没有更改需要提交")
        return
    
    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
    
    from datetime import datetime
    commit_msg = f"📊 重建搜索索引 - {len(stocks_dict)} 只股票 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
    print(f"  ✅ Git 提交：{commit_msg}")
    
    try:
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, timeout=30)
        print("  ✅ Git 推送成功")
        print("  ⏳ Railway 将自动重新部署（2-5 分钟）")
    except subprocess.TimeoutExpired:
        print("  ⚠️ 推送超时，但可能已在后台完成")
    
    print("\n" + "=" * 70)
    print("✅ 索引生成完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
