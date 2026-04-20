#!/usr/bin/env python3
"""
对比今天更新的个股的收盘市值和目标市值
接入东方财富 API 获取实时市值数据
"""
import json
import requests
from pathlib import Path
from datetime import datetime
import time

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
OUTPUT_FILE = Path("e:/github/stock-research-backup/data/reports/market_cap_comparison_today.json")
REPORT_MD_FILE = Path("e:/github/stock-research-backup/data/reports/market_cap_comparison_today.md")

def get_market_cap_from_eastmoney(code):
    """
    从东方财富获取实时市值（单位：亿元）
    API: https://push2.eastmoney.com/api/qt/stock/get
    """
    try:
        # 判断交易所
        if code.startswith('6'):
            market = "1"  # 上交所
        else:
            market = "0"  # 深交所
        
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': f'{market}.{code}',
            'fields': 'f116,f117,f118,f119,f120,f121,f122,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('data'):
            # f116: 总市值 (元)
            market_cap = data['data'].get('f116')
            if market_cap:
                # 转换为亿元
                return float(market_cap) / 100000000
        return None
    except Exception as e:
        print(f"  ⚠️ 获取 {code} 市值失败：{str(e)[:50]}")
        return None

def get_market_cap_from_sina(code):
    """
    从新浪财经获取实时市值（单位：亿元）
    API: https://hq.sinajs.cn/list=[市场缩写][股票代码]
    """
    try:
        # 判断交易所
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        url = f"https://hq.sinajs.cn/list={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gbk'
        
        # 解析返回数据
        # var hq_str_sh600000="浦发银行，8.50,8.49,8.47,8.51,8.46,8.47,8.48,3456789,29123456,..."
        data = response.text.strip()
        if '=' in data:
            parts = data.split('=')[1].strip('"').split(',')
            if len(parts) >= 45:
                # 第 45 个字段是总市值（元）
                market_cap = parts[44]
                if market_cap and market_cap != 'null':
                    return float(market_cap) / 100000000  # 转换为亿元
        return None
    except Exception as e:
        print(f"  ⚠️ 获取 {code} 市值失败：{str(e)[:50]}")
        return None

def get_market_cap(code, retry=3):
    """
    获取股票市值（优先使用东方财富，失败则使用新浪财经）
    """
    for i in range(retry):
        # 先尝试东方财富
        market_cap = get_market_cap_from_eastmoney(code)
        if market_cap:
            return market_cap
        
        # 失败则尝试新浪财经
        market_cap = get_market_cap_from_sina(code)
        if market_cap:
            return market_cap
        
        # 等待后重试
        if i < retry - 1:
            time.sleep(1)
    
    return None

def load_stocks():
    """加载股票数据"""
    if not MASTER_FILE.exists():
        print(f"❌ 股票数据文件不存在：{MASTER_FILE}")
        return {}
    
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('stocks', {})

def extract_today_stocks(stocks):
    """提取今天更新的有目标市值的股票"""
    today = datetime.now().strftime('%Y-%m-%d')
    today_stocks = []
    
    for code, stock in stocks.items():
        articles = stock.get('articles', [])
        target_valuations = []
        
        for article in articles:
            article_date = article.get('date', '')
            target_vals = article.get('target_valuation', [])
            
            # 只统计今天的
            if article_date == today and target_vals:
                for target_val in target_vals:
                    # 解析目标市值
                    target_market_cap = parse_valuation(target_val)
                    if target_market_cap:
                        target_valuations.append({
                            'text': target_val,
                            'value': target_market_cap
                        })
        
        if target_valuations:
            today_stocks.append({
                'code': code,
                'name': stock.get('name', ''),
                'industry': stock.get('industry', ''),
                'target_valuations': target_valuations,
                'avg_target': sum(tv['value'] for tv in target_valuations) / len(target_valuations),
                'current_market_cap': None,
                'diff': None,
                'diff_percent': None
            })
    
    return today_stocks

def parse_valuation(valuation_text):
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
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', value)
        if match:
            return float(match.group(1))
    return None

def generate_report(stocks_data):
    """生成对比报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'date': today,
        'total_stocks': len(stocks_data),
        'stocks': stocks_data
    }
    
    # 保存 JSON 报告
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成 Markdown 报告
    md_content = generate_markdown_report(stocks_data, today)
    with open(REPORT_MD_FILE, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✅ 报告已生成:")
    print(f"   JSON: {OUTPUT_FILE}")
    print(f"   Markdown: {REPORT_MD_FILE}")
    
    return report

def generate_markdown_report(stocks_data, date):
    """生成 Markdown 格式报告"""
    lines = []
    lines.append(f"# 今天 ({date}) 更新个股 - 市值对比报告")
    lines.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**股票数量**: {len(stocks_data)}")
    lines.append("\n---\n")
    
    # 表头
    lines.append("## 市值对比表")
    lines.append("\n| 代码 | 名称 | 行业 | 目标市值 (亿) | 当前市值 (亿) | 差异 (亿) | 差异 (%) | 估值来源 |")
    lines.append("|------|------|------|---------------|---------------|-----------|----------|----------|")
    
    # 按差异百分比排序（从大到小）
    sorted_stocks = sorted(
        [s for s in stocks_data if s.get('current_market_cap')],
        key=lambda x: x.get('diff_percent') or 0,
        reverse=True
    )
    
    for stock in sorted_stocks:
        code = stock['code']
        name = stock['name']
        industry = stock.get('industry', '')[:15]
        avg_target = stock.get('avg_target')
        current = stock.get('current_market_cap')
        diff = stock.get('diff')
        diff_percent = stock.get('diff_percent')
        
        # 格式化估值来源
        val_sources = [tv['text'][:20] for tv in stock.get('target_valuations', [])]
        val_source_str = '; '.join(val_sources[:2]) if val_sources else '-'
        if len(val_sources) > 2:
            val_source_str += f'... (共{len(val_sources)}条)'
        
        # 格式化数值
        target_str = f"{avg_target:.2f}" if avg_target is not None else '-'
        current_str = f"{current:.2f}" if current is not None else '-'
        diff_str = f"{diff:+.2f}" if diff is not None else '-'
        diff_percent_str = f"{diff_percent:+.2f}%" if diff_percent is not None else '-'
        
        lines.append(f"| {code} | {name} | {industry} | {target_str} | {current_str} | {diff_str} | {diff_percent_str} | {val_source_str} |")
    
    # 统计信息
    lines.append("\n---\n")
    lines.append("## 统计信息")
    
    stocks_with_data = [s for s in stocks_data if s.get('current_market_cap')]
    
    lines.append(f"\n- **有市值数据的股票**: {len(stocks_with_data)} / {len(stocks_data)}")
    
    if stocks_with_data:
        # 计算统计指标
        avg_target = sum(s.get('avg_target', 0) or 0 for s in stocks_with_data) / len(stocks_with_data)
        avg_current = sum(s.get('current_market_cap', 0) or 0 for s in stocks_with_data) / len(stocks_with_data)
        
        upside_stocks = [s for s in stocks_with_data if (s.get('diff_percent') or 0) > 0]
        downside_stocks = [s for s in stocks_with_data if (s.get('diff_percent') or 0) <= 0]
        
        lines.append(f"- **平均目标市值**: {avg_target:.2f} 亿")
        lines.append(f"- **平均当前市值**: {avg_current:.2f} 亿")
        lines.append(f"- **上涨空间股票**: {len(upside_stocks)} 只")
        lines.append(f"- **下跌风险股票**: {len(downside_stocks)} 只")
        
        # 找出上涨空间最大的 3 只
        if upside_stocks:
            top3_upside = sorted(upside_stocks, key=lambda x: x.get('diff_percent') or 0, reverse=True)[:3]
            lines.append(f"\n### 📈 上涨空间 TOP3")
            for i, stock in enumerate(top3_upside, 1):
                lines.append(f"{i}. **{stock['name']}** ({stock['code']}): {stock.get('diff_percent', 0):.2f}%")
        
        # 找出下跌风险最大的 3 只
        if downside_stocks:
            top3_downside = sorted(downside_stocks, key=lambda x: x.get('diff_percent') or 0)[:3]
            lines.append(f"\n### 📉 下跌风险 TOP3")
            for i, stock in enumerate(top3_downside, 1):
                lines.append(f"{i}. **{stock['name']}** ({stock['code']}): {stock.get('diff_percent', 0):.2f}%")
    
    # 使用说明
    lines.append("\n---\n")
    lines.append("## 数据说明")
    lines.append("\n- **目标市值**: 来自文章中的估值分析")
    lines.append("- **当前市值**: 来自东方财富/新浪财经实时数据")
    lines.append("- **差异**: 目标市值 - 当前市值")
    lines.append("- **差异 (%)**: (差异 / 当前市值) × 100%")
    lines.append("\n**注意**: 市值数据为实时数据，可能因市场波动而变化")
    
    return '\n'.join(lines)

def main():
    print("🚀 开始生成今天更新个股的市值对比报告...\n")
    
    # 1. 加载股票数据
    print("1️⃣ 加载股票数据...")
    stocks = load_stocks()
    print(f"   共加载 {len(stocks)} 只股票")
    
    # 2. 提取今天更新的股票
    print("\n2️⃣ 提取今天 ({}) 更新的股票...".format(datetime.now().strftime('%Y-%m-%d')))
    today_stocks = extract_today_stocks(stocks)
    print(f"   找到 {len(today_stocks)} 只有目标市值的股票")
    
    if not today_stocks:
        print("\n❌ 今天没有更新的股票有目标市值")
        return
    
    # 3. 获取实时市值
    print("\n3️⃣ 获取实时市值数据...")
    for i, stock in enumerate(today_stocks, 1):
        code = stock['code']
        print(f"  [{i}/{len(today_stocks)}] {code} {stock['name']}...", end=' ')
        
        market_cap = get_market_cap(code)
        stock['current_market_cap'] = market_cap
        
        if market_cap:
            # 计算差异
            avg_target = stock['avg_target']
            diff = avg_target - market_cap
            diff_percent = (diff / market_cap) * 100 if market_cap > 0 else 0
            
            stock['diff'] = diff
            stock['diff_percent'] = diff_percent
            
            print(f"✅ {market_cap:.2f}亿 (目标：{avg_target:.2f}亿，差异：{diff_percent:+.2f}%)")
        else:
            print(f"❌ 获取失败")
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 4. 生成报告
    print("\n4️⃣ 生成报告...")
    report = generate_report(today_stocks)
    
    # 5. 显示摘要
    print("\n5️⃣ 报告摘要:")
    print("-" * 80)
    
    stocks_with_data = [s for s in today_stocks if s.get('current_market_cap')]
    if stocks_with_data:
        upside_stocks = [s for s in stocks_with_data if (s.get('diff_percent') or 0) > 0]
        downside_stocks = [s for s in stocks_with_data if (s.get('diff_percent') or 0) <= 0]
        
        print(f"   有数据：{len(stocks_with_data)} 只")
        print(f"   上涨空间：{len(upside_stocks)} 只")
        print(f"   下跌风险：{len(downside_stocks)} 只")
        
        if upside_stocks:
            top_upside = max(upside_stocks, key=lambda x: x.get('diff_percent') or 0)
            print(f"\n   📈 上涨空间最大：{top_upside['name']} ({top_upside['code']}): {top_upside.get('diff_percent', 0):+.2f}%")
        
        if downside_stocks:
            top_downside = min(downside_stocks, key=lambda x: x.get('diff_percent') or 0)
            print(f"   📉 下跌风险最大：{top_downside['name']} ({top_downside['code']}): {top_downside.get('diff_percent', 0):+.2f}%")
    
    print("\n🎉 完成！")
    print(f"\n📄 查看报告:")
    print(f"   JSON: {OUTPUT_FILE}")
    print(f"   Markdown: {REPORT_MD_FILE}")

if __name__ == '__main__':
    main()
