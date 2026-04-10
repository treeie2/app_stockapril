#!/usr/bin/env python3
"""
个股研究数据库 Web 界面 - Railway 极简版
"""

from flask import Flask, jsonify, render_template, request, send_file
import json, gzip, os, requests
from pathlib import Path
from datetime import datetime

# 延迟导入 akshare（避免加载慢）
def get_akshare():
    try:
        import akshare as ak
        return ak
    except ImportError:
        return None

app = Flask(__name__)

# 文章API服务配置
ARTICLE_API_URL = os.environ.get('ARTICLE_API_URL', 'http://localhost:5001')

# 数据路径
DATA_DIR = Path(__file__).parent / 'data' / 'sentiment'
SEARCH_INDEX_FILE = DATA_DIR / 'search_index_full.json.gz'

# ─── Jaccard 相似度计算 ───
def jaccard_similarity(set1, set2):
    """计算两个集合的 Jaccard 相似度"""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def find_similar_stocks(code, top_k=10, min_similarity=0.1):
    """找出与指定股票最相似的股票"""
    if code not in stocks:
        return []
    
    target_concepts = set(stocks[code].get('concepts', []))
    if not target_concepts:
        return []
    
    similarities = []
    for c, d in stocks.items():
        if c == code:
            continue
        other_concepts = set(d.get('concepts', []))
        if not other_concepts:
            continue
        
        sim = jaccard_similarity(target_concepts, other_concepts)
        if sim >= min_similarity:
            # 找出共同概念
            common = target_concepts & other_concepts
            similarities.append({
                'code': c,
                'name': d.get('name', ''),
                'similarity': sim,
                'common_concepts': list(common),
                'common_count': len(common),
                'mention_count': d.get('mention_count', 0),
                'concepts': d.get('concepts', [])
            })
    
    # 按相似度排序
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    return similarities[:top_k]

# 加载社保基金数据
print("📋 加载社保基金数据...")
SOCIAL_SECURITY_FILE = Path(__file__).parent / 'data' / 'master' / 'social_security_2025q4.json'
social_security_stocks = set()
social_security_info = {}
try:
    with open(SOCIAL_SECURITY_FILE, 'r', encoding='utf-8') as f:
        ss_data = json.load(f)
    for stock in ss_data.get('stocks', []):
        code = stock.get('code')
        if code:
            social_security_stocks.add(code)
            social_security_info[code] = {
                'holding_ratio': stock.get('holding_ratio', ''),
                'note': stock.get('note', ''),
                'industry_group': stock.get('industry_group', '')
            }
    print(f"  ✅ 加载 {len(social_security_stocks)} 只社保基金新进股票")
except Exception as e:
    print(f"  ⚠️ 社保基金数据加载失败：{e}")

# Firebase 配置
FIREBASE_PROJECT_ID = "stock-research-669e1"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

def load_data_from_firebase():
    """从 Firebase 加载股票数据"""
    print("📋 尝试从 Firebase 加载数据...")
    
    try:
        url = f"{FIREBASE_BASE_URL}/stocks"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            
            stocks = {}
            concepts = {}
            
            for doc in documents:
                fields = doc.get('fields', {})
                
                # 转换 Firestore 格式
                code = fields.get('code', {}).get('stringValue', '')
                if not code:
                    continue
                
                stock = {
                    'name': fields.get('name', {}).get('stringValue', ''),
                    'code': code,
                    'board': fields.get('board', {}).get('stringValue', ''),
                    'industry': fields.get('industry', {}).get('stringValue', ''),
                    'concepts': [],
                    'products': [],
                    'core_business': [],
                    'industry_position': [],
                    'chain': [],
                    'partners': [],
                    'mention_count': int(fields.get('mention_count', {}).get('integerValue', '0') or 0),
                    'articles': []
                }
                
                # 获取概念
                concepts_arr = fields.get('concepts', {}).get('arrayValue', {}).get('values', [])
                stock['concepts'] = [c.get('stringValue', '') for c in concepts_arr if c.get('stringValue')]
                
                # 构建概念索引
                for concept in stock['concepts']:
                    if concept not in concepts:
                        concepts[concept] = {'stocks': []}
                    concepts[concept]['stocks'].append(code)
                
                # 获取文章
                articles = fields.get('articles', {}).get('arrayValue', {}).get('values', [])
                for article in articles:
                    article_fields = article.get('mapValue', {}).get('fields', {})
                    article_data = {
                        'title': article_fields.get('title', {}).get('stringValue', ''),
                        'date': article_fields.get('date', {}).get('stringValue', ''),
                        'source': article_fields.get('source', {}).get('stringValue', ''),
                        'accidents': [],
                        'insights': [],
                        'key_metrics': [],
                        'target_valuation': []
                    }
                    
                    # 获取 accidents
                    accidents = article_fields.get('accidents', {}).get('arrayValue', {}).get('values', [])
                    article_data['accidents'] = [a.get('stringValue', '') for a in accidents if a.get('stringValue')]
                    
                    # 获取 insights
                    insights = article_fields.get('insights', {}).get('arrayValue', {}).get('values', [])
                    article_data['insights'] = [i.get('stringValue', '') for i in insights if i.get('stringValue')]
                    
                    # 获取 key_metrics
                    metrics = article_fields.get('key_metrics', {}).get('arrayValue', {}).get('values', [])
                    article_data['key_metrics'] = [m.get('stringValue', '') for m in metrics if m.get('stringValue')]
                    
                    stock['articles'].append(article_data)
                
                stocks[code] = stock
            
            print(f"  ✅ 从 Firebase 加载 {len(stocks)} 只股票")
            print(f"  ✅ 加载 {len(concepts)} 个概念")
            return stocks, concepts
        else:
            print(f"  ⚠️ Firebase 加载失败: HTTP {response.status_code}")
            return None, None
    except Exception as e:
        print(f"  ⚠️ Firebase 加载出错: {e}")
        return None, None

def load_data_from_local():
    """从本地 JSON 加载数据"""
    print("📋 从本地文件加载数据...")
    
    MASTER_FILE_JSON = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
    MASTER_FILE_GZ = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json.gz'
    
    try:
        if MASTER_FILE_JSON.exists():
            print(f"  📋 读取 stocks_master.json ({MASTER_FILE_JSON.stat().st_size / 1024 / 1024:.2f} MB)...")
            with open(MASTER_FILE_JSON, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
        elif MASTER_FILE_GZ.exists():
            print(f"  📋 读取 stocks_master.json.gz...")
            with gzip.open(MASTER_FILE_GZ, 'rt', encoding='utf-8') as f:
                master_data = json.load(f)
        else:
            raise FileNotFoundError("未找到 stocks_master 数据文件")
        
        # 转换为字典格式
        stocks_list = master_data.get('stocks', [])
        stocks = {s['code']: s for s in stocks_list if 'code' in s}
        
        # 从概念字段提取所有概念
        concepts = {}
        for stock in stocks_list:
            for concept in stock.get('concepts', []):
                if concept not in concepts:
                    concepts[concept] = {'stocks': []}
                concepts[concept]['stocks'].append(stock['code'])
        
        print(f"  ✅ 加载 {len(stocks)} 只股票")
        print(f"  ✅ 加载 {len(concepts)} 个概念")
        return stocks, concepts
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return {}, {}

# 加载数据 - 优先从 Firebase，失败则从本地
print("📋 加载数据...")
stocks, concepts = load_data_from_firebase()
if stocks is None:
    stocks, concepts = load_data_from_local()

# 数据加载完成
print(f"📊 数据加载完成：{len(stocks)} 只股票，{len(concepts)} 个概念")

@app.route('/')
def dashboard():
    # 获取分页参数
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
    except:
        limit = 20
        offset = 0
    
    # 传递所有股票数据（只保留 A 股个股，过滤 ETF 和指数）
    all_stocks = []
    for c, d in stocks.items():
        # 过滤：只保留 A 股个股（code 以 00/30/60/68 开头）
        if not (c.startswith('00') or c.startswith('30') or c.startswith('60') or c.startswith('68')):
            continue
        
        # 过滤：名称包含 ETF、指数、中证、上证的
        name = d.get('name', '')
        if any(x in name for x in ['ETF', '指数', '中证', '上证', '深证', '创业板指']):
            continue
        
        stock = {'code': c, **d}
        # 修复：字段名是 industries 不是 industry
        stock['industry'] = d.get('industry', '') or d.get('industries', '')
        
        # 获取最新文章日期用于排序
        articles = d.get('articles', [])
        if articles:
            # 从 article_id 提取日期或从 published_at 获取
            first_article = articles[0]
            stock['latest_article_date'] = first_article.get('published_at', '') or first_article.get('article_id', '')[:10]
        else:
            stock['latest_article_date'] = ''
        
        # 优先使用 last_updated 字段（如果有）
        stock['last_updated'] = d.get('last_updated', '')
        
        all_stocks.append(stock)
    
    # 默认按 last_updated 排序（优先），没有则按最新文章日期倒序排列
    all_stocks.sort(key=lambda x: (x.get('last_updated', '') or '', x.get('latest_article_date', '')), reverse=True)
    
    # 分页
    total = len(all_stocks)
    has_more = offset + limit < total
    paginated_stocks = all_stocks[offset:offset + limit]
    
    # 计算文章数（安全方式）
    articles = set()
    for code, s in stocks.items():
        for a in s.get('articles', []):
            articles.add(f"{code}_{a.get('article_id', '')}")
    
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'stocks': paginated_stocks,
            'offset': offset + limit,
            'limit': limit,
            'total': total,
            'has_more': has_more
        })
    
    # 首次加载，渲染完整页面
    return render_template('dashboard.html', 
        stocks=paginated_stocks,
        total_stocks=len(paginated_stocks),
        total_mentions=sum(s.get('mention_count', 0) for s in paginated_stocks),
        total_articles=len(articles),
        has_more=has_more,
        next_offset=offset + limit,
        limit=limit)

@app.route('/stocks')
def stocks_list():
    # 按 last_updated 排序（最新的在前），没有更新时间的排在后面
    lst = sorted([{'code': c, **d} for c, d in stocks.items()], 
                 key=lambda x: (x.get('last_updated', '') or '', x.get('mention_count', 0)), 
                 reverse=True)
    return render_template('stocks.html', total=len(lst), stocks=lst)

@app.route('/social-security-new')
def social_security_new():
    """2025Q4 社保基金新进股票页面"""
    # 加载社保基金数据
    SS_FILE = Path(__file__).parent / 'data' / 'master' / 'social_security_2025q4.json'
    try:
        with open(SS_FILE, 'r', encoding='utf-8') as f:
            ss_data = json.load(f)
    except Exception as e:
        print(f"⚠️ 加载社保基金数据失败：{e}")
        ss_data = {'stocks': [], 'total_count': 0}
    
    # 检查哪些股票在数据库中
    enhanced_stocks = []
    for stock in ss_data.get('stocks', []):
        code = stock.get('code')
        in_db = code in stocks
        enhanced_stocks.append({**stock, 'in_database': in_db})
    
    # 按行业分组
    industry_groups = {}
    for stock in enhanced_stocks:
        industry = stock.get('industry_category', '其他')
        if industry not in industry_groups:
            industry_groups[industry] = []
        industry_groups[industry].append(stock)
    
    # 计算统计数据
    total_count = len(enhanced_stocks)
    industry_count = len(industry_groups)
    
    # 平均持股比例
    ratios = []
    max_ratio = 0
    max_ratio_stock = ''
    for stock in enhanced_stocks:
        ratio_str = stock.get('ratio', '0%')
        try:
            ratio_val = float(ratio_str.replace('%', ''))
            ratios.append(ratio_val)
            if ratio_val > max_ratio:
                max_ratio = ratio_val
                max_ratio_stock = f"{stock.get('name', '')} {ratio_str}"
        except:
            pass
    
    avg_ratio = f"{sum(ratios)/len(ratios):.2f}%" if ratios else '0%'
    
    return render_template('social_security_new.html',
                         industry_groups=industry_groups,
                         total_count=total_count,
                         industry_count=industry_count,
                         avg_ratio=avg_ratio,
                         max_ratio_stock=max_ratio_stock)

@app.route('/demo/cards')
def demo_cards():
    """卡片组件演示页面"""
    return render_template('demo_cards.html')

@app.route('/stock/<code>')
def stock_detail(code):
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    d = stocks[code]
    
    # 构建完整的 stock 对象
    stock = {
        'code': code,
        'name': d.get('name', ''),
        'board': d.get('board', ''),
        'industry': d.get('industry', ''),
        'mention_count': d.get('mention_count', 0),
        'concepts': d.get('concepts', []),
        'core_business': d.get('core_business', []),
        'industry_position': d.get('industry_position', []),
        'accident': d.get('accident', ''),
        'insights': d.get('insights', ''),
        'chain': d.get('chain', []),
        'key_metrics': d.get('key_metrics', []),
        'partners': d.get('partners', []),
        'products': d.get('products', []),
        'detail_texts': d.get('detail_texts', [])[:5]
    }
    
    # 统一文章字段格式
    raw_articles = d.get('articles', [])[:20]
    articles = []
    for a in raw_articles:
        article = {
            'id': a.get('article_id', ''),
            'title': a.get('article_title', a.get('title', '（无标题）')),
            'url': a.get('article_url', a.get('url', '')),
            'date': a.get('date', a.get('published_at', '')),
            'source': a.get('source', ''),
            'context': a.get('context', ''),
            'insights': a.get('insights', a.get('insight', [])),
            'accidents': a.get('accidents', [a.get('accident', '')] if a.get('accident') else []),
            'key_metrics': a.get('key_metrics', []),
            'target_valuation': a.get('target_valuation', []),
            'industry_position': a.get('industry_position', []),
            'products': a.get('products', []),
            'partners': a.get('partners', [])
        }
        articles.append(article)
    
    stock['articles'] = articles
    
    # 添加社保基金信息
    stock['is_social_security'] = code in social_security_stocks
    if stock['is_social_security']:
        ss_info = social_security_info.get(code, {})
        stock['social_security_holding_ratio'] = ss_info.get('holding_ratio', '')
        stock['social_security_note'] = ss_info.get('note', '')
        stock['social_security_industry_group'] = ss_info.get('industry_group', '')
    
    return render_template('stock_detail.html', stock=stock)

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
    q = request.args.get('q', '').lower().strip()
    results = []
    
    if q:
        # 全文搜索：名称、代码、概念、催化剂、投资洞察、公司概况
        for c, d in stocks.items():
            score = 0
            match_fields = []
            
            # 精确匹配代码（最高优先级）
            if q == c:
                score = 1000
                match_fields.append('代码')
            # 匹配名称
            elif q in d.get('name', '').lower():
                score = 500
                match_fields.append('名称')
            # 匹配概念
            elif any(q in concept.lower() for concept in d.get('concepts', [])):
                score = 300
                match_fields.append('概念')
            # 匹配催化剂（accident）- 支持数组和字符串
            accident = d.get('accident', '')
            accident_text = ','.join(accident).lower() if isinstance(accident, list) else accident.lower()
            if q in accident_text:
                score = 200
                match_fields.append('催化剂')
            # 匹配投资洞察（insights）- 支持数组和字符串
            insights = d.get('insights', '')
            insights_text = ','.join(insights).lower() if isinstance(insights, list) else insights.lower()
            if q in insights_text:
                score = 200
                match_fields.append('投资洞察')
            # 匹配公司概况（core_business）- 支持数组和字符串
            core_business = d.get('core_business', '')
            core_business_text = ','.join(core_business).lower() if isinstance(core_business, list) else core_business.lower()
            if q in core_business_text:
                score = 200
                match_fields.append('公司概况')
            # 匹配行业地位（industry_position）- 支持数组和字符串
            industry_position = d.get('industry_position', '')
            industry_position_text = ','.join(industry_position).lower() if isinstance(industry_position, list) else industry_position.lower()
            if q in industry_position_text:
                score = 150
                match_fields.append('行业地位')
            # 匹配产业链（chain）- 支持数组和字符串
            chain = d.get('chain', '')
            chain_text = ','.join(chain).lower() if isinstance(chain, list) else chain.lower()
            if q in chain_text:
                score = 150
                match_fields.append('产业链')
            
            if score > 0:
                results.append({
                    'code': c,
                    'name': d.get('name', ''),
                    'mention_count': d.get('mention_count', 0),
                    'concepts': d.get('concepts', [])[:5],
                    'score': score,
                    'match_fields': match_fields
                })
        
        # 按分数排序，同分按提及次数排序
        results.sort(key=lambda x: (-x['score'], -x['mention_count']))
    
    # 热门搜索（Top 20）
    top_stocks = sorted([{'code': c, **d} for c, d in stocks.items()], 
                        key=lambda x: x['mention_count'], reverse=True)[:20]
    
    return render_template('search.html', query=q, results=results, total=len(results), top_stocks=top_stocks)

@app.route('/api/stock/<code>/edit', methods=['POST'])
def api_stock_edit(code):
    """编辑股票信息（支持更多字段）"""
    if code not in stocks:
        return jsonify({'success': False, 'error': '股票不存在'}), 404
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '无效数据'}), 400
    
    # 可编辑的股票字段
    editable_fields = [
        'core_business', 'products', 'industry_position', 
        'chain', 'partners'
    ]
    
    updated = []
    for field in editable_fields:
        if field in data:
            stocks[code][field] = data[field]
            updated.append(field)
    
    # 文章相关字段（更新最新的一篇文章）
    article_fields = ['accidents', 'insights', 'target_valuation']
    article_updated = False
    
    if stocks[code].get('articles') and len(stocks[code]['articles']) > 0:
        latest_article = stocks[code]['articles'][0]
        for field in article_fields:
            if field in data:
                latest_article[field] = data[field]
                article_updated = True
    
    # 记录编辑日志
    if updated or article_updated:
        edit_log.append({
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'name': stocks[code].get('name', ''),
            'fields': updated + (['articles'] if article_updated else []),
            'changes': {field: data[field] for field in updated}
        })
        save_edit_log()
        
        # 保存到文件
        save_stocks_to_file()
    
    return jsonify({'success': True, 'updated_fields': updated})

@app.route('/api/stock/<code>')
def api_stock(code):
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    d = stocks[code]
    return jsonify({'code': code, 'name': d.get('name',''), 'board': d.get('board',''),
                   'mention_count': d.get('mention_count',0), 
                   'concepts': d.get('concepts',[]),
                   'industries': d.get('industries',[]), 
                   'products': d.get('products',[]),
                   'core_business': d.get('core_business',[]),
                   'industry_position': d.get('industry_position',[]),
                   'chain': d.get('chain',[]),
                   'partners': d.get('partners',[]),
                   'articles': d.get('articles',[])[:20], 
                   'detail_texts': d.get('detail_texts',[])[:5]})

@app.route('/api/search/suggest')
def api_suggest():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify({'suggestions': []})
    sug = [{'code': c, 'name': d.get('name',''), 'mention_count': d.get('mention_count',0)}
           for c, d in stocks.items() if q.lower() in d.get('name','').lower()]
    return jsonify({'suggestions': sug[:10]})

@app.route('/api/search/fulltext')
def api_fulltext_search():
    """全文搜索 API - 搜索文章标题、摘要、分析内容"""
    q = request.args.get('q', '').lower().strip()
    limit = request.args.get('limit', 20, type=int)
    
    if len(q) < 2:
        return jsonify({'results': [], 'total': 0})
    
    results = []
    
    for code, stock_data in stocks.items():
        name = stock_data.get('name', '')
        articles = stock_data.get('articles', [])
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            analysis = article.get('analysis', '')
            summary = article.get('summary', '')
            date = article.get('date', '')
            source = article.get('source', '')
            
            # 构建搜索文本
            search_text = f"{title} {content} {analysis} {summary}".lower()
            
            # 计算匹配度
            if q in search_text:
                # 计算匹配分数
                score = 0
                if q in title.lower():
                    score += 0.5  # 标题匹配权重高
                if q in content.lower():
                    score += 0.3
                if q in analysis.lower():
                    score += 0.2
                
                # 计算匹配次数
                match_count = search_text.count(q)
                score += min(match_count * 0.05, 0.2)  # 匹配次数加分，最高0.2
                
                # 生成摘要片段
                snippet = generate_snippet(search_text, q, content or summary or title)
                
                results.append({
                    'code': code,
                    'name': name,
                    'article_title': title,
                    'article_date': date,
                    'article_source': source,
                    'snippet': snippet,
                    'score': min(score, 1.0),
                    'match_count': match_count
                })
    
    # 按匹配分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 限制返回数量
    total = len(results)
    results = results[:limit]
    
    return jsonify({
        'results': results,
        'total': total,
        'query': q,
        'limit': limit
    })

def generate_snippet(text, query, original_content, max_length=150):
    """生成包含关键词的摘要片段"""
    if not original_content:
        return ""
    
    content_lower = original_content.lower()
    query_lower = query.lower()
    
    # 找到关键词位置
    pos = content_lower.find(query_lower)
    if pos == -1:
        # 如果找不到（可能因为大小写或特殊字符），返回前 max_length 个字符
        return original_content[:max_length] + "..." if len(original_content) > max_length else original_content
    
    # 计算片段起始位置（关键词前后各留一些上下文）
    start = max(0, pos - 50)
    end = min(len(original_content), pos + len(query) + 100)
    
    snippet = original_content[start:end]
    
    # 添加省略号
    if start > 0:
        snippet = "..." + snippet
    if end < len(original_content):
        snippet = snippet + "..."
    
    return snippet

# 数据文件路径
# 优先使用未压缩的 JSON 文件
if (Path(__file__).parent / 'data' / 'master' / 'stocks_master.json').exists():
    MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
else:
    MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json.gz'
EDIT_LOG_FILE = Path(__file__).parent / 'data' / 'edit_log.json'

# 编辑记录
edit_log = []

# 加载编辑记录
if EDIT_LOG_FILE.exists():
    try:
        with open(EDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            edit_log = json.load(f)
    except:
        edit_log = []

@app.route('/api/stock/<code>/accident', methods=['PUT'])
def update_accident(code):
    """更新股票的 accident（催化剂）字段"""
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    
    data = request.get_json()
    new_accident = data.get('accident', '')
    
    result = update_stock_field(code, 'accident', new_accident)
    
    # 记录编辑日志
    if result.get('success'):
        edit_log.append({
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'name': stocks[code].get('name', ''),
            'field': 'accident',
            'content': new_accident[:200] + '...' if len(new_accident) > 200 else new_accident
        })
        save_edit_log()
    
    return result

@app.route('/api/stock/<code>/insights', methods=['PUT'])
def update_insights(code):
    """更新股票的 insights 字段"""
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    
    data = request.get_json()
    new_insights = data.get('insights', '')
    
    result = update_stock_field(code, 'insights', new_insights)
    
    # 记录编辑日志
    if result.get('success'):
        edit_log.append({
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'name': stocks[code].get('name', ''),
            'field': 'insights',
            'content': new_insights[:200] + '...' if len(new_insights) > 200 else new_insights
        })
        save_edit_log()
    
    return result

def save_edit_log():
    """保存编辑日志"""
    try:
        with open(EDIT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(edit_log, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存编辑日志失败：{e}")

def save_stocks_to_file():
    """保存股票数据到文件"""
    try:
        # 转换为列表格式
        stocks_list = []
        for code, d in stocks.items():
            stock = {
                'code': code,
                'name': d.get('name', ''),
                'board': d.get('board', ''),
                'industry': d.get('industry', ''),
                'concepts': d.get('concepts', []),
                'products': d.get('products', []),
                'core_business': d.get('core_business', []),
                'industry_position': d.get('industry_position', []),
                'chain': d.get('chain', []),
                'partners': d.get('partners', []),
                'mention_count': d.get('mention_count', 0),
                'articles': d.get('articles', [])
            }
            stocks_list.append(stock)
        
        # 保存到文件
        data = {'stocks': stocks_list}
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存 {len(stocks_list)} 只股票到 {MASTER_FILE}")
    except Exception as e:
        print(f"❌ 保存股票数据失败：{e}")

@app.route('/api/sync', methods=['GET'])
def sync_edits():
    """同步编辑记录 - 导出所有修改"""
    return jsonify({
        'success': True,
        'count': len(edit_log),
        'edits': edit_log
    })

@app.route('/api/sync/export', methods=['GET'])
def export_edits():
    """导出编辑记录为 JSON 文件"""
    if not edit_log:
        return jsonify({'error': '没有编辑记录'}), 404
    
    # 生成导出文件
    export_data = {
        'export_time': datetime.now().isoformat(),
        'total_edits': len(edit_log),
        'edits': edit_log
    }
    
    export_file = EDIT_LOG_FILE.parent / f'edit_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return send_file(export_file, as_attachment=True)

@app.route('/api/sync/email', methods=['POST'])
def email_edits():
    """通过邮件发送编辑记录"""
    if not edit_log:
        return jsonify({'error': '没有编辑记录'}), 404
    
    data = request.get_json() or {}
    recipient = data.get('email', '')
    
    # 生成邮件内容
    email_content = f"""
主题：股票数据编辑同步 - {len(edit_log)} 条更新

编辑记录汇总：
================

"""
    for edit in edit_log:
        email_content += f"""
时间：{edit['timestamp']}
股票：{edit['name']} ({edit['code']})
字段：{edit['field']}
内容：{edit['content']}

---

"""
    
    # 保存到临时文件
    email_file = EDIT_LOG_FILE.parent / f'email_draft_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(email_file, 'w', encoding='utf-8') as f:
        f.write(email_content)
    
    return jsonify({
        'success': True,
        'message': f'邮件草稿已生成：{email_file.name}',
        'content': email_content
    })

@app.route('/api/sync/clear', methods=['POST'])
def clear_edits():
    """清空编辑记录"""
    global edit_log
    edit_log = []
    save_edit_log()
    return jsonify({'success': True, 'message': '编辑记录已清空'})

@app.route('/api/stock/<code>/similar')
def get_similar_stocks(code):
    """获取相似股票推荐"""
    top_k = request.args.get('top', 10, type=int)
    min_sim = request.args.get('min_sim', 0.1, type=float)
    
    similar = find_similar_stocks(code, top_k=top_k, min_similarity=min_sim)
    return jsonify({'similar': similar, 'count': len(similar)})

@app.route('/api/market-data')
def get_market_data():
    """获取实时行情数据（腾讯财经 API）"""
    codes = request.args.get('codes', '').split(',')
    codes = [c for c in codes if c.strip()]
    
    if not codes:
        return jsonify({'totalCap': 0}), 200
    
    try:
        result = {}
        total_cap = 0
        
        # 构建腾讯财经 API 请求
        symbols = []
        for code in codes:
            if code.startswith('6'):
                symbols.append(f'sh{code}')
            else:
                symbols.append(f'sz{code}')
        
        url = 'https://qt.gtimg.cn/q=' + ','.join(symbols)
        headers = {
            'Referer': 'https://stockapp.finance.qq.com/',
            'User-Agent': 'Mozilla/5.0'
        }
        
        # 使用 gb18030 编码（腾讯 API 默认）
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gb18030'
        
        if resp.status_code == 200:
            # 解析返回数据
            lines = resp.text.strip().split('\n')
            for line in lines:
                if '=' in line and '~' in line:
                    parts = line.split('=', 1)
                    if len(parts) >= 2:
                        # 提取股票代码：v_sh600519 -> 600519, v_sz300308 -> 300308
                        code_part = parts[0].split('_')
                        if len(code_part) >= 2:
                            full_code = code_part[-1]
                            # 去除市场前缀（sh600519 -> 600519, sz300308 -> 300308）
                            code = full_code[2:] if len(full_code) >= 2 else full_code
                            
                            # 解析数据：v_sh600000="51~浦发银行~600000~7.53~7.50~..."
                            data_str = parts[1].strip('"')
                            fields = data_str.split('~')
                            
                            if len(fields) >= 47:
                                # 字段说明（腾讯财经 API）：
                                # [0]:类型，[1]:名称，[2]:代码，[3]:当前价，[32]:涨跌幅%，[44]:总市值 (亿)，[39]:市盈率
                                price = float(fields[3]) if fields[3] else 0
                                change_pct = float(fields[32]) if fields[32] else 0
                                market_cap = float(fields[44]) if fields[44] else 0
                                pe_ratio = float(fields[39]) if fields[39] else None
                                
                                result[code] = {
                                    'price': price,
                                    'change': change_pct,
                                    'marketCap': market_cap,
                                    'peRatio': pe_ratio
                                }
                                
                                if market_cap:
                                    total_cap += market_cap
        
        result['totalCap'] = total_cap
        return jsonify(result)
    
    except Exception as e:
        print(f"获取行情数据失败：{e}")
        return jsonify({'totalCap': 0, 'error': str(e)}), 200

def update_stock_field(code, field, value):
    """通用函数：更新股票字段"""
    try:
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # 查找并更新股票
        updated = False
        for stock in master_data.get('stocks', []):
            if stock.get('code') == code:
                if 'llm_summary' not in stock:
                    stock['llm_summary'] = {}
                stock['llm_summary'][field] = value
                updated = True
                
                # 同步更新内存中的 stocks 字典
                stocks[code][field] = value
                break
        
        if not updated:
            return jsonify({'error': '股票不存在'}), 404
        
        # 保存回文件
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        # 重新构建搜索索引
        import subprocess
        subprocess.run(['python3', 'build_index.py'], 
                      cwd=Path(__file__).parent, 
                      capture_output=True)
        
        return jsonify({'success': True, 'message': '已保存'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════
# 文章数据同步 API（对接智能体）
# ═══════════════════════════════════════════════════════════

@app.route('/api/articles/sync', methods=['POST'])
def sync_articles_from_api():
    """
    从文章API服务同步数据到主项目
    可以手动触发或设置定时任务
    """
    try:
        # 1. 从API获取待导入数据
        resp = requests.post(
            f'{ARTICLE_API_URL}/api/sync/to-main',
            timeout=30
        )
        
        if resp.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'API服务返回错误: {resp.status_code}'
            }), 500
        
        data = resp.json()
        if not data.get('success'):
            return jsonify({
                'success': False,
                'error': data.get('error', 'Unknown error')
            }), 500
        
        sync_data = data.get('data', {})
        articles = sync_data.get('articles', [])
        stocks_data = sync_data.get('stocks', [])
        
        if not articles:
            return jsonify({
                'success': True,
                'message': '没有待同步的数据',
                'imported': 0
            })
        
        # 2. 导入数据
        from article_importer import ArticleImporter
        importer = ArticleImporter(api_base_url=ARTICLE_API_URL)
        stats = importer.import_articles(auto_confirm=True)
        
        return jsonify({
            'success': True,
            'message': f'同步完成',
            'stats': {
                'articles_processed': stats.get('articles_processed', 0),
                'stocks_created': stats.get('stocks_created', 0),
                'stocks_updated': stats.get('stocks_updated', 0),
                'errors': len(stats.get('errors', []))
            }
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': f'无法连接到文章API服务: {ARTICLE_API_URL}'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/articles/status', methods=['GET'])
def get_article_api_status():
    """检查文章API服务状态"""
    try:
        resp = requests.get(f'{ARTICLE_API_URL}/api/health', timeout=5)
        if resp.status_code == 200:
            return jsonify({
                'success': True,
                'api_status': 'connected',
                'api_url': ARTICLE_API_URL,
                'details': resp.json()
            })
        else:
            return jsonify({
                'success': False,
                'api_status': 'error',
                'api_url': ARTICLE_API_URL,
                'status_code': resp.status_code
            })
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'api_status': 'disconnected',
            'api_url': ARTICLE_API_URL,
            'message': '文章API服务未启动'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'api_status': 'error',
            'error': str(e)
        })


# Firebase 配置
FIREBASE_PROJECT_ID = "webstock-724"
FIREBASE_API_KEY = "AIzaSyDnWABBE1WZ3H_il95-TcBqpIAH9sisLUo"

def sync_to_firebase(stocks_dict, stats):
    """同步导入的数据到 Firebase Firestore"""
    try:
        import requests
        
        # 构建 Firestore REST API URL
        base_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"
        
        sync_count = 0
        errors = []
        
        # 只同步本次导入/更新的股票
        for code, stock in stocks_dict.items():
            try:
                # 构建文档路径
                doc_url = f"{base_url}/stocks/{code}"
                
                # 转换数据为 Firestore 格式
                firestore_data = {
                    "fields": {
                        "name": {"stringValue": stock.get("name", "")},
                        "code": {"stringValue": code},
                        "board": {"stringValue": stock.get("board", "")},
                        "industry": {"stringValue": stock.get("industry", "")},
                        "mention_count": {"integerValue": str(stock.get("mention_count", 0))},
                        "updated_at": {"timestampValue": datetime.now().isoformat() + "Z"}
                    }
                }
                
                # 添加概念数组
                concepts = stock.get("concepts", [])
                if concepts:
                    firestore_data["fields"]["concepts"] = {
                        "arrayValue": {
                            "values": [{"stringValue": c} for c in concepts]
                        }
                    }
                
                # 添加文章数组
                articles = stock.get("articles", [])
                if articles:
                    article_values = []
                    for article in articles:
                        article_values.append({
                            "mapValue": {
                                "fields": {
                                    "title": {"stringValue": article.get("title", "")},
                                    "date": {"stringValue": article.get("date", "")},
                                    "source": {"stringValue": article.get("source", "")},
                                    "insights": {
                                        "arrayValue": {
                                            "values": [{"stringValue": i} for i in article.get("insights", [])]
                                        }
                                    } if article.get("insights") else {"nullValue": None}
                                }
                            }
                        })
                    firestore_data["fields"]["articles"] = {
                        "arrayValue": {"values": article_values}
                    }
                
                # 发送到 Firestore
                resp = requests.patch(doc_url, json=firestore_data, timeout=10)
                if resp.status_code in [200, 201]:
                    sync_count += 1
                else:
                    errors.append(f"{code}: HTTP {resp.status_code}")
                    
            except Exception as e:
                errors.append(f"{code}: {str(e)}")
        
        return {
            'success': True,
            'synced_count': sync_count,
            'total_stocks': len(stocks_dict),
            'errors': errors[:5]  # 只返回前5个错误
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Firebase 测试页面
@app.route('/test-firebase')
def test_firebase():
    return render_template('test_firebase.html')


# 数据导入页面
@app.route('/import')
def import_data_page():
    return render_template('import_data.html')


# API: 导入股票数据
@app.route('/api/import/stocks', methods=['POST'])
def import_stocks():
    """导入股票数据JSON"""
    try:
        data = request.get_json()
        
        if not data or 'stocks' not in data:
            return jsonify({
                'success': False,
                'error': '无效的JSON格式，必须包含 "stocks" 字段'
            })
        
        import_stocks = data['stocks']
        if not isinstance(import_stocks, list):
            return jsonify({
                'success': False,
                'error': '"stocks" 必须是数组'
            })
        
        # 加载现有数据
        master_file = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
        existing_stocks = {}
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_stocks = {s['code']: s for s in existing_data.get('stocks', [])}
        
        # 统计
        stats = {
            'imported_stocks': 0,
            'new_stocks': 0,
            'updated_stocks': 0,
            'imported_articles': 0,
            'new_articles': 0,
            'duplicate_articles': 0
        }
        
        # 处理导入的股票
        for stock in import_stocks:
            code = stock.get('code')
            if not code:
                continue
            
            stats['imported_stocks'] += 1
            
            if code in existing_stocks:
                # 更新现有股票
                existing = existing_stocks[code]
                
                # 合并文章（去重）
                existing_articles = existing.get('articles', [])
                new_articles = stock.get('articles', [])
                
                existing_titles = {a.get('title') for a in existing_articles}
                
                for article in new_articles:
                    if article.get('title') not in existing_titles:
                        existing_articles.append(article)
                        stats['new_articles'] += 1
                        stats['imported_articles'] += 1
                    else:
                        stats['duplicate_articles'] += 1
                
                # 更新其他字段
                for key in ['name', 'board', 'industry', 'concepts', 'mention_count']:
                    if key in stock:
                        existing[key] = stock[key]
                
                existing['articles'] = existing_articles
                stats['updated_stocks'] += 1
            else:
                # 新增股票
                existing_stocks[code] = stock
                stats['new_stocks'] += 1
                stats['imported_articles'] += len(stock.get('articles', []))
        
        # 保存数据到本地
        output_data = {'stocks': list(existing_stocks.values())}
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # 更新内存中的数据
        global stocks
        stocks = existing_stocks
        
        # 同步到 Firebase
        firebase_sync_result = sync_to_firebase(existing_stocks, stats)
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {stats["imported_stocks"]} 只股票，新增 {stats["new_stocks"]} 只，更新 {stats["updated_stocks"]} 只',
            'stats': stats,
            'firebase_sync': firebase_sync_result
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'error': f'JSON解析错误: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'导入失败: {str(e)}'
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    print(f"🚀 启动于 port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
