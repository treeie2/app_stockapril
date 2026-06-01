#!/usr/bin/env python3
"""Try to fetch WeChat article using requests with mobile UA"""
import requests
import re
import json
import sys

URLS = [
    'https://mp.weixin.qq.com/s/mbJ8g4Loux5-KLmVEYytpw',
    'https://mp.weixin.qq.com/s/ekhYGTgAiivWqXGRHfyulg',
    'https://mp.weixin.qq.com/s/5SX419Pt_iIB92WombZGEQ',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

for url in URLS:
    print(f'\n{"="*60}')
    print(f'Fetching: {url}')
    print(f'{"="*60}')
    try:
        resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        print(f'Status: {resp.status_code}')
        print(f'Final URL: {resp.url}')
        print(f'Content length: {len(resp.text)}')
        
        if resp.status_code == 200:
            # Try to extract title
            title_match = re.search(r'var\s+msg_title\s*=\s*["\'](.+?)["\']', resp.text)
            if title_match:
                print(f'Title: {title_match.group(1)}')
            else:
                title_match = re.search(r'<title>(.*?)</title>', resp.text)
                if title_match:
                    print(f'Title (HTML): {title_match.group(1)}')
            
            # Try to extract content
            content_match = re.search(r'var\s+msg_content\s*=\s*["\'](.+?)["\']', resp.text, re.DOTALL)
            if content_match:
                print(f'Content found in msg_content var: {len(content_match.group(1))} chars')
            else:
                # Try rich_media_content
                content_match = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', resp.text, re.DOTALL)
                if content_match:
                    print(f'Content found in js_content div: {len(content_match.group(1))} chars')
                else:
                    # Save sample for analysis
                    with open(f'tmp_debug_{URLS.index(url)}.html', 'w', encoding='utf-8') as f:
                        f.write(resp.text[:5000])
                    print('Content extraction failed, saved first 5KB to debug file')
                    # Check for verification page
                    if '环境异常' in resp.text or '验证' in resp.text:
                        print('!!! Verification page detected (环境异常/验证) !!!')
                    elif '请输入验证码' in resp.text:
                        print('!!! CAPTCHA required !!!')
        else:
            print(f'Failed with status {resp.status_code}')
    except Exception as e:
        print(f'Error: {e}')

print('\nDone')