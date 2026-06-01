#!/usr/bin/env python3
"""Extract full article content from WeChat HTML"""
import requests
import re
import json
import html
from urllib.parse import unquote

URLS = [
    ('欧晶科技001269', 'https://mp.weixin.qq.com/s/mbJ8g4Loux5-KLmVEYytpw'),
    ('海得控制002184', 'https://mp.weixin.qq.com/s/ekhYGTgAiivWqXGRHfyulg'),
    ('华峰铝业601702', 'https://mp.weixin.qq.com/s/5SX419Pt_iIB92WombZGEQ'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

for name, url in URLS:
    print(f'\n{"="*60}')
    print(f'{name}')
    print(f'{url}')
    print(f'{"="*60}')
    
    resp = requests.get(url, headers=headers, timeout=30)
    
    # Extract title
    title = ''
    t = re.search(r'var\s+msg_title\s*=\s*["\'](.+?)["\']', resp.text)
    if t:
        title = t.group(1)
    else:
        t = re.search(r'<title>(.*?)</title>', resp.text)
        if t:
            title = t.group(1)
    print(f'Title: {title}')
    
    # Extract content from js_content div
    content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', resp.text, re.DOTALL)
    if content_match:
        raw_content = content_match.group(1)
        # Remove HTML tags but keep text
        text = re.sub(r'<[^>]+>', '\n', raw_content)
        text = html.unescape(text)
        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        # Save to file
        safe_name = name.replace('/', '_')
        with open(f'tmp_{safe_name}.txt', 'w', encoding='utf-8') as f:
            f.write(f'Title: {title}\n\n')
            f.write(text)
        
        print(f'Content extracted: {len(text)} chars')
        print(f'Saved to: tmp_{safe_name}.txt')
        
        # Print first 500 chars as preview
        print(f'\n--- Preview (first 500 chars) ---')
        print(text[:500])
    else:
        print('Could not find js_content')
        
        # Try to find content in msg_content variable
        mc = re.search(r'var\s+msg_content\s*=\s*["\'](.+?)["\']', resp.text, re.DOTALL)
        if mc:
            raw = mc.group(1)
            raw = raw.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            raw = unquote(raw)
            text = re.sub(r'<[^>]+>', '\n', raw)
            text = html.unescape(text)
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = text.strip()
            
            safe_name = name.replace('/', '_')
            with open(f'tmp_{safe_name}.txt', 'w', encoding='utf-8') as f:
                f.write(f'Title: {title}\n\n')
                f.write(text)
            
            print(f'Content extracted from msg_content: {len(text)} chars')
            print(f'Saved to: tmp_{safe_name}.txt')

print('\nAll done!')