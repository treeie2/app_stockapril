"""从 jl 文件夹的 HTML 文件中提取文章，生成 raw_material markdown"""
import re, html
from pathlib import Path

jl_dir = Path(r"e:\github\stock-research-backup\temp11\jl")
out_md = Path(r"e:\github\stock-research-backup\temp11\jl_raw_material.md")

articles = []

for html_path in sorted(jl_dir.glob("*/index.html")):
    raw = html_path.read_text(encoding="utf-8")
    
    # --- 提取标题 ---
    title_m = re.search(r'<h1[^>]*id="activity-name"[^>]*>.*?<span[^>]*class="js_title_inner"[^>]*>(.*?)</span>', raw, re.DOTALL)
    if not title_m:
        title_m = re.search(r'<h1[^>]*id="activity-name"[^>]*>(.*?)</h1>', raw, re.DOTALL)
    title = html.unescape(title_m.group(1).strip()) if title_m else html_path.parent.name
    
    # --- 提取发布日期 ---
    date_m = re.search(r'id="publish_time"[^>]*>\s*(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})', raw)
    date_str = date_m.group(1) if date_m else ""
    
    # --- 提取来源(公众号名称) ---
    source_m = re.search(r'id="js_name"[^>]*>\s*(\S+?)\s*</a>', raw)
    source = source_m.group(1).strip() if source_m else "国曜资本"
    
    # --- 提取正文 ---
    content_m = re.search(r'<div[^>]*class="rich_media_content[^"]*"[^>]*id="js_content"[^>]*>(.*?)</div>\s*<', raw, re.DOTALL)
    if not content_m:
        content_m = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<', raw, re.DOTALL)
    
    if content_m:
        raw_html = content_m.group(1)
        raw_html = re.sub(r'<style[^>]*>.*?</style>', '', raw_html, flags=re.DOTALL)
        raw_html = re.sub(r'<br\s*/?>', '\n', raw_html)
        raw_html = re.sub(r'</p>', '\n', raw_html)
        raw_html = re.sub(r'</div>', '\n', raw_html)
        raw_html = re.sub(r'</section>', '\n', raw_html)
        text = re.sub(r'<[^>]+>', '', raw_html)
        text = html.unescape(text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
    else:
        text = ""
        print(f"  ⚠️ 未找到正文: {title}")
    
    articles.append({
        "source": f"https://mp.weixin.qq.com/s/{html_path.parent.name}",
        "title": title,
        "date": date_str,
        "content": text,
    })

with open(out_md, "w", encoding="utf-8") as f:
    f.write("# Raw Material - jl\n\n")
    for a in articles:
        f.write("## Article\n")
        f.write(f"source: {a['source']}\n")
        f.write(f"title: {a['title']}\n")
        f.write(f"date: {a['date']}\n")
        f.write(f"fetched_at: {a['date']}\n\n")
        f.write(a["content"])
        f.write("\n\n---\n\n")

print(f"完成! 共 {len(articles)} 篇文章")
print(f"输出: {out_md}")