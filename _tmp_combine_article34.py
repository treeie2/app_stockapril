import json

today = "2026-06-01"

# ========== COMBINED: Article 3 (6) + Article 4 (12) ==========
source3 = "https://mp.weixin.qq.com/s/XD8d1ouX8r234wujXj9j2w"
source4 = "https://mp.weixin.qq.com/s/CTX26oFNML7WDwCHQ86WIQ"

stocks = [
    # === Article 3: 6 stocks ===
    {
        "name": "凌玮科技", "code": "301373", "board": "SZ",
        "industry": "基础化工-化学新材料-电子材料",
        "concepts": ["纳米硅微粉", "电子材料", "IC载板", "先进封装"],
        "products": ["纳米球形硅微粉", "电子电路基板材料"],
        "core_business": ["纳米球形硅微粉研发与生产", "高端电子材料"],
        "industry_position": ["国内稀缺的化学合成法球形硅微粉产业化企业"],
        "chain": ["上游-电子材料"],
        "partners": ["江苏辉迈"],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "【机构调研】笔记整理", "date": today, "source": source3,
            "core_business": ["纳米球形硅微粉研发与生产", "高端电子材料"],
            "industry_position": ["国内稀缺的化学合成法球形硅微粉产业化企业"],
            "chain": ["上游-电子材料"],
            "partners": ["江苏辉迈"],
            "accidents": ["收购江苏辉迈切入高端电子材料领域"],
            "insights": ["现金收购江苏辉迈切入纳米球形硅微粉，抢占IC载板、先进封装等前沿市场"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "信德新材", "code": "301349", "board": "SZ",
        "industry": "基础化工-化学新材料-碳纤维",
        "concepts": ["碳纤维", "沥青基碳纤维", "光伏", "半导体", "光纤"],
        "products": ["沥青基碳纤维制品"],
        "core_business": ["沥青基碳纤维制品研发与生产"],
        "industry_position": ["沥青基碳纤维制品行业领先企业"],
        "chain": ["中游-新材料制造"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "【机构调研】笔记整理", "date": today, "source": source3,
            "core_business": ["沥青基碳纤维制品研发与生产"],
            "industry_position": ["沥青基碳纤维制品行业领先企业"],
            "chain": ["中游-新材料制造"],
            "partners": [],
            "accidents": ["碳纤维制品进入光伏、光纤、半导体、热处理领域并陆续通过验证"],
            "insights": ["碳纤维制品已进入光伏、光纤、半导体、热处理领域并陆续验证通过，光纤领域已小批量供货"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "中仑新材", "code": "301565", "board": "SZ",
        "industry": "基础化工-塑料-膜材料",
        "concepts": ["BOPP", "新能源膜材", "BOPA", "薄膜电容器", "固态电池"],
        "products": ["BOPP新能源膜材", "BOPA膜材", "高性能膜材料"],
        "core_business": ["高性能膜材料研发与生产", "BOPP/BOPA新能源膜材"],
        "industry_position": ["薄膜电容器用BOPP基膜核心供应商"],
        "chain": ["中游-薄膜材料制造"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "【机构调研】笔记整理", "date": today, "source": source3,
            "core_business": ["高性能膜材料研发与生产", "BOPP/BOPA新能源膜材"],
            "industry_position": ["薄膜电容器用BOPP基膜核心供应商"],
            "chain": ["中游-薄膜材料制造"],
            "partners": [],
            "accidents": ["BOPP新能源膜材首条产线已投产，印尼项目一期投产"],
            "insights": [
                "BOPP新能源膜材适用于软包锂电池和固态电池铝塑膜",
                "BOPP新能源膜材作为薄膜电容器的关键基膜材料，成本占比约40%-50%",
                "AI数据中心需求带动高性能薄膜电容器配套需求",
                "首条BOPP新能源膜材产线已于25年11月投产，第二条预计今年下半年投产",
                "印尼长塑项目一期首条产线已于26年1月投产"
            ],
            "key_metrics": [
                "BOPP项目整体规划九条产线，总投资预算25亿元",
                "首条BOPP新能源膜材产线单线年产能约2400吨",
                "印尼项目规划四线共九万吨年产能"
            ],
            "target_valuation": []
        }]
    },
    {
        "name": "奕瑞科技", "code": "688301", "board": "SH",
        "industry": "机械设备-专用设备-检测设备",
        "concepts": ["PCB背钻CT检测", "晶圆厂", "VR/AR", "先进封装", "光子计数CT", "液冷"],
        "products": ["PCB背钻CT检测设备", "光子计数CT"],
        "core_business": ["CT检测设备研发与生产", "高端影像设备"],
        "industry_position": ["PCB背钻CT检测设备领域领先企业"],
        "chain": ["中游-专用设备制造"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "【机构调研】笔记整理", "date": today, "source": source3,
            "core_business": ["CT检测设备研发与生产", "高端影像设备"],
            "industry_position": ["PCB背钻CT检测设备领域领先企业"],
            "chain": ["中游-专用设备制造"],
            "partners": [],
            "accidents": ["PCB背钻CT检测设备今年Q3起批量出货"],
            "insights": [
                "PCB背钻CT检测设备单台价值量200万元级别，兼具耗材逻辑",
                "晶圆厂VR/AR眼镜新产品大年，预计利润大幅增长",
                "先进封装3D堆叠催生CT检测需求",
                "光子计数CT开启高端影像设备升级换代"
            ],
            "key_metrics": ["PCB背钻CT检测设备单台价值量200万元级别"],
            "target_valuation": []
        }]
    },
    {
        "name": "永鼎股份", "code": "600105", "board": "SH",
        "industry": "通信-光通信-光芯片/光纤",
        "concepts": ["光芯片", "EML", "CW光源", "光纤光缆", "高温超导", "可控核聚变"],
        "products": ["EML光芯片", "CW光源", "光纤光缆", "高温超导带材"],
        "core_business": ["光芯片研发与生产", "光纤光缆制造", "高温超导带材"],
        "industry_position": ["国内稀缺的EML/CW光源光芯片量产企业", "高温超导带材少数量产企业"],
        "chain": ["上游-光芯片/光器件", "中游-光纤光缆"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "【机构调研】笔记整理", "date": today, "source": source3,
            "core_business": ["光芯片研发与生产", "光纤光缆制造", "高温超导带材"],
            "industry_position": ["国内稀缺的EML/CW光源光芯片量产企业", "高温超导带材少数量产企业"],
            "chain": ["上游-光芯片/光器件", "中游-光纤光缆"],
            "partners": [],
            "accidents": ["CW光源放量出货且产能持续爬坡"],
            "insights": [
                "鼎芯光电CW光源放量出货，后续有望获得大客户订单",
                "光纤持续涨价，公司积极扩产",
                "东部超导高温超导带材计划扩产5万公里，预计今年盈利"
            ],
            "key_metrics": [
                "光纤产能计划扩产到3600万芯公里",
                "光棒产能计划扩产到950吨",
                "高温超导带材计划扩产5万公里"
            ],
            "target_valuation": []
        }]
    },
    {
        "name": "珀莱雅", "code": "603605", "board": "SH",
        "industry": "消费-美妆护肤-化妆品",
        "concepts": ["美妆护肤", "618电商", "彩妆", "出海"],
        "products": ["护肤品", "彩妆"],
        "core_business": ["护肤品及彩妆研发与销售"],
        "industry_position": ["国内美妆护肤龙头", "国货美妆品牌标杆"],
        "chain": ["下游-品牌消费品"],
        "partners": ["花知晓"],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "【机构调研】笔记整理", "date": today, "source": source3,
            "core_business": ["护肤品及彩妆研发与销售"],
            "industry_position": ["国内美妆护肤龙头", "国货美妆品牌标杆"],
            "chain": ["下游-品牌消费品"],
            "partners": ["花知晓"],
            "accidents": ["618第一阶段天猫稳健抖音高增，收购花知晓控股"],
            "insights": [
                "618第一阶段主品牌天猫稳健、抖音高增，整体止跌企稳",
                "收购花知晓51%股权实现控股，2025年营收17.26亿元",
                "多个子品牌OR、原色波塔、惊时保持翻倍高增"
            ],
            "key_metrics": [
                "收购花知晓12.55%股权对价3.51亿元",
                "花知晓2025年营收17.26亿元，净利润2.80亿元"
            ],
            "target_valuation": ["目标价80.2元，给予2026年20x目标PE"]
        }]
    },
    # === Article 4: 12 stocks ===
    {
        "name": "合锻智能", "code": "603011", "board": "SH",
        "industry": "机械设备-专用设备-层压设备",
        "concepts": ["PCB层压设备", "真空层压机", "AI PCB", "核聚变"],
        "products": ["真空层压机", "PCB层压设备"],
        "core_business": ["真空层压设备研发与制造"],
        "industry_position": ["PCB真空层压设备国产替代核心标的"],
        "chain": ["上游-专用设备制造"],
        "partners": ["拉法"],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["真空层压设备研发与制造"],
            "industry_position": ["PCB真空层压设备国产替代核心标的"],
            "chain": ["上游-专用设备制造"],
            "partners": ["拉法"],
            "accidents": ["PCB层压设备供需缺口持续扩大，国产替代加速"],
            "insights": [
                "全球真空层压设备市场空间50-60亿，未来3-4年有望迈向数百亿",
                "拉法国产化后竞争优势凸显，较博可便宜20%-30%，交期仅6个月",
                "合锻已加码产线+招募行业团队，配套到位后可快速翻倍"
            ],
            "key_metrics": ["真空层压设备20亿产值，5亿利润预期"],
            "target_valuation": ["目标看250亿市值"]
        }]
    },
    {
        "name": "联瑞新材", "code": "688300", "board": "SH",
        "industry": "基础化工-化学新材料-填料材料",
        "concepts": ["PTFE填料", "M8/M9材料", "球硅", "IC载板", "先进封装"],
        "products": ["化学法球硅", "硅微粉"],
        "core_business": ["高端硅微粉及填料研发与生产"],
        "industry_position": ["PTFE方案填料核心供应商", "高端材料平台型企业"],
        "chain": ["上游-电子材料"],
        "partners": ["生益科技"],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["高端硅微粉及填料研发与生产"],
            "industry_position": ["PTFE方案填料核心供应商", "高端材料平台型企业"],
            "chain": ["上游-电子材料"],
            "partners": ["生益科技"],
            "accidents": ["正交背板PTFE方案测试超预期，填料用量大幅提升"],
            "insights": [
                "M8/M9驱动化学法球硅需求倍增",
                "公司卡位生益链，在下游份额中快速提升",
                "M8/M9用化学法球硅单价范围20-40万/吨逐级提升"
            ],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "巨轮股份", "code": "002031", "board": "SZ",
        "industry": "机械设备-专用设备-机器人零部件",
        "concepts": ["机器人", "RV减速器", "轮胎模具"],
        "products": ["轮胎模具", "RV减速器"],
        "core_business": ["轮胎模具制造", "RV减速器及工业机器人"],
        "industry_position": ["轮胎模具领域领先企业"],
        "chain": ["中游-专用设备制造"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["轮胎模具制造", "RV减速器及工业机器人"],
            "industry_position": ["轮胎模具领域领先企业"],
            "chain": ["中游-专用设备制造"],
            "partners": [],
            "accidents": ["OpenAI官宣进军机器人赛道"],
            "insights": ["OpenAI进军机器人赛道有望带动机器人产业链发展"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "麦格米特", "code": "002851", "board": "SZ",
        "industry": "电力设备-电源设备-服务器电源",
        "concepts": ["AI服务器电源", "NV电源", "PSU", "HVDC", "数据中心"],
        "products": ["服务器电源PSU", "HVDC", "Sidecar", "SST"],
        "core_business": ["服务器电源研发与生产", "AI数据中心电源解决方案"],
        "industry_position": ["英伟达服务器电源核心供应商"],
        "chain": ["中游-电源设备制造"],
        "partners": ["英伟达"],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["服务器电源研发与生产", "AI数据中心电源解决方案"],
            "industry_position": ["英伟达服务器电源核心供应商"],
            "chain": ["中游-电源设备制造"],
            "partners": ["英伟达"],
            "accidents": ["英伟达GTC台北大会展示Vera Rubin，电源配套升级"],
            "insights": [
                "从GB200到Rubin，电源产品功率密度持续提升",
                "PSU由5.5kw增至18+kw，NVL72机柜用量由198/264kw增至440kw",
                "构建全栈电源产品矩阵，覆盖北美头部云厂商"
            ],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "新宙邦", "code": "300037", "board": "SZ",
        "industry": "基础化工-氟化工-含氟精细化工",
        "concepts": ["氟化液", "高纯PFA", "半导体冷却", "液冷", "PTFE"],
        "products": ["氟化液", "含氟化学品"],
        "core_business": ["含氟精细化学品研发与生产"],
        "industry_position": ["氟化液国产替代领先企业"],
        "chain": ["上游-氟化工材料"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["含氟精细化学品研发与生产"],
            "industry_position": ["氟化液国产替代领先企业"],
            "chain": ["上游-氟化工材料"],
            "partners": [],
            "accidents": ["3M退出氟化液市场，国产替代机会"],
            "insights": [
                "3M因环保原因退出氟化液市场，释放1.2万吨产能",
                "全氟聚醚价格50万元/吨，氢氟醚20万元/吨",
                "液冷方案迭代带动氟化液应用前景"
            ],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "金石资源", "code": "603979", "board": "SH",
        "industry": "基础化工-氟化工-氟材料",
        "concepts": ["氟化液", "低聚体", "萤石"],
        "products": ["萤石", "氟化液"],
        "core_business": ["萤石矿开采与氟化工"],
        "industry_position": ["国内萤石龙头"],
        "chain": ["上游-矿产资源"],
        "partners": ["诺亚"],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["萤石矿开采与氟化工"],
            "industry_position": ["国内萤石龙头"],
            "chain": ["上游-矿产资源"],
            "partners": ["诺亚"],
            "accidents": ["3M退出氟化液市场，国产替代机会"],
            "insights": ["持有诺亚15.7%股权，诺亚在低聚体领域较为领先"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "尚太科技", "code": "001301", "board": "SZ",
        "industry": "电力设备-锂电-负极材料",
        "concepts": ["锂电池负极", "石墨化", "人造石墨"],
        "products": ["锂电池负极材料", "人造石墨"],
        "core_business": ["锂电池负极材料研发与生产"],
        "industry_position": ["锂电池负极材料行业领先企业"],
        "chain": ["上游-锂电材料"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["锂电池负极材料研发与生产"],
            "industry_position": ["锂电池负极材料行业领先企业"],
            "chain": ["上游-锂电材料"],
            "partners": [],
            "accidents": ["负极涨价Q2盈利拐点明确"],
            "insights": [
                "负极谈价顺利，基础价格预计上涨1-2k",
                "Q2起盈利拐点明确，单位盈利明显修复",
                "石墨化自供比例提升+委外比例下降降本"
            ],
            "key_metrics": [],
            "target_valuation": ["27年单吨净利有望恢复至0.3万+，对应27年仅10x"]
        }]
    },
    {
        "name": "贝特瑞", "code": "835185", "board": "BJ",
        "industry": "电力设备-锂电-负极材料",
        "concepts": ["锂电池负极", "正极材料"],
        "products": ["锂电池负极材料", "正极材料"],
        "core_business": ["锂电池负极材料及正极材料研发与生产"],
        "industry_position": ["全球锂电池负极材料龙头"],
        "chain": ["上游-锂电材料"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["锂电池负极材料及正极材料研发与生产"],
            "industry_position": ["全球锂电池负极材料龙头"],
            "chain": ["上游-锂电材料"],
            "partners": [],
            "accidents": ["负极涨价Q2盈利拐点明确"],
            "insights": ["负极行业需求持续高增，26年全球锂电需求增长35%+"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "璞泰来", "code": "603659", "board": "SH",
        "industry": "电力设备-锂电-负极/隔膜",
        "concepts": ["锂电池负极", "隔膜涂覆", "石墨化"],
        "products": ["锂电池负极材料", "隔膜涂覆"],
        "core_business": ["锂电池负极材料及隔膜涂覆研发与生产"],
        "industry_position": ["锂电池负极材料行业领先企业"],
        "chain": ["上游-锂电材料"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["锂电池负极材料及隔膜涂覆研发与生产"],
            "industry_position": ["锂电池负极材料行业领先企业"],
            "chain": ["上游-锂电材料"],
            "partners": [],
            "accidents": ["负极涨价Q2盈利拐点明确"],
            "insights": ["负极行业需求持续高增"],
            "key_metrics": [],
            "target_valuation": []
        }]
    },
    {
        "name": "万顺新材", "code": "300057", "board": "SZ",
        "industry": "有色金属-铝加工-铝箔",
        "concepts": ["锂电池铝箔", "钠电池负极铝箔", "钠电池"],
        "products": ["铝箔", "锂电池铝箔", "钠电池负极铝箔"],
        "core_business": ["铝箔及电池铝箔研发与生产"],
        "industry_position": ["铝箔行业重要企业，钠电负极铝箔潜在标的"],
        "chain": ["上游-金属材料加工"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["铝箔及电池铝箔研发与生产"],
            "industry_position": ["铝箔行业重要企业，钠电负极铝箔潜在标的"],
            "chain": ["上游-金属材料加工"],
            "partners": [],
            "accidents": ["铝箔涨价盈利弹性"],
            "insights": ["铝箔涨价盈利弹性，新基地落地量增", "钠电负极铝箔可跟踪进展"],
            "key_metrics": [],
            "target_valuation": ["26、27年预计2.5、4亿利润"]
        }]
    },
    {
        "name": "中伟新材", "code": "300919", "board": "SZ",
        "industry": "电力设备-锂电-前驱体",
        "concepts": ["前驱体", "钠电池正极", "镍资源"],
        "products": ["三元前驱体", "钠电池正极材料"],
        "core_business": ["锂电池前驱体材料研发与生产"],
        "industry_position": ["全球三元前驱体龙头"],
        "chain": ["上游-锂电材料"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["锂电池前驱体材料研发与生产"],
            "industry_position": ["全球三元前驱体龙头"],
            "chain": ["上游-锂电材料"],
            "partners": [],
            "accidents": ["钠电正极材料布局"],
            "insights": [
                "前驱体材料稳定，镍资源受益于镍价上涨",
                "钠电正极100GWh、30%份额，弹性3亿"
            ],
            "key_metrics": ["钠电正极100GWh、30%份额"],
            "target_valuation": ["对应150亿增量"]
        }]
    },
    {
        "name": "禾川科技", "code": "688320", "board": "SH",
        "industry": "机械设备-工控设备-伺服系统",
        "concepts": ["工控自动化", "伺服系统", "PLC", "激光", "锂电"],
        "products": ["伺服系统", "PLC", "驱动器"],
        "core_business": ["伺服系统及工控自动化产品研发与生产"],
        "industry_position": ["国内工控自动化领先企业"],
        "chain": ["中游-工业自动化设备"],
        "partners": [],
        "mention_count": 1, "last_updated": today,
        "articles": [{
            "title": "今天的一些信息整理6.1", "date": today, "source": source4,
            "core_business": ["伺服系统及工控自动化产品研发与生产"],
            "industry_position": ["国内工控自动化领先企业"],
            "chain": ["中游-工业自动化设备"],
            "partners": [],
            "accidents": ["5月订单同比增长130%"],
            "insights": [
                "5月订单同增130%，激光、锂电、包装、机床表现优异",
                "工控复苏超预期"
            ],
            "key_metrics": ["5月订单同比增长130%"],
            "target_valuation": []
        }]
    }
]

output = {"stocks": stocks}
with open("data/stocks_master_2026-06-01.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Combined JSON: {len(stocks)} stocks from 2 articles")
for s in stocks:
    print(f"  {s['code']} {s['name']} ({s['board']}) - {s['industry']}")