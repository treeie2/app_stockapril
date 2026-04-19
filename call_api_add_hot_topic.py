#!/usr/bin/env python3
"""
提取热点信息并调用豆包 API 处理
"""
import json
import re
import subprocess
import sys

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
        
        # 提取内容部分
        content = re.sub(r'^(\w+)(?:方面|板块)[：:]', '', section).strip()
        
        # 提取相关个股 - 改进匹配逻辑
        stocks = []
        
        # 匹配 "XX股份"、"XX稀土"、"XX有色" 等格式
        stock_patterns = [
            r'([\u4e00-\u9fa5]{2,6}股份)',
            r'([\u4e00-\u9fa5]{2,6}稀土)',
            r'([\u4e00-\u9fa5]{2,6}有色)',
            r'([\u4e00-\u9fa5]{2,6}科技)',
            r'([\u4e00-\u9fa5]{2,6}矿业)',
            r'([\u4e00-\u9fa5]{2,6}集团)',
        ]
        
        for pattern in stock_patterns:
            matches = re.findall(pattern, content)
            stocks.extend(matches)
        
        # 去重
        stocks = list(set(stocks))
        
        # 驱动因素是完整内容
        drivers = content
        
        if topic_name and drivers:
            hot_topics.append({
                'name': topic_name,
                'drivers': drivers,
                'stocks': stocks
            })
    
    return hot_topics


def call_doubao_api(text):
    """调用豆包 API 处理文本"""
    
    # 构建 prompt
    prompt = f"""请从以下文本中提取热点投资信息，以JSON格式返回：

文本内容：
{text}

请提取以下信息并以JSON格式返回：
{{
  "hot_topics": [
    {{
      "name": "热点名称（如：稀土、钨等）",
      "drivers": "驱动因素描述",
      "stocks": ["相关个股1", "相关个股2"]
    }}
  ]
}}

注意：
1. 热点名称要简洁，通常是行业或板块名称
2. 驱动因素要包含价格变动、供需关系、政策影响等关键信息
3. 相关个股要准确提取公司名称，如"北方稀土"、"中稀有色"等"""

    # 构建 API 请求
    api_data = {
        "model": "doubao-seed-2-0-lite-260215",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    # 构建 curl 命令
    curl_cmd = [
        'curl', 'https://ark.cn-beijing.volces.com/api/v3/responses',
        '-H', 'Authorization: Bearer 7b514c18-fdfc-41cc-9aa9-ed8ff79f5799',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(api_data, ensure_ascii=False)
    ]
    
    print("🤖 调用豆包 API...\n")
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ API 调用成功")
            print("\n响应内容:")
            print(result.stdout)
            return result.stdout
        else:
            print(f"❌ API 调用失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 调用出错: {e}")
        return None


def main():
    # 你提供的文本
    text = """稀土方面：Q2精矿交易价上调至3.88万元/吨，环比大涨45%确立右侧反转。供给端一季度产量增速仅2%；需求端受2025年出口管制影响，海外（占比30%-40%）提前补库拉动6%-7%额外需求，全年需求增速预期达10%-14%。供需错配驱动中稀有色、北方稀土一季度业绩分别增长2倍和超1倍，产业链向下游延伸平滑周期。

钨方面：历经1个半月回调去库近尾声，贸易商废钨囤货不足2个月，下游自2月下旬未补库，预计4月底至5月中旬库存降至1个季度水位。80万精矿价格构筑底部，后续有望向130-140万均值回归，交易核心正实质性切换至产业微观供需错配兑现。"""
    
    print("="*60)
    print("🔍 第一步：本地提取热点信息")
    print("="*60)
    
    topics = extract_hot_topic_info(text)
    
    for i, topic in enumerate(topics, 1):
        print(f"\n【热点 {i}】")
        print(f"名称: {topic['name']}")
        print(f"驱动因素: {topic['drivers'][:80]}...")
        print(f"相关个股: {', '.join(topic['stocks']) if topic['stocks'] else '未识别'}")
    
    print("\n" + "="*60)
    print("🤖 第二步：调用豆包 API 进一步优化")
    print("="*60)
    
    # 调用 API
    response = call_doubao_api(text)
    
    if response:
        print("\n✅ 处理完成!")
        # 尝试解析 JSON 响应
        try:
            data = json.loads(response)
            print("\n解析后的数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except:
            print("\n原始响应:")
            print(response)
    else:
        print("\n⚠️ API 调用失败，使用本地提取结果:")
        print(json.dumps(topics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
