#!/usr/bin/env python3
"""
手动添加股票信息到 stocks_master.json
"""
import json
from pathlib import Path
from datetime import datetime

MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")
TODAY = datetime.now().strftime('%Y-%m-%d')

# 手动添加的股票信息
MANUAL_STOCKS = [
    {
        'code': '300416',
        'name': '苏试试验',
        'source': 'manual_input',
        'title': '国机精工持续推荐：航天轴承 + 金刚石技术领军公司',
        'content': '''
国机精工持续推荐：航天轴承 + 金刚石技术领军公司早盘上涨 6%，近 2 周上涨 25%。我们近期新发航天轴承专题报告，强调航天轴承行业壁垒高、格局优，公司作为龙头将极大受益。金刚石散热近期产业进展加快，联想、曙光等均开展了金刚石散热产品的部署。公司是国内金刚石领域第一梯队，金刚石散热片已和算力、光模块等领域的多家龙头公司对接送样，建议重点关注！

#β1：商业航天【轴研所核心卡位】
公司旗下轴研所在我国航天领域市占率 90% 以上，配套长征系列国家队 + 商业航天企业。公司特种轴承在火箭发动机涡轮泵、卫星飞轮及太阳能帆板组件中均为核心产品，预计单箭/单星价值量为 200 万元/50 万元，预计到 28 年我国实现 200 发火箭/5000 颗卫星入轨，则对应 29 亿收入/10 亿利润。

#β2：金刚石散热【三磨所技术领先】
公司旗下三磨所是我国磨料磨具行业唯一的综合性研究开发机构。金刚石散热片：公司与 H 客户深入合作，光模块散热产品快速推进，批量后弹性空间大。

#β3：半导体设备【国产替代加速】
减薄砂轮、划片刀、陶瓷吸盘等目前国产化率仅为 5%，公司已实现对日企 DISCO 的国产替代。未来三年公司利润有望快速突破 20 亿元以上，30 倍 PE 对应 600 亿市值、翻倍以上空间。
'''
    },
    {
        'code': '603005',
        'name': '晶方科技',
        'source': 'manual_input',
        'title': 'TGV（玻璃通孔）技术全解析 + 核心企业梳理',
        'content': '''
TGV（玻璃通孔）技术是先进封装领域的核心技术，用于玻璃基板上的垂直互连。公司在 TGV 领域有深入布局，是玻璃基板封装技术的领军企业。
'''
    },
    {
        'code': '603019',
        'name': '中科曙光',
        'source': 'manual_input',
        'title': '金刚石散热产品部署',
        'content': '''
金刚石散热近期产业进展加快，中科曙光开展了金刚石散热产品的部署。
'''
    },
    {
        'code': '300604',
        'name': '长川科技',
        'source': 'manual_input',
        'title': '半导体测试设备',
        'content': '''
半导体测试设备领域的重要企业。
'''
    },
    {
        'code': '688012',
        'name': '中微公司',
        'source': 'manual_input',
        'title': '半导体设备国产替代',
        'content': '''
半导体设备国产替代加速，公司在刻蚀设备领域处于国内领先地位。
'''
    },
    {
        'code': '000977',
        'name': '浪潮信息',
        'source': 'manual_input',
        'title': 'AI 服务器龙头',
        'content': '''
2026 年预计 50 亿元以上利润，预计 Q1 已经开始展现部分利润率弹性，海外超节点的弹性更大。
'''
    },
    {
        'code': '603118',
        'name': '共进股份',
        'source': 'manual_input',
        'title': '乐鑫科技子公司明栈科技',
        'content': '''
Anthropic 给出了官方参考硬件，M5StickC Plus/ M5StickS3，这是深圳公司明栈科技的产品，该公司是乐鑫科技的子公司，24 年二季度乐鑫科技完成对明栈科技 57% 的股权收购，并且该产品的芯片也采用乐鑫科技的 ESP32-S3。Anthropic 官方推荐乐鑫科技的配件值得关注。我们也发现，市面上已经有第三方公司基于明栈科技的 M5 封装成 Anthropic 的电子宠物开始众筹售卖，定价高达 99 美金，且众筹需求很高。持续关注，后续 Anthropic 的海量用户有望带来硬件伴侣的需求。
'''
    },
    {
        'code': '603118',
        'name': '共进股份',
        'source': 'manual_input',
        'title': '华勤技术 AI 服务器',
        'content': '''
华勤技术 2026 年预计 50 亿元以上利润，其中 AI 服务器预计或达 500 亿收入（市占率提升，50% 以增长），超节点将在下半年进入规模量产交付；交换机产品收入在 2026 年实现翻倍增长。
'''
    }
]

def add_manual_stocks():
    """添加手动输入的股票信息"""
    # 读取现有数据
    if MASTER_FILE.exists():
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
    else:
        master_data = {'stocks': {}}
    
    stocks = master_data.get('stocks', {})
    added_count = 0
    
    for stock_info in MANUAL_STOCKS:
        code = stock_info['code']
        name = stock_info['name']
        
        # 创建或更新股票记录
        if code not in stocks:
            stocks[code] = {
                'name': name,
                'articles': [],
                'mention_count': 0
            }
        
        # 确保 articles 字段存在
        if 'articles' not in stocks[code]:
            stocks[code]['articles'] = []
        
        # 创建文章记录
        article_record = {
            'source': stock_info['source'],
            'title': stock_info['title'],
            'date': TODAY,
            'fetched_at': datetime.now().isoformat()
        }
        
        # 提取关键信息
        content = stock_info['content']
        
        # 提取核心业务
        if '航天轴承' in content or '金刚石' in content:
            article_record['core_business'] = ['航天轴承', '金刚石散热片', '半导体设备']
            article_record['industry_position'] = ['国内金刚石领域第一梯队', '航天领域市占率 90% 以上']
        
        if 'TGV' in content or '玻璃通孔' in content:
            article_record['core_business'] = ['TGV 玻璃通孔', '先进封装']
            article_record['industry_position'] = ['玻璃基板封装技术领军企业']
        
        if 'AI 服务器' in content:
            article_record['core_business'] = ['AI 服务器', '交换机']
            article_record['target_valuation'] = ['2026 年预计 50 亿元以上利润']
        
        if '半导体设备' in content or '半导体测试' in content:
            article_record['core_business'] = ['半导体测试设备', '刻蚀设备']
            article_record['industry_position'] = ['国产替代领先企业']
        
        # 检查文章是否已存在
        existing = False
        for existing_article in stocks[code]['articles']:
            if existing_article.get('source') == stock_info['source'] and \
               existing_article.get('title') == stock_info['title']:
                existing = True
                break
        
        if not existing:
            stocks[code]['articles'].append(article_record)
            stocks[code]['mention_count'] = stocks[code].get('mention_count', 0) + 1
            added_count += 1
            print(f"✅ 添加：{name} ({code}) - {article_record['title'][:30]}...")
        else:
            print(f"⏭️  跳过：{name} ({code}) - 文章已存在")
    
    # 保存回文件
    master_data['stocks'] = stocks
    
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！添加了 {added_count} 条记录")
    return added_count

if __name__ == '__main__':
    print("🚀 开始添加手动输入的股票信息...\n")
    add_manual_stocks()
    print("\n🎉 处理完成！")
