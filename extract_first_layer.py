#!/usr/bin/env python3
"""从 raw_material/topdown_formatted 文章中提取 products/core_business/industry_position/chain/partners"""

import json, re
from pathlib import Path

MASTER = Path('data/stocks/stocks_master.json')
VALUE = Path('data/stocks/value_2026-06-05.json')
RM_DIR = Path('raw_material/topdown_formatted')

with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)
with open(VALUE, 'r', encoding='utf-8') as f:
    value = json.load(f)

TOTAL_FIELDS = ['products', 'core_business', 'industry_position', 'chain', 'partners']

def read_article_text(fp):
    """读取文章纯文本（跳过头部的 ## Article 元数据）"""
    text = fp.read_text(encoding='utf-8', errors='replace')
    lines = text.split('\n')
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('## Article'):
            continue
        # skips source/fetched_at/title meta lines
        if line.strip().startswith('source:') or line.strip().startswith('fetched_at:') or line.strip().startswith('title:'):
            continue
        if line.strip() == '' and i > 5:
            body_start = i + 1
            break
    body = '\n'.join(lines[body_start:])
    # Clean noise
    body = re.sub(r'在小说阅读器读本章|去阅读|在小说阅读器中沉浸阅读', '', body)
    body = re.sub(r'深度价值分析|深度价值展望|原创', '', body)
    return body.strip()

def extract_products(text):
    """提取主营产品"""
    results = []
    # Pattern 1: "公司主营/核心产品为XX"
    for pat in [r'主营[：:]\s*(.+?)(?:[。；\n]|$)', r'核心产品[：:]\s*(.+?)(?:[。；\n]|$)',
                r'主要产品[包含是为有][：:]?\s*(.+?)(?:[。；\n]|$)', 
                r'产品线[：:]\s*(.+?)(?:[。\n]|$)']:
        m = re.search(pat, text)
        if m:
            item = m.group(1).strip().rstrip('，,')
            if item and len(item) < 120:
                results.append(item)
    
    # Pattern 2: Extract from 产品线/business section headers and following content
    section_blocks = re.split(r'[（\(][一二三四五六七八九十\d]+[）\)]', text)
    for block in section_blocks:
        block = block.strip()
        if any(k in block[:30] for k in ['产品', '业务', '主营']):
            # Take first substantive sentence
            sens = re.split(r'[。\n]', block)
            for s in sens[:3]:
                s = s.strip()
                if s and len(s) > 6 and len(s) < 100:
                    results.append(s)
    
    # Pattern 3: Product names from filename context + text indicators
    # Look for "产品" / "产品是" / "包括" patterns near specific items
    for pat in [r'(?:产品|提供|生产|开发|制造)[：:]?\s*(.+?)(?:[。\n])',
                r'(?:机柜|设备|系统|材料|芯片|模块|器件|组件|电容|光纤|光模块|服务器|软件|平台).+?产品',
                r'产品(?:涵盖|包括|覆盖)[：:]?\s*(.+?)(?:[。；\n]|$)']:
        for m in re.finditer(pat, text):
            item = m.group(1).strip().rstrip('，,') if m.lastindex else m.group(0).strip()
            if item and len(item) < 120 and item not in results:
                results.append(item)
    
    return list(dict.fromkeys(results[:4]))  # deduplicate, max 4

def extract_core_business(text):
    """提取核心业务描述"""
    results = []
    
    # Look for "核心" "主营" "主要从事" etc.
    for pat in [r'核心(?:业务|逻辑)[：:]?\s*(.+?)(?:[。\n])',
                r'主要从事[：:]?\s*(.+?)(?:[。\n])',
                r'主业[：:]?\s*(.+?)(?:[。\n])',
                r'(?:公司|集团).+?主要从事[：:]?\s*(.+?)(?:[。\n])']:
        for m in re.finditer(pat, text):
            item = m.group(1).strip().rstrip('，,')
            if item and len(item) > 6 and len(item) < 150:
                results.append(item)
    
    # From "一、核心投资逻辑" or "核心逻辑" sections
    for m in re.finditer(r'(?:核心投资逻辑|核心逻辑)[：:]*?\s*(.+?)(?:[。\n])', text):
        item = m.group(1).strip()
        if item and len(item) > 8 and len(item) < 150:
            results.append(item)
    
    # "是一家" / "作为一家" pattern
    for m in re.finditer(r'(?:是一家|作为(?:一家|国内|全球)).+?(?:公司|企业|龙头|厂商|供应商)', text):
        item = m.group(0).strip()
        if len(item) < 150:
            results.append(item)
    
    return list(dict.fromkeys(results[:3]))

def extract_industry_position(text):
    """提取行业地位"""
    results = []
    
    for pat in [r'市场地位[：:]\s*(.+?)(?:[。\n])',
                r'(?:国内|全球|行业)(?:领先|龙头|前列|首家|唯一|第一|前三|前五)',
                r'(?:市占率|市场份额)[^\n。]*?(?:[%％\d]+)[^\n。]*',
                r'(?:龙头|领先|霸主|标杆)[^\n。]{0,60}']:
        for m in re.finditer(pat, text):
            item = m.group(0).strip()
            if item and len(item) > 5 and len(item) < 120:
                results.append(item)
    
    # "壁垒" section
    for m in re.finditer(r'(?:竞争壁垒|护城河|壁垒)[：:]*?\s*(.+?)(?:[。\n])', text):
        item = m.group(1).strip()
        if item and len(item) > 6 and len(item) < 120:
            results.append(item)
    
    return list(dict.fromkeys(results[:3]))

def extract_chain(text):
    """提取产业链位置"""
    results = []
    
    for pat in [r'(?:产业链|产业生态|价值链|供应链)[^\n。]{0,80}',
                r'(?:上下游|上游|下游|中游)[^\n。]{0,60}',
                r'[（(](?:上游|中游|下游)[）)][^\n。]{0,40}',
                r'横跨[^\n。]{0,40}',
                r'纵向[^\n。]{0,40}']:
        for m in re.finditer(pat, text):
            item = m.group(0).strip()
            if item and len(item) > 5 and len(item) < 120:
                results.append(item)
    
    return list(dict.fromkeys(results[:3]))

def extract_partners(text):
    """提取合作伙伴/客户"""
    results = []
    
    for pat in [r'(?:合作|战略合作|深度合作|绑定|携手)[^\n。]*?(?:华为|腾讯|阿里|字节|百度|英伟达|AMD|Intel|微软|谷歌|Meta|特斯拉|苹果|三星|比亚迪|宁德|中芯|台积|长鑫|长江存储|华虹|中兴|烽火|大唐|中兴通讯|[A-Z][a-z]+(?:公司|集团|科技|股份|有限|控股))[^\n。]*',
                r'(?:客户|大客户|核心客户|主要客户)[包含有为是][^\n。]{0,60}',
                r'切入[^\n。]{0,40}(?:供应链|产业链|体系)',
                r'(?:华为|腾讯|阿里|字节|百度|英伟达|AMD|Intel|微软|谷歌|Meta|特斯拉|苹果|三星|比亚迪|宁德|中芯|台积|长鑫|长江存储)[^\n。]{0,40}(?:合作|客户|供应商|配套)']:
        for m in re.finditer(pat, text):
            item = m.group(0).strip()
            if item and len(item) > 5 and len(item) < 120:
                results.append(item)
    
    # "合资" pattern
    for m in re.finditer(r'合资[^\n。]{0,80}', text):
        item = m.group(0).strip()
        if item not in results:
            results.append(item)
    
    return list(dict.fromkeys(results[:3]))

# ── Process all 85 stocks ──
total_filled = 0
stats = {f: 0 for f in TOTAL_FIELDS}

for code in sorted(value['stocks'].keys()):
    s = master['stocks'].get(code, value['stocks'][code])
    stock_name = s.get('name', '')
    
    # Find matching file
    matched = None
    for fp in RM_DIR.glob('*.md'):
        m = re.search(r'[（(](\d{6})', fp.name)
        if m and m.group(1) == code:
            matched = fp
            break
    
    if not matched:
        continue
    
    text = read_article_text(matched)
    if len(text) < 50:
        continue
    
    extractors = {
        'products': extract_products,
        'core_business': extract_core_business,
        'industry_position': extract_industry_position,
        'chain': extract_chain,
        'partners': extract_partners,
    }
    
    changed = False
    for field, extractor in extractors.items():
        if not s.get(field) or len(s.get(field, [])) == 0:
            result = extractor(text)
            if result:
                s[field] = result
                stats[field] += 1
                total_filled += len(result)
                changed = True
    
    if changed:
        pass  # will be saved below

# Save
with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"处理完成！")
print(f"从 85 只股票的文章中提取：")
for f in TOTAL_FIELDS:
    print(f"  {f}: {stats[f]} 只股票补全")
print(f"共填充 {total_filled} 个字段值")

# Show samples
print("\n=== 示例 ===")
for code in ['603070', '000037', '600869']:
    s = master['stocks'].get(code, {})
    print(f"\n{s.get('name','')} ({code}):")
    for f in TOTAL_FIELDS:
        vals = s.get(f, [])
        print(f"  {f}: {vals[:2]}")
