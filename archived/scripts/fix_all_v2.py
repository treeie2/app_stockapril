#!/usr/bin/env python3
"""
完整修复 - 8 个问题一次性解决
"""

import re

# ============ 修复 1-3: dashboard.html - 刷新按钮 + 行业替代板块 + 列表排版 ============
print('修复 dashboard.html...')

with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 重新设计刷新按钮（放在表头顶部，独立一行）
old_filter_section = '''<div class="filters">
            <button class="fbtn" data-board="全部">全部</button>
            <button class="fbtn" data-board="主板">主板</button>
            <button class="fbtn" data-board="创业板">创业板</button>
            <button class="fbtn" data-board="科创板">科创板</button>
            <button class="fbtn" data-board="北交所">北交所</button>
            <select class="sort-sel" id="sortSel">
                <option value="mention">按热度</option>
                <option value="chg_up">涨幅 ↑</option>
                <option value="chg_down">跌幅 ↑</option>
                <option value="articles">按文章数</option>
                <option value="name">名称</option>
            </select>
        </div>'''

new_filter_section = '''<!-- 刷新按钮（顶部独立） -->
        <div class="refresh-bar">
            <button id="refreshBtn" class="market-refresh" onclick="fetchMarket(true)">
                <span class="icon">🔄</span>
                <span class="text">刷新行情</span>
            </button>
            <span id="refreshStatus" class="refresh-status"></span>
        </div>
        
        <!-- 筛选和排序 -->
        <div class="filters">
            <button class="fbtn active" data-board="全部">全部</button>
            <button class="fbtn" data-board="主板">主板</button>
            <button class="fbtn" data-board="创业板">创业板</button>
            <button class="fbtn" data-board="科创板">科创板</button>
            <button class="fbtn" data-board="北交所">北交所</button>
            <select class="sort-sel" id="sortSel">
                <option value="mention">按热度</option>
                <option value="chg_up">涨幅 ↑</option>
                <option value="chg_down">跌幅 ↑</option>
                <option value="articles">按文章数</option>
                <option value="name">名称</option>
            </select>
        </div>'''

content = content.replace(old_filter_section, new_filter_section)

# 2. 移除表头内的刷新按钮
old_th_price = '''<th class="num" style="min-width:80px;">
                            最新价
                            <button id="refreshBtn" class="market-refresh" title="刷新股价" onclick="fetchMarket(true)">
                                <span class="icon">🔄</span>
                                <span class="text">刷新</span>
                            </button>
                        </th>'''

new_th_price = '''<th class="num" style="min-width:80px;">最新价</th>'''

content = content.replace(old_th_price, new_th_price)

# 3. 用行业替代板块列，优化列间距
old_thead = '''<thead>
                    <tr>
                        <th style="width:36px;text-align:center;">#</th>
                        <th>股票</th>
                        <th class="col-board">板块</th>
                        <th class="col-concepts">概念</th>
                        <th class="num" style="min-width:80px;">最新价</th>
                        <th class="num" style="min-width:80px;">涨跌幅</th>
                        <th class="num" style="min-width:100px;">总市值</th>
                        <th class="num" style="min-width:50px;">提及</th>
                        <th class="num" style="min-width:50px;">文章</th>
                    </tr>
                </thead>'''

new_thead = '''<thead>
                    <tr>
                        <th style="width:36px;text-align:center;">#</th>
                        <th style="min-width:140px;">股票</th>
                        <th style="min-width:120px;">行业</th>
                        <th style="min-width:200px;">概念</th>
                        <th class="num" style="min-width:70px;">最新价</th>
                        <th class="num" style="min-width:70px;">涨跌幅</th>
                        <th class="num" style="min-width:90px;">总市值</th>
                        <th class="num" style="min-width:45px;">提及</th>
                        <th class="num" style="min-width:45px;">文章</th>
                    </tr>
                </thead>'''

content = content.replace(old_thead, new_thead)

# 4. 修改数据行：用行业替代板块
old_td_board = '''<td class="col-board">
                            {% if stock.board %}<span class="board-b">{{ stock.board }}</span>{% endif %}
                            {% if stock.industries and stock.industries[0] %}<div style="font-size:.65rem;color:var(--t3);margin-top:.2rem">{{ stock.industries[0] }}</div>{% endif %}
                        </td>'''

new_td_industry = '''<td class="col-industry">
                            {% if stock.industries and stock.industries[0] %}
                                <span class="industry-tag">{{ stock.industries[0] }}</span>
                            {% else %}
                                <span style="color:var(--t3)">—</span>
                            {% endif %}
                        </td>'''

content = content.replace(old_td_board, new_td_industry)

# 5. 添加新的 CSS 样式
old_css_filters = '''.filters {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }'''

new_css = '''.refresh-bar {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
            padding: 12px 16px;
            background: linear-gradient(135deg, rgba(139,92,246,.08), rgba(124,58,237,.05));
            border: 1px solid rgba(139,92,246,.2);
            border-radius: 8px;
        }
        
        .market-refresh {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #8b5cf6, #7c3aed);
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.85rem;
            font-weight: 600;
            color: white;
            box-shadow: 0 2px 8px rgba(139,92,246,.3);
        }
        .market-refresh:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(139,92,246,.4);
        }
        .market-refresh:active {
            transform: translateY(0);
        }
        .market-refresh .icon {
            font-size: 1rem;
            transition: transform 0.3s;
        }
        .market-refresh.refreshing .icon {
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .refresh-status {
            font-size: 0.8rem;
            color: var(--text-muted);
        }
        
        .industry-tag {
            display: inline-block;
            background: rgba(6,182,212,.1);
            color: #22d3ee;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .filters {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }'''

content = content.replace(old_css_filters, new_css)

# 6. 修改 fetchMarket 函数，添加状态提示
old_fetch_status = '''if(force && btn) btn.classList.remove('refreshing');'''

new_fetch_status = '''if(force && btn) {
                btn.classList.remove('refreshing');
                const status = document.getElementById('refreshStatus');
                if(status) {
                    status.textContent = loaded > 0 ? `✅ 已更新 ${loaded} 只股票` : '⚠️ 无数据';
                    setTimeout(() => status.textContent = '', 3000);
                }
            }'''

content = content.replace(old_fetch_status, new_fetch_status)

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ dashboard.html 修复完成')

# ============ 修复 4-8: stock_detail.html - accidents + 多文章 + 编辑按钮 ============
print('修复 stock_detail.html...')

with open('templates/stock_detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查编辑按钮是否已存在
if 'edit-btn-hero' not in content:
    # 添加编辑按钮
    old_hero = '''<div class="stock-name-hero">{{ stock.name }}</div>'''
    new_hero = '''<div style="display:flex;align-items:center;gap:0.8rem;">
                        <div class="stock-name-hero">{{ stock.name }}</div>
                        <div class="stock-code-hero">{{ stock.code }}</div>
                    </div>
                    <button class="edit-btn-hero" onclick="editStock('{{ stock.code }}')" title="编辑股票信息">✏️ 编辑</button>'''
    content = content.replace(old_hero, new_hero)

# 检查编辑按钮样式
if '.edit-btn-hero {' not in content:
    old_hero_css = '.stock-name-hero {'
    new_hero_css = '''.edit-btn-hero {
            background: linear-gradient(135deg, rgba(139,92,246,.2), rgba(124,58,237,.1));
            border: 1px solid rgba(139,92,246,.5);
            color: #a78bfa;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .edit-btn-hero:hover {
            background: rgba(139,92,246,.3);
            border-color: rgba(139,92,246,.7);
            transform: translateY(-1px);
        }
        .stock-name-hero {'''
    content = content.replace(old_hero_css, new_hero_css)

# 检查行业显示
if '所属行业' not in content and 'stock.industries' not in content:
    # 在公司画像部分添加行业
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

# 检查文章循环（多篇文章显示）
if 'for article in stock.articles' not in content:
    # 找到文章部分并修改
    old_articles = '''{% if stock.articles and stock.articles | length > 0 %}
                    {% set article = stock.articles[0] %}'''
    
    new_articles = '''{% if stock.articles and stock.articles | length > 0 %}
                    <!-- 多篇文章循环 -->
                    {% for article in stock.articles %}'''
    
    content = content.replace(old_articles, new_articles)
    
    # 修改文章结束标签
    old_end = '''{% endif %}'''
    new_end = '''{% endfor %}
                {% else %}
                    <div style="text-align:center;color:var(--text-muted);padding:2rem;">
                        暂无文章数据
                    </div>
                {% endif %}'''
    
    # 只替换文章部分的结束标签
    content = re.sub(
        r'(\{% if stock\.articles.*?%>\n.*?{% endif %\})',
        lambda m: m.group(0).replace('{% endif %}', '{% endfor %}\n                {% else %}\n                    <div style="text-align:center;color:var(--text-muted);padding:2rem;">暂无文章数据</div>\n                {% endif %}'),
        content,
        flags=re.DOTALL
    )

# 检查 accidents 显示
if 'article.accidents' not in content:
    # 在文章部分添加 accidents
    old_insights = '''{% if article.insights and article.insights | length > 0 %}'''
    new_insights = '''{% if article.accidents and article.accidents | length > 0 %}
                        <div class="info-block block-accidents">
                            <div class="info-block-title">⚠️ 催化剂</div>
                            <ul class="info-list">
                                {% for item in article.accidents %}
                                    <li>{{ item }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                    {% endif %}
                    
                    {% if article.insights and article.insights | length > 0 %}'''
    content = content.replace(old_insights, new_insights)

# 检查编辑功能
if 'function editStock' not in content:
    # 添加编辑功能脚本
    old_scripts = '''</script>
</body>'''
    
    new_scripts = '''
        // 编辑功能
        function editStock(code) {
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
        }
        
        function saveEdit(code) {
            const data = {
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

print('\n✅ 所有修复完成！')
print('📝 修复内容:')
print('  1. 刷新按钮重新设计（顶部独立，紫色渐变）')
print('  2. 首页用行业替代板块')
print('  3. 列表列间距优化')
print('  4. 个股页面显示 accidents（催化剂）')
print('  5. 个股页面支持多篇文章循环')
print('  6. 个股页面编辑按钮（可编辑行业地位/产业链/合作伙伴）')
print('  7. 概念/核心业务不可编辑（系统自动生成）')
