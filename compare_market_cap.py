#!/usr/bin/env python3
"""
对比目标市值和当前市值
从 stocks_master.json 中提取所有有目标市值的股票，并生成对比报告
"""
import json
from pathlib import Path
from datetime import datetime
import requests

# 文件路径
MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
OUTPUT_FILE = Path("e:/github/stock-research-backup/data/reports/market_cap_comparison.json")
REPORT_MD_FILE = Path("e:/github/stock-research-backup/data/reports/market_cap_comparison.md")

# 获取当前市值的 API（如果需要实时数据）
# 这里使用示例数据，实际使用时可以接入新浪财经、东方财富等 API
def get_current_market_cap(code):
    """
    获取当前市值（单位：亿元）
    实际使用时可以接入实时 API
    """
    # 这里返回 None，表示需要从外部 API 获取
    # 示例：可以接入 akshare、tushare 等库
    return None

def load_stocks():
    """加载股票数据"""
    if not MASTER_FILE.exists():
        print(f"❌ 股票数据文件不存在：{MASTER_FILE}")
        return {}
    
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('stocks', {})

def extract_target_valuations(stocks):
    """提取有目标市值的股票"""
    target_stocks = []
    
    for code, stock in stocks.items():
        # 检查 valuation 字段
        valuation = stock.get('valuation', {})
        target_market_cap = valuation.get('target_market_cap') if valuation else None
        
        # 检查文章中的 target_valuation
        articles = stock.get('articles', [])
        article_valuations = []
        for article in articles:
            target_vals = article.get('target_valuation', [])
            if target_vals:
                article_valuations.extend(target_vals)
        
        # 如果有目标市值
        if target_market_cap or article_valuations:
            stock_info = {
                'code': code,
                'name': stock.get('name', ''),
                'industry': stock.get('industry', ''),
                'target_market_cap': target_market_cap,
                'article_valuations': article_valuations,
                'current_market_cap': None,  # 待填充
                'market_cap_diff': None,  # 待计算
                'market_cap_diff_percent': None,  # 待计算
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            target_stocks.append(stock_info)
    
    return target_stocks

def parse_valuation_text(valuation_text):
    """解析估值文本，提取市值数据"""
    import re
    
    if not valuation_text:
        return None
    
    # 如果是数字，直接返回
    if isinstance(valuation_text, (int, float)):
        return float(valuation_text)
    
    # 尝试匹配"目标市值 XXX 亿"
    match = re.search(r'目标市值.*?(\d+(?:\.\d+)?)\s*亿', valuation_text)
    if match:
        return float(match.group(1))
    
    # 尝试匹配"XXX 亿"
    match = re.search(r'(\d+(?:\.\d+)?)\s*亿', valuation_text)
    if match:
        return float(match.group(1))
    
    return None

def safe_float(value):
    """安全地转换为浮点数"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # 尝试从字符串中提取数字
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
    return None

def generate_report(stocks_data):
    """生成市值对比报告"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_stocks': len(stocks_data),
        'stocks': stocks_data
    }
    
    # 保存 JSON 报告
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成 Markdown 报告
    md_content = generate_markdown_report(stocks_data)
    with open(REPORT_MD_FILE, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 报告已生成:")
    print(f"   JSON: {OUTPUT_FILE}")
    print(f"   Markdown: {REPORT_MD_FILE}")
    
    return report

def generate_markdown_report(stocks_data):
    """生成 Markdown 格式报告"""
    lines = []
    lines.append("# 目标市值 vs 当前市值对比报告")
    lines.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**股票数量**: {len(stocks_data)}")
    lines.append("\n---\n")
    
    # 表头
    lines.append("## 市值对比表")
    lines.append("\n| 代码 | 名称 | 行业 | 目标市值 (亿) | 当前市值 (亿) | 差异 (亿) | 差异 (%) | 文章估值 |")
    lines.append("|------|------|------|---------------|---------------|-----------|----------|----------|")
    
    # 按目标市值排序
    sorted_stocks = sorted(
        [s for s in stocks_data if s.get('target_market_cap')],
        key=lambda x: x.get('target_market_cap') or 0,
        reverse=True
    )
    
    for stock in sorted_stocks:
        code = stock['code']
        name = stock['name']
        industry = stock.get('industry', '')[:20]  # 截断行业名称
        target = safe_float(stock.get('target_market_cap'))
        current = safe_float(stock.get('current_market_cap'))
        
        # 计算差异
        diff = None
        diff_percent = None
        if target is not None and current is not None and current > 0:
            diff = target - current
            diff_percent = (diff / current) * 100
        
        # 格式化文章估值
        article_vals = stock.get('article_valuations', [])
        article_val_str = ', '.join([str(v) for v in article_vals[:2]]) if article_vals else '-'
        if len(article_vals) > 2:
            article_val_str += f'... (共{len(article_vals)}条)'
        
        # 格式化数值
        target_str = f"{target:.2f}" if target is not None else '-'
        current_str = f"{current:.2f}" if current is not None else '-'
        diff_str = f"{diff:+.2f}" if diff is not None else '-'
        diff_percent_str = f"{diff_percent:+.2f}%" if diff_percent is not None else '-'
        
        lines.append(f"| {code} | {name} | {industry} | {target_str} | {current_str} | {diff_str} | {diff_percent_str} | {article_val_str} |")
    
    # 统计信息
    lines.append("\n---\n")
    lines.append("## 统计信息")
    
    stocks_with_target = [s for s in stocks_data if s.get('target_market_cap')]
    stocks_with_current = [s for s in stocks_data if s.get('current_market_cap')]
    
    lines.append(f"\n- **有目标市值的股票**: {len(stocks_with_target)} 只")
    lines.append(f"- **有当前市值的股票**: {len(stocks_with_current)} 只")
    
    if stocks_with_current:
        avg_target = sum(s.get('target_market_cap', 0) or 0 for s in stocks_with_target) / len(stocks_with_target) if stocks_with_target else 0
        avg_current = sum(s.get('current_market_cap', 0) or 0 for s in stocks_with_current) / len(stocks_with_current)
        
        lines.append(f"- **平均目标市值**: {avg_target:.2f} 亿")
        lines.append(f"- **平均当前市值**: {avg_current:.2f} 亿")
    
    # 使用说明
    lines.append("\n---\n")
    lines.append("## 使用说明")
    lines.append("\n1. **目标市值**: 来自文章的估值分析或手动设置的目标市值")
    lines.append("2. **当前市值**: 需要从实时数据源获取（如接入 akshare、tushare 等）")
    lines.append("3. **差异**: 目标市值 - 当前市值")
    lines.append("4. **差异 (%)**: (差异 / 当前市值) × 100%")
    lines.append("\n### 后续优化")
    lines.append("- 接入实时市值 API（如 akshare、tushare、东方财富等）")
    lines.append("- 添加定时更新功能")
    lines.append("- 导出 Excel 格式报告")
    
    return '\n'.join(lines)

def main():
    print("🚀 开始生成市值对比报告...\n")
    
    # 1. 加载股票数据
    print("1️⃣ 加载股票数据...")
    stocks = load_stocks()
    print(f"   共加载 {len(stocks)} 只股票")
    
    # 2. 提取有目标市值的股票
    print("\n2️⃣ 提取有目标市值的股票...")
    target_stocks = extract_target_valuations(stocks)
    print(f"   找到 {len(target_stocks)} 只有目标市值的股票")
    
    # 3. 生成报告
    print("\n3️⃣ 生成报告...")
    report = generate_report(target_stocks)
    
    # 4. 显示前 10 只股票
    print("\n4️⃣ 前 10 只股票预览:")
    print("-" * 80)
    for i, stock in enumerate(target_stocks[:10], 1):
        target = safe_float(stock.get('target_market_cap'))
        target_str = f"{target:.2f}亿" if target is not None else '-'
        print(f"  {i:2d}. {stock['code']} {stock['name']}: 目标市值 {target_str}")
    
    print("\n🎉 完成！")
    print(f"\n📄 查看报告:")
    print(f"   JSON: {OUTPUT_FILE}")
    print(f"   Markdown: {REPORT_MD_FILE}")

if __name__ == '__main__':
    main()
