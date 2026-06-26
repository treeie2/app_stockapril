"""
共享合并工具模块 (v2.5)
提取 6 个脚本中重复的文章合并/分片读写逻辑，统一为公共函数。
所有脚本直接 import 此模块，不再各自实现去重逻辑。

使用示例:
    from merge_utils import merge_articles, load_master, save_master
    master = load_master(PROJECT_ROOT)
    for code, new_stock in new_stocks.items():
        existing = master['stocks'].setdefault(code, new_stock)
        existing['articles'] = merge_articles(existing.get('articles', []), new_stock.get('articles', []))
        merge_set_fields(existing, new_stock)
    save_master(PROJECT_ROOT, master)
"""

import json
import re
from datetime import date
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

SET_FIELDS = ['concepts', 'products', 'core_business', 'industry_position', 'chain', 'partners']

# ─── 日期格式规范 (v2.8): 统一使用 YYYY-MM-DD ───

def normalize_date_string(raw: str) -> str:
    """将各种日期格式规范化到 YYYY-MM-DD。
    
    支持输入:
      - YYYYMMDD       → YYYY-MM-DD
      - YYYY-MM-DD     → 不变
      - YYYY/MM/DD     → YYYY-MM-DD
      - MM.DD           → 当年 YYYY-MM-DD
      - 空字符串         → 返回空字符串
    """
    raw = str(raw).strip()
    if not raw:
        return raw
    
    # YYYYMMDD → YYYY-MM-DD
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    
    # 已经符合 YYYY-MM-DD
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
        return raw
    
    # YYYY/MM/DD
    m = re.fullmatch(r'(\d{4})/(\d{2})/(\d{2})', raw)
    if m:
        return f"{m[1]}-{m[2]}-{m[3]}"
    
    # MM.DD → 当年
    m = re.fullmatch(r'(\d{2})\.(\d{2})', raw)
    if m:
        yr = date.today().year
        return f"{yr}-{m[1]}-{m[2]}"
    
    return raw


def normalize_stock_dates(stock: Dict) -> Tuple[int, int]:
    """规范化单只股票的日期字段，返回 (修复的 last_updated 数, 修复的 article.date 数)"""
    fixed_lu = 0
    fixed_art = 0
    
    # 规范化 last_updated
    lu = stock.get('last_updated', '')
    if lu:
        new_lu = normalize_date_string(lu)
        if new_lu != lu:
            stock['last_updated'] = new_lu
            fixed_lu = 1
    
    # 规范化 articles[].date
    for a in stock.get('articles', []):
        ad = a.get('date', '')
        if ad:
            new_ad = normalize_date_string(ad)
            if new_ad != ad:
                a['date'] = new_ad
                fixed_art += 1
    
    return fixed_lu, fixed_art


def normalize_all_stock_dates(stocks: Dict) -> Dict[str, int]:
    """规范化所有股票的日期字段，返回统计信息"""
    stats = {'last_updated': 0, 'article_date': 0, 'stocks_affected': 0}
    for code, s in stocks.items():
        fl, fa = normalize_stock_dates(s)
        if fl or fa:
            stats['last_updated'] += fl
            stats['article_date'] += fa
            stats['stocks_affected'] += 1
    return stats


def merge_articles(existing: List[Dict], new_articles: List[Dict]) -> List[Dict]:
    """
    按 (title, source) 去重合并文章列表。返回合并后的列表。
    """
    if not new_articles:
        return existing
    existing_keys = {(a.get('title', ''), a.get('source', '')) for a in existing}
    for a in new_articles:
        key = (a.get('title', ''), a.get('source', ''))
        if key not in existing_keys:
            existing.append(a)
            existing_keys.add(key)
    return existing


def merge_set_fields(existing: Dict, new_stock: Dict) -> None:
    """
    合并 set 字段（concepts, products, core_business, industry_position, chain, partners）。
    直接在 existing 字典上修改。
    """
    for field in SET_FIELDS:
        if new_stock.get(field):
            existing_set = set(existing.get(field) or [])
            if isinstance(new_stock[field], str):
                existing_set.add(new_stock[field])
            else:
                existing_set.update(new_stock[field])
            existing[field] = sorted(existing_set)


def load_master(project_root: Path) -> Dict:
    """加载主数据文件 data/stocks/stocks_master.json"""
    path = project_root / 'data' / 'stocks' / 'stocks_master.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_master(project_root: Path, master: Dict) -> Path:
    """保存主数据文件。同时自动生成 .json.gz 压缩版供 Vercel 读取。返回文件路径。"""
    path = project_root / 'data' / 'stocks' / 'stocks_master.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    # 自动生成 gz 压缩版
    _save_gz(path)
    return path


def _save_gz(json_path: Path) -> Path:
    """生成 json.gz 压缩版（Vercel 部署优先读取 .gz 节省空间）。"""
    import gzip
    gz_path = json_path.with_suffix(json_path.suffix + '.gz')
    with open(json_path, 'r', encoding='utf-8') as f_in:
        with gzip.open(gz_path, 'wt', encoding='utf-8', compresslevel=9) as f_out:
            f_out.write(f_in.read())
    return gz_path


def load_or_create_shard(project_root: Path, date_str: str) -> Dict:
    """加载或创建日期分片文件 data/stocks/YYYY-MM-DD.json"""
    path = project_root / 'data' / 'stocks' / f'{date_str}.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'date': date_str, 'update_count': 0, 'stocks': {}}


def save_shard(project_root: Path, date_str: str, shard: Dict) -> Path:
    """保存日期分片文件。返回文件路径。"""
    path = project_root / 'data' / 'stocks' / f'{date_str}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(shard, f, ensure_ascii=False, indent=2)
    return path


def is_duplicate_article(articles: List[Dict], new_article: Dict) -> bool:
    """检查新文章是否已在列表中存在（按 source 去重）"""
    new_source = new_article.get('source', '')
    return any(a.get('source', '') == new_source for a in articles) if new_source else False
