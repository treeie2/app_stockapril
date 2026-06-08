#!/usr/bin/env python3
"""生成三篇新文章的中间JSON文件"""
import json
from pathlib import Path

ROOT = Path(__file__).parent  # scripts 目录
SKILL_DIR = ROOT.parent  # skill根目录
PROJECT_DIR = SKILL_DIR.parents[2]  # 项目根目录

today = '2026-06-08'

url1 = 'https://mp.weixin.qq.com/s/63qAcdPPP2PxVa0XOBsz7Q'  # 顺络电子
url2 = 'https://mp.weixin.qq.com/s/AvLis4FyYJX91lKteLt4jw'  # 泰金新能
url3 = 'https://mp.weixin.qq.com/s/zGuJIe2fJuufJNqMYvpjaw'  # 中巨芯

# 构建中间数据
stocks = []

# === 顺络电子 002138 (已有，追加文章) ===
stocks.append({
    "code": "002138",
    "name": "顺络电子",
    "board": "SZ",
    "industry": "电子-元件-被动元件",
    "concepts": ["电感", "MLCC", "AI算力", "钽电容", "TLVR电感"],
    "products": ["TLVR电感", "钽电容", "片式电感"],
    "core_business": ["电感元件研发与制造", "钽电容研发与制造"],
    "industry_position": ["全球电感行业前三", "国内民用钽电容进展最快"],
    "chain": ["中游-被动元件制造"],
    "partners": ["苹果", "英伟达(N)", "谷歌", "亚马逊"],
    "mention_count": 1,
    "last_updated": today,
    "articles": [
        {
            "title": "顺络电子，翻倍空间？",
            "date": "2026-06-08",
            "source": url1,
            "accidents": [
                "7月中全系列产品再次涨价35%、高端产品涨价70%+",
                "TLVR电感交货期延长到32-40周，排产已延伸至2028年",
                "海外AI大厂N客户部分订单陆续向国内企业转移",
                "公司上半年已通过N客户的验证并收到订单锁定产能",
                "公司产品于26年Q2进入苹果，已锁定二供资格"
            ],
            "insights": [
                "TLVR电感市场份额有望从15%提升至30%以上",
                "日韩同行因原材料供应问题，Q3将出现15%的产能缺口",
                "钽电容业务迎来重大突破，进入苹果供应链",
                "海外存储大厂海力士订单年内落地，铠侠、闪迪已完成审厂",
                "基础业务叠加AI两大增量对应估值900亿"
            ],
            "key_metrics": [
                "TLVR电感交货期32-40周",
                "市场份额从15%提升至30%+",
                "钽电容现有10亿支产能，今年再扩产3亿只",
                "苹果二供对应约8-10亿稳定收入",
                "现货价格涨15%-30%"
            ],
            "target_valuation": [
                "900亿（基础业务+TLVR电感+AI钽电容两大增量）"
            ],
            "expected_price": [],
            "expected_performance": [],
            "market_valuation": [],
            "core_business": ["电感元件研发与制造", "钽电容研发与制造"],
            "industry_position": ["全球电感行业前三", "国内民用钽电容进展最快"],
            "chain": ["中游-被动元件制造"],
            "partners": ["苹果", "英伟达(N)", "谷歌", "亚马逊"]
        }
    ]
})

# === 泰金新能 688813 (已有，追加文章) ===
stocks.append({
    "code": "688813",
    "name": "泰金新能",
    "board": "SH",
    "industry": "专用设备制造业",
    "concepts": ["铜箔设备", "光模块陶瓷封装", "科创次新股", "PET铜箔", "PCB概念"],
    "products": ["光模块陶瓷封装", "铜箔设备", "钛电极", "HVLP铜箔"],
    "core_business": ["高端电解成套装备研发制造", "金属玻璃封接制品", "钛电极"],
    "industry_position": ["国内铜箔表面处理设备唯一", "光模块陶瓷封装双寡头格局下新进入者"],
    "chain": ["中游-专用设备制造"],
    "partners": ["京瓷", "中瓷电子"],
    "mention_count": 1,
    "last_updated": today,
    "articles": [
        {
            "title": "泰金新能，翻倍空间？",
            "date": "2026-06-08",
            "source": url2,
            "accidents": [
                "光模块陶瓷封装近期已涨价15%",
                "子公司赛尔电子突破北美光模块大客户",
                "HVLP铜箔极度紧缺，持续涨价"
            ],
            "insights": [
                "光模块陶瓷封装领域为京瓷+中瓷双寡头垄断，导入新供应商迫在眉睫",
                "赛尔电子从事玻璃、陶瓷封装等30年，承担多次国家级科研项目",
                "铜箔表面处理设备全国唯一，性能对标日本三船",
                "未来赛尔有望直接对标中瓷电子，市值空间弹性大"
            ],
            "key_metrics": [
                "光模块陶瓷封装单只价值量200-300元，净利率有望达40%",
                "HVLP+载体年扩产5万吨+，单万吨7亿",
                "RTF年扩产6万吨，单万吨4亿",
                "锂电&HTE合计年扩产30万吨，单万吨3亿+"
            ],
            "target_valuation": [
                "550亿（光模块封装200亿+铜箔设备350亿），较目前翻倍空间"
            ],
            "expected_price": [],
            "expected_performance": [],
            "market_valuation": [],
            "core_business": ["高端电解成套装备研发制造", "金属玻璃封接制品", "钛电极"],
            "industry_position": ["国内铜箔表面处理设备唯一", "光模块陶瓷封装双寡头格局下新进入者"],
            "chain": ["中游-专用设备制造"],
            "partners": ["京瓷", "中瓷电子"]
        }
    ]
})

# === 中巨芯 688549 (已有但无文章，追加) ===
stocks.append({
    "code": "688549",
    "name": "中巨芯",
    "board": "SH",
    "industry": "电子-电子化学品-电子化学品Ⅲ",
    "concepts": ["六氟化钨", "存储芯片", "氟化工", "半导体材料"],
    "products": ["六氟化钨(WF6)", "电子湿化学品", "电子特种气体"],
    "core_business": ["电子湿化学品研发与生产", "电子特种气体生产"],
    "industry_position": ["国内第二大六氟化钨产能供应商"],
    "chain": ["中游-半导体材料制造"],
    "partners": ["长存", "中芯国际(SMIC)", "海力士", "铠侠"],
    "mention_count": 1,
    "last_updated": today,
    "articles": [
        {
            "title": "中巨芯，翻倍空间？",
            "date": "2026-06-08",
            "source": url3,
            "accidents": [
                "日本六氟化钨即将库存耗尽或于下月断供",
                "六氟化钨主流参考价达180万元/吨（去年仅30-40万元/吨）",
                "出口价达220万元/吨",
                "全球存储大厂进入新一轮扩产周期"
            ],
            "insights": [
                "日本或将出清2900吨WF6产能（全球产能约1万吨），供给出清有望催化价格继续上涨",
                "3D NAND层数不断叠加导致单位芯片对WF6消耗量显著提升",
                "公司拥有600吨WF6产能，当前接近满产并已确定扩产至2000吨",
                "存储大厂长存、长鑫、海力士扩产带动WF6需求激增",
                "预计今年收入40%以上增速并摘U"
            ],
            "key_metrics": [
                "WF6产能600吨，扩产至2000吨",
                "WF6价格从30-40万/吨涨至180万/吨",
                "客户：长存、SMIC、海力士",
                "半导体营收预计占8成以上"
            ],
            "target_valuation": [
                "485亿，当前位置胜率赔率俱佳"
            ],
            "expected_price": [],
            "expected_performance": ["2026年收入40%以上增速并摘U"],
            "market_valuation": [],
            "core_business": ["电子湿化学品研发与生产", "电子特种气体生产"],
            "industry_position": ["国内第二大六氟化钨产能供应商"],
            "chain": ["中游-半导体材料制造"],
            "partners": ["长存", "中芯国际(SMIC)", "海力士", "铠侠"]
        }
    ]
})

# 构建中间文件
data = {
    "date": today,
    "total_stocks": len(stocks),
    "stocks": stocks
}

# 保存到技能目录的data下
out_path = SKILL_DIR / 'data' / f'stocks_master_{today}.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'中间文件已生成: {out_path}')
print(f'共 {len(stocks)} 只股票')
for s in stocks:
    print(f'  {s["code"]} {s["name"]} | {len(s["articles"])}篇文章')

# 保存一份到项目根目录data/stocks下（作为日期分片）
project_out = PROJECT_DIR / 'data' / 'stocks' / f'{today}.json'
# 如果已有该文件，读取并合并
if project_out.exists():
    existing = json.loads(project_out.read_text(encoding='utf-8'))
    existing_stocks = existing.get('stocks', {})
    for s in stocks:
        code = s['code']
        if code in existing_stocks:
            # 合并文章
            existing_articles = existing_stocks[code].get('articles', [])
            new_titles = [(a['title'], a['source']) for a in s.get('articles', [])]
            for a in existing_articles:
                if (a['title'], a['source']) not in new_titles:
                    s['articles'].append(a)
            # 更新计数
            s['mention_count'] = len(s['articles'])
        existing_stocks[code] = s
    existing['stocks'] = existing_stocks
    existing['update_count'] = len(existing_stocks)
    existing['date'] = today
    with open(project_out, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f'项目分片已更新(合并): {project_out}')
else:
    project_data = {
        "date": today,
        "update_count": len(stocks),
        "stocks": {s['code']: s for s in stocks}
    }
    project_out.parent.mkdir(parents=True, exist_ok=True)
    with open(project_out, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, ensure_ascii=False, indent=2)
    print(f'项目分片已创建: {project_out}')