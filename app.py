"""
ModelScope 部署入口
股票研究数据库 Web 应用
"""
from flask import Flask, jsonify, render_template, request
import json
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# 数据路径
MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'

# 全局数据
stocks = {}
concepts = {}

def load_data():
    """加载股票数据"""
    global stocks, concepts
    try:
        if MASTER_FILE.exists():
            with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            stocks_list = data.get('stocks', [])
            stocks = {s['code']: s for s in stocks_list if 'code' in s}
            
            # 构建概念索引
            concepts = {}
            for stock in stocks_list:
                for concept in stock.get('concepts', []):
                    if concept not in concepts:
                        concepts[concept] = {'stocks': []}
                    concepts[concept]['stocks'].append(stock['code'])
            
            print(f"✅ 加载 {len(stocks)} 只股票，{len(concepts)} 个概念")
        else:
            print(f"⚠️ 数据文件不存在: {MASTER_FILE}")
            stocks, concepts = {}, {}
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        stocks, concepts = {}, {}

# 启动时加载数据
load_data()

@app.route('/')
def dashboard():
    """首页 - 仪表板"""
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
    except:
        limit = 20
        offset = 0
    
    # 过滤 A 股个股
    all_stocks = []
    for c, d in stocks.items():
        if not (c.startswith('00') or c.startswith('30') or c.startswith('60') or c.startswith('68')):
            continue
        name = d.get('name', '')
        if any(x in name for x in ['ETF', '指数', '中证', '上证', '深证', '创业板指']):
            continue
        
        all_stocks.append({
            'code': c,
            'name': d.get('name', ''),
            'industry': d.get('industry', ''),
            'concepts': d.get('concepts', [])[:5],
            'board': d.get('board', ''),
            'mention_count': d.get('mention_count', 0),
            'articles': d.get('articles', [])[:3]
        })
    
    # 按提及次数排序
    all_stocks.sort(key=lambda x: x['mention_count'], reverse=True)
    
    total = len(all_stocks)
    paginated_stocks = all_stocks[offset:offset + limit]
    
    return render_template('dashboard.html',
                         stocks=paginated_stocks,
                         total_stocks=total,
                         limit=limit,
                         offset=offset)

@app.route('/stocks')
def stocks_list():
    """股票列表页"""
    lst = [{**{'code': c}, **d} for c, d in stocks.items()]
    return render_template('stocks.html', total=len(lst), stocks=lst)

@app.route('/stock/<code>')
def stock_detail(code):
    """股票详情页"""
    if code not in stocks:
        return render_template('stock_detail.html', error='股票不存在')
    
    stock = stocks[code]
    return render_template('stock_detail.html',
                         code=code,
                         name=stock.get('name', ''),
                         industry=stock.get('industry', ''),
                         concepts=stock.get('concepts', []),
                         board=stock.get('board', ''),
                         mention_count=stock.get('mention_count', 0),
                         articles=stock.get('articles', []))

@app.route('/concepts')
def concepts_list():
    """概念列表页"""
    concept_list = []
    for name, data in concepts.items():
        concept_list.append({
            'name': name,
            'stock_count': len(data.get('stocks', []))
        })
    concept_list.sort(key=lambda x: x['stock_count'], reverse=True)
    return render_template('concepts.html', concepts=concept_list)

@app.route('/concept/<name>')
def concept_detail(name):
    """概念详情页"""
    if name not in concepts:
        return render_template('concept_detail.html', error='概念不存在')
    
    stock_codes = concepts[name].get('stocks', [])
    lst = [stocks[c] for c in stock_codes if c in stocks]
    return render_template('concept_detail.html', concept=name, stocks=lst)

@app.route('/search')
def search():
    """搜索页面"""
    q = request.args.get('q', '').strip()
    results = []
    
    if q:
        for code, stock in stocks.items():
            name = stock.get('name', '')
            if q.lower() in name.lower() or q in code:
                results.append({
                    'code': code,
                    'name': name,
                    'industry': stock.get('industry', ''),
                    'concepts': stock.get('concepts', [])
                })
    
    # 热门股票
    top_stocks = sorted([{'code': c, **d} for c, d in stocks.items()],
                       key=lambda x: x.get('mention_count', 0),
                       reverse=True)[:10]
    
    return render_template('search.html',
                         query=q,
                         results=results,
                         total=len(results),
                         top_stocks=top_stocks)

@app.route('/import')
def import_data_page():
    """数据导入页面"""
    return render_template('import_data.html')

@app.route('/api/stocks')
def api_stocks():
    """API: 获取股票列表"""
    return jsonify({
        'stocks': list(stocks.values()),
        'total': len(stocks)
    })

@app.route('/api/stock/<code>')
def api_stock_detail(code):
    """API: 获取股票详情"""
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    return jsonify(stocks[code])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
