#!/usr/bin/env python3
"""Process raw_material/topdown/ HTML files and merge into value_2026-06-05.json"""
import json, re, pandas as pd
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

VALUE_JSON = Path(__file__).parent / 'data/stocks/value_2026-06-05.json'
TOPDOWN = Path(__file__).parent / 'raw_material/topdown'
RAW_OUT = Path(__file__).parent / 'raw_material' / 'topdown_formatted'
MIN_FILE = Path(__file__).parent / 'data/stocks/stocks_master.min.json'
MASTER_FILE = Path(__file__).parent / 'data/stocks/stocks_master.json'
IND_XLS = Path(__file__).parent / 'archived/同花顺行业.xls'
CON_XLS = Path(__file__).parent / 'archived/所属概念.xls'

with open(VALUE_JSON, 'r', encoding='utf-8') as f:
    value = json.load(f)
print('Loaded existing: %d stocks' % len(value['stocks']))

def code_from_name(name):
    m = re.search(r'[（(](\d{6})', name)
    return m.group(1) if m else None

def stock_name_from_name(name):
    m = re.match(r'^[ _]*([^\d（(_{]+)', name)
    return m.group(1).strip().rstrip('_ ') if m else ''

def get_clean_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script','style','noscript']): tag.decompose()
    return '\n'.join(l.strip() for l in soup.get_text(separator='\n').split('\n') if l.strip())

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
    lines = text.split('\n')
    accidents, insights, key_metrics, target_valuation = [], [], [], []
    for line in lines[:200]:
        ls = line.strip()
        if len(ls) < 12: continue
        if not re.search(r'[\u4e00-\u9fff]', ls): continue
        has_num = bool(re.search(r'[\d]', ls))
        if has_num and any(k in ls for k in ['亿','万','%','倍']):
            if any(k in ls for k in ['营收','收入','利润','净利','市值','PE','增长','毛利','率','周转','占比','订单','产能']):
                if ls not in key_metrics: key_metrics.append(ls[:80])
        if any(k in ls for k in ['目标市值','目标价','看到','看向','上看','看翻倍','给予']):
            if ls not in target_valuation: target_valuation.append(ls[:80])
        if has_num and any(k in ls for k in ['成立','发布','合作','投资','建设','投产','推出','获得','中标','签订','收购','布局','量产','突破','认证','交付']):
            a = ls.strip('- ').strip('# ').strip()[:80]
            if a not in accidents: accidents.append(a)
        if any(k in ls for k in ['看好','认为','建议','警惕','预期','展望','核心','有望','关注']):
            if ls not in insights: insights.append(ls[:100])
    return {
        'accidents': accidents[:5], 'insights': insights[:3],
        'key_metrics': key_metrics[:6], 'target_valuation': target_valuation[:3],
    }

# Lookups
name_to_code, code_to_stock = {}, {}
for src in [MIN_FILE, MASTER_FILE]:
    try:
        with open(src, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for code, s in d.get('stocks', {}).items():
            n = s.get('name', '')
            if n: name_to_code[n] = code; name_to_code[n.lower()] = code; code_to_stock[code] = s
    except: pass

ind_map, con_map = {}, {}
for _, row in pd.read_excel(IND_XLS, sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0]; v = str(row['所属同花顺行业']).strip()
    if v and v != 'nan': ind_map[k] = v
for _, row in pd.read_excel(CON_XLS, sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0].strip(); cs = str(row['所属概念']).strip()
    if cs and cs != 'nan': con_map[k] = [c.strip() for c in cs.split(';') if c.strip()]

# Process
dirs = sorted([d for d in TOPDOWN.iterdir() if d.is_dir()])
new_stocks = updated_stocks = 0

for subdir in dirs:
    name = subdir.name
    html_file = subdir / 'index.html'
    if not html_file.exists(): continue

    code = code_from_name(name)
    sn = stock_name_from_name(name)
    if not code and sn: code = name_to_code.get(sn, name_to_code.get(sn.lower()))
    if not code: continue
    if code in code_to_stock: sn = code_to_stock[code].get('name', sn)

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

    if code not in value['stocks']:
        value['stocks'][code] = {
            'name': sn, 'code': code, 'board': '', 'industry': '',
            'concepts': [], 'products': [], 'core_business': [], 'industry_position': [],
            'chain': [], 'partners': [], 'mention_count': 0, 'articles': [], 'last_updated': date,
        }
        if code in ind_map: value['stocks'][code]['industry'] = ind_map[code]
        if code in con_map: value['stocks'][code]['concepts'] = con_map[code]
        if code in code_to_stock: value['stocks'][code]['board'] = code_to_stock[code].get('board', '')
        new_stocks += 1
    else:
        updated_stocks += 1

    r = value['stocks'][code]
    existing = {(a['title'], a['source']) for a in r['articles']}
    if (title, source) not in existing:
        r['articles'].append(article)
        r['mention_count'] = len(r['articles'])
        r['last_updated'] = max(r['last_updated'], date)

dates = [s['last_updated'] for s in value['stocks'].values()]
value['update_count'] = len(value['stocks'])
value['last_updated'] = max(dates) if dates else ''
with open(VALUE_JSON, 'w', encoding='utf-8') as f:
    json.dump(value, f, ensure_ascii=False, indent=2)

print('Processed %d dirs' % len(dirs))
print('New: %d, Updated: %d' % (new_stocks, updated_stocks))
print('Total: %d stocks' % len(value['stocks']))
