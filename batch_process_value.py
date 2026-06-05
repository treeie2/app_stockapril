#!/usr/bin/env python3
"""Batch process raw_material/value/*.md -> raw_material/ + merge into stocks_master.json"""
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
VALUE_DIR = BASE / 'raw_material' / 'value'
RAW_DIR = BASE / 'raw_material'
MASTER = BASE / 'data' / 'stocks' / 'stocks_master.json'
MIN_FILE = BASE / 'data' / 'stocks' / 'stocks_master.min.json'

# Load master
with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)

# Build name->code lookup
name_to_code = {}
for src in [MIN_FILE, MASTER]:
    try:
        with open(src, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for code, s in d.get('stocks', {}).items():
            n = s.get('name', '')
            if n:
                name_to_code[n] = code
                name_to_code[n.lower()] = code
    except:
        pass

def code_from_filename(fname):
    m = re.search(r'[（(](\d{6})', fname)
    return m.group(1) if m else None

def stock_name_from_filename(fname):
    m = re.match(r'^([^（(_]+)', fname)
    return m.group(1).strip().rstrip(' _') if m else ''

def clean_text(text):
    text = re.sub(r'\*\{[^}]*\}', '', text)
    text = re.sub(r'\.[a-zA-Z_-]+\{[^}]*\}', '', text)
    text = re.sub(r'#[a-zA-Z_-]+\{[^}]*\}', '', text)
    text = re.sub(r'@media[^}]*\}', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'https?://mmbiz\.qpic\.cn[^\s)]*', '[image]', text)
    text = re.sub(r'\n{4,}', '\n\n', text)
    text = re.sub(r' {3,}', '  ', text)
    return text.strip()

def extract_source(clean):
    m = re.search(r'https://mp\.weixin\.qq\.com/s/[a-zA-Z0-9_-]+', clean)
    return m.group(0) if m else ''

def extract_title(lines):
    for line in lines[:10]:
        l = line.strip()
        if l and '=' not in l and '原创' not in l and len(l) > 5:
            return l[:80]
    return '深度价值分析报告'

def extract_date(text):
    m = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
    return m.group(1).replace('/', '-') if m else datetime.now().strftime('%Y-%m-%d')

# Batch process
files = sorted(VALUE_DIR.glob('*.md'))
converted = merged = skipped = 0
today = datetime.now().strftime('%Y-%m-%d')

print(f'Total: {len(files)} files')

for fp in files:
    fname = fp.stem
    raw = fp.read_text(encoding='utf-8', errors='replace')
    
    code = code_from_filename(fname)
    if not code:
        sn = stock_name_from_filename(fname)
        code = name_to_code.get(sn, name_to_code.get(sn.lower()))
    
    if not code:
        skipped += 1
        continue
    
    sn = stock_name_from_filename(fname)
    if not sn:
        skipped += 1; continue
    
    clean = clean_text(raw)
    if len(clean) < 100:
        skipped += 1; continue
    
    lines = clean.split('\n')
    title = extract_title(lines)
    source = extract_source(clean)
    date = extract_date(clean)
    
    # Save raw_material
    rm = f"""## Article
source: {source}
fetched_at: {datetime.now().isoformat()}
title: {title}

{clean}
"""
    out_dir = RAW_DIR / 'value_formatted'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f'{fname}.md').write_text(rm, encoding='utf-8')
    converted += 1
    
    # Merge into master
    if code not in master['stocks']:
        master['stocks'][code] = {
            'name': sn, 'code': code,
            'board': '', 'industry': '', 'concepts': [],
            'products': [], 'core_business': [], 'industry_position': [],
            'chain': [], 'partners': [], 'mention_count': 0,
            'articles': [], 'last_updated': today
        }
    
    s = master['stocks'][code]
    existing_titles = {(a.get('title',''), a.get('source','')) for a in s.get('articles',[])}
    key = (title, source)
    if key not in existing_titles:
        s.setdefault('articles', []).append({
            'title': title, 'date': date, 'source': source,
            'accidents': [], 'insights': [], 'key_metrics': [], 'target_valuation': []
        })
        s['mention_count'] = len(s['articles'])
        s['last_updated'] = today
        merged += 1

master['last_updated'] = datetime.now().isoformat()
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

total = len(master['stocks'])
print(f'Converted: {converted} raw_material files')
print(f'Merged: {merged} stock articles')
print(f'Skipped: {skipped} (no code found)')
print(f'Master total: {total} stocks')
