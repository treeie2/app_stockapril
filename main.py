#!/usr/bin/env python3
"""
个股研究数据库 Web 界面 - Railway 极简版
"""

from flask import Flask, jsonify, render_template, request
import json, gzip, os
from pathlib import Path

app = Flask(__name__)

# 数据路径
DATA_DIR = Path(__file__).parent / 'data' / 'sentiment'
SEARCH_INDEX_FILE = DATA_DIR / 'search_index_full.json.gz'

# 加载数据
print("📋 加载数据...")
try:
    with gzip.open(SEARCH_INDEX_FILE, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    stocks = data.get('stocks', {})
    concepts = data.get('concepts', {})
    print(f"  ✅ 加载 {len(stocks)} 只股票")
    print(f"  ✅ 加载 {len(concepts)} 个概念")
except Exception as e:
    print(f"  ❌ 错误：{e}")
    stocks, concepts = {}, {}

@app.route('/')
def dashboard():
    top = sorted([{'code': c, **d} for c, d in stocks.items()], 
                 key=lambda x: x['mention_count'], reverse=True)[:20]
    for i, s in enumerate(top): s['rank'] = i + 1
    
    # 计算文章数（安全方式）
    articles = set()
    for code, s in stocks.items():
        for a in s.get('articles', []):
            articles.add(f"{code}_{a.get('article_id', '')}")
    
    return render_template('dashboard.html', 
        total_stocks=len(stocks),
        total_mentions=sum(s.get('mention_count', 0) for s in stocks.values()),
        total_articles=len(articles),
        update_time=Path(SEARCH_INDEX_FILE).stat().st_mtime,
        top_20=top)

@app.route('/stocks')
def stocks_list():
    lst = sorted([{'code': c, **d} for c, d in stocks.items()], 
                 key=lambda x: x['mention_count'], reverse=True)
    return render_template('stocks.html', total=len(lst), stocks=lst)

@app.route('/stock/<code>')
def stock_detail(code):
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    d = stocks[code]
    
    # 筛选核心概念：按概念热度排序，最多显示 10 个
    all_concepts = d.get('concepts', [])
    core_concepts = []
    other_concepts = []
    
    # 按概念包含的股票数量排序（热门概念优先）
    sorted_concepts = sorted(all_concepts, key=lambda c: len(concepts.get(c, [])), reverse=True)
    
    # 前 10 个为核心概念，其余为其他概念
    core_concepts = sorted_concepts[:10]
    other_concepts = sorted_concepts[10:]
    
    return render_template('stock_detail.html', 
        code=code, name=d.get('name',''), board=d.get('board',''),
        mention_count=d.get('mention_count',0),
        core_concepts=core_concepts, other_concepts=other_concepts,
        all_concepts=all_concepts,
        industries=d.get('industries',[]),
        products=d.get('products',[]), articles=d.get('articles',[])[:20],
        detail_texts=d.get('detail_texts',[])[:5])

@app.route('/concepts')
def concepts_list():
    lst = [{'name': n, 'count': len(c)} for n, c in concepts.items()]
    lst.sort(key=lambda x: x['count'], reverse=True)
    return render_template('concepts.html', concepts=lst)

@app.route('/concept/<name>')
def concept_detail(name):
    codes = concepts.get(name, [])
    lst = []
    for c in codes:
        if c in stocks:
            s = stocks[c]
            lst.append({'code': c, 'name': s.get('name',''), 
                       'mention_count': s.get('mention_count',0),
                       'board': s.get('board',''),
                       'other_concepts': [x for x in s.get('concepts',[]) if x != name]})
    lst.sort(key=lambda x: x['mention_count'], reverse=True)
    return render_template('concept_detail.html', concept=name, stocks=lst)

@app.route('/search')
def search():
    q = request.args.get('q', '').lower()
    results = []
    if q:
        for c, d in stocks.items():
            if q in d.get('name','').lower() or q in c:
                results.append({'code': c, 'name': d.get('name',''), 
                               'mention_count': d.get('mention_count',0),
                               'concepts': d.get('concepts',[])[:5]})
    results.sort(key=lambda x: x['mention_count'], reverse=True)
    return render_template('search.html', query=q, results=results, total=len(results))

@app.route('/api/stock/<code>')
def api_stock(code):
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    d = stocks[code]
    return jsonify({'code': code, 'name': d.get('name',''), 'board': d.get('board',''),
                   'mention_count': d.get('mention_count',0), 'concepts': d.get('concepts',[]),
                   'industries': d.get('industries',[]), 'products': d.get('products',[]),
                   'articles': d.get('articles',[])[:20], 'detail_texts': d.get('detail_texts',[])[:5]})

@app.route('/api/search/suggest')
def api_suggest():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify({'suggestions': []})
    sug = [{'code': c, 'name': d.get('name',''), 'mention_count': d.get('mention_count',0)}
           for c, d in stocks.items() if q.lower() in d.get('name','').lower()]
    return jsonify({'suggestions': sug[:10]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 启动于 port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
