#!/usr/bin/env python3
"""
从文本中提取热点信息：热点名称、驱动因素、相关个股
"""
import re
import json

def extract_hot_topic_info(text):
    """从文本中提取热点信息"""
    
    # 识别热点板块（以"方面："或"板块"等关键词分隔）
    sections = re.split(r'(?=\n\s*\w+方面：|\n\s*\w+板块)', text)
    
    hot_topics = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # 提取热点名称
        name_match = re.match(r'^(\w+)(?:方面|板块)', section)
        if not name_match:
            continue
        
        topic_name = name_match.group(1)
        
        # 提取驱动因素（冒号后的内容，直到出现个股或结尾）
        # 移除热点名称部分
        content = re.sub(r'^(\w+)(?:方面|板块)[：:]', '', section).strip()
        
        # 提取相关个股（括号内的股票名称）
        stock_matches = re.findall(r'([\u4e00-\u9fa5]{2,8})(?:\(|（|\[)', content)
        # 或者匹配"XX股份"、"XX稀土"等格式
        stock_patterns = re.findall(r'([\u4e00-\u9fa5]{2,6}(?:股份|稀土|有色|科技|矿业))', content)
        
        stocks = list(set(stock_matches + stock_patterns))
        
        # 驱动因素是除个股外的内容
        drivers = content
        # 移除个股名称，保留驱动因素描述
        for stock in stocks:
            drivers = drivers.replace(stock, '')
        # 清理多余的标点符号
        drivers = re.sub(r'[（(][^）)]+[）)]', '', drivers)  # 移除括号内容
        drivers = re.sub(r'\s+', ' ', drivers).strip()
        
        if topic_name and drivers:
            hot_topics.append({
                'name': topic_name,
                'drivers': drivers,
                'stocks': stocks
            })
    
    return hot_topics


def main():
    # 你提供的文本
    text = """稀土方面：Q2精矿交易价上调至3.88万元/吨，环比大涨45%确立右侧反转。供给端一季度产量增速仅2%；需求端受2025年出口管制影响，海外（占比30%-40%）提前补库拉动6%-7%额外需求，全年需求增速预期达10%-14%。供需错配驱动中稀有色、北方稀土一季度业绩分别增长2倍和超1倍，产业链向下游延伸平滑周期。

钨方面：历经1个半月回调去库近尾声，贸易商废钨囤货不足2个月，下游自2月下旬未补库，预计4月底至5月中旬库存降至1个季度水位。80万精矿价格构筑底部，后续有望向130-140万均值回归，交易核心正实质性切换至产业微观供需错配兑现。"""
    
    print("🔍 提取热点信息...\n")
    
    topics = extract_hot_topic_info(text)
    
    for i, topic in enumerate(topics, 1):
        print(f"【热点 {i}】")
        print(f"名称: {topic['name']}")
        print(f"驱动因素: {topic['drivers'][:100]}...")
        print(f"相关个股: {', '.join(topic['stocks']) if topic['stocks'] else '未识别'}")
        print()
    
    # 输出 JSON 格式供 API 使用
    print("="*60)
    print("JSON 格式输出:")
    print(json.dumps(topics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
