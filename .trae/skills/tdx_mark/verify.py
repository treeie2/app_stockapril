#!/usr/bin/env python3
"""验证生成的 mark.dat 文件"""
with open('.trae/skills/tdx_mark/mark_2026-05-24.dat', 'rb') as f:
    raw = f.read()

# 检查GBK编码
try:
    text = raw.decode('gbk')
    print("✅ GBK 编码: 正常")
except:
    print("❌ GBK 编码: 异常")

# 检查文件大小
print(f"📦 文件大小: {len(raw) / 1024:.1f} KB")

# 检查沪电股份和利扬芯片
tip_start = text.find('[TIP]')
tip_section = text[tip_start:]

for code, name in [('00002463', '沪电股份'), ('01688135', '利扬芯片')]:
    for line in tip_section.split('\n'):
        if line.startswith(code + '='):
            print(f"\n✅ {name} ({code}):")
            print(f"   {line[:200]}")
            break

# 检查统计
print(f"\n📊 总行数: {len(text.splitlines())} 行")
print(f"📊 [MARK] 条目: {text.count('[MARK]')}")
print(f"📊 [TIP] 条目: {len([l for l in text.splitlines() if '=' in l and not l.startswith('[')])}")