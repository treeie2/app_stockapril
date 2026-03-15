#!/usr/bin/env python3
"""
Phase 6: Web 功能增强
- 全局搜索框（搜索第一、二层信息）
- 个股独立详情页（三层数据展示）
- 手动删除功能
"""

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime
import os

app = Flask(__name__, template_folder=Path(__file__).parent / "stocks" / "research_db" / "web" / "templates")

# ============== 数据路径 ==============

BASE_DIR = Path("/home/admin/openclaw/workspace/stocks/research_db")
MASTER_FILE = BASE_DIR / "master" / "stocks_master_extended.json"
MENTIONS_FILE = BASE_DIR / "sentiment" / "company_mentions_v2.json"
MARKET_FILE = BASE_DIR / "fundamentals" / "market_data.json"
DELETION_LOG_FILE = BASE_DIR / "web" / "deletion_log.json"

# ============== 数据加载 ==============

def load_json(file_path):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json(file_path, data):
    """保存 JSON 文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

# ============== 路由 ==============

@app.route('/')
def dashboard():
    """仪表板首页"""
    return render_template('dashboard.html')

@app.route('/api/dashboard')
def api_dashboard():
    """仪表板数据 API"""
    master = load_json(MASTER_FILE)
    mentions = load_json(MENTIONS_FILE)
    
    if not master or not mentions:
        return jsonify({"error": "数据加载失败"})
    
    stats = {
        "total_stocks": master.get("total_stocks", 0),
        "total_mentions": mentions.get("statistics", {}).get("meaningful_mentions", 0),
        "total_companies": len(mentions.get("companies", {})),
        "total_articles": mentions.get("statistics", {}).get("total_articles", 731),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    companies = mentions.get("companies", {})
    top_stocks = sorted(
        companies.items(),
        key=lambda x: len(x[1].get("mentions", [])),
        reverse=True
    )[:10]
    
    top_10 = [
        {
            "rank": i + 1,
            "code": code,
            "name": data.get("name", ""),
            "mentions": len(data.get("mentions", [])),
            "with_target": data.get("summary", {}).get("with_target", 0),
            "concepts": data.get("summary", {}).get("concepts", [])[:3]
        }
        for i, (code, data) in enumerate(top_stocks)
    ]
    
    industry_dist = {}
    for stock in master.get("stocks", [])[:100]:
        industry = stock.get("industry", "其他")
        industry_dist[industry] = industry_dist.get(industry, 0) + 1
    
    return jsonify({
        "stats": stats,
        "top_10": top_10,
        "industry_distribution": industry_dist
    })

@app.route('/stocks')
def stocks_list():
    """股票列表页"""
    return render_template('stocks.html')

@app.route('/api/stocks')
def api_stocks():
    """股票列表 API"""
    master = load_json(MASTER_FILE)
    mentions = load_json(MENTIONS_FILE)
    
    if not master:
        return jsonify({"error": "数据加载失败"})
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    
    stocks = master.get("stocks", [])
    
    if search:
        stocks = [s for s in stocks if search.lower() in s.get("name", "").lower() or search in s.get("code", "")]
    
    if industry:
        stocks = [s for s in stocks if industry in s.get("industry", "")]
    
    total = len(stocks)
    start = (page - 1) * limit
    end = start + limit
    
    companies = mentions.get("companies", {}) if mentions else {}
    
    result_stocks = []
    for stock in stocks[start:end]:
        code = stock.get("code")
        mention_data = companies.get(code, {})
        
        result_stocks.append({
            **stock,
            "mention_count": len(mention_data.get("mentions", [])),
            "with_target": mention_data.get("summary", {}).get("with_target", 0),
            "concepts": mention_data.get("summary", {}).get("concepts", [])[:5]
        })
    
    return jsonify({
        "total": total,
        "page": page,
        "limit": limit,
        "stocks": result_stocks
    })

@app.route('/stock/<code>')
def stock_detail(code):
    """股票详情页"""
    return render_template('stock_detail.html', code=code)

@app.route('/api/stock/<code>')
def api_stock_detail(code):
    """股票详情 API - 完整三层数据"""
    mentions = load_json(MENTIONS_FILE)
    master = load_json(MASTER_FILE)
    
    if not mentions:
        return jsonify({"error": "数据加载失败"})
    
    companies = mentions.get("companies", {})
    stock_data = companies.get(code)
    
    if not stock_data:
        return jsonify({"error": "股票未找到"}), 404
    
    # 第一层：基本信息
    basic_info = {
        "code": code,
        "name": stock_data.get("name", ""),
        "mention_count": stock_data.get("mention_count", 0),
        "summary": stock_data.get("summary", {})
    }
    
    # 从 master 获取更多信息
    if master:
        for s in master.get("stocks", []):
            if s.get("code") == code:
                basic_info["industry"] = s.get("industry", "")
                basic_info["board"] = s.get("board", "")
                break
    
    # 第二层：概念、产品、产业链
    layer2 = {
        "concepts": stock_data.get("summary", {}).get("concepts", []),
        "products": list(set(stock_data.get("summary", {}).get("products", []))),
        "events": stock_data.get("summary", {}).get("events", {}),
        "supply_chain": stock_data.get("summary", {}).get("supply_chain", [])
    }
    
    # 第三层：所有提及（按时间排序）
    mentions_list = stock_data.get("mentions", [])
    mentions_list.sort(key=lambda x: x.get("article_id", ""), reverse=True)
    
    return jsonify({
        "basic": basic_info,
        "layer2": layer2,
        "mentions": mentions_list,
        "total_mentions": len(mentions_list)
    })

@app.route('/api/stock/<code>/delete', methods=['POST'])
def delete_mention(code):
    """删除特定提及记录"""
    data = request.json
    article_id = data.get('article_id')
    reason = data.get('reason', '用户手动删除')
    
    if not article_id:
        return jsonify({"error": "缺少 article_id"}), 400
    
    mentions = load_json(MENTIONS_FILE)
    if not mentions:
        return jsonify({"error": "数据加载失败"})
    
    companies = mentions.get("companies", {})
    stock_data = companies.get(code)
    
    if not stock_data:
        return jsonify({"error": "股票未找到"}), 404
    
    # 找到并删除提及
    original_count = len(stock_data.get("mentions", []))
    stock_data["mentions"] = [
        m for m in stock_data.get("mentions", [])
        if m.get("article_id") != article_id
    ]
    new_count = len(stock_data["mentions"])
    
    if original_count == new_count:
        return jsonify({"error": "未找到该提及记录"}), 404
    
    # 更新提及计数
    stock_data["mention_count"] = new_count
    
    # 更新 summary
    if stock_data.get("summary", {}):
        stock_data["summary"]["total_mentions"] = new_count
    
    # 保存
    if save_json(MENTIONS_FILE, mentions):
        # 记录删除日志
        log_deletion(code, article_id, reason)
        return jsonify({
            "success": True,
            "message": f"已删除提及记录",
            "article_id": article_id,
            "new_count": new_count
        })
    else:
        return jsonify({"error": "保存失败"}), 500

def log_deletion(code, article_id, reason):
    """记录删除日志"""
    log = load_json(DELETION_LOG_FILE) or {"deletions": []}
    log["deletions"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stock_code": code,
        "article_id": article_id,
        "reason": reason
    })
    save_json(DELETION_LOG_FILE, log)

@app.route('/api/deletion-log')
def get_deletion_log():
    """获取删除日志"""
    log = load_json(DELETION_LOG_FILE) or {"deletions": []}
    return jsonify(log)

@app.route('/search')
def search():
    """搜索页面"""
    return render_template('search.html')

@app.route('/api/search')
def api_search():
    """搜索 API - 支持第一、二层搜索"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 50, type=int)
    search_type = request.args.get('type', 'all')  # all, stock, concept, product
    
    if not query:
        return jsonify({"error": "查询为空"})
    
    mentions = load_json(MENTIONS_FILE)
    master = load_json(MASTER_FILE)
    
    if not mentions:
        return jsonify({"error": "数据加载失败"})
    
    results = []
    companies = mentions.get("companies", {})
    
    # 搜索类型 1: 股票名称/代码（第一层）
    if search_type in ['all', 'stock']:
        for code, data in companies.items():
            name = data.get("name", "")
            if query.lower() in name.lower() or query in code:
                relevance = 1.0 if query == name or query == code else 0.9
                results.append({
                    "type": "stock",
                    "code": code,
                    "name": name,
                    "relevance": relevance,
                    "mention_count": len(data.get("mentions", [])),
                    "concepts": data.get("summary", {}).get("concepts", [])[:3]
                })
    
    # 搜索类型 2: 概念标签（第二层）
    if search_type in ['all', 'concept']:
        for code, data in companies.items():
            concepts = data.get("summary", {}).get("concepts", [])
            if any(query.lower() in c.lower() for c in concepts):
                matched_concepts = [c for c in concepts if query.lower() in c.lower()]
                results.append({
                    "type": "concept",
                    "code": code,
                    "name": data.get("name", ""),
                    "matched": matched_concepts,
                    "relevance": 0.8,
                    "mention_count": len(data.get("mentions", []))
                })
    
    # 搜索类型 3: 产品（第二层）
    if search_type in ['all', 'product']:
        for code, data in companies.items():
            products = data.get("summary", {}).get("products", [])
            if any(query.lower() in p.lower() for p in products):
                matched_products = [p for p in products if query.lower() in p.lower()]
                results.append({
                    "type": "product",
                    "code": code,
                    "name": data.get("name", ""),
                    "matched": matched_products,
                    "relevance": 0.7,
                    "mention_count": len(data.get("mentions", []))
                })
    
    # 搜索类型 4: 行业（第二层）
    if search_type in ['all', 'industry']:
        if master:
            for stock in master.get("stocks", []):
                industry = stock.get("industry", "")
                if query.lower() in industry.lower():
                    code = stock.get("code")
                    company_data = companies.get(code, {})
                    results.append({
                        "type": "industry",
                        "code": code,
                        "name": stock.get("name", ""),
                        "industry": industry,
                        "relevance": 0.75,
                        "mention_count": len(company_data.get("mentions", []))
                    })
    
    # 去重并按相关度排序
    seen = set()
    unique_results = []
    for r in results:
        key = f"{r['type']}_{r['code']}"
        if key not in seen:
            seen.add(key)
            unique_results.append(r)
    
    unique_results.sort(key=lambda x: (x.get('relevance', 0), x.get('mention_count', 0)), reverse=True)
    
    return jsonify({
        "total": len(unique_results),
        "query": query,
        "results": unique_results[:limit]
    })

@app.route('/api/search/suggest')
def api_search_suggest():
    """搜索建议 API"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({"suggestions": []})
    
    mentions = load_json(MENTIONS_FILE)
    if not mentions:
        return jsonify({"suggestions": []})
    
    suggestions = []
    companies = mentions.get("companies", {})
    
    # 股票名称建议
    for code, data in companies.items():
        name = data.get("name", "")
        if query.lower() in name.lower():
            suggestions.append({
                "type": "stock",
                "text": f"{name} ({code})",
                "code": code
            })
    
    # 概念建议
    all_concepts = set()
    for data in companies.values():
        concepts = data.get("summary", {}).get("concepts", [])
        all_concepts.update(concepts)
    
    for concept in all_concepts:
        if query.lower() in concept.lower():
            suggestions.append({
                "type": "concept",
                "text": f"概念：{concept}"
            })
    
    return jsonify({
        "suggestions": suggestions[:10]
    })

# ============== 启动 ==============

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 启动个股研究数据库 Web 界面 (Phase 6)")
    print("=" * 70)
    print(f"\n📁 数据目录：{BASE_DIR}")
    print(f"📊 功能:")
    print(f"   ✅ 全局搜索框（第一、二层）")
    print(f"   ✅ 个股详情页（三层数据）")
    print(f"   ✅ 手动删除功能")
    print(f"\n🌐 访问地址：http://localhost:5000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
