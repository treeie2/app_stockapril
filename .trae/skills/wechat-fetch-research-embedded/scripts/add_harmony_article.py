#!/usr/bin/env python3
"""生成鸿蒙7.0文章的中间JSON文件"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
SKILL_DIR = ROOT.parent
PROJECT_DIR = SKILL_DIR.parents[2]

today = '2026-06-08'
url = 'https://mp.weixin.qq.com/s/BbKZCNaXFLfxi9966KxFRA'

stocks = []

# === 润和软件 300339 ===
stocks.append({
    "code": "300339", "name": "润和软件", "board": "SZ",
    "industry": "计算机-IT服务-IT服务Ⅲ",
    "concepts": ["鸿蒙", "开源鸿蒙", "OpenHarmony", "信创"],
    "products": ["HiHope行业发行版"],
    "core_business": ["开源鸿蒙行业发行版研发", "行业定制化系统开发"],
    "industry_position": ["开源鸿蒙创始单位之一"],
    "chain": ["中游-操作系统发行版"],
    "partners": ["华为"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["华为HDC 2026发布鸿蒙7.0纯血鸿蒙，6月12日东莞松山湖召开"],
        "insights": [
            "润和软件是开源鸿蒙创始单位之一，基于OpenHarmony做行业发行版HiHope",
            "鸿蒙7.0彻底告别安卓兼容，全栈代码自研率100%，基于1.1亿行自研代码",
            "政务、教育领域已落地，未来政企市场鸿蒙推广直接受益"
        ],
        "key_metrics": ["鸿蒙7.0内存占用降低30%", "应用安装速度快27%", "内容加载速度快31%"],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["开源鸿蒙行业发行版研发", "行业定制化系统开发"],
        "industry_position": ["开源鸿蒙创始单位之一"],
        "chain": ["中游-操作系统发行版"], "partners": ["华为"]
    }]
})

# === 诚迈科技 300598 ===
stocks.append({
    "code": "300598", "name": "诚迈科技", "board": "SZ",
    "industry": "计算机-软件开发-垂直应用软件",
    "concepts": ["鸿蒙", "开源鸿蒙", "信创", "国产替代"],
    "products": ["望龙电脑"],
    "core_business": ["鸿蒙行业ISV", "鸿蒙PC生态"],
    "industry_position": ["鸿蒙PC生态先行者"],
    "chain": ["中游-操作系统生态"], "partners": ["华为"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["诚迈科技推出望龙电脑，鸿蒙PC生态重要一环"],
        "insights": [
            "诚迈科技是华为鸿蒙核心ISV，推出了鸿蒙PC '望龙电脑'",
            "鸿蒙7.0一套系统适配万物，PC是至关重要的一环",
            "如果鸿蒙PC在政企市场打开局面，诚迈科技将直接受益"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["鸿蒙行业ISV", "鸿蒙PC生态"],
        "industry_position": ["鸿蒙PC生态先行者"],
        "chain": ["中游-操作系统生态"], "partners": ["华为"]
    }]
})

# === 软通动力 301236 ===
stocks.append({
    "code": "301236", "name": "软通动力", "board": "SZ",
    "industry": "计算机-IT服务-IT服务Ⅲ",
    "concepts": ["鸿蒙", "开源鸿蒙", "昇腾", "鲲鹏", "信创"],
    "products": ["开源鸿蒙AIPC"],
    "core_business": ["鸿蒙生态ISV", "PC制造", "昇腾/鲲鹏合作伙伴"],
    "industry_position": ["鸿蒙生态全能选手，软硬件兼备"],
    "chain": ["中游-操作系统生态"], "partners": ["华为", "同方计算机"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["软通动力收购同方计算机，补齐PC硬件能力"],
        "insights": [
            "软通动力是鸿蒙核心ISV，收购同方计算机后推出开源鸿蒙AIPC",
            "同时是华为昇腾、鲲鹏服务器及鸿蒙PC核心合作伙伴",
            "鸿蒙7.0推广离不开这种软硬一体的合作伙伴"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["鸿蒙生态ISV", "PC制造", "昇腾/鲲鹏合作伙伴"],
        "industry_position": ["鸿蒙生态全能选手，软硬件兼备"],
        "chain": ["中游-操作系统生态"], "partners": ["华为", "同方计算机"]
    }]
})

# === 智微智能 001339 ===
stocks.append({
    "code": "001339", "name": "智微智能", "board": "SZ",
    "industry": "计算机-计算机设备-其他计算机设备",
    "concepts": ["昇腾", "鸿蒙", "AIPC", "算力"],
    "products": ["昇腾算力产品", "AIPC代工"],
    "core_business": ["昇腾算力硬件研发", "AIPC代工制造"],
    "industry_position": ["华为昇腾金牌供应商"],
    "chain": ["中游-算力硬件制造"], "partners": ["华为"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["智微智能多款产品完成开源鸿蒙适配认证", "AIPC代工实现0到1突破"],
        "insights": [
            "智微智能是华为昇腾金牌供应商，为鸿蒙设备提供算力底座",
            "AIPC代工业务受益于鸿蒙PC推广",
            "鸿蒙7.0端侧运行大模型需要强大算力支持"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["昇腾算力硬件研发", "AIPC代工制造"],
        "industry_position": ["华为昇腾金牌供应商"],
        "chain": ["中游-算力硬件制造"], "partners": ["华为"]
    }]
})

# === 法本信息 300925 ===
stocks.append({
    "code": "300925", "name": "法本信息", "board": "SZ",
    "industry": "计算机-软件开发-垂直应用软件",
    "concepts": ["鸿蒙", "信创"],
    "products": ["鸿蒙应用开发服务"],
    "core_business": ["鸿蒙应用开发与适配"],
    "industry_position": [],
    "chain": ["中游-应用开发服务"], "partners": ["华为"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["鸿蒙7.0彻底告别安卓兼容，所有App需重新开发鸿蒙原生版本"],
        "insights": [
            "法本信息承接大量鸿蒙应用开发和适配项目",
            "鸿蒙7.0彻底告别安卓兼容，所有App必须重新开发鸿蒙原生版本",
            "鸿蒙用户越多，App迁移需求越大，法本信息业务越忙"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["鸿蒙应用开发与适配"],
        "industry_position": [],
        "chain": ["中游-应用开发服务"], "partners": ["华为"]
    }]
})

# === 瑞芯微 603893 ===
stocks.append({
    "code": "603893", "name": "瑞芯微", "board": "SH",
    "industry": "电子-半导体-数字芯片设计",
    "concepts": ["端侧AI", "SoC", "NPU", "AI芯片", "半导体"],
    "products": ["端侧SoC芯片", "NPU"],
    "core_business": ["端侧SoC芯片研发设计", "NPU研发"],
    "industry_position": ["A股物联网SoC芯片第一大上市公司", "端侧算力龙头"],
    "chain": ["上游-芯片设计"], "partners": ["华为"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["鸿蒙7.0将百亿参数大模型端侧本地部署"],
        "insights": [
            "瑞芯微是端侧算力龙头公司，A股物联网SoC芯片第一大",
            "正在推进NPU研发，旗舰芯片定位国产第一梯队",
            "鸿蒙7.0端侧部署大模型需要强大的端侧芯片扛算力"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["端侧SoC芯片研发设计", "NPU研发"],
        "industry_position": ["A股物联网SoC芯片第一大上市公司", "端侧算力龙头"],
        "chain": ["上游-芯片设计"], "partners": ["华为"]
    }]
})

# === 广和通 300638 ===
stocks.append({
    "code": "300638", "name": "广和通", "board": "SZ",
    "industry": "通信-通信设备-通信终端及配件",
    "concepts": ["端侧AI", "AI模组", "AI玩具", "物联网"],
    "products": ["端侧AI模组"],
    "core_business": ["端侧AI模组研发制造"],
    "industry_position": ["华为AI玩具独家高性能AI模组供应商"],
    "chain": ["中游-通信模组制造"], "partners": ["华为", "字节跳动", "腾讯"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["鸿蒙7.0端侧AI能力需要AI模组落地"],
        "insights": [
            "广和通是华为AI玩具独家高性能AI模组供应商",
            "AI模组可将芯片、内存、通信模块集成，嵌入AI玩具等设备",
            "鸿蒙7.0端侧AI能力需要模组落地，广和通是卖铲人"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["端侧AI模组研发制造"],
        "industry_position": ["华为AI玩具独家高性能AI模组供应商"],
        "chain": ["中游-通信模组制造"], "partners": ["华为", "字节跳动", "腾讯"]
    }]
})

# === 恒玄科技 688608 ===
stocks.append({
    "code": "688608", "name": "恒玄科技", "board": "SH",
    "industry": "电子-半导体-数字芯片设计",
    "concepts": ["AIoT", "SoC", "端侧AI", "智能穿戴", "AI音频"],
    "products": ["AIoT SoC芯片", "AI音频芯片"],
    "core_business": ["低功耗AIoT芯片研发设计", "AI音频芯片研发设计"],
    "industry_position": ["AIoT SoC龙头", "端侧AI音频芯片核心供应商"],
    "chain": ["上游-芯片设计"], "partners": ["华为"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["鸿蒙7.0伴随式小艺支持离线语音识别98%准确率"],
        "insights": [
            "恒玄科技是AIoT SoC龙头，专注低功耗AIoT芯片",
            "产品广泛应用于AI耳机、智能眼镜、智能手表等穿戴设备",
            "鸿蒙7.0离线语音识别功能需要低功耗高性能音频芯片支持"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["低功耗AIoT芯片研发设计", "AI音频芯片研发设计"],
        "industry_position": ["AIoT SoC龙头", "端侧AI音频芯片核心供应商"],
        "chain": ["上游-芯片设计"], "partners": ["华为"]
    }]
})

# === 乐鑫科技 688018 ===
stocks.append({
    "code": "688018", "name": "乐鑫科技", "board": "SH",
    "industry": "电子-半导体-数字芯片设计",
    "concepts": ["WiFi SoC", "端侧AI", "AIoT", "物联网"],
    "products": ["WiFi MCU芯片", "无线SoC方案"],
    "core_business": ["WiFi MCU芯片研发设计", "无线SoC方案"],
    "industry_position": ["WiFi MCU芯片全球市占率第一(35%)"],
    "chain": ["上游-芯片设计"], "partners": ["华为", "字节跳动"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["鸿蒙设备互联互通带动WiFi芯片需求"],
        "insights": [
            "乐鑫科技WiFi MCU芯片全球市占率第一（35%）",
            "鸿蒙设备互联互通需要WiFi作为核心通信方式",
            "与华为、字节跳动有深度合作"
        ],
        "key_metrics": ["WiFi MCU全球市占率35%"],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["WiFi MCU芯片研发设计", "无线SoC方案"],
        "industry_position": ["WiFi MCU芯片全球市占率第一(35%)"],
        "chain": ["上游-芯片设计"], "partners": ["华为", "字节跳动"]
    }]
})

# === 晶晨股份 688099 ===
stocks.append({
    "code": "688099", "name": "晶晨股份", "board": "SH",
    "industry": "电子-半导体-数字芯片设计",
    "concepts": ["多媒体SoC", "端侧AI", "智能家居", "机器人"],
    "products": ["多媒体SoC芯片"],
    "core_business": ["多媒体SoC芯片研发设计"],
    "industry_position": ["多媒体SoC龙头"],
    "chain": ["上游-芯片设计"], "partners": ["谷歌"],
    "mention_count": 1, "last_updated": today,
    "articles": [{
        "title": "鸿蒙7.0来了：1.1亿行自研代码、百亿大模型塞进手机（附股）",
        "date": today, "source": url,
        "accidents": ["鸿蒙7.0端侧AI推广带动多媒体SoC新需求"],
        "insights": [
            "晶晨股份是多媒体SoC龙头，在智能家居、机顶盒领域有深厚积累",
            "正发力AI硬件如智能家居机器人",
            "鸿蒙7.0推广后可能切入鸿蒙生态，打开新增长空间"
        ],
        "key_metrics": [],
        "target_valuation": [],
        "expected_price": [], "expected_performance": [], "market_valuation": [],
        "core_business": ["多媒体SoC芯片研发设计"],
        "industry_position": ["多媒体SoC龙头"],
        "chain": ["上游-芯片设计"], "partners": ["谷歌"]
    }]
})

# 构建中间文件
data = {"date": today, "total_stocks": len(stocks), "stocks": stocks}

out_path = SKILL_DIR / 'data' / f'stocks_master_{today}_harmony.json'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'中间文件已生成: {out_path}')
print(f'共 {len(stocks)} 只股票')
for s in stocks:
    print(f'  {s["code"]} {s["name"]}')