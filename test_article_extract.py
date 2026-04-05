import requests
import re
import html
import sqlite3

url = 'https://mp.weixin.qq.com/s/FvWStj9Y_Qmg7V4S9IOdug'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

print('Fetching article...')
response = requests.get(url, headers=headers, timeout=30)
response.encoding = 'utf-8'

if response.status_code == 200:
    text = response.text
    
    # Extract title
    safe_html = text.replace('(', ' ').replace(')', ' ')
    title_match = re.search(r'<h1[^>]*class="rich_media_title[^"]*"[^>]*>(.*?)</h1>', safe_html, re.DOTALL)
    title = title_match.group(1).strip() if title_match else 'Unknown'
    title = re.sub(r'<[^>]*>', '', title)
    title = html.unescape(title)
    print(f'Title: {title}')
    print()
    
    # Clean text
    text = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), text)
    text = text.replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ')
    text = text.replace('{', ' ').replace('}', ' ')
    clean_text = re.sub(r'<[^>]*>', '', text)
    clean_text = html.unescape(clean_text)
    
    # Method 1: Exact match from database
    print('Loading stock names from database...')
    conn = sqlite3.connect('data/stock_research.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM stocks')
    all_stock_names = [row['name'] for row in cursor.fetchall()]
    conn.close()
    print(f'Total stocks in DB: {len(all_stock_names)}')
    
    found_stocks = set()
    for stock_name in all_stock_names:
        if stock_name in clean_text:
            found_stocks.add(stock_name)
    
    print(f'\nFound stocks by exact match: {sorted(found_stocks)}')
    print(f'Total found: {len(found_stocks)}')
else:
    print(f'Failed: {response.status_code}')
