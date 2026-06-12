"""
Extract structured valuation data from article target_valuation texts
and populate stock-level valuation fields.

Usage: python extract_valuation.py
"""
import json, re, os, copy
from collections import defaultdict

MASTER_PATH = 'data/stocks/stocks_master.json'
BACKUP_PATH = 'data/stocks/stocks_master_valuation_bak.json'

def load_master():
    with open(MASTER_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_master(data):
    with open(MASTER_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_target_market_cap(text):
    """Extract target market cap in 亿元."""
    values = []
    
    # Pattern: 目标市值（亿）：400.0  or 目标市值（亿）:400.0
    m = re.findall(r'目标市值[（(]亿[）)]?\s*[:：]\s*([\d.]+)', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 目标市值2500亿
    m = re.findall(r'目标市值\s*(\d+)\s*亿', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 总市值约329亿元
    m = re.findall(r'总市值[约]?(\d+)\s*亿[元]?', text)
    values.extend([float(x) for x in m])
    
    # Pattern: XXX亿 (as standalone valuation target)
    # e.g., "20000亿", "短期350亿,中期500亿"
    m = re.findall(r'(?:短期|中期|长期|目标)?(\d{3,6})\s*亿(?!元|美元|港元)', text)
    for v in m:
        val = float(v)
        # Filter: reasonable market cap range (1亿 to 50000亿)
        if 1 <= val <= 50000:
            values.append(val)
    
    # Pattern: XXXXe (e stands for 亿)
    m = re.findall(r'(\d+)\s*e(?![\w])', text)
    for v in m:
        val = float(v)
        if 1 <= val <= 50000:
            values.append(val)
    
    # Pattern: 按...净利×XX倍PE≈XXX亿
    m = re.findall(r'≈\s*(\d{3,6})\s*亿', text)
    values.extend([float(x) for x in m if 1 <= float(x) <= 50000])
    
    return max(values) if values else None

def parse_target_price(text):
    """Extract target price in 元."""
    values = []
    
    # Pattern: 目标价: 66.56元  or 目标价66.56元
    m = re.findall(r'目标价\s*[:：]?\s*([\d.]+)\s*元', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 目标价115.3元/股
    m = re.findall(r'目标价\s*([\d.]+)\s*元/股', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 目标位23.00元
    m = re.findall(r'目标位\s*([\d.]+)\s*元', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 目标价看至14元
    m = re.findall(r'目标价看至\s*([\d.]+)\s*元', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 目标价850元
    m = re.findall(r'目标价\s*(\d{3,6})\s*元(?!/)', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 目标价56-62元 (range)
    m = re.findall(r'目标价\s*([\d.]+)\s*[-~]\s*([\d.]+)\s*元', text)
    for a, b in m:
        values.extend([float(a), float(b)])
    
    # Pattern: 买入价X-Y元，目标Z元
    m = re.findall(r'目标[价位]?\s*([\d.]+)\s*元', text)
    values.extend([float(x) for x in m if 1 <= float(x) <= 2000])
    
    # Pattern: 目标价看至30-35元
    m = re.findall(r'目标价看至\s*([\d.]+)\s*[-~]\s*([\d.]+)\s*元', text)
    for a, b in m:
        values.extend([float(a), float(b)])

def parse_pe(text):
    """Extract PE ratio."""
    values = []
    
    # Pattern: PE 14/9x or PE 25.3/17.8倍
    m = re.findall(r'PE\s*[:：]?\s*([\d.]+)\s*[/倍]', text)
    values.extend([float(x) for x in m])
    
    # Pattern: PE为276倍
    m = re.findall(r'PE[为约]?\s*([\d.]+)\s*倍', text)
    values.extend([float(x) for x in m])
    
    # Pattern: PE 65.13  (standalone)
    m = re.findall(r'PE\s*[:：]?\s*(\d+\.?\d*)', text)
    for v in m:
        val = float(v)
        if 3 <= val <= 500:  # reasonable PE range
            values.append(val)
    
    # Pattern: PE(TTM)约17倍
    m = re.findall(r'PE[（(]TTM[）)]\s*约\s*(\d+)\s*倍', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 动态PE 86.03倍
    m = re.findall(r'动态PE\s*([\d.]+)\s*倍', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 市盈率（PE-TTM）约在65至81倍
    m = re.findall(r'市盈率[（(]PE-TTM[）)]\s*约在\s*(\d+)', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 金安国纪：PE 14/9x
    m = re.findall(r'PE\s*(\d+)\s*/\s*\d+', text)
    values.extend([float(x) for x in m])
    
    # Pattern: PE在24.8-25.7倍
    m = re.findall(r'PE[在]\s*([\d.]+)\s*[-~]\s*([\d.]+)\s*倍', text)
    for a, b in m:
        values.extend([float(a), float(b)])
    
    # Pattern: PE在24.8-25.7倍之间
    m = re.findall(r'PE\s*在\s*(\d+\.?\d*)\s*[-~]\s*(\d+\.?\d*)\s*倍', text)
    for a, b in m:
        values.extend([float(a), float(b)])
    
    # Pattern: 2026年PE在24.8倍
    m = re.findall(r'PE[在约]?\s*(\d+\.?\d*)\s*倍', text)
    values.extend([float(x) for x in m if 3 <= float(x) <= 500])
    
    return values[0] if values else None

def parse_rating(text):
    """Extract rating."""
    ratings = []
    
    patterns = [
        r'(强烈推荐)[★☆]*',
        r'(推荐)[（(]?[★☆Ⅴ]+[）)]?',
        r'(买入)',
        r'(增持)',
        r'(持有)',
        r'(中性)',
        r'(卖出)',
    ]
    for pat in patterns:
        m = re.findall(pat, text)
        ratings.extend(m)
    
    if not ratings:
        return None
    
    # Priority: 强烈推荐 > 买入 > 增持 > 推荐 > 持有 > 中性 > 卖出
    priority = ['强烈推荐', '买入', '增持', '推荐', '持有', '中性', '卖出']
    for p in priority:
        if p in ratings:
            return p
    return ratings[0]

def parse_upside(text):
    """Extract upside percentage."""
    values = []
    
    # Pattern: 上涨空间约11%
    m = re.findall(r'上涨空间\s*约?\s*([\d.]+)\s*%', text)
    values.extend([float(x) for x in m])
    
    # Pattern: 上涨空间约11%
    m = re.findall(r'(?:预期收益|上涨)[+]?([\d.]+)\s*%', text)
    values.extend([float(x) for x in m])
    
    return values[-1] if values else None

def extract_valuation_from_article(article):
    """Extract valuation data from a single article."""
    result = {
        'target_market_cap_values': [],
        'target_market_cap_billion_values': [],
        'target_price_values': [],
        'pe_values': [],
        'upside_values': [],
        'ratings': [],
    }
    
    texts = article.get('target_valuation', [])
    if not texts:
        return result
    
    for text in texts:
        if not text:
            continue
        
        # Target market cap
        cap = parse_target_market_cap(text)
        if cap is not None:
            result['target_market_cap_values'].append(cap)
        
        # Target price
        price = parse_target_price(text)
        if price is not None:
            result['target_price_values'].append(price)
        
        # PE
        pe = parse_pe(text)
        if pe is not None:
            result['pe_values'].append(pe)
        
        # Rating
        rating = parse_rating(text)
        if rating:
            result['ratings'].append(rating)
        
        # Upside
        upside = parse_upside(text)
        if upside is not None:
            result['upside_values'].append(upside)
    
    return result

def merge_article_results(results):
    """Merge multiple article extraction results into a single valuation dict."""
    all_mcaps = []
    all_billions = []
    all_prices = []
    all_pes = []
    all_upsides = []
    all_ratings = []
    
    for r in results:
        all_mcaps.extend(r['target_market_cap_values'])
        all_billions.extend(r['target_market_cap_billion_values'])
        all_prices.extend(r['target_price_values'])
        all_pes.extend(r['pe_values'])
        all_upsides.extend(r['upside_values'])
        all_ratings.extend(r['ratings'])
    
    valuation = {}
    
    # Target market cap: use max value across articles
    if all_mcaps:
        max_cap = max(all_mcaps)
        valuation['target_market_cap'] = f"{max_cap:.1f} 亿" if max_cap < 10000 else f"{max_cap/10000:.2f} 万亿"
        valuation['target_market_cap_billion'] = max_cap
    
    # Target price: use max
    if all_prices:
        max_price = max(all_prices)
        valuation['target_price'] = f"{max_price:.2f} 元"
    
    # PE: use the most common (mode) or the median
    if all_pes:
        all_pes.sort()
        median_pe = all_pes[len(all_pes) // 2]
        valuation['pe'] = f"{median_pe:.1f} 倍 PE"
    
    # Upside: use max
    if all_upsides:
        max_upside = max(all_upsides)
        valuation['upside'] = f"{max_upside:.1f}%"
    
    # Rating: use the highest priority
    if all_ratings:
        priority = ['强烈推荐', '买入', '增持', '推荐', '持有', '中性', '卖出']
        best_rating = all_ratings[0]
        for r in all_ratings:
            for p in priority:
                if r == p and priority.index(r) < priority.index(best_rating):
                    best_rating = r
                    break
        valuation['rating'] = best_rating
    
    return valuation

def process_all_stocks():
    """Main processing function."""
    data = load_master()
    stocks = data['stocks']
    
    # Backup
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[BACKUP] Saved to {BACKUP_PATH}")
    
    stats = {
        'total': len(stocks),
        'with_articles': 0,
        'extracted': 0,
        'already_had_valuation': 0,
        'target_market_cap': 0,
        'target_price': 0,
        'pe': 0,
        'upside': 0,
        'rating': 0,
    }
    
    for code, stock in stocks.items():
        articles = stock.get('articles', [])
        if not articles:
            continue
        
        stats['with_articles'] += 1
        
        # Check if already has valuation
        old_val = stock.get('valuation')
        if old_val:
            stats['already_had_valuation'] += 1
        
        # Process each article
        results = []
        for article in articles:
            r = extract_valuation_from_article(article)
            results.append(r)
        
        # Merge results
        merged = merge_article_results(results)
        
        if merged:
            # Merge with existing valuation (don't overwrite if already present)
            if old_val:
                for k, v in old_val.items():
                    if k not in merged and v:
                        merged[k] = v
            
            stock['valuation'] = merged
            stats['extracted'] += 1
            
            if 'target_market_cap_billion' in merged:
                stats['target_market_cap'] += 1
            if 'target_price' in merged:
                stats['target_price'] += 1
            if 'pe' in merged:
                stats['pe'] += 1
            if 'upside' in merged:
                stats['upside'] += 1
            if 'rating' in merged:
                stats['rating'] += 1
    
    # Update metadata
    data['valuation_extracted_at'] = json.loads(open(MASTER_PATH, 'r', encoding='utf-8').read()).get('updated_at', '')
    
    save_master(data)
    
    print(f"\n=== 估值提取统计 ===")
    print(f"股票总数: {stats['total']}")
    print(f"有文章: {stats['with_articles']}")
    print(f"成功提取估值: {stats['extracted']}")
    print(f"已有估值字段: {stats['already_had_valuation']}")
    print(f"提取结果分布:")
    print(f"  目标市值: {stats['target_market_cap']}")
    print(f"  目标价:   {stats['target_price']}")
    print(f"  PE:       {stats['pe']}")
    print(f"  上涨空间: {stats['upside']}")
    print(f"  评级:     {stats['rating']}")
    
    # Print some samples
    print(f"\n=== 采样 (前10只) ===")
    count = 0
    for code, stock in stocks.items():
        if stock.get('valuation') and count < 10:
            print(f"{code} {stock['name']}: {json.dumps(stock['valuation'], ensure_ascii=False)}")
            count += 1
    
    return data

if __name__ == '__main__':
    process_all_stocks()