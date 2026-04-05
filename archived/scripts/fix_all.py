#!/usr/bin/env python3
"""
综合修复脚本 - 8 个问题一次性修复
"""

import re

# ============ 修复 1: dashboard.html - 板块显示 + 间距优化 ============
print('修复 dashboard.html...')

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复板块显示：检查 board 字段
old_board = '''<td class="col-board">
                            {% if stock.board %}<span class="board-b">{{ stock.board }}</span>{% endif %}
                            {% if stock.industry %}<div style="font-size:.65rem;color:var(--t3);margin-top:.2rem">{{ stock.industry }}</div>{% endif %}
                        </td>'''

new_board = '''<td class="col-board">
                            {% if stock.board %}<span class="board-b">{{ stock.board }}</span>{% endif %}
                            {% if stock.industries and stock.industries[0] %}<div style="font-size:.65rem;color:var(--t3);margin-top:.2rem">{{ stock.industries[0] }}</div>{% endif %}
                        </td>'''

content = content.replace(old_board, new_board)

# 优化间距：减小 col-board 的宽度
content = content.replace(
    '.col-board {',
    '.col-board { min-width: 100px; max-width: 140px; }'
)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ dashboard.html 修复完成')

# ============ 修复 2: stock_detail.html - 添加行业、编辑按钮 ============
print('修复 stock_detail.html...')

with open('templates/stock_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加行业显示（在公司画像部分）
old_core = '''{% if stock.core_business and stock.core_business | length > 0 %}
                    <div>
                        <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;">核心业务</div>
                        <ul class="info-list">
                            {% for item in stock.core_business %}
                                <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                {% endif %}'''

new_core = '''{% if stock.industries and stock.industries[0] %}
                    <div>
                        <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;">所属行业</div>
                        <div style="font-size:0.85rem;color:var(--text-primary);">{{ stock.industries[0] }}</div>
                    </div>
                {% endif %}
                
                {% if stock.core_business and stock.core_business | length > 0 %}
                    <div>
                        <div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:0.4rem;font-weight:600;">核心业务</div>
                        <ul class="info-list">
                            {% for item in stock.core_business %}
                                <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                {% endif %}'''

content = content.replace(old_core, new_core)

# 添加编辑按钮
old_title = '''<h1 class="stock-name">{{ stock.name }} <span class="stock-code">{{ stock.code }}</span></h1>'''
new_title = '''<div style="display:flex;justify-content:space-between;align-items:center;">
    <h1 class="stock-name">{{ stock.name }} <span class="stock-code">{{ stock.code }}</span></h1>
    <button class="edit-btn" onclick="editStock('{{ stock.code }}')" title="编辑股票信息">✏️ 编辑</button>
</div>'''

content = content.replace(old_title, new_title)

# 添加编辑按钮样式
old_styles = '.stock-name {'
new_styles = '''.edit-btn {
    background: rgba(139,92,246,.15);
    border: 1px solid rgba(139,92,246,.3);
    color: #a78bfa;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s;
}
.edit-btn:hover {
    background: rgba(139,92,246,.25);
    border-color: rgba(139,92,246,.5);
}
.stock-name {'''

content = content.replace(old_styles, new_styles)

# 添加编辑功能脚本
old_scripts = '''</script>
</body>'''

new_scripts = '''
        function editStock(code) {
            const data = {
                concepts: {{ stock.concepts | tojson }},
                core_business: {{ stock.core_business | tojson }},
                industry_position: {{ stock.industry_position | tojson }},
                chain: {{ stock.chain | tojson }},
                partners: {{ stock.partners | tojson }}
            };
            
            const modal = document.createElement('div');
            modal.className = 'edit-modal';
            modal.innerHTML = `
                <div class="edit-content">
                    <h3>编辑股票信息 - ${code}</h3>
                    <div class="edit-section"><label>概念标签（逗号分隔）</label><textarea id="edit-concepts">${data.concepts.join(',')}</textarea></div>
                    <div class="edit-section"><label>核心业务（逗号分隔）</label><textarea id="edit-core">${data.core_business.join(',')}</textarea></div>
                    <div class="edit-section"><label>行业地位（逗号分隔）</label><textarea id="edit-pos">${data.industry_position.join(',')}</textarea></div>
                    <div class="edit-section"><label>产业链（逗号分隔）</label><textarea id="edit-chain">${data.chain.join(',')}</textarea></div>
                    <div class="edit-section"><label>合作伙伴（逗号分隔）</label><textarea id="edit-partners">${data.partners.join(',')}</textarea></div>
                    <div class="edit-actions">
                        <button class="edit-save" onclick="saveEdit('${code}')">💾 保存</button>
                        <button class="edit-cancel" onclick="this.closest('.edit-modal').remove()">✖ 取消</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        function saveEdit(code) {
            const data = {
                concepts: document.getElementById('edit-concepts').value.split(',').map(s => s.trim()).filter(s => s),
                core_business: document.getElementById('edit-core').value.split(',').map(s => s.trim()).filter(s => s),
                industry_position: document.getElementById('edit-pos').value.split(',').map(s => s.trim()).filter(s => s),
                chain: document.getElementById('edit-chain').value.split(',').map(s => s.trim()).filter(s => s),
                partners: document.getElementById('edit-partners').value.split(',').map(s => s.trim()).filter(s => s)
            };
            
            fetch(`/api/stock/${code}/edit`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(res => {
                if(res.success) { alert('保存成功！'); location.reload(); }
                else { alert('保存失败：' + res.error); }
            })
            .catch(e => alert('请求失败：' + e));
        }
        
        const editStyle = document.createElement('style');
        editStyle.textContent = `
            .edit-modal{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:10000}
            .edit-content{background:var(--card-bg);padding:2rem;border-radius:12px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto}
            .edit-content h3{margin:0 0 1.5rem 0;color:var(--text-primary)}
            .edit-section{margin-bottom:1rem}
            .edit-section label{display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:0.4rem}
            .edit-section textarea{width:100%;min-height:60px;background:var(--input-bg);border:1px solid var(--border);border-radius:6px;padding:0.6rem;color:var(--text-primary);font-size:0.85rem;resize:vertical}
            .edit-actions{display:flex;gap:0.8rem;margin-top:1.5rem}
            .edit-save,.edit-cancel{padding:0.6rem 1.2rem;border-radius:6px;border:none;cursor:pointer;font-size:0.85rem}
            .edit-save{background:linear-gradient(135deg,#8b5cf6,#7c3aed);color:white}
            .edit-cancel{background:var(--card-bg);color:var(--text-muted);border:1px solid var(--border)}
        `;
        document.head.appendChild(editStyle);
    </script>
</body>'''

content = content.replace(old_scripts, new_scripts)

with open('templates/stock_detail.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ stock_detail.html 修复完成')

# ============ 修复 3: main.py - 添加编辑 API ============
print('修复 main.py...')

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_api = '''@app.route('/api/stock/<code>')
def api_stock(code):'''

new_api = '''@app.route('/api/stock/<code>/edit', methods=['POST'])
def api_stock_edit(code):
    if code not in stocks:
        return jsonify({'success': False, 'error': '股票不存在'}), 404
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '无效数据'}), 400
    if 'concepts' in data: stocks[code]['concepts'] = data['concepts']
    if 'core_business' in data: stocks[code]['core_business'] = data['core_business']
    if 'industry_position' in data: stocks[code]['industry_position'] = data['industry_position']
    if 'chain' in data: stocks[code]['chain'] = data['chain']
    if 'partners' in data: stocks[code]['partners'] = data['partners']
    return jsonify({'success': True})

@app.route('/api/stock/<code>')
def api_stock(code):'''

content = content.replace(old_api, new_api)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py 修复完成')

print('\n✅ 所有修复完成！')
