import sys
sys.stdout.reconfigure(encoding='utf-8')

t = open('templates/stock_detail.html', 'r', encoding='utf-8').read()
print('Has industry_background:', 'industry_background' in t)
print('Has industry-bg:', 'industry-bg' in t)

# 显示 IB 区块完整代码
idx = t.find('{% if article.industry_background')
if idx > 0:
    end = t.find('{% endif %}', idx) + len('{% endif %}')
    block = t[idx:end]
    print(f'\n=== IB 显示区块 ({len(block)} chars) ===')
    print(block)
else:
    print('\n❌ NO industry_background block found!')
