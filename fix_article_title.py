#!/usr/bin/env python3
"""
修复文章标题字段名：article.title → article.article_title
"""

print('修复 stock_detail.html 文章标题字段...')

with open('templates/stock_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复文章标题
content = content.replace(
    '{{ article.title | default',
    '{{ article.article_title | default'
)

# 修复其他可能的字段引用
content = content.replace(
    'article.title',
    'article.article_title'
)

# 检查并修复文章循环
old_loop = '''{% for article in stock.articles %}'''
new_loop = '''<!-- 文章循环：{{ stock.articles | length }} 篇 -->
                    {% for article in stock.articles %}'''

content = content.replace(old_loop, new_loop)

# 添加文章计数显示
old_counter = '''<div class="section-title">调研文章</div>'''
new_counter = '''<div class="section-title">
                    调研文章 
                    <span style="font-size:0.75rem;color:var(--text-muted);font-weight:400;">
                        ({{ stock.articles | length }}篇)
                    </span>
                </div>'''

content = content.replace(old_counter, new_counter)

with open('templates/stock_detail.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ stock_detail.html 文章标题字段修复完成')

# ============ 验证索引数据结构 ============
print('\n验证索引数据结构...')

import json
import gzip

try:
    with open('data/sentiment/search_index_full.json.gz', 'rb') as f:
        data = json.loads(gzip.decompress(f.read()).decode('utf-8'))
    
    # 检查金风科技
    stock = data.stocks.get('002202', {})
    print(f"\n金风科技 002202:")
    print(f"  文章数：{len(stock.get('articles', []))}")
    
    if stock.get('articles'):
        article = stock['articles'][0]
        print(f"  第一篇文章字段:")
        for key in ['article_id', 'article_title', 'date', 'source', 'accident', 'insights']:
            val = article.get(key)
            if isinstance(val, list):
                print(f"    {key}: [{len(val)} 项]")
            elif isinstance(val, str) and len(val) > 50:
                print(f"    {key}: {val[:50]}...")
            else:
                print(f"    {key}: {val}")
    
    # 检查多篇文章的股票
    multi_article_stocks = [code for code, s in data.stocks.items() if len(s.get('articles', [])) > 1]
    print(f"\n多篇文章的股票数量：{len(multi_article_stocks)}")
    if multi_article_stocks:
        print(f"  示例：{multi_article_stocks[:5]}")
        # 检查第一个多文章股票
        sample = multi_article_stocks[0]
        sample_stock = data.stocks[sample]
        print(f"\n  {sample} ({sample_stock.get('name', '')}):")
        for i, art in enumerate(sample_stock['articles'][:3]):
            print(f"    文章{i+1}: {art.get('article_title', '无标题')}")
    
    print('\n✅ 索引数据结构验证完成')
    
except Exception as e:
    print(f'❌ 验证失败：{e}')
