#!/usr/bin/env python3
"""
个股研究数据库 Web 界面 v3.0 - Railway 兼容版
- 显示详情文字
- 全文搜索
- 概念标签链接
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# ============== 数据路径（Railway 兼容） ==============
# Railway 环境下使用相对路径（数据文件与 main.py 同目录）
# 本地环境下使用绝对路径
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Railway 环境
    DATA_DIR = Path(__file__).parent / 'data'
else:
    # 本地环境
    DATA_DIR = Path('/home/admin/openclaw/workspace/stocks/research_db')

MENTIONS_FILE = DATA_DIR / 'sentiment' / 'company_mentions.json'
# Railway 使用精简版数据（3MB vs 282MB，避免 OOM）
SEARCH_INDEX_FILE = DATA_DIR / 'sentiment' / 'search_index_lite.json.gz'

# ============== 加载数据 ==============
print("📋 加载数据...")
print(f"   数据目录：{DATA_DIR}")

try:
    # 加载搜索索引（主数据源）- 支持 gzip 压缩
    if SEARCH_INDEX_FILE.suffix == '.gz':
        import gzip
        with gzip.open(SEARCH_INDEX_FILE, 'rt', encoding='utf-8') as f:
            search_index = json.load(f)
    else:
        # 尝试 .gz 文件，如果不存在则用普通文件
        gz_file = SEARCH_INDEX_FILE.with_suffix('.json.gz')
        if gz_file.exists():
            import gzip
            with gzip.open(gz_file, 'rt', encoding='utf-8') as f:
                search_index = json.load(f)
            print("  📦 使用 gzip 压缩数据")
        else:
            with open(SEARCH_INDEX_FILE, 'r', encoding='utf-8') as f:
                search_index = json.load(f)

    stocks_data = search_index.get('stocks', {})
    concepts_data = search_index.get('concepts', {})
    fulltext_data = search_index.get('fulltext', {})

    print(f"  ✅ 加载 {len(stocks_data)} 只股票")
    print(f"  ✅ 加载 {len(fulltext_data)} 个全文索引词")
except FileNotFoundError as e:
    print(f"  ⚠️ 数据文件未找到：{e}")
    print("  💡 请确保数据文件已上传到 Railway 项目")
    # 使用空数据继续运行
    stocks_data = {}
    concepts_data = {}
    fulltext_data = {}

# ============== HTML 模板 ==============

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个股研究数据库 - 仪表板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="text-xl font-bold text-gray-900">📊 个股研究数据库</a>
                </div>
                <div class="flex items-center space-x-6">
                    <div class="relative">
                        <input type="text" id="global-search" placeholder="搜索股票、概念、全文..." 
                               class="w-96 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <div id="search-suggestions" class="absolute top-full right-0 mt-1 w-96 bg-white border border-gray-300 rounded-lg shadow-lg hidden max-h-96 overflow-y-auto"></div>
                    </div>
                    <a href="/" class="text-blue-600 font-medium">仪表板</a>
                    <a href="/stocks" class="text-gray-600 hover:text-gray-900">股票列表</a>
                    <a href="/concepts" class="text-gray-600 hover:text-gray-900">概念大全</a>
                    <a href="/search" class="text-gray-600 hover:text-gray-900">高级搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">股票池</div>
                <div class="text-3xl font-bold text-blue-600 mt-2">{{ total_stocks }}</div>
                <div class="text-xs text-gray-500 mt-1">只股票</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">总提及次数</div>
                <div class="text-3xl font-bold text-green-600 mt-2">{{ total_mentions }}</div>
                <div class="text-xs text-gray-500 mt-1">条</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">文章数量</div>
                <div class="text-3xl font-bold text-purple-600 mt-2">{{ total_articles }}</div>
                <div class="text-xs text-gray-500 mt-1">篇</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <div class="text-sm text-gray-600">更新时间</div>
                <div class="text-lg font-bold text-orange-600 mt-2">{{ update_time }}</div>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow mb-8">
            <div class="px-6 py-4 border-b">
                <h2 class="text-lg font-semibold text-gray-900">📈 有效提及 Top 20</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">排名</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">股票</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">提及次数</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">概念标签</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">行业</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {% for stock in top_20 %}
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stock.rank }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <a href="/stock/{{ stock.code }}" class="text-blue-600 hover:text-blue-900 font-medium">
                                    {{ stock.name }} ({{ stock.code }})
                                </a>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ stock.mention_count }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex flex-wrap gap-1">
                                    {% for concept in stock.concepts[:5] %}
                                    <a href="/concept/{{ concept }}" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded hover:bg-blue-200">
                                        {{ concept }}
                                    </a>
                                    {% endfor %}
                                    {% if stock.concepts|length > 5 %}
                                    <span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">+{{ stock.concepts|length - 5 }}</span>
                                    {% endif %}
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                {{ stock.industries[0] if stock.industries else '-' }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <script>
        // 全局搜索
        const searchInput = document.getElementById('global-search');
        const suggestionsDiv = document.getElementById('search-suggestions');

        searchInput.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            if (query.length < 2) {
                suggestionsDiv.classList.add('hidden');
                return;
            }

            try {
                const response = await fetch(`/api/search/suggest?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.suggestions.length > 0) {
                    suggestionsDiv.innerHTML = data.suggestions.map(s => `
                        <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-0" onclick="location.href='/stock/${s.code}'">
                            <div class="font-medium">${s.name} (${s.code})</div>
                            <div class="text-xs text-gray-500">${s.mention_count} 次提及</div>
                        </div>
                    `).join('');
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    location.href = `/search?q=${encodeURIComponent(query)}`;
                }
            }
        });
    </script>
</body>
</html>
"""

STOCK_DETAIL_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ code }} - 个股详情</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="/" class="text-xl font-bold text-gray-900">📊 个股研究数据库</a>
                </div>
                <div class="flex items-center space-x-6">
                    <div class="relative">
                        <input type="text" id="global-search" placeholder="搜索股票、概念、全文..." 
                               class="w-96 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <div id="search-suggestions" class="absolute top-full right-0 mt-1 w-96 bg-white border border-gray-300 rounded-lg shadow-lg hidden max-h-96 overflow-y-auto"></div>
                    </div>
                    <a href="/" class="text-gray-600 hover:text-gray-900">仪表板</a>
                    <a href="/stocks" class="text-gray-600 hover:text-gray-900">股票列表</a>
                    <a href="/concepts" class="text-gray-600 hover:text-gray-900">概念大全</a>
                    <a href="/search" class="text-gray-600 hover:text-gray-900">高级搜索</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div id="loading" class="text-center py-12">
            <i class="fas fa-spinner fa-spin text-4xl text-blue-600"></i>
            <p class="mt-4 text-gray-600">加载数据中...</p>
        </div>

        <div id="content" class="hidden">
            <!-- 第一层：基本信息 -->
            <div class="bg-white rounded-lg shadow mb-6">
                <div class="px-6 py-4 border-b">
                    <h1 id="stock-title" class="text-2xl font-bold text-gray-900"></h1>
                </div>
                <div class="px-6 py-4">
                    <div class="grid grid-cols-4 gap-4">
                        <div>
                            <div class="text-sm text-gray-600">股票代码</div>
                            <div id="stock-code" class="text-xl font-mono font-bold text-blue-600"></div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600">提及次数</div>
                            <div id="stock-mentions" class="text-xl font-bold text-green-600"></div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600">所属板块</div>
                            <div id="stock-board" class="text-xl font-bold text-purple-600"></div>
                        </div>
                        <div>
                            <div class="text-sm text-gray-600">文章数量</div>
                            <div id="stock-articles" class="text-xl font-bold text-orange-600"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 第二层：概念标签、行业、产品 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">🏷️ 概念标签</h2>
                    </div>
                    <div class="p-6">
                        <div id="concepts" class="flex flex-wrap gap-2"></div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">🏢 行业分类</h2>
                    </div>
                    <div class="p-6">
                        <div id="industries" class="space-y-2 text-gray-700"></div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b">
                        <h2 class="text-lg font-semibold text-gray-900">📦 产品信息</h2>
                    </div>
                    <div class="p-6">
                        <div id="products" class="text-gray-700"></div>
                    </div>
                </div>
            </div>

            <!-- 第三层：详情文字（大段文字描述） -->
            <div class="bg-white rounded-lg shadow mb-6">
                <div class="px-6 py-4 border-b">
                    <h2 class="text-lg font-semibold text-gray-900">📝 详情文字</h2>
                    <p class="text-sm text-gray-500 mt-1">从文章中提取的与该股票相关的大段文字描述</p>
                </div>
                <div class="p-6">
                    <div id="detail-texts" class="space-y-4"></div>
                </div>
            </div>

            <!-- 第四层：所有提及文章 -->
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b">
                    <h2 class="text-lg font-semibold text-gray-900">📰 提及文章 <span id="article-count" class="text-sm text-gray-500 ml-2"></span></h2>
                </div>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">文章标题</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">日期</th>
                            </tr>
                        </thead>
                        <tbody id="articles-table" class="bg-white divide-y divide-gray-200"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        const stockCode = "{{ code }}";

        async function loadStockData() {
            try {
                const response = await fetch(`/api/stock/${stockCode}`);
                const data = await response.json();

                if (data.error) {
                    alert(data.error);
                    return;
                }

                document.getElementById('stock-title').textContent = `${data.name} (${data.code})`;
                document.getElementById('stock-code').textContent = data.code;
                document.getElementById('stock-mentions').textContent = data.mention_count;
                document.getElementById('stock-board').textContent = data.board || '未知';
                document.getElementById('stock-articles').textContent = data.articles.length;

                // 概念标签
                const conceptsDiv = document.getElementById('concepts');
                if (data.concepts && data.concepts.length > 0) {
                    conceptsDiv.innerHTML = data.concepts.map(c => 
                        `<a href="/concept/${encodeURIComponent(c)}" class="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full hover:bg-blue-200">${c}</a>`
                    ).join('');
                } else {
                    conceptsDiv.innerHTML = '<span class="text-gray-400">暂无概念标签</span>';
                }

                // 行业分类
                const industriesDiv = document.getElementById('industries');
                if (data.industries && data.industries.length > 0) {
                    industriesDiv.innerHTML = data.industries.map(i => `<div>📁 ${i}</div>`).join('');
                } else {
                    industriesDiv.innerHTML = '<span class="text-gray-400">暂无行业分类</span>';
                }

                // 产品信息
                const productsDiv = document.getElementById('products');
                if (data.products && data.products.length > 0) {
                    productsDiv.innerHTML = data.products.map(p => `<div>📦 ${p}</div>`).join('');
                } else {
                    productsDiv.innerHTML = '<span class="text-gray-400">暂无产品信息</span>';
                }

                // 详情文字
                const detailsDiv = document.getElementById('detail-texts');
                if (data.detail_texts && data.detail_texts.length > 0) {
                    detailsDiv.innerHTML = data.detail_texts.map((text, i) => `
                        <div class="border-l-4 border-blue-500 pl-4 py-2 bg-gray-50 rounded">
                            <div class="text-xs text-gray-500 mb-1">详情 #${i+1}</div>
                            <div class="text-gray-800 whitespace-pre-wrap">${text}</div>
                        </div>
                    `).join('');
                } else {
                    detailsDiv.innerHTML = '<span class="text-gray-400">暂无详情文字</span>';
                }

                // 提及文章
                const articlesTbody = document.getElementById('articles-table');
                document.getElementById('article-count').textContent = `(${data.articles.length}篇)`;
                
                if (data.articles.length > 0) {
                    articlesTbody.innerHTML = data.articles.map(a => `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4">
                                <div class="text-sm font-medium text-gray-900">${a.source}</div>
                                <div class="text-xs text-gray-500">${a.article_id}</div>
                            </td>
                            <td class="px-6 py-4 text-sm text-gray-600">${a.category}</td>
                            <td class="px-6 py-4 text-sm text-gray-600">${a.date}</td>
                        </tr>
                    `).join('');
                } else {
                    articlesTbody.innerHTML = '<tr><td colspan="3" class="px-6 py-4 text-center text-gray-400">暂无文章</td></tr>';
                }

                document.getElementById('loading').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');

            } catch (error) {
                console.error('Error loading stock data:', error);
                alert('加载数据失败');
            }
        }

        // 全局搜索
        const searchInput = document.getElementById('global-search');
        const suggestionsDiv = document.getElementById('search-suggestions');

        searchInput.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            if (query.length < 2) {
                suggestionsDiv.classList.add('hidden');
                return;
            }

            try {
                const response = await fetch(`/api/search/suggest?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.suggestions.length > 0) {
                    suggestionsDiv.innerHTML = data.suggestions.map(s => `
                        <div class="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b last:border-0" onclick="location.href='/stock/${s.code}'">
                            <div class="font-medium">${s.name} (${s.code})</div>
                            <div class="text-xs text-gray-500">${s.mention_count} 次提及</div>
                        </div>
                    `).join('');
                    suggestionsDiv.classList.remove('hidden');
                } else {
                    suggestionsDiv.classList.add('hidden');
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
                suggestionsDiv.classList.add('hidden');
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    location.href = `/search?q=${encodeURIComponent(query)}`;
                }
            }
        });

        loadStockData();
    </script>
</body>
</html>
"""

STOCKS_LIST_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>股票列表</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <div class="space-x-4">
                <a href="/" class="text-gray-600">仪表板</a>
                <a href="/stocks" class="text-blue-600">股票列表</a>
                <a href="/concepts" class="text-gray-600">概念大全</a>
                <a href="/search" class="text-gray-600">搜索</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold mb-6">📋 全部股票 ({{ total }})</h1>
        <div class="bg-white rounded-lg shadow">
            <table class="min-w-full">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left">代码</th>
                        <th class="px-6 py-3 text-left">名称</th>
                        <th class="px-6 py-3 text-left">板块</th>
                        <th class="px-6 py-3 text-left">提及</th>
                        <th class="px-6 py-3 text-left">概念</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in stocks %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="px-6 py-4 font-mono">{{ stock.code }}</td>
                        <td class="px-6 py-4">
                            <a href="/stock/{{ stock.code }}" class="text-blue-600 hover:underline">{{ stock.name }}</a>
                        </td>
                        <td class="px-6 py-4">{{ stock.board }}</td>
                        <td class="px-6 py-4">{{ stock.mention_count }}</td>
                        <td class="px-6 py-4">
                            <div class="flex flex-wrap gap-1">
                                {% for c in stock.concepts[:3] %}
                                <a href="/concept/{{ c }}" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded hover:bg-blue-200">{{ c }}</a>
                                {% endfor %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

CONCEPTS_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>概念大全</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <div class="space-x-4">
                <a href="/" class="text-gray-600">仪表板</a>
                <a href="/stocks" class="text-gray-600">股票列表</a>
                <a href="/concepts" class="text-blue-600">概念大全</a>
                <a href="/search" class="text-gray-600">搜索</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold mb-6">🏷️ 全部概念</h1>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {% for concept in concepts %}
                <a href="/concept/{{ concept.name }}" class="p-4 border rounded-lg hover:bg-blue-50 hover:border-blue-300">
                    <div class="font-medium text-blue-800">{{ concept.name }}</div>
                    <div class="text-sm text-gray-500 mt-1">{{ concept.count }} 只股票</div>
                </a>
                {% endfor %}
            </div>
        </div>
    </main>
</body>
</html>
"""

SEARCH_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>搜索</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <div class="space-x-4">
                <a href="/" class="text-gray-600">仪表板</a>
                <a href="/stocks" class="text-gray-600">股票列表</a>
                <a href="/concepts" class="text-gray-600">概念大全</a>
                <a href="/search" class="text-blue-600">搜索</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h1 class="text-2xl font-bold mb-4">🔍 高级搜索</h1>
            <div class="flex gap-4">
                <input type="text" id="search-input" placeholder="搜索：股票名称、代码、概念、产品、全文内容..." 
                       class="flex-1 px-4 py-3 border rounded-lg text-lg" value="{{ query or '' }}">
                <button onclick="performSearch()" class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                    搜索
                </button>
            </div>
            <div class="mt-4 text-sm text-gray-500">
                <i class="fas fa-info-circle"></i> 支持搜索股票名称、代码、概念标签、产品信息，以及详情文字全文
            </div>
        </div>

        {% if query %}
        <div id="results">
            <div class="mb-4">
                <h2 class="text-lg font-semibold">搜索结果 <span id="result-count" class="text-sm text-gray-500">({{ total }}条)</span></h2>
            </div>
            <div class="bg-white rounded-lg shadow">
                <table class="min-w-full">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left">股票</th>
                            <th class="px-6 py-3 text-left">提及次数</th>
                            <th class="px-6 py-3 text-left">匹配内容</th>
                            <th class="px-6 py-3 text-left">概念</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for result in results %}
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-6 py-4">
                                <a href="/stock/{{ result.code }}" class="text-blue-600 font-bold hover:underline">
                                    {{ result.name }} ({{ result.code }})
                                </a>
                            </td>
                            <td class="px-6 py-4">{{ result.mention_count }} 次</td>
                            <td class="px-6 py-4">
                                {% if result.match_type == 'stock' %}
                                <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">股票名称/代码</span>
                                {% elif result.match_type == 'concept' %}
                                <span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">概念：{{ result.matched_term }}</span>
                                {% elif result.match_type == 'product' %}
                                <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">产品：{{ result.matched_term }}</span>
                                {% elif result.match_type == 'fulltext' %}
                                <span class="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">全文匹配</span>
                                {% endif %}
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex flex-wrap gap-1">
                                    {% for c in result.concepts[:3] %}
                                    <a href="/concept/{{ c }}" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded hover:bg-blue-200">{{ c }}</a>
                                    {% endfor %}
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% else %}
        <div class="text-center py-12">
            <i class="fas fa-search text-6xl text-gray-300"></i>
            <p class="mt-4 text-gray-600">输入关键词开始搜索</p>
        </div>
        {% endif %}
    </main>

    <script>
        async function performSearch() {
            const query = document.getElementById('search-input').value.trim();
            if (query) {
                location.href = '/search?q=' + encodeURIComponent(query);
            }
        }

        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') performSearch();
        });
    </script>
</body>
</html>
"""

CONCEPT_DETAIL_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>概念：{{ concept }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-xl font-bold">📊 个股研究数据库</h1>
            <div class="space-x-4">
                <a href="/" class="text-gray-600">仪表板</a>
                <a href="/stocks" class="text-gray-600">股票列表</a>
                <a href="/concepts" class="text-blue-600">概念大全</a>
                <a href="/search" class="text-gray-600">搜索</a>
            </div>
        </div>
    </nav>
    <main class="max-w-7xl mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow mb-6">
            <div class="px-6 py-4 border-b">
                <h1 class="text-2xl font-bold">🏷️ 概念：{{ concept }}</h1>
                <p class="text-sm text-gray-500 mt-2">共 {{ stocks|length }} 只股票包含此概念</p>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow">
            <table class="min-w-full">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left">代码</th>
                        <th class="px-6 py-3 text-left">名称</th>
                        <th class="px-6 py-3 text-left">提及次数</th>
                        <th class="px-6 py-3 text-left">板块</th>
                        <th class="px-6 py-3 text-left">其他概念</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in stocks %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="px-6 py-4 font-mono">{{ stock.code }}</td>
                        <td class="px-6 py-4">
                            <a href="/stock/{{ stock.code }}" class="text-blue-600 hover:underline">{{ stock.name }}</a>
                        </td>
                        <td class="px-6 py-4">{{ stock.mention_count }} 次</td>
                        <td class="px-6 py-4">{{ stock.board }}</td>
                        <td class="px-6 py-4">
                            <div class="flex flex-wrap gap-1">
                                {% for c in stock.other_concepts[:5] %}
                                <a href="/concept/{{ c }}" class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded hover:bg-gray-200">{{ c }}</a>
                                {% endfor %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
</body>
</html>
"""

# ============== 路由 ==============

@app.route('/')
def dashboard():
    # 计算统计数据
    total_stocks = len(stocks_data)
    total_mentions = sum(s.get('mention_count', 0) for s in stocks_data.values())
    total_articles = len(set(
        f"{s['code']}_{a['article_id']}" 
        for s in stocks_data.values() 
        for a in s.get('articles', [])
    ))
    
    # Top 20 股票
    top_20 = sorted(
        [{'code': code, **data} for code, data in stocks_data.items()],
        key=lambda x: x['mention_count'],
        reverse=True
    )[:20]
    
    for i, stock in enumerate(top_20):
        stock['rank'] = i + 1
    
    return render_template_string(DASHBOARD_HTML,
        total_stocks=total_stocks,
        total_mentions=total_mentions,
        total_articles=total_articles,
        update_time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        top_20=top_20
    )

@app.route('/stocks')
def stocks_list():
    stocks = sorted(
        [{'code': code, **data} for code, data in stocks_data.items()],
        key=lambda x: x['mention_count'],
        reverse=True
    )
    
    return render_template_string(STOCKS_LIST_HTML, total=len(stocks), stocks=stocks)

@app.route('/stock/<code>')
def stock_detail(code):
    return render_template_string(STOCK_DETAIL_HTML, code=code)

@app.route('/concepts')
def concepts_list():
    concepts = [
        {'name': name, 'count': len(codes)}
        for name, codes in concepts_data.items()
    ]
    concepts.sort(key=lambda x: x['count'], reverse=True)
    
    return render_template_string(CONCEPTS_HTML, concepts=concepts)

@app.route('/concept/<concept_name>')
def concept_detail(concept_name):
    codes = concepts_data.get(concept_name, [])
    stocks = []
    
    for code in codes:
        if code in stocks_data:
            s = stocks_data[code]
            other_concepts = [c for c in s.get('concepts', []) if c != concept_name]
            stocks.append({
                'code': code,
                'name': s.get('name', ''),
                'mention_count': s.get('mention_count', 0),
                'board': s.get('board', ''),
                'other_concepts': other_concepts
            })
    
    stocks.sort(key=lambda x: x['mention_count'], reverse=True)
    
    return render_template_string(CONCEPT_DETAIL_HTML, 
        concept=concept_name, 
        stocks=stocks
    )

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    
    if query:
        # 搜索股票
        for code, data in stocks_data.items():
            if query.lower() in data.get('name', '').lower() or query in code:
                results.append({
                    'code': code,
                    'name': data.get('name', ''),
                    'mention_count': data.get('mention_count', 0),
                    'concepts': data.get('concepts', [])[:5],
                    'match_type': 'stock',
                    'matched_term': query
                })
        
        # 搜索概念
        for name, codes in concepts_data.items():
            if query.lower() in name.lower():
                for code in codes:
                    if code in stocks_data:
                        s = stocks_data[code]
                        if not any(r['code'] == code for r in results):
                            results.append({
                                'code': code,
                                'name': s.get('name', ''),
                                'mention_count': s.get('mention_count', 0),
                                'concepts': s.get('concepts', [])[:5],
                                'match_type': 'concept',
                                'matched_term': name
                            })
        
        # 全文搜索
        for term, codes in fulltext_data.items():
            if query.lower() in term.lower():
                for code in codes:
                    if code in stocks_data:
                        s = stocks_data[code]
                        if not any(r['code'] == code for r in results):
                            results.append({
                                'code': code,
                                'name': s.get('name', ''),
                                'mention_count': s.get('mention_count', 0),
                                'concepts': s.get('concepts', [])[:5],
                                'match_type': 'fulltext',
                                'matched_term': term
                            })
    
    results.sort(key=lambda x: x['mention_count'], reverse=True)
    
    return render_template_string(SEARCH_HTML, 
        query=query, 
        results=results, 
        total=len(results)
    )

@app.route('/api/stock/<code>')
def api_stock(code):
    if code not in stocks_data:
        return jsonify({'error': '股票不存在'})
    
    data = stocks_data[code]
    return jsonify({
        'code': code,
        'name': data.get('name', ''),
        'board': data.get('board', ''),
        'mention_count': data.get('mention_count', 0),
        'concepts': data.get('concepts', []),
        'industries': data.get('industries', []),
        'products': data.get('products', []),
        'articles': data.get('articles', []),
        'detail_texts': data.get('detail_texts', [])
    })

@app.route('/api/search/suggest')
def api_search_suggest():
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    suggestions = []
    
    # 股票名称建议
    for code, data in stocks_data.items():
        if query.lower() in data.get('name', '').lower():
            suggestions.append({
                'code': code,
                'name': data.get('name', ''),
                'mention_count': data.get('mention_count', 0)
            })
    
    return jsonify({'suggestions': suggestions[:10]})

# ============== 启动 ==============

@app.errorhandler(500)
def internal_error(error):
    return "服务器内部错误，请稍后重试", 500

@app.errorhandler(404)
def not_found(error):
    return "页面未找到", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 70)
    print("🚀 启动个股研究数据库 Web 界面 v3.0")
    print("=" * 70)
    print(f"\n🌐 访问地址：http://localhost:{port}")
    print("\n功能:")
    print("  ✅ 详情文字显示")
    print("  ✅ 全文搜索")
    print("  ✅ 概念标签链接")
    print("=" * 70)
    app.run(host='0.0.0.0', port=port, debug=False)
