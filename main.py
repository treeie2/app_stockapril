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
    # 传递所有股票数据（按提及次数排序）
    all_stocks = sorted([{'code': c, **d} for c, d in stocks.items()], 
                        key=lambda x: x['mention_count'], reverse=True)
    
    # 计算文章数（安全方式）
    articles = set()
    for code, s in stocks.items():
        for a in s.get('articles', []):
            articles.add(f"{code}_{a.get('article_id', '')}")
    
    return render_template('dashboard.html', 
        stocks=all_stocks,
        total_stocks=len(stocks),
        total_mentions=sum(s.get('mention_count', 0) for s in stocks.values()),
        total_articles=len(articles))

@app.route('/stocks')
def stocks_list():
    lst = sorted([{'code': c, **d} for c, d in stocks.items()], 
                 key=lambda x: x['mention_count'], reverse=True)
    return render_template('stocks.html', total=len(lst), stocks=lst)

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
        'articles': d.get('articles', [])[:20],
        'detail_texts': d.get('detail_texts', [])[:5]
    }
    
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
    """编辑股票信息（只允许编辑部分字段）"""
    if code not in stocks:
        return jsonify({'success': False, 'error': '股票不存在'}), 404
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '无效数据'}), 400
    # 只允许编辑以下字段
    if 'industry_position' in data: stocks[code]['industry_position'] = data['industry_position']
    if 'chain' in data: stocks[code]['chain'] = data['chain']
    if 'partners' in data: stocks[code]['partners'] = data['partners']
    # 注意：concepts 和 core_business 不可编辑
    return jsonify({'success': True})

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

# 数据文件路径
MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 启动于 port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
