"""
生成第一层信息提取报告
"""
import json
from pathlib import Path

MASTER_FILE = Path("data/stocks/stocks_master.json")

# 加载数据
with open(MASTER_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
    stocks = data.get('stocks', {})

# 统计
total = len(stocks)
complete = sum(1 for s in stocks.values() if s.get('products') and s.get('core_business') and s.get('industry_position'))
partial = sum(1 for s in stocks.values() if (s.get('products') or s.get('core_business') or s.get('industry_position')) and not (s.get('products') and s.get('core_business') and s.get('industry_position')))
empty = sum(1 for s in stocks.values() if not s.get('products') and not s.get('core_business') and not s.get('industry_position'))

# 找出有完整信息的股票示例
complete_stocks = [(code, s) for code, s in stocks.items() if s.get('products') and s.get('core_business') and s.get('industry_position')]

print("=" * 80)
print("📊 个股第一层信息完整度报告")
print("=" * 80)
print(f"\n总股票数：{total}")
print(f"\n完整度统计:")
print(f"  ✅ 完整（3 个字段都有）：{complete} 只 ({complete/total*100:.1f}%)")
print(f"  ⚠️  部分（有 1-2 个字段）：{partial} 只 ({partial/total*100:.1f}%)")
print(f"  ❌ 无第一层信息：{empty} 只 ({empty/total*100:.1f}%)")

print(f"\n数据来源:")
print(f"  - stocks_master.json: {total} 只")
print(f"  - raw_material/stocks_from_raw_materials_complete_2026-04-23.json: 32 只（已全部在 master 中）")
print(f"  - skill 日期分片文件：14 只（本次补充 8 只）")

print(f"\n本次更新:")
print(f"  ✅ 补充了 8 只股票的第一层信息:")
print(f"     - 300658 延江股份")
print(f"     - 301336 趣睡科技")
print(f"     - 301468 博盈特焊")
print(f"     - 600183 生益科技")
print(f"     - 603186 华正新材")
print(f"     - 603308 应流股份")
print(f"     - 605589 圣泉集团")
print(f"     - 688519 南亚新材")

print(f"\n示例股票（完整第一层信息）:")
for code, stock in complete_stocks[:3]:
    print(f"\n  {code} {stock.get('name')}:")
    print(f"    产品：{stock.get('products', [])[:3]}")
    print(f"    核心业务：{stock.get('core_business', [])[:2]}")
    print(f"    行业地位：{stock.get('industry_position', [])[:2]}")

print("\n" + "=" * 80)
print("建议:")
print("  1. 继续从 Firebase 同步更多研究数据")
print("  2. 使用 wechat-fetch-research-embedded skill 从公众号文章提取更多信息")
print("  3. 手动补充或从其他数据源导入")
print("=" * 80)
