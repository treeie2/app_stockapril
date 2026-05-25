#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 9 篇文章涉及的个股估值信息到 master_stock.json
"""
import json
from pathlib import Path
from datetime import datetime

# 读取 master_stock.json
master_file = Path(__file__).parent / 'data' / 'stocks' / 'stocks_master.json'
with open(master_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 创建股票代码索引（stocks 是对象，不是数组）
stock_map = data['stocks']

# 9 篇文章的个股信息
articles = [
    {
        'code': '001233',
        'name': '海安集团',
        'article_url': 'https://mp.weixin.qq.com/s/Q9OB6VbBXCurZajgPuWWyg',
        'article_title': '海安集团，2 倍空间？',
        'article_date': '2026-05-05',
        'source': '天风汽车',
        'valuation': {
            'target_market_cap': '180-360 亿',
            'target_market_cap_billion': 36.0,  # 360 亿
            'pe_ratio': '15-20x',
            'summary': '巨型工程机械轮胎龙头，26/27 年利润 7.1e/8.8e，基于 27 年 20x 对应 180e 目标市值，中期 20% 市占率对应 360e 市值'
        },
        'insights': [
            '一季度不及预期是短期影响，4 月已解决，Q2 是第一个业绩释放期',
            '格局：CR3=80%，海安市占率 7%，净利率 25%+',
            '26 年订单超 20e，仍有 10e 在谈',
            '全年产能增幅 20-30%，新产线 5 月到位'
        ],
        'key_metrics': [
            '26/27 年利润：7.1e/8.8e',
            'PE：16x/13x',
            '目标市值：180e (60% 空间) - 360e (2 倍空间)'
        ]
    },
    {
        'code': '688521',
        'name': '芯原股份',
        'article_url': 'https://mp.weixin.qq.com/s/ewG2cMTpMimebJr4dE3kFw',
        'article_title': '芯原股份，翻倍空间？',
        'article_date': '2026-05-05',
        'source': '未知',
        'valuation': {
            'target_market_cap': '3000 亿+',
            'target_market_cap_billion': 300.0,
            'summary': '国产算力芯片龙头，9 天新签 37e 订单，全年订单环比高增，短期看翻倍以上空间'
        },
        'insights': [
            '海外四大 CSP capex 上行带来硬件投资机遇',
            '9 天新签 37e 订单超预期，证明能力和客户需求',
            '国产算力需求旺盛，26 年 ASIC 占 AI 服务器芯片 40%',
            '两大头部客户 Q1/Q2 转量产'
        ],
        'key_metrics': [
            '9 天新签订单：37e',
            '目标市值：3000 亿+',
            '空间：翻倍以上'
        ]
    },
    {
        'code': '000066',
        'name': '中国长城',
        'article_url': 'https://mp.weixin.qq.com/s/hEu1t-SMbV1o-wWArekESg',
        'article_title': '中国长城，翻倍空间？',
        'article_date': '2026-05-05',
        'source': '国海计算机',
        'valuation': {
            'target_market_cap': '1000 亿',
            'target_market_cap_billion': 100.0,
            'summary': 'CPU+ 高端电源+AI 服务器，电源业务 600 亿 + 飞腾股权 560 亿 + 军工电子 340 亿'
        },
        'insights': [
            '2025 年营收 158 亿 (+11.31%)，亏损收窄至 -0.56 亿',
            '子公司飞腾信息是国内 Top 级 CPU 厂商，持股 28.035%',
            '长城电源是国内服务器电源龙头，市占率国内第一',
            'AI 服务器/通用服务器品类齐全'
        ],
        'key_metrics': [
            '2025 年营收：158.09 亿 (+11.31%)',
            '2025 年净利润：-0.56 亿 (减亏 96.23%)',
            '飞腾 CPU 累计应用：1300 万片+',
            '目标市值：1000 亿 (翻倍空间)'
        ]
    },
    {
        'code': '688020',
        'name': '方邦股份',
        'article_url': 'https://mp.weixin.qq.com/s/NsRw20cz8ot5JBHytmUJvQ',
        'article_title': '方邦股份，2 倍空间？',
        'article_date': '2026-04-27',
        'source': '天风电新',
        'valuation': {
            'target_market_cap': '200-300 亿',
            'target_market_cap_billion': 30.0,
            'summary': '载体铜箔国产替代，27 年 600 万平产能对应 3 亿利润，50x 给 150 亿，加主业 200 亿+'
        },
        'insights': [
            '载体铜箔：2-3 年后百亿市场，已开始涨价',
            '三井占 95% 份额，3 月底涨价 12%',
            '方邦产能 40 万平/月，可快速增至 60 万平',
            '已通过 H、CX 小批量供应，预计 26Q3 大批量'
        ],
        'key_metrics': [
            '当前产能：40 万平/月',
            '可扩展产能：60 万平/月',
            '27 年利润：3 亿 (600 万平*50 元/平)',
            '目标市值：200-300 亿 (2 倍 + 空间)'
        ]
    },
    {
        'code': '688665',
        'name': '联讯仪器',
        'article_url': 'https://mp.weixin.qq.com/s/hBQ41Wi3xUANml8H2Ql-eQ',
        'article_title': '联讯仪器，翻倍空间？',
        'article_date': '2026-04-27',
        'source': '国金机械',
        'valuation': {
            'target_market_cap': '2000 亿',
            'target_market_cap_billion': 200.0,
            'summary': '光模块测试设备龙头，26-28 年收入 25e/56e/120e，千亿是开始'
        },
        'insights': [
            '光模块设备行业 2 年 10 倍增长',
            '测试环节增速超过行业，价值量从 20% 提升到 35%',
            '联讯增速超过测试环节，因国产化率提升',
            '产业链延伸上游，订单持续超预期'
        ],
        'key_metrics': [
            '26-28 年收入：25e/56e/120e',
            '光模块测试设备空间：84e/149e/245e',
            '目标市值：2000 亿 (5 倍空间)'
        ]
    },
    {
        'code': '300322',
        'name': '硕贝德',
        'article_url': 'https://mp.weixin.qq.com/s/k_AdMAWYkC63PF5K9A2MYA',
        'article_title': '硕贝德，170% 空间？',
        'article_date': '2026-04-27',
        'source': '未知',
        'valuation': {
            'target_market_cap': '400 亿',
            'target_market_cap_billion': 40.0,
            'summary': '液冷预期差标的，busbar+ 光模块液冷 27 年利润 11 亿，30x PE 给 330 亿'
        },
        'insights': [
            'busbar 液冷：泰科订单导入顺利，安费诺审厂通过',
            '26-27 年 NV 市场空间 100 亿，硕贝德份额 60%',
            '光模块液冷：泰科审厂完毕，等终端客户审厂',
            '天线：卫通天线量产出货'
        ],
        'key_metrics': [
            '26-27 年 busbar 液冷利润：6 亿',
            '27 年光模块液冷利润：5.4 亿',
            'AI 液冷总利润：11 亿',
            '目标市值：400 亿 (170% 空间)'
        ]
    },
    {
        'code': '688138',
        'name': '凌玮科技',
        'article_url': 'https://mp.weixin.qq.com/s/JXmzfn_g6l91Ha9G1z5Q_g',
        'article_title': '凌玮科技，4 倍空间？',
        'article_date': '2026-04-26',
        'source': '东北计算机',
        'valuation': {
            'target_market_cap': '492 亿',
            'target_market_cap_billion': 49.2,
            'summary': '添加剂 + 树脂刚起步，3000t*60w*70%+4e 利润，30x PE 给 492 亿'
        },
        'insights': [
            '添加剂 + 树脂刚刚开始，H2 有望量价齐升',
            '主业 1.7e 利润，化学法硅微粉 3000t 对应 3.8e 利润',
            'M8+9 市场 1.5wt 需求，缺口 40%',
            '价格从 20w/t 向 100w/t 区间通胀'
        ],
        'key_metrics': [
            '主业利润：1.7e',
            '硅微粉利润：3.8e (3000t*20w/t)',
            '目标市值：492 亿 (4 倍空间)'
        ]
    },
    {
        'code': '002203',
        'name': '海亮股份',
        'article_url': 'https://mp.weixin.qq.com/s/IawQF2Vefka-lCB6xsrmLA',
        'article_title': '海亮股份，160% 空间？',
        'article_date': '2026-04-26',
        'source': '天风电新',
        'valuation': {
            'target_market_cap': '560-1100 亿',
            'target_market_cap_billion': 110.0,
            'summary': '北美基地 26/27 年利润 14e/30e，数据中心贡献 2e/9e，对应 560e/1100e 市值'
        },
        'insights': [
            '北美工业回流 + 数据中心产业链稀缺标的',
            '铜管：订单排到 8 月，年底 1w 吨/月产能',
            '铜排：核心客户伊顿、施耐德需求超产能',
            '26/27 年总利润 22e/40e'
        ],
        'key_metrics': [
            '26/27 年北美基地利润：14e/30e',
            '26/27 年数据中心利润：2e/9e',
            '26/27 年总利润：22e/40e',
            '目标市值：560e/1100e (160% 空间)'
        ]
    },
    {
        'code': '301613',
        'name': '智微智能',
        'article_url': 'https://mp.weixin.qq.com/s/dQDjLHpKUsJOPVRIOf0YOg',
        'article_title': '智微智能，翻倍空间？',
        'article_date': '2026-04-26',
        'source': '未知',
        'valuation': {
            'target_market_cap': '400 亿',
            'target_market_cap_billion': 40.0,
            'summary': '国产算力隐形冠军，26 年业绩 6e，27 年 12e+，27 年 400 亿市值'
        },
        'insights': [
            '26Q1 净利润 1.1 亿 (+159%)，大超预期',
            '华为昇腾生态金牌供应商，参与 Atlas 900 超节点项目',
            '算力租赁子公司腾云智算净利润 2 亿/季度',
            '合同负债从 5000 万暴增至 8.6 亿'
        ],
        'key_metrics': [
            '26Q1 净利润：1.1 亿 (+159%)',
            '26 年业绩考核：6 亿 (+250%)',
            '27 年利润：12e+',
            '目标市值：400 亿 (翻倍空间)'
        ]
    }
]

# 更新或添加股票信息
today = datetime.now().strftime('%Y-%m-%d')
updated_count = 0
added_count = 0

for article in articles:
    code = article['code']
    
    if code in stock_map:
        # 更新现有股票
        stock = stock_map[code]
        print(f"更新股票：{code} - {article['name']}")
        
        # 更新估值信息
        if 'valuation' not in stock:
            stock['valuation'] = {}
        
        # 合并估值信息（保留已有字段，添加新字段）
        for key, value in article['valuation'].items():
            stock['valuation'][key] = value
        
        # 更新 insights
        if article['insights']:
            if 'insights' not in stock or not stock['insights']:
                stock['insights'] = '\n'.join(article['insights'])
            else:
                # 追加到现有 insights
                stock['insights'] += '\n\n' + '\n'.join(article['insights'])
        
        # 更新 key_metrics
        if article['key_metrics']:
            if 'key_metrics' not in stock or not stock['key_metrics']:
                stock['key_metrics'] = article['key_metrics']
            else:
                # 合并并去重
                existing = set(stock['key_metrics'])
                for metric in article['key_metrics']:
                    if metric not in existing:
                        stock['key_metrics'].append(metric)
        
        # 添加文章引用
        article_ref = f"[{article['article_date']}] {article['source']}: {article['article_title']} ({article['article_url']})"
        if 'articles' not in stock:
            stock['articles'] = []
        
        # 创建文章对象
        article_obj = {
            'date': article['article_date'],
            'title': article['article_title'],
            'source': article['article_url'],
            'accidents': [],
            'insights': article['insights'],
            'key_metrics': article['key_metrics'],
            'valuation': article['valuation']
        }
        
        stock['articles'].insert(0, article_obj)
        stock['articles'] = stock['articles'][:10]  # 保留最新 10 条
        
        # 更新 last_updated
        stock['last_updated'] = today
        
        updated_count += 1
    else:
        # 添加新股票
        print(f"添加新股票：{code} - {article['name']}")
        
        new_stock = {
            'code': code,
            'name': article['name'],
            'board': 'SZ' if code.startswith(('00', '30')) else 'SH',
            'industry': '',
            'mention_count': 1,
            'last_updated': today,
            'concepts': [],
            'core_business': [],
            'industry_position': [],
            'accident': '',
            'insights': '\n'.join(article['insights']) if article['insights'] else '',
            'chain': [],
            'key_metrics': article['key_metrics'],
            'partners': [],
            'products': [],
            'articles': [{
                'date': article['article_date'],
                'title': article['article_title'],
                'source': article['article_url'],
                'accidents': [],
                'insights': article['insights'],
                'key_metrics': article['key_metrics'],
                'valuation': article['valuation']
            }],
            'valuation': article['valuation']
        }
        
        stock_map[code] = new_stock
        added_count += 1

# 保存更新后的数据到单独的文件（不合并到 master_stock）
today = datetime.now().strftime('%Y-%m-%d')
output_file = Path(__file__).parent / 'data' / f'stocks_master_{today}.json'

# 创建新的数据结构
output_data = {
    'stocks': {},
    'update_info': {
        'date': today,
        'source': '9 篇微信公众号文章',
        'article_count': len(articles),
        'updated_stocks': updated_count,
        'new_stocks': added_count
    }
}

# 将所有 9 只股票添加到输出数据
for article in articles:
    code = article['code']
    stock = stock_map[code]
    output_data['stocks'][code] = stock

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n{'='*80}")
print(f"更新完成！")
print(f"{'='*80}")
print(f"更新股票：{updated_count} 只")
print(f"添加新股票：{added_count} 只")
print(f"总股票数：{len(data['stocks'])} 只")
print(f"输出文件：{output_file}")
print(f"\n下一步：")
print(f"1. 检查输出文件是否正确")
print(f"2. 备份原文件：cp stocks_master.json stocks_master.json.bak")
print(f"3. 替换原文件：mv stocks_master_updated.json stocks_master.json")
print(f"4. 同步到 Firebase")
