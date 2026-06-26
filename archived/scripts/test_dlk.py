import re, html, requests

url = 'https://mp.weixin.qq.com/s/LYz3-fNpKaO_oQsR3ao66Q'

# 使用更完整的 headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}
response = requests.get(url, headers=headers, timeout=30)
text = response.text

print('Original contains 德科立:', '德科立' in text)

# 检查我们的清理过程
text2 = text.replace('(', ' ').replace(')', ' ').replace('[', ' ').replace(']', ' ')
print('After bracket replace:', '德科立' in text2)

text3 = text2.replace('{', ' ').replace('}', ' ')
print('After brace replace:', '德科立' in text3)

# 问题可能在这里 - 正则表达式 r'<[^>]*>' 会匹配 <span style="color: rgb(255, 218, 169);"> 这样的标签
# 但因为我们替换了括号，标签可能被破坏了
clean_text = re.sub(r'<[^>]*>', '', text3)
print('After tag removal:', '德科立' in clean_text)

# 让我们看看德科立周围的原始内容
idx = text.find('德科立')
print('Original context:', repr(text[max(0,idx-50):idx+50]))
