#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理 raw_material/value 中的离线文章：
1. 清洗CSS/HTML垃圾内容
2. 提取元数据（标题、日期、原文URL、股票代码）
3. 生成 raw_material 格式文件
4. 提取结构化数据，生成合并JSON
"""

import os
import re
import json
import sys
from datetime import datetime
from collections import defaultdict

VALUE_DIR = r'e:\firebase++\app_stockapril\raw_material\value'
RAW_DIR = r'e:\firebase++\app_stockapril\raw_material'
OUTPUT_JSON = r'e:\firebase++\app_stockapril\data\value_stocks_output.json'

# 行业级报告文件名列表（不以单个股票为核心）
INDUSTRY_KEYWORDS = [
    '产业链', '板块', '行业', '赛道', '全景', '全球',
    '投资机会', '深度研报', '策略报告', '涨价逻辑',
    '地缘政治', '宏观', '时代', '产业', '十五五',
    'SpaceX', 'Token出海', '储能即', '出海',
]

# 综合资讯/每日汇总类文章标题关键词（应跳过，不归入个股）
DIGEST_TITLE_KEYWORDS = [
    '今天的一些信息整理',
    '信息汇总',
    '信息整理',
    '调研纪要',  # 除非是特定个股的调研纪要
]


def strip_css_and_html(text):
    """Strip CSS styles and HTML junk from article text."""
    # Remove CSS blocks: everything between { and } that follows a selector
    text = re.sub(r'\s*\*\{[^}]*\}', '', text)
    text = re.sub(r'\s*\.\w[\w-]*\{[^}]*\}', '', text)
    text = re.sub(r'\s*#\w[\w-]*\{[^}]*\}', '', text)
    text = re.sub(r'\s*\w+\.\w[\w-]*\{[^}]*\}', '', text)
    # Remove HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove inline SVG/data URIs
    text = re.sub(r'data:image/svg\+xml[^)]+', '', text)
    text = re.sub(r'!\[\]\(data:image[^)]+\)', '', text)
    # Remove image markdown
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove http://...images
    text = re.sub(r'http://mmbiz\.qpic\.cn[^\s\)]*', '', text)
    # Remove "阅读" "赞" buttons
    text = re.sub(r'\s*(阅读|赞)\s*', '', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def parse_article_metadata(text):
    """Extract metadata from the article text."""
    result = {
        'title': '',
        'date': '',
        'source': '',
        'stock_code': '',
        'stock_name': '',
        'is_industry_report': False,
        'content': '',
    }

    lines = text.split('\n')
    processed_lines = []

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Skip CSS junk lines
        if not line_stripped or line_stripped.startswith('* {'):
            continue
        if re.match(r'^[\s\.#\w-]+\{[^}]*\}', line_stripped):
            continue
        if re.match(r'^(body|\.\w+|#\w+|\w+\.\w+)\{', line_stripped):
            continue

        # Extract date line: "原创 深度价值分析 深度价值展望 YYYY-MM-DD HH:MM 广东"
        date_match = re.search(
            r'原创\s+深度价值(?:分析)?\s*深度价值展望\s+(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}',
            line_stripped
        )
        if date_match:
            result['date'] = date_match.group(1)
            continue

        # Extract source URL: "> 原文地址: [URL]"
        source_match = re.search(r'原文地址:\s*\[?(https?://[^\s\]\)]+)', line_stripped)
        if source_match:
            result['source'] = source_match.group(1).rstrip(')')
            continue

        # Extract title (first meaningful line that's not CSS junk)
        if not result['title'] and line_stripped and len(line_stripped) > 5:
            # Skip lines that look like CSS or too short
            if not line_stripped.startswith('*') and not line_stripped.startswith('.'):
                # Clean the title from CSS-like suffix
                title = re.sub(r'\s*\\\*\{.*', '', line_stripped)
                title = re.sub(r'\s+\*$', '', title)
                title = title.strip()
                if title and len(title) > 3:
                    result['title'] = title

        # Keep content lines
        if line_stripped and not line_stripped.startswith('![') and not re.match(r'^\s*(阅读|赞)\s*$', line_stripped):
            processed_lines.append(line)

    result['content'] = '\n'.join(processed_lines).strip()
    return result


def extract_stock_info(filename, title, content):
    """Extract stock code and name from filename or title."""
    result = {'stock_code': '', 'stock_name': '', 'is_industry_report': False}

    # Check if it's an industry report
    name_lower = filename.lower()
    for kw in INDUSTRY_KEYWORDS:
        if kw in name_lower:
            result['is_industry_report'] = True
            break

    # Pattern 1: 股票名（CODE) from filename like '万控智造（603070_sh)...'
    m = re.search(r'(.+?)[（(](\d{6})[_\.]?(?:sh|sz)?[)）]', filename)
    if m:
        result['stock_name'] = m.group(1)
        result['stock_code'] = m.group(2)
        return result

    # Pattern 2: 股票名_CODE_ from filename like '三安光电_600703_...'
    m = re.search(r'(.+?)[_ ](\d{6})[_ ]', filename)
    if m:
        result['stock_name'] = m.group(1).strip('_ ')
        result['stock_code'] = m.group(2)
        return result

    # Pattern 3: 股票名（CODE) from title
    m = re.search(r'(.+?)[（(](\d{6})[_\.]?(?:sh|sz)?[)）]', title)
    if m:
        result['stock_name'] = m.group(1)
        result['stock_code'] = m.group(2)
        return result

    # Pattern 4: 股票名 CODE from title like '三安光电 600703'
    m = re.search(r'(.+?)\s+(\d{6})\s', title)
    if m:
        result['stock_name'] = m.group(1).strip()
        result['stock_code'] = m.group(2)
        return result

    # If no stock code found, it's likely an industry report
    result['is_industry_report'] = True
    return result


def extract_structured_data(content, stock_info):
    """Extract structured data from the article content."""
    structured = {
        'accidents': [],
        'insights': [],
        'key_metrics': [],
        'target_valuation': [],
    }

    lines = content.split('\n')
    current_section = ''

    # Identify key sections
    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Detect section headings
        if re.match(r'^#{1,4}\s+', line_stripped) or re.match(r'^[^#\n]{2,}==+$', line_stripped):
            heading = re.sub(r'^#+\s*', '', line_stripped).rstrip('= ')
            current_section = heading

        # Extract key metrics (lines with numbers/percentages/货币单位)
        if re.search(r'[万亿千百]?[元股]|%|\d{4}年|\d{4}Q[1-4]', line_stripped) and len(line_stripped) > 5:
            # Filter out table formatting lines
            if not re.match(r'^[\|\-\s:]+$', line_stripped) and not line_stripped.startswith('**'):
                structured['key_metrics'].append(line_stripped[:120])

        # Extract target valuation
        if re.search(r'目标[价市估]|看到\s*\d+[亿倍]|[市目]值\s*\d+', line_stripped):
            structured['target_valuation'].append(line_stripped[:120])

        # Extract insights (lines with "核心逻辑" "投资逻辑" etc.)
        if re.search(r'核心(逻辑|看点|驱动|投资)|投资逻辑|估值(逻辑|重估)|戴维斯双击', line_stripped):
            structured['insights'].append(line_stripped[:200])

        # Extract accidents (lines with time-specific events)
        if re.search(r'\d{4}年\d{1,2}月|落地|投产|获批|签约|中标|公告|发布|量产|突破|入组|入选', line_stripped):
            if len(line_stripped) > 10 and len(line_stripped) < 200:
                structured['accidents'].append(line_stripped[:150])

    # Deduplicate while preserving order
    for key in structured:
        seen = set()
        deduped = []
        for item in structured[key]:
            if item not in seen:
                seen.add(item)
                deduped.append(item)
        structured[key] = deduped[:10]  # Limit to 10 items each

    return structured


def extract_core_fields(content, stock_info):
    """Extract core business fields for the stock."""
    fields = {
        'core_business': [],
        'industry_position': [],
        'chain': [],
        'partners': [],
    }

    lines = content.split('\n')
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        lower = line_stripped.lower()

        # Industry position (行业地位)
        if re.search(r'(龙头|领先|第一|寡头|市占率|份额|核心供应商)', line_stripped):
            fields['industry_position'].append(line_stripped[:100])

        # Core business
        if re.search(r'(主营业务|核心业务|主要产品|专注于|深耕)', line_stripped):
            fields['core_business'].append(line_stripped[:100])

        # Industry chain position
        if re.search(r'产业链|中游|上游|下游|垂直|环节', line_stripped):
            fields['chain'].append(line_stripped[:100])

        # Partners
        partner_match = re.findall(
            r'(?:合作|绑定|供应|客户|伙伴)[：:为与和]\s*([\u4e00-\u9fa5\w]{2,10}(?:股份|集团|科技|电子|能源|医药|工业|控股)?)',
            line_stripped
        )
        for p in partner_match:
            fields['partners'].append(p)

        # Known company names
        known_companies = re.findall(
            r'(?:阿里巴巴|字节跳动|腾讯|华为|比亚迪|特斯拉|宁德时代|隆基|中芯国际|长鑫|京东方|中航|上汽)',
            line_stripped
        )
        fields['partners'].extend(known_companies)

    # Deduplicate
    for key in fields:
        fields[key] = list(dict.fromkeys(fields[key]))[:5]

    return fields


def clean_content_for_raw(content):
    """Clean content for raw_material format - remove remaining junk."""
    # Remove the metadata line with "原创 深度价值"
    content = re.sub(r'原创\s+深度价值.*?\d{2}:\d{2}\s+.*', '', content)
    # Remove source line
    content = re.sub(r'>\s*原文地址:.*', '', content)
    # Remove "风险提示与免责声明" blocks
    content = re.sub(r'风险提示与免责声明[^。]*。', '', content)
    content = re.sub(r'免责声明[^。]*。', '', content)
    # Remove SVG junk
    content = re.sub(r'data:image/svg\+xml[^>]*>', '', content)
    # Clean up
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    return content.strip()


def process_articles():
    """Main processing function."""
    os.makedirs(RAW_DIR, exist_ok=True)

    all_files = sorted([f for f in os.listdir(VALUE_DIR) if f.endswith('.md')])
    print(f"找到 {len(all_files)} 篇文章待处理")

    # Group raw_material by date
    raw_by_date = defaultdict(list)
    # Collect all structured entries
    all_stocks = {}
    stats = {'single_stock': 0, 'industry': 0, 'no_date': 0}

    for idx, filename in enumerate(all_files):
        filepath = os.path.join(VALUE_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='gbk') as f:
                    raw_text = f.read()
            except:
                print(f"  [ERROR] 无法读取: {filename}")
                continue

        # Strip CSS
        cleaned = strip_css_and_html(raw_text)

        # Parse metadata
        meta = parse_article_metadata(cleaned)
        if not meta['title']:
            meta['title'] = filename.replace('.md', '').replace('_', ' ')[:80]

        # Extract stock info
        stock_info = extract_stock_info(filename, meta['title'], meta['content'])
        meta['stock_code'] = stock_info['stock_code']
        meta['stock_name'] = stock_info['stock_name']
        meta['is_industry_report'] = stock_info['is_industry_report']

        # 检查标题是否为综合资讯/每日汇总类文章，是则跳过不归入个股
        if not meta['is_industry_report']:
            for kw in DIGEST_TITLE_KEYWORDS:
                if kw in meta['title']:
                    meta['is_industry_report'] = True
                    print(f"  [跳过综合资讯] {filename} -> {meta['title'][:50]}")
                    break

        if not meta['date']:
            stats['no_date'] += 1
            # Try to extract date from filename
            date_m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            if date_m:
                meta['date'] = date_m.group(1)
            else:
                meta['date'] = '2026-01-01'  # fallback

        # Clean content for raw_material
        clean_content = clean_content_for_raw(meta['content'])

        # ===== STEP 1: Generate raw_material =====
        raw_content = f"""## Article
source: {meta['source'] if meta['source'] else 'https://mp.weixin.qq.com/s/unknown'}
fetched_at: {meta['date']}T08:00:00
title: {meta['title']}

{clean_content}
"""
        raw_by_date[meta['date']].append(raw_content)

        # ===== STEP 2: Build structured JSON =====
        if not meta['is_industry_report'] and meta['stock_code']:
            stats['single_stock'] += 1

            # Extract structured data
            struct_data = extract_structured_data(clean_content, stock_info)
            core_fields = extract_core_fields(clean_content, stock_info)

            stock_entry = {
                'name': meta['stock_name'],
                'code': meta['stock_code'],
                'board': 'SH' if meta['stock_code'].startswith(('6', '9')) else 'SZ',
                'industry_position': core_fields['industry_position'],
                'core_business': core_fields['core_business'],
                'chain': core_fields['chain'],
                'partners': core_fields['partners'],
                'mention_count': 1,
                'last_updated': meta['date'],
                'articles': [
                    {
                        'title': meta['title'],
                        'date': meta['date'],
                        'source': meta['source'] if meta['source'] else '',
                        'accidents': struct_data['accidents'],
                        'insights': struct_data['insights'],
                        'key_metrics': struct_data['key_metrics'],
                        'target_valuation': struct_data['target_valuation'],
                    }
                ]
            }

            # Merge if stock already exists
            code = meta['stock_code']
            if code in all_stocks:
                existing = all_stocks[code]
                existing['mention_count'] += 1
                # Update last_updated if newer
                if meta['date'] > existing['last_updated']:
                    existing['last_updated'] = meta['date']
                # Add article if not duplicate
                existing_sources = {a['source'] for a in existing['articles'] if a['source']}
                if stock_entry['articles'][0]['source'] not in existing_sources:
                    existing['articles'].append(stock_entry['articles'][0])
                # Merge fields
                for field in ['industry_position', 'core_business', 'chain']:
                    existing[field] = list(dict.fromkeys(existing[field] + core_fields[field]))
            else:
                all_stocks[code] = stock_entry
        else:
            stats['industry'] += 1

        if (idx + 1) % 50 == 0:
            print(f"  已处理 {idx + 1}/{len(all_files)} 篇...")

    # ===== Write raw_material files =====
    print(f"\n写入 raw_material 文件...")
    written_raw = 0
    for date_str, articles in sorted(raw_by_date.items()):
        # Find existing raw_material files for this date
        existing_count = len([
            f for f in os.listdir(RAW_DIR)
            if f.startswith(f'raw_material_{date_str}')
        ])

        # Get the next suffix number
        suffix = ''
        if existing_count > 0:
            # Try to use the value suffix
            suffix = '_value'

        # If there's already a _value file, append number
        output_name = f'raw_material_{date_str}{suffix}.md'
        output_path = os.path.join(RAW_DIR, output_name)
        counter = 2
        while os.path.exists(output_path):
            output_name = f'raw_material_{date_str}{suffix}_{counter}.md'
            output_path = os.path.join(RAW_DIR, output_name)
            counter += 1

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(articles))
        written_raw += 1

    # ===== Write structured JSON =====
    print(f"\n写入结构化JSON...")
    output = {
        'version': '2.3',
        'updated_at': datetime.now().strftime('%Y-%m-%d'),
        'total_stocks': len(all_stocks),
        'total_articles': sum(s['mention_count'] for s in all_stocks.values()),
        'stocks': all_stocks,
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # ===== Print summary =====
    print(f"\n{'='*60}")
    print(f"处理完成！")
    print(f"{'='*60}")
    print(f"总文章数: {len(all_files)}")
    print(f"  个股报告: {stats['single_stock']}")
    print(f"  行业报告: {stats['industry']}")
    print(f"  未识别日期: {stats['no_date']}")
    print(f"生成 raw_material 文件数: {written_raw}")
    print(f"提取个股数: {len(all_stocks)}")
    print(f"输出 JSON: {OUTPUT_JSON}")

    # Print first 20 stocks
    print(f"\n提取的个股列表（前30只）:")
    stock_list = sorted(all_stocks.items(), key=lambda x: x[1]['last_updated'], reverse=True)
    for code, s in stock_list[:30]:
        print(f"  {code} {s['name']} - {s['last_updated']} ({s['mention_count']}篇)")

    return output


if __name__ == '__main__':
    result = process_articles()