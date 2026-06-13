"""真正的误归因文章清理脚本"""
import json
import re

with open('data/stocks/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stocks = data['stocks']
code_name = {c: s.get('name', '') for c, s in stocks.items()}

# 明确要删除的: 标题包含其他股票代码.SH/SZ 且不是本股票
# 组合: (所属股票代码, 文章标题关键词) 
delete_list = [
    # 鹏鼎控股下面的无关文章
    ('002938', '利通电子（603629.SH）'),
    ('002938', '深科技（000021.SZ）高端存储'),
    # 四方股份下面的无关文章
    ('601126', '深科技（000021.SZ）高端存储'),
    ('601126', '生益科技（600183.SH）'),
    ('601126', '鼎泰高科 (301377.SZ)'),
    # 中钨高新下面
    ('000657', '鼎泰高科 (301377.SZ)'),
    # 回天新材下面
    ('300041', '天洋新材（603330.SH）'),
    # 鼎龙股份下面
    ('300054', '四方股份（601126.SH）'),
    # 鼎泰高科下面
    ('301377', '中钨高新 (000657.SZ)'),
    # 生益电子下面
    ('688183', '生益科技（600183.SH）'),
    # 德邦科技下面
    ('688035', '天洋新材（603330.SH）'),
]

total_deleted = 0
for belong_code, keyword in delete_list:
    articles = stocks[belong_code].get('articles', [])
    before = len(articles)
    stocks[belong_code]['articles'] = [a for a in articles if keyword not in a.get('title', '')]
    after = len(stocks[belong_code]['articles'])
    deleted = before - after
    if deleted > 0:
        print(f"✅ [{belong_code} {stocks[belong_code].get('name','')}] 删除 {deleted} 篇({keyword})")
        stocks[belong_code]['mention_count'] = after
        total_deleted += deleted

print(f"\n共删除 {total_deleted} 篇误归因文章")

with open('data/stocks/stocks_master.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存 stocks_master.json")