#!/usr/bin/env python3
"""
手动抓取微信公众号文章并保存到 raw_material
支持多个链接
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re

def fetch_wechat_article(url):
    """抓取微信公众号文章"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = soup.find('h1', class_='rich_media_title') or soup.find('h2', class_='rich_media_title')
        title = title.get_text(strip=True) if title else "无标题"
        
        # 提取发布时间
        publish_time = soup.find('em', id='publish_time')
        if publish_time:
            date_str = publish_time.get_text(strip=True)
        else:
            # 尝试从脚本中提取
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'svr_time' in script.string:
                    match = re.search(r'"publish_time":"([^"]+)"', script.string)
                    if match:
                        date_str = match.group(1)
                        break
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 提取正文内容
        content_div = soup.find('div', id='js_content')
        if content_div:
            # 清理图片标签
            for img in content_div.find_all('img'):
                img.decompose()
            
            # 提取文本
            content = content_div.get_text(separator='\n', strip=True)
            # 清理多余空行
            content = re.sub(r'\n{3,}', '\n\n', content)
        else:
            content = "无法提取正文内容"
        
        return {
            'title': title,
            'date': date_str,
            'content': content,
            'url': url,
            'success': True
        }
    except Exception as e:
        print(f"❌ 抓取失败：{str(e)[:100]}")
        return {
            'title': '抓取失败',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'content': f'无法抓取文章：{str(e)}',
            'url': url,
            'success': False
        }

def save_to_raw_material(article, file_suffix=''):
    """保存到 raw_material 文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    suffix = f"_{file_suffix}" if file_suffix else ''
    raw_material_file = Path(f"e:/github/stock-research-backup/raw_material/raw_material_{today}{suffix}.md")
    
    # 确保目录存在
    raw_material_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 构建 markdown 内容
    markdown_content = f"""## Article
source: {article['url']}
fetched_at: {datetime.now().isoformat()}
title: {article['title']}
date: {article['date']}

{article['content']}

---

"""
    
    # 追加到文件
    with open(raw_material_file, 'a', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ 文章已保存到：{raw_material_file}")
    return raw_material_file

def main():
    # 两个文章链接
    urls = [
        "https://mp.weixin.qq.com/s/5bluU2s8izAKQ9K3Fb2KGA",
        "https://mp.weixin.qq.com/s/6PeirSTCbFUP9h2JdS5i2Q"
    ]
    
    print(f"🚀 开始抓取 {len(urls)} 篇文章...\n")
    
    success_count = 0
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] 抓取：{url}")
        article = fetch_wechat_article(url)
        
        if article['success']:
            print(f"  📄 标题：{article['title']}")
            print(f"  📅 日期：{article['date']}")
            print(f"  📝 内容长度：{len(article['content'])} 字符")
            
            # 保存到文件
            save_to_raw_material(article, file_suffix=f"_{i}")
            success_count += 1
        else:
            print(f"  ❌ 抓取失败")
        print()
    
    print(f"\n✅ 完成！成功抓取 {success_count}/{len(urls)} 篇文章")

if __name__ == '__main__':
    main()
