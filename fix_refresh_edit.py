#!/usr/bin/env python3
"""
修复：行情刷新 + 编辑按钮 + 编辑权限
"""

# ============ 修复 1: dashboard.html - 重新设计刷新按钮 ============
print('修复 dashboard.html...')

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除旧的刷新按钮样式
old_refresh_style = '''.refresh-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
            margin-left: 6px;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.2s;
        }
        .refresh-btn:hover {
            background: rgba(139,92,246,.15);
        }
        .refresh-btn:active {
            transform: rotate(180deg);
        }
        .refresh-btn.spinning {
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }'''

new_refresh_style = '''.market-refresh {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: linear-gradient(135deg, rgba(139,92,246,.1), rgba(139,92,246,.05));
            border: 1px solid rgba(139,92,246,.3);
            border-radius: 6px;
            padding: 4px 10px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.75rem;
            color: #a78bfa;
            margin-left: 8px;
        }
        .market-refresh:hover {
            background: rgba(139,92,246,.15);
            border-color: rgba(139,92,246,.5);
        }
        .market-refresh .icon {
            font-size: 0.9rem;
            transition: transform 0.3s;
        }
        .market-refresh.refreshing .icon {
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }'''

content = content.replace(old_refresh_style, new_refresh_style)

# 修改表头刷新按钮
old_th = '''<th class="num" style="min-width:80px;">
                            最新价
                            <button id="refreshBtn" class="refresh-btn" title="刷新股价" onclick="fetchMarket(true)">🔄</button>
                        </th>'''

new_th = '''<th class="num" style="min-width:80px;">
                            最新价
                            <button id="refreshBtn" class="market-refresh" title="刷新股价" onclick="fetchMarket(true)">
                                <span class="icon">🔄</span>
                                <span class="text">刷新</span>
                            </button>
                        </th>'''

content = content.replace(old_th, new_th)

# 修改 fetchMarket 函数，添加错误处理
old_fetch = '''        let marketLoaded = false;
        async function fetchMarket(force = false) {
            const codes = rows.map(r => r.dataset.code);
            if(!codes.length) return;
            
            const btn = document.getElementById('refreshBtn');
            
            // 手动刷新：显示加载状态
            if(force) {
                btn?.classList.add('spinning');
                rows.forEach(r => {
                    const code = r.dataset.code;
                    const pEl = document.getElementById(`p-${code}`);
                    const cEl = document.getElementById(`c-${code}`);
                    const mcEl = document.getElementById(`mc-${code}`);
                    if(pEl) pEl.innerHTML = '<span class="loading-price">🔄</span>';
                    if(cEl) cEl.innerHTML = '<span class="loading-price">—</span>';
                    if(mcEl) mcEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                });
            }
            
            try {
                const res = await fetch(`/api/market-data?codes=${codes.join(',')}`);
                const data = await res.json();
                codes.forEach(code => {
                    const d = data[code];
                    const pEl = document.getElementById(`p-${code}`);
                    const cEl = document.getElementById(`c-${code}`);
                    const mcEl = document.getElementById(`mc-${code}`);
                    if(!pEl) return;
                    if(!d) {
                        pEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                        cEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                        return;
                    }
                    const isUp = d.change >= 0;
                    const cls = isUp ? 'up' : 'down';
                    const sign = isUp ? '+' : '';
                    pEl.innerHTML = `<span class="col-price ${cls}">${d.price.toFixed(2)}</span>`;
                    cEl.innerHTML = `<span class="col-chg ${cls}">${sign}${d.change.toFixed(2)}%</span>`;
                    if(mcEl)
                        mcEl.innerHTML = d.marketCap ? `<span class="col-cap">${d.marketCap.toFixed(0)}亿</span>` : '—';
                    const row = document.querySelector(`tr[data-code="${code}"]`);
                    if(row) row.dataset.chg = d.change;
                });
                marketLoaded = true;
            } catch(e) {
                console.log('行情获取失败', e);
                if(force) {
                    rows.forEach(r => {
                        const code = r.dataset.code;
                        const pEl = document.getElementById(`p-${code}`);
                        const cEl = document.getElementById(`c-${code}`);
                        if(pEl) pEl.innerHTML = '<span style="color:var(--t3)">失败</span>';
                        if(cEl) cEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                    });
                }
            } finally {
                if(force && btn) btn.classList.remove('spinning');
            }
        }'''

new_fetch = '''        let marketLoaded = false;
        async function fetchMarket(force = false) {
            const codes = rows.map(r => r.dataset.code);
            if(!codes.length) return;
            
            const btn = document.getElementById('refreshBtn');
            
            if(force) {
                btn?.classList.add('refreshing');
                rows.forEach(r => {
                    const code = r.dataset.code;
                    const pEl = document.getElementById(`p-${code}`);
                    const cEl = document.getElementById(`c-${code}`);
                    const mcEl = document.getElementById(`mc-${code}`);
                    if(pEl) pEl.innerHTML = '<span class="loading-price">🔄</span>';
                    if(cEl) cEl.innerHTML = '<span class="loading-price">—</span>';
                    if(mcEl) mcEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                });
            }
            
            try {
                const res = await fetch(`/api/market-data?codes=${codes.join(',')}`);
                const data = await res.json();
                
                let loaded = 0;
                codes.forEach(code => {
                    const d = data[code];
                    const pEl = document.getElementById(`p-${code}`);
                    const cEl = document.getElementById(`c-${code}`);
                    const mcEl = document.getElementById(`mc-${code}`);
                    if(!pEl) return;
                    if(!d || !d.price) {
                        pEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                        cEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                        return;
                    }
                    loaded++;
                    const isUp = d.change >= 0;
                    const cls = isUp ? 'up' : 'down';
                    const sign = isUp ? '+' : '';
                    pEl.innerHTML = `<span class="col-price ${cls}">${d.price.toFixed(2)}</span>`;
                    cEl.innerHTML = `<span class="col-chg ${cls}">${sign}${d.change.toFixed(2)}%</span>`;
                    if(mcEl)
                        mcEl.innerHTML = d.marketCap ? `<span class="col-cap">${d.marketCap.toFixed(0)}亿</span>` : '—';
                    const row = document.querySelector(`tr[data-code="${code}"]`);
                    if(row) row.dataset.chg = d.change;
                });
                
                if(loaded > 0) marketLoaded = true;
                
                // 更新按钮文本
                if(btn) {
                    const textSpan = btn.querySelector('.text');
                    if(textSpan) textSpan.textContent = loaded > 0 ? '已更新' : '无数据';
                    setTimeout(() => { if(textSpan) textSpan.textContent = '刷新'; }, 2000);
                }
            } catch(e) {
                console.log('行情获取失败', e);
                if(force) {
                    rows.forEach(r => {
                        const code = r.dataset.code;
                        const pEl = document.getElementById(`p-${code}`);
                        const cEl = document.getElementById(`c-${code}`);
                        if(pEl) pEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                        if(cEl) cEl.innerHTML = '<span style="color:var(--t3)">—</span>';
                    });
                    alert('行情获取失败，请稍后重试');
                }
            } finally {
                if(force && btn) btn.classList.remove('refreshing');
            }
        }'''

content = content.replace(old_fetch, new_fetch)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ dashboard.html 修复完成')

# ============ 修复 2: stock_detail.html - 编辑按钮显示 + 编辑权限 ============
print('修复 stock_detail.html...')

with open('templates/stock_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查编辑按钮是否存在
if 'edit-btn' not in content:
    # 添加编辑按钮
    old_title = '''<h1 class="stock-name">{{ stock.name }} <span class="stock-code">{{ stock.code }}</span></h1>'''
    new_title = '''<div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;">
        <h1 class="stock-name" style="margin:0;">{{ stock.name }} <span class="stock-code">{{ stock.code }}</span></h1>
        <button class="edit-btn" onclick="editStock('{{ stock.code }}')" title="编辑股票信息">✏️ 编辑</button>
    </div>'''
    content = content.replace(old_title, new_title)

# 修改编辑权限：只有行业地位/产业链/合作伙伴可编辑
old_edit_func = '''function editStock(code) {
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
        }'''

new_edit_func = '''function editStock(code) {
            const data = {
                industry_position: {{ stock.industry_position | tojson }},
                chain: {{ stock.chain | tojson }},
                partners: {{ stock.partners | tojson }}
            };
            
            const modal = document.createElement('div');
            modal.className = 'edit-modal';
            modal.innerHTML = `
                <div class="edit-content">
                    <h3>编辑股票信息 - ${code}</h3>
                    <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:1rem;">
                        💡 提示：概念标签和核心业务由系统自动生成，暂不支持手动编辑
                    </div>
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
        }'''

content = content.replace(old_edit_func, new_edit_func)

# 修改保存函数
old_save_func = '''function saveEdit(code) {
            const data = {
                concepts: document.getElementById('edit-concepts').value.split(',').map(s => s.trim()).filter(s => s),
                core_business: document.getElementById('edit-core').value.split(',').map(s => s.trim()).filter(s => s),
                industry_position: document.getElementById('edit-pos').value.split(',').map(s => s.trim()).filter(s => s),
                chain: document.getElementById('edit-chain').value.split(',').map(s => s.trim()).filter(s => s),
                partners: document.getElementById('edit-partners').value.split(',').map(s => s.trim()).filter(s => s)
            };'''

new_save_func = '''function saveEdit(code) {
            const data = {
                industry_position: document.getElementById('edit-pos').value.split(',').map(s => s.trim()).filter(s => s),
                chain: document.getElementById('edit-chain').value.split(',').map(s => s.trim()).filter(s => s),
                partners: document.getElementById('edit-partners').value.split(',').map(s => s.trim()).filter(s => s)
            };'''

content = content.replace(old_save_func, new_save_func)

with open('templates/stock_detail.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ stock_detail.html 修复完成')

# ============ 修复 3: main.py - 修改编辑权限 ============
print('修复 main.py...')

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_edit_api = '''@app.route('/api/stock/<code>/edit', methods=['POST'])
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
    return jsonify({'success': True})'''

new_edit_api = '''@app.route('/api/stock/<code>/edit', methods=['POST'])
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
    return jsonify({'success': True})'''

content = content.replace(old_edit_api, new_edit_api)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py 修复完成')

print('\n✅ 所有修复完成！')
print('📝 修复内容:')
print('  1. 重新设计刷新按钮（更美观，带"刷新"文字）')
print('  2. 添加行情加载错误处理')
print('  3. 编辑按钮显示修复')
print('  4. 编辑权限：只允许编辑行业地位/产业链/合作伙伴')
print('  5. 概念标签和核心业务不可编辑（系统自动生成）')
