#!/usr/bin/env python3
"""Batch process raw_material/agzh/ - 112 HTML articles, extract and merge to master."""
import json, re
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

AGZH = Path('raw_material/agzh')
MASTER = Path('data/stocks/stocks_master.json')
VALUE_JSON = Path('data/stocks/value_2026-06-05.json')
RM_FMT = Path('raw_material/agzh_formatted')
RM_FMT.mkdir(exist_ok=True)

with open(MASTER, 'r', encoding='utf-8') as f: master = json.load(f)
if VALUE_JSON.exists():
    with open(VALUE_JSON, 'r', encoding='utf-8') as f: value = json.load(f)
else:
    value = {'stocks': {}, 'last_updated': ''}

# Lookups
ind_map, con_map, name_to_code = {}, {}, {}
for _, row in pd.read_excel('archived/同花顺行业.xls', sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0]; v = str(row['所属同花顺行业']).strip()
    if v and v != 'nan': ind_map[k] = v
for _, row in pd.read_excel('archived/所属概念.xls', sheet_name=0).iterrows():
    k = str(row['股票代码']).split('.')[0].strip(); cs = str(row['所属概念']).strip()
    if cs and cs != 'nan': con_map[k] = [c.strip() for c in cs.split(';') if c.strip()]
for code, s in master['stocks'].items():
    n = s.get('name', '')
    if n: name_to_code[n] = code; name_to_code[n.lower()] = code

def clean_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script','style','noscript','link','meta']): tag.decompose()
    return '\n'.join(l.strip() for l in soup.get_text(separator='\n').split('\n') if l.strip())

def extract_date(text, html):
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', text)
    if m: return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', html)
    if m: return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
    return ''

def extract_metrics(text):
    accidents, insights, key_metrics, target_valuation = [], [], [], []
    for line in text.split('\n'):
        ls = line.strip()
        if len(ls) < 8 or not re.search(r'[\u4e00-\u9fff]', ls): continue
        has_num = bool(re.search(r'[\d.]+', ls))
        # key_metrics
        if has_num and any(k in ls for k in ['亿','万','%','倍','美元']):
            if any(k in ls for k in ['营收','收入','利润','净利','市值','PE','增长','毛利','率','周转','占比','订单','产能','市占','元','均价','用量','涨幅','暴涨']):
                km = ls[:90]; [key_metrics.append(km) if km not in key_metrics else None]
        # target_valuation
        if has_num and any(k in ls for k in ['目标市值','目标价','看到','看向','上看','看翻倍','给予','目标位','目标']):
            tv = ls[:90]; [target_valuation.append(tv) if tv not in target_valuation else None]
        # accidents
        if has_num and any(k in ls for k in ['成立','发布','合作','投资','建设','投产','推出','获得','中标','签订','收购','布局','量产','突破','认证','交付','公告','宣布','获批','过会','涨停','封板']):
            a = ls.strip('- ').strip('# ').strip()[:80]; [accidents.append(a) if a not in accidents else None]
        # insights
        if any(k in ls for k in ['看好','认为','建议','警惕','预期','展望','核心','有望','关注','逻辑','建议','空间','受益','看好','必须','强烈','重点']):
            ins = ls[:90]; [insights.append(ins) if ins not in insights else None]
    return {
        'accidents': accidents[:6], 'insights': insights[:4],
        'key_metrics': key_metrics[:8], 'target_valuation': target_valuation[:3],
    }

def extract_first_layer_from_text(text, code):
    """Extract first-layer fields from rich article text."""
    result = {'products':[], 'core_business':[], 'industry_position':[], 'chain':[], 'partners':[]}
    if not code: return result
    # Already in master
    if code in master['stocks']:
        ms = master['stocks'][code]
        for f in result:
            if ms.get(f): result[f] = ms[f]
    if not result['core_business']:
        for p in [r'主要从事[：:]\s*(.+?)[。\n]', r'核心(?:业务|逻辑)[：:]?\s*(.+?)[。\n]']:
            m = re.search(p, text); 
            if m: result['core_business'].append(m.group(1).strip()[:80]); break
    if not result['industry_position']:
        for p in [r'国内[（(]?唯一[）)]?[^\n。]{0,40}', r'全球[^\n。]{0,20}(?:龙头|第一|领先|市占率)', r'(?:龙头|领先|霸主)[^\n。]{0,50}']:
            ms = re.findall(p, text)
            if ms: result['industry_position'] = [m.strip() for m in ms[:2]]; break
    if not result['partners']:
        partners_in_text = re.findall(r'(?:华为|腾讯|阿里|字节|百度|英伟达|AMD|Intel|微软|谷歌|Meta|特斯拉|苹果|三星|比亚迪|宁德|中芯|台积(?:电)?|长鑫|长江存储|华虹|中兴|浪潮)[^\n。]{0,30}(?:合作|客户|供应商|配套|买入|订单)', text)
        if partners_in_text: result['partners'] = [p.strip()[:80] for p in partners_in_text[:3]]
    if not result['products']:
        for p in [r'主要产品[包含是][：:]?\s*(.+?)[。\n]', r'产品线[：:]\s*(.+?)[。\n]', r'提供[^\n。]{5,50}(?:产品|方案|服务)']:
            m = re.search(p, text)
            if m: result['products'].append(m.group(1).strip()[:80] if m.lastindex else m.group(0).strip()[:80]); break
    return result

# ── Process ──
processed = new_stocks = updated_stocks = skipped_topic = 0

for sub_dir in sorted(AGZH.iterdir()):
    if not sub_dir.is_dir(): continue
    html_file = sub_dir / 'index.html'
    if not html_file.exists(): continue
    
    html = html_file.read_text(encoding='utf-8', errors='replace')
    text = clean_text(html)
    if len(text) < 100: continue
    
    dir_name = sub_dir.name
    # Extract codes from dir name
    codes = re.findall(r'[（(](\d{6})', dir_name)
    # Extract from text
    text_codes = re.findall(r'[（(](\d{6})', text)
    for c in text_codes:
        if c not in codes: codes.append(c)
    # Limit
    codes = codes[:10]
    
    if not codes:
        # Try to match company names from text
        for line in text.split('\n'):
            for name, code in name_to_code.items():
                if len(name) >= 2 and name in line and code not in codes:
                    codes.append(code)
                    break
            if codes: break
    
    if not codes:
        skipped_topic += 1
        continue
    
    date = extract_date(text, html) or '2026-06-05'
    # Title = first meaningful line
    lines = [l.strip() for l in text.split('\n') if l.strip() and '原创' not in l and '免责' not in l and '风险提示' not in l and len(l.strip()) > 10]
    title = lines[0][:80] if lines else dir_name[:80]
    
    extracted = extract_metrics(text)
    
    # Save raw_material
    safe_name = re.sub(r'[\\/:*?"<>|]', '_', dir_name)[:60]
    rm_content = f"""## Article
source: 
fetched_at: {datetime.now().isoformat()}
title: {title}

{text}
"""
    (RM_FMT / f"{safe_name}.md").write_text(rm_content, encoding='utf-8')
    
    # Update each stock
    for code in codes:
        if code not in master['stocks']:
            continue  # skip unknown codes
        
        if code not in value['stocks']:
            ms = master['stocks'][code]
            value['stocks'][code] = {
                'name': ms.get('name', ''), 'code': code, 'board': ms.get('board', ''),
                'industry': ind_map.get(code, ms.get('industry', '')),
                'concepts': con_map.get(code, ms.get('concepts', [])),
                'products': ms.get('products', []), 'core_business': ms.get('core_business', []),
                'industry_position': ms.get('industry_position', []),
                'chain': ms.get('chain', []), 'partners': ms.get('partners', []),
                'mention_count': 0, 'articles': [], 'last_updated': date,
            }
        vs = value['stocks'][code]
        
        article = {
            'title': title, 'date': date, 'source': '',
            'accidents': extracted['accidents'], 'insights': extracted['insights'],
            'key_metrics': extracted['key_metrics'], 'target_valuation': extracted['target_valuation'],
        }
        known = {(a.get('title',''), a.get('date','')) for a in vs.get('articles', [])}
        if (title, date) not in known:
            vs.setdefault('articles', []).append(article)
            vs['mention_count'] = len(vs['articles'])
            vs['last_updated'] = max(vs.get('last_updated',''), date)
        
        # Try to fill first-layer from rich text
        fl = extract_first_layer_from_text(text, code)
        for f in ['products','core_business','industry_position','chain','partners']:
            if fl.get(f) and not vs.get(f):
                vs[f] = fl[f]
        
        updated_stocks += 1
    processed += 1

# Save value JSON
dates = [s.get('last_updated','') for s in value['stocks'].values()]
value['last_updated'] = max(dates) if dates else datetime.now().strftime('%Y-%m-%d')
with open(VALUE_JSON, 'w', encoding='utf-8') as f:
    json.dump(value, f, ensure_ascii=False, indent=2)

# ── Merge to master ──
merged = 0
for code, vs in value['stocks'].items():
    if code not in master['stocks']: continue
    ms = master['stocks'][code]
    known = {(a.get('title',''), a.get('date','')) for a in ms.get('articles', [])}
    new_articles = [a for a in vs.get('articles',[]) if (a.get('title',''), a.get('date','')) not in known]
    if new_articles:
        ms.setdefault('articles', []).extend(new_articles)
        ms['mention_count'] = len(ms['articles'])
    for f in ['board','industry','concepts','products','core_business','industry_position','chain','partners']:
        if vs.get(f) and (f not in ms or not ms.get(f)):
            ms[f] = vs[f]
    ms['last_updated'] = max(ms.get('last_updated',''), vs.get('last_updated',''))
    merged += 1

master['last_updated'] = datetime.now().isoformat()
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f'=== AGZH 处理完成 ===')
print(f'HTML 文件: {processed}')
print(f'跳过(主题类): {skipped_topic}')
print(f'合并到master: {merged} 只股票')
print(f'Value JSON: {len(value["stocks"])} 只')

# Show sample codes with stats
stocks_info = [(sum(len(a.get("accidents",[])) for a in s.get("articles",[])), 
                sum(len(a.get("insights",[])) for a in s.get("articles",[])),
                sum(len(a.get("key_metrics",[])) for a in s.get("articles",[])), 
                code, s.get("name","")) 
               for code,s in value["stocks"].items() 
               if s.get("articles") and any(a.get("title","").startswith(lines[0][:10] if lines else "") for a in s["articles"])]
print(f'\n含新文章的股票示例:')
for acc,ins,km,code,name in sorted(stocks_info, reverse=True)[:10]:
    print(f'  {code} {name}: acc={acc} ins={ins} km={km}')
