#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert manually formatted raw_material to standard Article format."""

from pathlib import Path
import re

def convert_file(input_path: str, output_path: str):
    """Convert the manually formatted file to standard Article format."""
    content = Path(input_path).read_text(encoding='utf-8')
    
    # Split by articles (marked by "# " at start of line followed by article title)
    articles = re.split(r'\n(?=# (?:磷化铟|TGV|航天轴承))', content)
    
    output_lines = []
    
    for i, article in enumerate(articles):
        article = article.strip()
        if not article or article.startswith('# 2026-04-21'):
            continue
        
        # Extract title
        title_match = re.match(r'^# (.+?)(?:\n|$)', article)
        if not title_match:
            continue
        
        title = title_match.group(1).strip()
        
        # Extract source and date from metadata
        source_match = re.search(r'\*\*来源\*\*: (.+?)(?:\n|$)', article)
        source = source_match.group(1).strip() if source_match else "微信公众号"
        
        date_match = re.search(r'\*\*文章日期\*\*: (.+?)(?:\n|$)', article)
        date = date_match.group(1).strip() if date_match else "2026-04-21"
        
        # Extract content (everything after the article header)
        content_start = article.find('## 文章正文')
        if content_start == -1:
            content_start = article.find('## 提取数据')
        if content_start == -1:
            content_start = len(title_match.group(0))
        
        article_content = article[content_start:].strip()
        
        # Remove the trailing metadata sections
        article_content = re.sub(r'\n---\n\*\*数据来源\*\*:.*$', '', article_content, flags=re.DOTALL)
        
        # Write in standard format
        output_lines.append("## Article")
        output_lines.append(f"source: manual:{source}")
        output_lines.append(f"fetched_at: 2026-04-21T09:26:37+00:00")
        output_lines.append(f"title: {title}")
        output_lines.append(f"date: {date}")
        output_lines.append("")
        output_lines.append(article_content)
        output_lines.append("")
        output_lines.append("---")
        output_lines.append("")
    
    output_content = "\n".join(output_lines)
    Path(output_path).write_text(output_content, encoding='utf-8')
    print(f"✅ Converted {input_path} -> {output_path}")
    print(f"   Generated {len(articles)} articles")

if __name__ == "__main__":
    input_file = "e:/github/stock-research-backup/raw_material/raw_material_2026-04-21.md"
    output_file = "e:/github/stock-research-backup/raw_material/raw_material_2026-04-21_standard.md"
    convert_file(input_file, output_file)
