"""
ModelScope 创空间入口 - 使用 Gradio 包装 Flask 应用
"""
import gradio as gr
import requests
import json

# 加载股票数据
import os
from pathlib import Path

MASTER_FILE = Path(__file__).parent / 'data' / 'master' / 'stocks_master.json'

stocks = {}
concepts = {}

def load_data():
    global stocks, concepts
    try:
        if MASTER_FILE.exists():
            with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            stocks_list = data.get('stocks', [])
            stocks = {s['code']: s for s in stocks_list if 'code' in s}
            
            concepts = {}
            for stock in stocks_list:
                for concept in stock.get('concepts', []):
                    if concept not in concepts:
                        concepts[concept] = {'stocks': []}
                    concepts[concept]['stocks'].append(stock['code'])
            
            print(f"✅ 加载 {len(stocks)} 只股票，{len(concepts)} 个概念")
        else:
            print(f"⚠️ 数据文件不存在")
            stocks, concepts = {}, {}
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        stocks, concepts = {}, {}

load_data()

# 获取热门股票
def get_hot_stocks():
    hot = sorted([{'code': c, **d} for c, d in stocks.items()],
                key=lambda x: x.get('mention_count', 0),
                reverse=True)[:20]
    result = "## 🔥 热门股票 TOP 20\n\n"
    for i, s in enumerate(hot, 1):
        result += f"{i}. **{s['name']}** ({s['code']}) - {s.get('industry', 'N/A')[:20]}... - 提及: {s.get('mention_count', 0)}\n"
    return result

# 搜索股票
def search_stock(query):
    if not query:
        return "请输入搜索关键词"
    
    results = []
    for code, stock in stocks.items():
        name = stock.get('name', '')
        if query.lower() in name.lower() or query in code:
            results.append({
                'code': code,
                'name': name,
                'industry': stock.get('industry', ''),
                'concepts': ', '.join(stock.get('concepts', [])[:5]),
                'mention_count': stock.get('mention_count', 0)
            })
    
    if not results:
        return f"未找到包含 '{query}' 的股票"
    
    result_text = f"## 搜索结果: {query}\n\n"
    result_text += f"共找到 {len(results)} 只股票\n\n"
    
    for r in results[:30]:
        result_text += f"### {r['name']} ({r['code']})\n"
        result_text += f"- 行业: {r['industry'][:30] if r['industry'] else 'N/A'}...\n"
        result_text += f"- 概念: {r['concepts']}\n"
        result_text += f"- 提及次数: {r['mention_count']}\n\n"
    
    return result_text

# 获取概念列表
def get_concepts():
    concept_list = []
    for name, data in concepts.items():
        concept_list.append({
            'name': name,
            'count': len(data.get('stocks', []))
        })
    concept_list.sort(key=lambda x: x['count'], reverse=True)
    
    result = "## 🏷️ 概念板块 TOP 50\n\n"
    for i, c in enumerate(concept_list[:50], 1):
        result += f"{i}. **{c['name']}** - {c['count']} 只股票\n"
    return result

# 获取股票详情
def get_stock_detail(code):
    if not code:
        return "请输入股票代码"
    
    code = code.strip()
    if code not in stocks:
        return f"未找到股票代码: {code}"
    
    stock = stocks[code]
    result = f"## 📈 {stock.get('name', '')} ({code})\n\n"
    result += f"**行业**: {stock.get('industry', 'N/A')}\n\n"
    result += f"**板块**: {stock.get('board', 'N/A')}\n\n"
    result += f"**概念**: {', '.join(stock.get('concepts', []))}\n\n"
    result += f"**提及次数**: {stock.get('mention_count', 0)}\n\n"
    
    articles = stock.get('articles', [])
    if articles:
        result += f"**相关文章** ({len(articles)} 篇):\n\n"
        for i, article in enumerate(articles[:5], 1):
            result += f"{i}. **{article.get('title', 'N/A')}**\n"
            result += f"   - 日期: {article.get('date', 'N/A')}\n"
            result += f"   - 来源: {article.get('source', 'N/A')}\n"
            insights = article.get('insights', [])
            if insights:
                result += f"   - 洞察: {insights[0][:50] if insights[0] else 'N/A'}...\n"
            result += "\n"
    
    return result

# 创建 Gradio 界面
with gr.Blocks(title="股票研究数据库", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📊 股票研究数据库")
    gr.Markdown("基于 AI 分析的股票投资研究工具，包含 3152 只 A 股股票数据")
    
    with gr.Tab("🔥 热门股票"):
        hot_output = gr.Markdown()
        hot_btn = gr.Button("刷新热门股票", variant="primary")
        hot_btn.click(get_hot_stocks, outputs=hot_output)
        # 初始加载
        demo.load(get_hot_stocks, outputs=hot_output)
    
    with gr.Tab("🔍 股票搜索"):
        with gr.Row():
            search_input = gr.Textbox(label="搜索关键词", placeholder="输入股票名称或代码...")
            search_btn = gr.Button("搜索", variant="primary")
        search_output = gr.Markdown()
        search_btn.click(search_stock, inputs=search_input, outputs=search_output)
    
    with gr.Tab("📈 股票详情"):
        with gr.Row():
            code_input = gr.Textbox(label="股票代码", placeholder="例如: 000001")
            detail_btn = gr.Button("查询", variant="primary")
        detail_output = gr.Markdown()
        detail_btn.click(get_stock_detail, inputs=code_input, outputs=detail_output)
    
    with gr.Tab("🏷️ 概念板块"):
        concept_output = gr.Markdown()
        concept_btn = gr.Button("刷新概念列表", variant="primary")
        concept_btn.click(get_concepts, outputs=concept_output)
        # 初始加载
        demo.load(get_concepts, outputs=concept_output)
    
    gr.Markdown("---")
    gr.Markdown("💡 提示: 数据包含行业分类、概念标签、AI 投资洞察等信息")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
