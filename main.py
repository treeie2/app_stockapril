#!/usr/bin/env python3
"""
个股研究数据库 Web 界面 - Railway 极简版
"""

from flask import Flask, jsonify, render_template, request, send_file
import json, gzip, os
from pathlib import Path
from datetime import datetime

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
        code=code, 
        name=d.get('name',''), 
        board=d.get('board',''),
        mention_count=d.get('mention_count',0),
        concepts=core_concepts,  # 模板用 concepts
        core_business=d.get('core_business', ''),
        industry_position=d.get('industry_position', ''),
        accident=d.get('accident', ''),
        insights=d.get('insights', ''),
        chain=d.get('chain', ''),
        key_metrics=d.get('key_metrics', ''),
        partners=d.get('partners', []),
        products=d.get('products', []), 
        articles=d.get('articles', [])[:20],
        detail_texts=d.get('detail_texts', [])[:5])

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
