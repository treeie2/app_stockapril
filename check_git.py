import json
import os

temp_path = os.path.join(os.environ['TEMP'], 'git_master.json')

# 尝试不同编码
for enc in ['utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'utf-8']:
    try:
        with open(temp_path, 'r', encoding=enc) as f:
            d = json.load(f)
        print(f'Successfully read with encoding: {enc}')
        break
    except:
        continue

lu = [(c, s.get('last_updated')) for c, s in d['stocks'].items() if s.get('last_updated') == '2026-05-09']
print(f'Git HEAD 2026-05-09: {len(lu)}')

# 也检查本地文件
with open('data/master/stocks_master.json', 'r', encoding='utf-8') as f:
    local = json.load(f)

local_lu = [(c, s.get('last_updated')) for c, s in local['stocks'].items() if s.get('last_updated') == '2026-05-09']
print(f'Local 2026-05-09: {len(local_lu)}')
