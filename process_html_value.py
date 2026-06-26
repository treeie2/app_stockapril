#!/usr/bin/env python3
"""Process 67 directories of index.html -> raw_material + structured JSON"""
import json, re
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

BASE = Path(__file__).parent
VALUE_DIR = BASE / 'raw_material' / 'value'
RAW_OUT = BASE / 'raw_material' / 'value_formatted'
VALUE_JSON = BASE / 'data/stocks/value_2026-06-05.json'
MASTER_FILE = BASE / 'data/stocks/stocks_master.json'
MIN_FILE = BASE / 'data/stocks/stocks_master.min.json'
IND_XLS = BASE / 'archived/同花顺行业.xls'
CON_XLS = BASE / 'archived/所属概念.xls'

# ── Helpers ──

def code_from_name(name):
    m = re.search(r'[（(](\d{6})', name)
    return m.group(1) if m else None

def stock_name_from_name(name):
    m = re.match(r'^[_\s]*([^\d（(_{]+)', name)
    return m.group(1).strip().rstrip('_ ') if m else ''

def get_clean_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Remove script/style
    for tag in soup(['script','style','noscript']):
        tag.decompose()
    text = soup.get_text(separator='\n')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

def extract_date(text):
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', text)
    return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))) if m else None

def extract_source(html):
    m = re.search(r'https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+', html)
    return m.group(0) if m else ''

def extract_title(text):
    for line in text.split('\n')[:15]:
        ls = line.strip()
        if ls and len(ls) > 8 and '=' not in ls and '原创' not in ls and '免责' not in ls and '风险' not in ls:
            return ls[:100]
    return '分析报告'

def extract_metrics(text):
    """Extract accidents, insights, key_metrics, target_valuation from clean text."""
    lines = text.split('\n')
    accidents, insights, key_metrics, target_valuation = [], [], [], []
    
    for line in lines[:200]:
        ls = line.strip()
        if len(ls) < 10: continue
        has_cn = bool(re.search(r'[\u4e00-\u9fff]', ls))
        has_num = bool(re.search(r'[\d]', ls))
        if not has_cn: continue
        
        # KEY METRICS: financial numbers
        if has_num and any(k in ls for k in ['亿','万','%','倍']):
            if any(k in ls for k in ['营收','收入','利润','净利','市值','PE','增长','毛利','率','周转','占比','订单','产能']):
                if ls not in key_metrics: key_metrics.append(ls[:80])
        
        # TARGET VALUATION
        if any(k in ls for k in ['目标市值','目标价','看到','看向','上看','看翻倍','给予']):
            if ls not in target_valuation: target_valuation.append(ls[:80])
        
        # ACCIDENTS: factual events
        if has_num and any(k in ls for k in ['成立','发布','合作','投资','建设','投产','推出','获得','中标','签订','收购','布局','量产','突破','认证','交付']):
            a = ls.strip('- ').strip('# ').strip()[:80]
            if a not in accidents: accidents.append(a)
        
        # INSIGHTS: opinions
        if any(k in ls for k in ['看好','认为','建议','警惕','预期','展望','核心','有望','关注']):
            if ls not in insights: insights.append(ls[:100])
    
    return {
        'accidents': accidents[:5], 'insights': insights[:3],
        'key_metrics': key_metrics[:6], 'target_valuation': target_valuation[:3],
    }

# ── Load lookup ──
name_to_code = {}
code_to_stock = {}
for src in [MIN_FILE, MASTER_FILE]:
    try:
        with open(src, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for code, s in d.get('stocks', {}).items():
            n = s.get('name', '')
            if n: name_to_code[n] = code; name_to_code[n.lower()] = code; code_to_stock[code] = s
    except: pass

# ── Load Excel ──
import pandas as pd
ind_map, con_map = {}, {}
for _, row in pd.read_excel(IND_XLS, sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0]
    v = str(row['所属同花顺行业']).strip()
    if v and v != 'nan': ind_map[k] = v
for _, row in pd.read_excel(CON_XLS, sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0].strip()
    cs = str(row['所属概念']).strip()
    if cs and cs != 'nan': con_map[k] = [c.strip() for c in cs.split(';') if c.strip()]

# ── Process ──
dirs = sorted([d for d in VALUE_DIR.iterdir() if d.is_dir()])
results = {}
stats = {'individual': 0, 'industry': 0, 'no_code': 0}

for subdir in dirs:
    name = subdir.name
    html_file = subdir / 'index.html'
    if not html_file.exists(): continue
    
    code = code_from_name(name)
    sn = stock_name_from_name(name)
    if not code and sn:
        code = name_to_code.get(sn, name_to_code.get(sn.lower()))
    if not code:
        stats['no_code'] += 1; continue
    if code in code_to_stock:
        sn = code_to_stock[code].get('name', sn)
    
    stats['individual'] += 1
    html = html_file.read_text(encoding='utf-8', errors='replace')
    clean = get_clean_text(html)
    if len(clean) < 100: continue
    
    date = extract_date(html) or datetime.now().strftime('%Y-%m-%d')
    source = extract_source(html)
    title = extract_title(clean)
    extracted = extract_metrics(clean)
    
    # Save raw_material
    rm = "## Article\nsource: %s\nfetched_at: %s\ntitle: %s\n\n%s" % (
        source, datetime.now().isoformat(), title, clean)
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    (RAW_OUT / (subdir.name + '.md')).write_text(rm, encoding='utf-8')
    
    article = {
        'title': title, 'date': date, 'source': source,
        'accidents': extracted['accidents'], 'insights': extracted['insights'],
        'key_metrics': extracted['key_metrics'], 'target_valuation': extracted['target_valuation'],
    }
    
    if code not in results:
        results[code] = {
            'name': sn, 'code': code, 'board': '', 'industry': '',
            'concepts': [], 'products': [], 'core_business': [], 'industry_position': [],
            'chain': [], 'partners': [], 'mention_count': 0, 'articles': [],
            'last_updated': date,
        }
        # Fill from Excel
        if code in ind_map: results[code]['industry'] = ind_map[code]
        if code in con_map: results[code]['concepts'] = con_map[code]
        if code in code_to_stock:
            cs = code_to_stock[code]
            results[code]['board'] = cs.get('board', '')
    
    r = results[code]
    existing = {(a['title'], a['source']) for a in r['articles']}
    if (title, source) not in existing:
        r['articles'].append(article)
        r['mention_count'] = len(r['articles'])
        r['last_updated'] = max(r['last_updated'], date)

# ── Save ──
dates = [s['last_updated'] for s in results.values()]
out = {
    'date': '2026-06-05',
    'update_count': len(results),
    'last_updated': max(dates) if dates else '',
    'stocks': results,
}
VALUE_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

print('Individual: %d, Industry: %d, No code: %d' % (stats['individual'], stats['industry'], stats['no_code']))
print('Stocks: %d' % len(results))

# Show sample
s = results.get('300276', {})
if s:
    print()
    print('Sample:', s['name'], '(' + s['code'] + ')')
    print('  industry:', s.get('industry',''))
    print('  concepts:', s.get('concepts',[])[:3])
    if s.get('articles'):
        a = s['articles'][0]
        print('  accidents:', a.get('accidents',[])[:2])
        print('  insights:', a.get('insights',[])[:2])
        print('  key_metrics:', a.get('key_metrics',[])[:3])
