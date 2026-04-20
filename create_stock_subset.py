#!/usr/bin/env python3
"""
创建股票子集功能
用于将股票分组管理，如"核电"、"特高压"、"固态电池"等概念子集
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 子集定义文件路径
SUBSETS_FILE = Path("e:/github/stock-research-backup/data/master/stock_subsets.json")
MASTER_FILE = Path("e:/github/stock-research-backup/data/master/stocks_master.json")

# 核电概念股票列表
NUCLEAR_STOCKS = [
    {"code": "600089", "name": "特变电工", "reason": "全球变压器龙头，核电变压器核心供应商"},
    {"code": "601179", "name": "中国西电", "reason": "电力装备综合巨头，特高压设备市占率超40%"},
    {"code": "600550", "name": "保变电气", "reason": "核电变压器专家，三代核电技术供应商"},
    {"code": "600312", "name": "平高电气", "reason": "特高压开关龙头，核电开关设备供应商"},
    {"code": "002130", "name": "沃尔核材", "reason": "核电电缆附件核心供应商，华龙一号供应商"},
    {"code": "603308", "name": "应流股份", "reason": "高端铸锻件供应商，核电关键部件供应商"},
    {"code": "600973", "name": "宝胜股份", "reason": "核级电缆领军者，国内最全核级电缆许可证"},
    {"code": "300617", "name": "安靠智电", "reason": "地下智能输电先锋，核电输电系统供应商"},
    {"code": "600268", "name": "国电南自", "reason": "电力自动化专家，核电国产替代标杆"},
    {"code": "002112", "name": "三变科技", "reason": "特种变压器专业厂商，核电配电供应商"}
]


def load_subsets() -> Dict:
    """加载子集定义文件"""
    if SUBSETS_FILE.exists():
        with open(SUBSETS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"subsets": {}, "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()}


def save_subsets(subsets_data: Dict):
    """保存子集定义文件"""
    SUBSETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    subsets_data["updated_at"] = datetime.now().isoformat()
    with open(SUBSETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(subsets_data, f, ensure_ascii=False, indent=2)


def create_subset(subset_name: str, description: str = "", stocks: List[Dict] = None) -> bool:
    """
    创建一个新的股票子集
    
    Args:
        subset_name: 子集名称，如"核电"、"特高压"
        description: 子集描述
        stocks: 初始股票列表，每个股票包含code, name, reason
    
    Returns:
        bool: 是否创建成功
    """
    subsets_data = load_subsets()
    
    if subset_name in subsets_data["subsets"]:
        print(f"⚠️ 子集 '{subset_name}' 已存在，将更新股票列表")
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 构建子集数据
    subset_data = {
        "name": subset_name,
        "description": description,
        "created_at": today,
        "updated_at": today,
        "stock_count": len(stocks) if stocks else 0,
        "stocks": {}
    }
    
    # 添加股票到子集
    if stocks:
        for stock in stocks:
            code = stock["code"]
            subset_data["stocks"][code] = {
                "code": code,
                "name": stock["name"],
                "added_at": today,
                "reason": stock.get("reason", ""),
                "order": len(subset_data["stocks"]) + 1
            }
    
    subsets_data["subsets"][subset_name] = subset_data
    save_subsets(subsets_data)
    
    print(f"✅ 子集 '{subset_name}' 创建/更新成功！")
    print(f"   包含股票: {len(stocks) if stocks else 0} 只")
    return True


def add_stocks_to_subset(subset_name: str, stocks: List[Dict]) -> bool:
    """
    向现有子集添加股票
    
    Args:
        subset_name: 子集名称
        stocks: 要添加的股票列表
    
    Returns:
        bool: 是否添加成功
    """
    subsets_data = load_subsets()
    
    if subset_name not in subsets_data["subsets"]:
        print(f"❌ 子集 '{subset_name}' 不存在，请先创建")
        return False
    
    subset = subsets_data["subsets"][subset_name]
    today = datetime.now().strftime('%Y-%m-%d')
    
    added_count = 0
    for stock in stocks:
        code = stock["code"]
        if code not in subset["stocks"]:
            subset["stocks"][code] = {
                "code": code,
                "name": stock["name"],
                "added_at": today,
                "reason": stock.get("reason", ""),
                "order": len(subset["stocks"]) + 1
            }
            added_count += 1
            print(f"  ➕ 添加: {code} {stock['name']}")
        else:
            print(f"  ⚠️ 已存在: {code} {stock['name']}")
    
    subset["stock_count"] = len(subset["stocks"])
    subset["updated_at"] = today
    save_subsets(subsets_data)
    
    print(f"\n✅ 成功添加 {added_count} 只股票到 '{subset_name}'")
    return True


def remove_stocks_from_subset(subset_name: str, stock_codes: List[str]) -> bool:
    """
    从子集中移除股票
    
    Args:
        subset_name: 子集名称
        stock_codes: 要移除的股票代码列表
    
    Returns:
        bool: 是否移除成功
    """
    subsets_data = load_subsets()
    
    if subset_name not in subsets_data["subsets"]:
        print(f"❌ 子集 '{subset_name}' 不存在")
        return False
    
    subset = subsets_data["subsets"][subset_name]
    today = datetime.now().strftime('%Y-%m-%d')
    
    removed_count = 0
    for code in stock_codes:
        if code in subset["stocks"]:
            stock_name = subset["stocks"][code]["name"]
            del subset["stocks"][code]
            removed_count += 1
            print(f"  ➖ 移除: {code} {stock_name}")
    
    # 重新排序
    for i, (code, stock) in enumerate(subset["stocks"].items(), 1):
        stock["order"] = i
    
    subset["stock_count"] = len(subset["stocks"])
    subset["updated_at"] = today
    save_subsets(subsets_data)
    
    print(f"\n✅ 成功从 '{subset_name}' 移除 {removed_count} 只股票")
    return True


def list_subsets():
    """列出所有子集"""
    subsets_data = load_subsets()
    
    if not subsets_data["subsets"]:
        print("📭 暂无子集")
        return
    
    print("\n📁 所有子集:")
    print("-" * 60)
    for name, subset in subsets_data["subsets"].items():
        print(f"\n🔹 {name}")
        print(f"   描述: {subset.get('description', '无')}")
        print(f"   股票数: {subset['stock_count']}")
        print(f"   创建时间: {subset['created_at']}")
        print(f"   更新时间: {subset['updated_at']}")


def get_subset_detail(subset_name: str):
    """获取子集详细信息"""
    subsets_data = load_subsets()
    
    if subset_name not in subsets_data["subsets"]:
        print(f"❌ 子集 '{subset_name}' 不存在")
        return
    
    subset = subsets_data["subsets"][subset_name]
    
    print(f"\n📋 子集详情: {subset_name}")
    print("=" * 60)
    print(f"描述: {subset.get('description', '无')}")
    print(f"股票数量: {subset['stock_count']}")
    print(f"创建时间: {subset['created_at']}")
    print(f"更新时间: {subset['updated_at']}")
    print("\n股票列表:")
    print("-" * 60)
    
    # 按order排序
    sorted_stocks = sorted(subset["stocks"].items(), key=lambda x: x[1].get("order", 999))
    for code, stock in sorted_stocks:
        print(f"  {stock['order']:2d}. {code} {stock['name']}")
        if stock.get('reason'):
            print(f"      理由: {stock['reason']}")


def sync_subset_to_master(subset_name: str):
    """
    将子集中的股票同步到 stocks_master.json 的 concepts 字段
    为每只子集中的股票添加子集名称作为概念标签
    """
    subsets_data = load_subsets()
    
    if subset_name not in subsets_data["subsets"]:
        print(f"❌ 子集 '{subset_name}' 不存在")
        return False
    
    subset = subsets_data["subsets"][subset_name]
    
    # 读取 master 文件
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    stocks = master_data.get('stocks', {})
    today = datetime.now().strftime('%Y-%m-%d')
    
    updated_count = 0
    for code in subset["stocks"]:
        if code in stocks:
            stock = stocks[code]
            concepts = stock.get('concepts', [])
            if subset_name not in concepts:
                concepts.append(subset_name)
                stock['concepts'] = concepts
                stock['updated_at'] = today
                updated_count += 1
                print(f"  ✅ 更新概念: {code} {stock['name']} → 添加 '{subset_name}'")
        else:
            print(f"  ⚠️ 股票不存在: {code}")
    
    # 保存 master 文件
    with open(MASTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 成功同步 {updated_count} 只股票的概念标签")
    return True


def main():
    """主函数 - 创建核电子集"""
    print("🚀 创建股票子集功能\n")
    
    # 1. 创建核电子集
    print("1️⃣ 创建'核电'子集...")
    create_subset(
        subset_name="核电",
        description="核电产业链核心公司，涵盖核电设备、材料、自动化等细分领域",
        stocks=NUCLEAR_STOCKS
    )
    
    # 2. 显示子集详情
    print("\n2️⃣ 查看子集详情...")
    get_subset_detail("核电")
    
    # 3. 同步到 master（添加概念标签）
    print("\n3️⃣ 同步到 stocks_master.json...")
    sync_subset_to_master("核电")
    
    # 4. 列出所有子集
    print("\n4️⃣ 查看所有子集...")
    list_subsets()
    
    print("\n🎉 完成！")


if __name__ == '__main__':
    main()
