#!/usr/bin/env python3
"""
process_groups.py — 处理来自 /tmp/stock_groups/ 的分组文件
支持格式：.txt（同花顺）、.sel（通达信，纯文本兼容）、手动输入

用法：
  python process_groups.py                    # 处理 /tmp/stock_groups/ 下所有文件
  python process_groups.py --dry-run           # 预览但不写入
  python process_groups.py --file xxx.txt      # 处理单个文件
"""

import json, os, sys, re, hashlib
from pathlib import Path
from datetime import datetime

# ===== 配置 =====
BASE_DIR = Path(__file__).parent
GROUPS_FILE = BASE_DIR / "data" / "groups" / "groups.json"
STOCKS_MASTER = BASE_DIR / "data" / "stocks" / "stocks_master.json"
TMP_DIR = Path("/tmp/stock_groups")  # Linux 路径
CATEGORY_MAP = {
    "半导体": "半导体材料", "芯片": "半导体材料", "封测": "封装与PCB",
    "封装": "封装与PCB", "PCB": "封装与PCB", "MLCC": "元器件",
    "电子": "元器件", "电容": "元器件", "电感": "元器件",
    "AI": "AI算力链", "算力": "AI算力链", "光模块": "AI算力链",
    "CPO": "AI算力链", "连接器": "AI算力链", "服务器": "AI算力链",
    "新能源": "新能源", "锂": "新能源", "光伏": "新能源", "储能": "新能源",
    "机器人": "物理AI与机器人", "人形": "物理AI与机器人",
    "航天": "航天", "卫星": "航天", "SpaceX": "航天",
    "通讯": "通讯电子", "手机": "通讯电子", "5G": "通讯电子",
    "华为": "华为产业链",
    "材料": "半导体材料", "金属": "稀有金属", "稀土": "稀有金属",
}

# ===== 股票名称→代码映射 =====
def load_code_map():
    """从 stocks_master.json 加载 名称→代码 映射"""
    if not STOCKS_MASTER.exists():
        print(f"❌ 找不到 {STOCKS_MASTER}")
        return {}
    
    with open(STOCKS_MASTER, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    name_map = {}  # name -> code
    code_set = set()
    for code, stock in data.get("stocks", {}).items():
        name = stock.get("name", "").strip()
        if name:
            if name not in name_map:
                name_map[name] = []
            name_map[name].append(code)
        code_set.add(code)
    
    print(f"📋 已加载 {len(name_map)} 个名称 -> {len(code_set)} 个代码")
    return name_map, code_set

# ===== 解析同花顺 .txt 文件 =====
def parse_ths_txt(filepath: Path) -> dict:
    """解析同花顺 .txt 分组文件"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    # 推断分组名称：取文件名去掉 THS_ 前缀
    fname = filepath.stem
    if fname.startswith("THS_"):
        group_name = fname[4:]
    elif fname.startswith("同花顺_"):
        group_name = fname[4:]
    else:
        group_name = fname
    
    stocks = []
    desc_lines = []
    for line in lines:
        # 尝试匹配股票代码
        code_match = re.search(r'\b(\d{6})\b', line)
        if code_match:
            stocks.append(code_match.group(1))
        else:
            # 无代码的行可能是描述或纯名称
            cleaned = re.sub(r'[\s\-,;，；]+', ' ', line).strip()
            if cleaned:
                desc_lines.append(cleaned)
    
    return {
        "name": group_name,
        "description": " ".join(desc_lines[:3]) if desc_lines else f"{group_name}相关股票",
        "stocks_raw": stocks,
        "source": str(filepath)
    }

# ===== 解析通达信 .sel 文件 =====
def parse_tdx_sel(filepath: Path) -> dict:
    """解析通达信 .sel 文本格式（非二进制）"""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # .sel 文件可能是文本格式：每行一个股票代码
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    
    fname = filepath.stem
    if fname.startswith("TDX_"):
        group_name = fname[4:]
    elif fname.startswith("通达信_"):
        group_name = fname[4:]
    else:
        group_name = fname
    
    stocks = []
    for line in lines:
        code_match = re.search(r'\b(\d{6})\b', line)
        if code_match:
            stocks.append(code_match.group(1))
    
    return {
        "name": group_name,
        "description": f"通达信自选股 - {group_name}（{len(stocks)}只）",
        "stocks_raw": stocks,
        "source": str(filepath)
    }

# ===== 名称→代码转换 =====
def resolve_codes(stocks_raw: list, name_map: dict) -> list:
    """将原始股票名称转换为6位代码"""
    codes = []
    unmatched = []
    for item in stocks_raw:
        # 已经是6位数字代码
        if re.match(r'^\d{6}$', item):
            codes.append(item)
            continue
        
        # 尝试名称匹配
        item_clean = item.strip().replace(' ', '')
        if item_clean in name_map:
            code_list = name_map[item_clean]
            if len(code_list) == 1:
                codes.append(code_list[0])
            else:
                codes.extend(code_list)  # 同名多代码
        else:
            unmatched.append(item_clean)
    
    if unmatched and len(unmatched) < 20:
        print(f"  ⚠️ 未匹配到代码: {', '.join(unmatched)}")
    elif unmatched:
        print(f"  ⚠️ 未匹配 {len(unmatched)} 个名称")
    
    return codes, unmatched

# ===== 智能推断 category =====
def infer_category(name: str, description: str) -> str:
    """根据分组名称推断分类"""
    text = name + description
    for keyword, category in CATEGORY_MAP.items():
        if keyword in text:
            return category
    return "产业链/IPO"

# ===== 生成分组 ID =====
def gen_group_id(name: str) -> str:
    ts = int(datetime.now().timestamp() * 1000)
    safe_name = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)[:30]
    return f"group_{ts}_{safe_name}"

# ===== 自动配色 =====
COLORS = ["#3b82f6","#ef4444","#10b981","#f59e0b","#8b5cf6","#ec4899",
          "#06b6d4","#f97316","#14b8a6","#6366f1","#d946ef","#eab308",
          "#dc2626","#7c3aed","#2563eb","#0891b2","#a855f7","#f43f5e"]

def get_color(index: int) -> str:
    return COLORS[index % len(COLORS)]

# ===== 主处理函数 =====
def process_groups(dry_run=False, filepath=None):
    name_map, code_set = load_code_map()
    if not name_map:
        print("❌ 无法加载股票数据，退出")
        return
    
    # 加载现有分组
    existing_groups = []
    if GROUPS_FILE.exists():
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            existing_groups = json.load(f).get("groups", [])
    print(f"📁 现有分组: {len(existing_groups)} 个")
    
    existing_names = {g["name"] for g in existing_groups}
    
    # 收集待处理文件
    if filepath:
        files = [Path(filepath)]
    else:
        files = []
        if TMP_DIR.exists():
            for f in TMP_DIR.glob("*"):
                if f.suffix.lower() in ('.txt', '.sel'):
                    files.append(f)
        else:
            print(f"⚠️ {TMP_DIR} 不存在，使用 --file 指定文件")
    
    if not files:
        print("📂 没有找到待处理的分组文件")
        # 显示现有分组列表
        print(f"\n现有 {len(existing_groups)} 个分组:")
        for g in existing_groups:
            print(f"  - {g['name']} ({len(g.get('stocks',[]))}只)")
        return
    
    print(f"📂 发现 {len(files)} 个待处理文件:")
    for f in files:
        print(f"  - {f.name}")
    
    new_groups = []
    updated_groups = []
    skipped_groups = []
    
    for i, f in enumerate(files):
        print(f"\n{'='*50}")
        print(f"处理: {f.name}")
        
        # 解析
        if f.suffix.lower() == '.sel':
            parsed = parse_tdx_sel(f)
        else:
            parsed = parse_ths_txt(f)
        
        group_name = parsed["name"]
        print(f"  名称: {group_name}")
        print(f"  来源: {parsed['source']}")
        
        # 名称→代码转换
        codes, unmatched = resolve_codes(parsed["stocks_raw"], name_map)
        print(f"  股票: {len(codes)} 只 (未匹配: {len(unmatched)})")
        
        if not codes:
            print(f"  ⚠️ 没有匹配到任何股票代码，跳过")
            skipped_groups.append(group_name)
            continue
        
        # 去重检查
        if group_name in existing_names:
            # 更新已有分组
            existing = next(g for g in existing_groups if g["name"] == group_name)
            old_set = set(existing.get("stocks", []))
            new_codes = [c for c in codes if c not in old_set]
            if new_codes:
                existing["stocks"].extend(new_codes)
                existing["description"] = parsed["description"]
                existing["updated_at"] = datetime.now().strftime("%Y-%m-%d")
                print(f"  🔄 更新分组: +{len(new_codes)} 只新股票")
                updated_groups.append(group_name)
            else:
                print(f"  ⏭️ 分组已存在，无新增")
                skipped_groups.append(group_name)
        else:
            # 新建分组
            group = {
                "id": gen_group_id(group_name),
                "name": group_name,
                "description": parsed["description"],
                "color": get_color(len(existing_groups) + len(new_groups)),
                "icon": "📊",
                "stocks": codes,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "updated_at": datetime.now().strftime("%Y-%m-%d"),
                "category": infer_category(group_name, parsed["description"])
            }
            existing_groups.append(group)
            existing_names.add(group_name)
            new_groups.append(group_name)
            print(f"  ✅ 新增分组: {len(codes)} 只股票, 分类: {group['category']}")
    
    # 输出汇总
    print(f"\n{'='*50}")
    print(f"📊 处理汇总:")
    print(f"  ✅ 新增: {len(new_groups)} 个")
    print(f"  🔄 更新: {len(updated_groups)} 个")
    print(f"  ⏭️ 跳过: {len(skipped_groups)} 个")
    
    if new_groups:
        print(f"\n  新增分组:")
        for n in new_groups:
            g = next(g for g in existing_groups if g["name"] == n)
            print(f"    - {n} ({len(g['stocks'])}只, 分类:{g.get('category','-')})")
    
    if dry_run:
        print("\n🔍 DRY RUN - 未实际写入文件")
        return
    
    # 写入
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"groups": existing_groups}, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存到 {GROUPS_FILE} ({len(existing_groups)} 个分组)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="处理股票分组文件")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入")
    parser.add_argument("--file", "-f", type=str, help="处理单个文件")
    args = parser.parse_args()
    process_groups(dry_run=args.dry_run, filepath=args.file)
