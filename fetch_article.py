#!/usr/bin/env python3
"""
手动抓取微信公众号文章并保存到 raw_material
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
        'url': url
    }

def save_to_raw_material(article):
    """保存到 raw_material 文件"""
    today = datetime.now().strftime('%Y-%m-%d')
    raw_material_file = Path(f"e:/github/stock-research-backup/raw_material/raw_material_{today}.md")
    
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
    
    print(f"✅ 文章已保存到: {raw_material_file}")
    return raw_material_file

def main():
    url = "https://mp.weixin.qq.com/s/cJqK4aWM24AFml-5VyFeCA"
    
    print(f"🚀 开始抓取文章: {url}")
    
    try:
        article = fetch_wechat_article(url)
        print(f"📄 标题: {article['title']}")
        print(f"📅 日期: {article['date']}")
        print(f"📝 内容长度: {len(article['content'])} 字符")
        
        # 保存到 raw_material
        raw_material_file = save_to_raw_material(article)
        
        print(f"\n✅ 抓取完成！")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
