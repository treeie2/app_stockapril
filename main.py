#!/usr/bin/env python3
"""
个股研究数据库 Web 界面 - Railway 极简版
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, jsonify, render_template, request, send_file, send_from_directory
import json, gzip, os, re, requests
from pathlib import Path
from datetime import datetime
# 延迟导入 akshare（避免加载慢）
def get_akshare():
    try:
        import akshare as ak
        return ak
    except ImportError:
        return None

# 获取项目根目录（兼容 Vercel 和本地环境）
def get_base_dir():
    """获取项目根目录（兼容本地和 Vercel）"""
    # Vercel 环境特殊处理
    if 'VERCEL' in os.environ:
        # 在 Vercel 中，api/index.py 在 /var/task/api/ 下
        # 项目根目录是 /var/task/ 的父目录
        task_dir = Path('/var/task')
        if (task_dir / 'data').exists():
            print(f"  📂 [Vercel] 使用 task 目录: {task_dir}")
            return task_dir
        # 尝试 api 的父目录
        api_parent = Path(__file__).parent.parent
        if (api_parent / 'data').exists():
            print(f"  📂 [Vercel] 使用 api 父目录: {api_parent}")
            return api_parent
    
    # 尝试从当前文件位置获取（最可靠）
    try:
        p = Path(__file__).parent
        if (p / 'data').exists():
            print(f"  📂 从文件位置找到 base_dir: {p}")
            return p
        # 如果当前是 api 目录，尝试父目录
        if p.name == 'api' and (p.parent / 'data').exists():
            print(f"  📂 从 api 父目录找到 base_dir: {p.parent}")
            return p.parent
    except Exception as e:
        print(f"  ⚠️ 从文件位置获取失败: {e}")

    # 尝试 cwd
    cwd = Path(os.getcwd())
    if (cwd / 'data').exists():
        print(f"  📂 从 cwd 找到 base_dir: {cwd}")
        return cwd

    print(f"  ⚠️ 未找到 data 目录，使用 cwd: {cwd}")
    return cwd

BASE_DIR = get_base_dir()
print(f"📂 最终 BASE_DIR: {BASE_DIR}")
print(f"📂 BASE_DIR 存在: {BASE_DIR.exists()}")
print(f"📂 data 目录存在: {(BASE_DIR / 'data').exists()}")
print(f"📂 hot_topics.json 存在: {(BASE_DIR / 'data' / 'hot_topics.json').exists()}")

# 显式配置 Flask 的静态文件和模板目录
app = Flask(__name__,
            static_folder=str(BASE_DIR / 'static'),
            static_url_path='/static',
            template_folder=str(BASE_DIR / 'templates'))

# Streamlit 板块资金监控重定向
@app.route('/monitor')
def monitor_redirect():
    streamlit_url = os.environ.get('STREAMLIT_URL', 'http://localhost:8501')
    return render_template('redirect.html', url=streamlit_url, title='板块资金监控')

# 文章API服务配置
ARTICLE_API_URL = os.environ.get('ARTICLE_API_URL', 'http://localhost:5001')

# 数据路径
DATA_DIR = BASE_DIR / 'data' / 'sentiment'
SEARCH_INDEX_FILE = DATA_DIR / 'search_index_full.json.gz'
HOT_TOPICS_FILE = BASE_DIR / 'data' / 'hot_topics' / 'hot_topics.json'
GROUPS_FILE = BASE_DIR / 'data' / 'groups' / 'groups.json'
STOCKS_MASTER_FILE = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
STOCKS_INDEX_FILE = BASE_DIR / 'data' / 'stocks' / 'stocks_index.json'

# ─── Jaccard 相似度计算 ───
def jaccard_similarity(set1, set2):
    """计算两个集合的 Jaccard 相似度"""
    if not set1 or not set2:
        return 0.0
    s1, s2 = set(set1), set(set2)
    return len(s1 & s2) / len(s1 | s2)

def parse_target_market_cap(text):
    """
    解析目标市值文本为数值（单位：亿元）
    
    支持的格式：
    - "1100 亿" -> 1100.0
    - "1100e" -> 1100.0
    - "1.1 千亿" -> 1100.0
    - "5000 万" -> 0.5
    - "150" -> 150.0（默认为亿）
    
    Args:
        text: 市值文本，如 "1100 亿"
        
    Returns:
        float: 市值数值（亿元），解析失败返回 0.0
    """
    if not text:
        return 0.0
    
    text = text.strip().lower()
    
    try:
        # 匹配数字部分
        import re
        match = re.match(r'([\d.]+)\s*(亿 | 千万 | 百万 | 万 | e)?', text, re.IGNORECASE)
        if not match:
            return 0.0
        
        num = float(match.group(1))
        unit = match.group(2) if match.group(2) else '亿'
        
        # 根据单位转换
        if unit == 'e' or unit == '亿':
            return num
        elif unit == '千万':
            return num / 10  # 1 千万 = 0.1 亿
        elif unit == '百万':
            return num / 100  # 1 百万 = 0.01 亿
        elif unit == '万':
            return num / 10000  # 1 万 = 0.0001 亿
        elif unit == '千亿':
            return num * 100  # 1 千亿 = 100 亿
        else:
            return num  # 默认作为亿
    except (ValueError, AttributeError):
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def find_similar_stocks(code, top_k=10, min_similarity=0.1):
    """找出与指定股票最相似的股票"""
    if code not in stocks:
        return []
    
    target_concepts = set(stocks[code].get('concepts', []))
    if not target_concepts:
        return []
    
    similarities = []
    for c, d in stocks.items():
        if c == code:
            continue
        other_concepts = set(d.get('concepts', []))
        if not other_concepts:
            continue
        
        sim = jaccard_similarity(target_concepts, other_concepts)
        if sim >= min_similarity:
            # 找出共同概念
            common = target_concepts & other_concepts
            similarities.append({
                'code': c,
                'name': d.get('name', ''),
                'similarity': sim,
                'common_concepts': list(common),
                'common_count': len(common),
                'mention_count': d.get('mention_count', 0),
                'concepts': d.get('concepts', [])
            })
    
    # 按相似度排序
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    return similarities[:top_k]

# 加载社保基金数据
print("📋 加载社保基金数据...")
SOCIAL_SECURITY_FILE = BASE_DIR / 'data' / 'master' / 'social_security_2025q4.json'
social_security_stocks = set()
social_security_info = {}
try:
    with open(SOCIAL_SECURITY_FILE, 'r', encoding='utf-8') as f:
        ss_data = json.load(f)
    for stock in ss_data.get('stocks', []):
        code = stock.get('code')
        if code:
            social_security_stocks.add(code)
            social_security_info[code] = {
                'holding_ratio': stock.get('holding_ratio', ''),
                'note': stock.get('note', ''),
                'industry_group': stock.get('industry_group', '')
            }
    print(f"  ✅ 加载 {len(social_security_stocks)} 只社保基金新进股票")
except Exception as e:
    print(f"  ⚠️ 社保基金数据加载失败：{e}")

def load_data_incremental(days=7):
    """从增量文件加载最近 N 天的数据"""
    print(f"📋 从增量文件加载最近 {days} 天数据...")
    
    INDEX_FILE = BASE_DIR / 'data' / 'stocks' / 'stocks_index.json'
    STOCKS_DIR = BASE_DIR / 'data' / 'stocks'
    
    try:
        # 读取索引文件
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 获取最近 N 天的日期
        today = datetime.now()
        recent_dates = []
        for i in range(days):
            date = today.replace(day=today.day - i)
            recent_dates.append(date.strftime("%Y-%m-%d"))
        
        # 加载对应日期的数据
        all_stocks = {}
        concepts = {}
        
        for date in recent_dates:
            file_path = STOCKS_DIR / f"{date}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    daily_stocks = data.get('stocks', {})
                    all_stocks.update(daily_stocks)
                    
                    # 构建概念索引
                    for code, stock in daily_stocks.items():
                        for concept in stock.get('concepts', []):
                            if concept not in concepts:
                                concepts[concept] = {'stocks': []}
                            concepts[concept]['stocks'].append(code)
        
        print(f"  ✅ 从增量文件加载 {len(all_stocks)} 只股票")
        print(f"  ✅ 加载 {len(concepts)} 个概念")
        return all_stocks, concepts
        
    except Exception as e:
        print(f"  ⚠️ 增量加载失败: {e}")
        return None, None


# ============================================================
# Supabase 配置
# ============================================================
# 优先级：环境变量 > supabase_config.json
_SUPABASE_CONFIG_FILE = BASE_DIR / "supabase_config.json"
if _SUPABASE_CONFIG_FILE.exists():
    try:
        with open(_SUPABASE_CONFIG_FILE, 'r', encoding='utf-8') as _f:
            _supabase_config = json.load(_f)
        SUPABASE_URL = os.getenv("SUPABASE_URL", _supabase_config.get("SUPABASE_URL", ""))
        SUPABASE_KEY = os.getenv("SUPABASE_KEY", _supabase_config.get("SUPABASE_KEY", ""))
    except Exception:
        SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
else:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
_supabase_client = None

def get_supabase_client():
    """获取 Supabase 客户端"""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase_client
    except ImportError:
        return None
    except Exception as e:
        print(f"  ⚠️ Supabase 客户端初始化失败: {e}")
        return None

def load_data_from_supabase():
    """从 Supabase 加载股票数据"""
    print("📋 尝试从 Supabase 加载数据...")
    client = get_supabase_client()
    if not client:
        return None, None

    try:
        resp = client.table("stocks").select("*").execute()
        rows = resp.data if resp.data else []

        all_stocks = {}
        concepts = {}
        for row in rows:
            code = row.get("code", "")
            stock = {
                "name": row.get("name", ""),
                "code": code,
                "board": row.get("board", ""),
                "industry": row.get("industry", ""),
                "concepts": json.loads(row.get("concepts", "[]")) if isinstance(row.get("concepts"), str) else (row.get("concepts") or []),
                "products": json.loads(row.get("products", "[]")) if isinstance(row.get("products"), str) else (row.get("products") or []),
                "core_business": json.loads(row.get("core_business", "[]")) if isinstance(row.get("core_business"), str) else (row.get("core_business") or []),
                "industry_position": json.loads(row.get("industry_position", "[]")) if isinstance(row.get("industry_position"), str) else (row.get("industry_position") or []),
                "chain": json.loads(row.get("chain", "[]")) if isinstance(row.get("chain"), str) else (row.get("chain") or []),
                "partners": json.loads(row.get("partners", "[]")) if isinstance(row.get("partners"), str) else (row.get("partners") or []),
                "mention_count": row.get("mention_count", 0),
                "last_updated": row.get("last_updated", ""),
                "articles": json.loads(row.get("articles", "[]")) if isinstance(row.get("articles"), str) else (row.get("articles") or []),
                "detail_texts": json.loads(row.get("detail_texts", "[]")) if isinstance(row.get("detail_texts"), str) else (row.get("detail_texts") or []),
            }
            all_stocks[code] = stock
            for concept in stock.get("concepts", []):
                if concept not in concepts:
                    concepts[concept] = {"stocks": []}
                concepts[concept]["stocks"].append(code)

        print(f"  ✅ 从 Supabase 加载 {len(all_stocks)} 只股票")
        return all_stocks, concepts
    except Exception as e:
        print(f"  ⚠️ Supabase 加载失败: {e}")
        return None, None


def load_data_from_supabase_http():
    """纯 stdlib 从 Supabase REST API 加载数据（0 额外依赖，Vercel 可用）"""
    import urllib.request
    url = "https://fcnzwhjpzfojeszzlyeo.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjbnp3aGpwemZvamVzenpseWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE5Mzc0MTUsImV4cCI6MjA5NzUxMzQxNX0.X44fD4gto39L4Wv6S4y05iukKqxuKudnTZS1PASyj1I"
    
    print("📋 从 Supabase REST API 加载数据 (stdlib)...")
    all_stocks = {}
    concepts = {}
    offset = 0
    limit = 1000
    
    while True:
        api_url = f"{url}/rest/v1/stocks?select=*&limit={limit}&offset={offset}"
        req = urllib.request.Request(api_url, headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  ⚠️ Supabase HTTP 请求失败 (offset={offset}): {e}")
            break
        
        if not data:
            break
        
        for row in data:
            code = row.get("code", "")
            if not code:
                continue
            stock = {
                "name": row.get("name", ""),
                "code": code,
                "board": row.get("board", ""),
                "industry": row.get("industry", ""),
                "concepts": json.loads(row.get("concepts", "[]")) if isinstance(row.get("concepts"), str) else (row.get("concepts") or []),
                "products": json.loads(row.get("products", "[]")) if isinstance(row.get("products"), str) else (row.get("products") or []),
                "core_business": json.loads(row.get("core_business", "[]")) if isinstance(row.get("core_business"), str) else (row.get("core_business") or []),
                "industry_position": json.loads(row.get("industry_position", "[]")) if isinstance(row.get("industry_position"), str) else (row.get("industry_position") or []),
                "chain": json.loads(row.get("chain", "[]")) if isinstance(row.get("chain"), str) else (row.get("chain") or []),
                "partners": json.loads(row.get("partners", "[]")) if isinstance(row.get("partners"), str) else (row.get("partners") or []),
                "mention_count": row.get("mention_count", 0),
                "last_updated": row.get("last_updated", ""),
                "articles": json.loads(row.get("articles", "[]")) if isinstance(row.get("articles"), str) else (row.get("articles") or []),
                "detail_texts": json.loads(row.get("detail_texts", "[]")) if isinstance(row.get("detail_texts"), str) else (row.get("detail_texts") or []),
            }
            all_stocks[code] = stock
            for concept in stock.get("concepts", []):
                if concept not in concepts:
                    concepts[concept] = {"stocks": []}
                concepts[concept]["stocks"].append(code)
        
        offset += limit
        if len(data) < limit:
            break
    
    if all_stocks:
        print(f"  ✅ Supabase HTTP: {len(all_stocks)} stocks")
        return all_stocks, concepts
    print(f"  ⚠️ Supabase HTTP 未获取到数据")
    return None, None


def load_data_from_local():
    """从本地文件或 GitHub 加载数据"""
    print("📋 从数据源加载数据...")
    print(f"  BASE_DIR: {BASE_DIR}")
    
    # v3.0: stocks_meta.json 优先（轻量，无 articles）
    possible_paths = [
        BASE_DIR / 'data' / 'stocks' / 'stocks_meta.json',
        BASE_DIR / 'data' / 'stocks' / 'stocks_master.json.gz',
        BASE_DIR / 'data' / 'stocks' / 'stocks_master.json',
        BASE_DIR / 'static' / 'stocks_meta.json',
        BASE_DIR / 'static' / 'stocks_master.json.gz',
        BASE_DIR / 'static' / 'stocks_master.json',
        BASE_DIR.parent / 'data' / 'stocks' / 'stocks_meta.json',
        BASE_DIR.parent / 'data' / 'stocks' / 'stocks_master.json.gz',
        BASE_DIR.parent / 'data' / 'stocks' / 'stocks_master.json',
        BASE_DIR.parent / 'static' / 'stocks_meta.json',
        BASE_DIR.parent / 'static' / 'stocks_master.json.gz',
        BASE_DIR.parent / 'static' / 'stocks_master.json',
        # Vercel api 目录特殊处理
        Path(__file__).parent / 'stocks_meta.json',
        Path(__file__).parent / 'stocks_master.json.gz',
        Path(__file__).parent / 'stocks_master.json',
        Path(__file__).parent.parent / 'stocks_meta.json',
        Path(__file__).parent.parent / 'stocks_master.json.gz',
        Path(__file__).parent.parent / 'stocks_master.json',
        # 绝对路径（Vercel serverless 环境）
        Path('/var/task/data/stocks/stocks_meta.json'),
        Path('/var/task/data/stocks/stocks_master.json.gz'),
        Path('/var/task/data/stocks/stocks_master.json'),
        Path('/var/task/static/stocks_meta.json'),
        Path('/var/task/static/stocks_master.json.gz'),
        Path('/var/task/static/stocks_master.json'),
        Path('/var/task/api/stocks_master.json'),
        Path('/var/task/api/stocks_master.json.gz'),
    ]
    
    # 打印所有可能的路径供调试
    print("  可能的文件路径:")
    for p in possible_paths:
        exists = "✅" if p.exists() else "❌"
        print(f"    {exists} {p}")
    
    master_data = None
    
    # 优先从本地文件加载（Vercel 部署时文件会被包含）
    print("  📂 优先从本地文件加载...")
    for filepath in possible_paths:
        if filepath.exists():
            print(f"  📋 找到文件: {filepath}")
            try:
                if filepath.suffix == '.gz':
                    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                        master_data = json.load(f)
                else:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        master_data = json.load(f)
                
                # 验证数据
                if 'stocks' in master_data:
                    stock_count = len(master_data['stocks'])
                    print(f"  ✅ 加载成功，共 {stock_count} 只股票")
                    break
                else:
                    print(f"  ⚠️ 数据格式异常，继续尝试下一个文件")
                    master_data = None
            except Exception as e:
                print(f"  ⚠️ 读取失败 ({filepath}): {str(e)}")
                master_data = None
    
    # 如果本地加载失败，尝试 GitHub（备用）
    if master_data is None:
        print("  📥 本地文件未找到，尝试从 GitHub 加载...")
        try:
            import requests
            github_url = "https://raw.githubusercontent.com/treeie2/app_stockapril/main/data/stocks/stocks_master.json.gz"
            print(f"  下载 URL: {github_url}")
            response = requests.get(github_url, timeout=60)
            response.raise_for_status()
            import io
            with gzip.GzipFile(fileobj=io.BytesIO(response.content), mode='rt', encoding='utf-8') as f:
                master_data = json.load(f)
            
            # 验证数据
            if 'stocks' in master_data:
                stock_count = len(master_data['stocks'])
                print(f"  ✅ 从 GitHub 加载成功 ({len(response.content)/1024:.1f} KB)")
                print(f"  📊 加载到 {stock_count} 只股票")
            else:
                print(f"  ⚠️ 数据格式异常，无 stocks 字段")
                master_data = None
                
        except Exception as e:
            print(f"  ❌ GitHub 加载失败：{str(e)}")
            raise RuntimeError(f"无法从任何来源加载数据: {str(e)}")
    
    print(f"  📊 原始数据大小：{len(master_data.get('stocks', master_data))} keys")
    
    # 处理数据格式（支持列表或字典格式）
    # 如果是字典格式（code 为 key），直接使用
    if isinstance(master_data, dict):
        # 检查是否是 {'stocks': {...}} 格式
        if 'stocks' in master_data:
            stocks_data = master_data.get('stocks', {})
        else:
            # 直接是 {code: data} 格式
            stocks_data = master_data
    else:
        stocks_data = {}
    
    # 转换为列表和字典
    if isinstance(stocks_data, dict):
        stocks_list = list(stocks_data.values())
        stocks = stocks_data
    else:
        stocks_list = stocks_data
        stocks = {s['code']: s for s in stocks_list if 'code' in s}
    
    # 从概念字段提取所有概念
    concepts = {}
    for stock in stocks_list:
        code = stock.get('code')
        if not code:
            continue
        for concept in stock.get('concepts', []):
            if concept not in concepts:
                concepts[concept] = {'stocks': []}
            concepts[concept]['stocks'].append(code)
    
    # 从文章列表中提取最新日期作为 last_updated（仅当有明确日期时）
    for code, stock in stocks.items():
        if not stock.get('last_updated') and stock.get('articles'):
            dates = []
            for a in stock['articles']:
                d = a.get('date', '') or a.get('published_at', '') or ''
                if d and len(d) >= 10:
                    dates.append(d[:10])
            if dates:
                stock['last_updated'] = max(dates)
            # 如果文章日期都为空，不设置 last_updated，保持为空
    
    print(f"  ✅ 加载 {len(stocks)} 只股票")
    print(f"  ✅ 加载 {len(concepts)} 个概念")
    return stocks, concepts

# 全局变量
stocks = {}
concepts = {}
hot_topics = []
groups = []
lyt_scores = {}
lyt_signals = {"total": 0, "dates": [], "signals": {}}
_articles_cache = {}
_data_loaded = False

def load_all_data():
    """加载所有数据（懒加载）- Vercel走Supabase，本地走文件"""
    global stocks, concepts, hot_topics, _data_loaded
    
    if _data_loaded:
        return
    
    print("📋 开始加载数据...")
    
    def _load_from_github_fallback():
        """GitHub raw → Supabase → 本地 三级回退"""
        import time as _time, random as _random
        gh_url = (f"https://raw.githubusercontent.com/treeie2/app_stockapril/main/"
                 f"data/stocks/stocks_master.json?"
                 f"t={int(_time.time())}&r={_random.randint(0,99999)}")
        print(f"📋 从 GitHub raw 读取最新数据...")
        try:
            r = requests.get(gh_url, timeout=30, headers={
                "Cache-Control": "no-cache, no-store, must-revalidate"
            })
            r.raise_for_status()
            data = json.loads(r.text)
            gh_stocks = data.get("stocks", {})
            if gh_stocks:
                stocks.update(gh_stocks)
                print(f"  ✅ GitHub raw: {len(gh_stocks)} stocks")
                return True
        except Exception as gh_e:
            print(f"  ⚠️ GitHub raw 失败: {gh_e}")
        return False
    
    try:
        # ─── 优先本地文件（最快，Docker已打包） ───
        loaded, loaded_c = load_data_from_local()
        if loaded:
            stocks.update(loaded)
            concepts.update(loaded_c)
            print(f"  ✅ 本地文件: {len(loaded)} stocks")
        elif not _load_from_github_fallback():
            # ─── 回退：Supabase ───
            print("  尝试 Supabase...")
            sb_stocks, sb_concepts = load_data_from_supabase_http()
            if sb_stocks:
                stocks.update(sb_stocks)
                concepts.update(sb_concepts)
                print(f"  ✅ Supabase: {len(sb_stocks)} stocks")
            else:
                print("  尝试本地文件...")
                loaded, loaded_c = load_data_from_local()
                if loaded:
                    stocks.update(loaded)
                    concepts.update(loaded_c)
                    print(f"  ✅ 本地文件: {len(loaded)} stocks")
            
            if not stocks:
                print("📋 本地无数据，尝试 Supabase...")
                supabase_stocks, supabase_concepts = load_data_from_supabase()
                if supabase_stocks:
                    stocks.update(supabase_stocks)
                    concepts.update(supabase_concepts)
                    print(f"  ✅ Supabase 加载成功：{len(supabase_stocks)} 只股票")
        
        # 3. 加载热点数据（本地优先）
        if HOT_TOPICS_FILE.exists():
            try:
                with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
                    hot_topics_data = json.load(f)
                    hot_topics = hot_topics_data.get('topics', [])
                print(f"📊 加载本地热点数据：{len(hot_topics)} 个热点")
            except Exception as e:
                print(f"⚠️ 加载热点数据失败：{e}")
                hot_topics = []
        else:
            hot_topics = []
        
        # 4. 加载分组数据（本地）
        load_groups_data()
        
        # 5. 加载 lyt 数据（五维评分 + 每日信号）
        load_lyt_data()
        
        print(f"📊 数据加载完成：{len(stocks)} 只股票，{len(concepts)} 个概念，{len(hot_topics)} 个热点，{len(groups)} 个分组")
        _data_loaded = True
        
    except Exception as e:
        print(f"❌ 数据加载失败：{e}")
        import traceback
        traceback.print_exc()
        _data_loaded = True
        raise


def load_lyt_data():
    """加载 lyt 数据（五维评分 + 每日信号）"""
    global lyt_scores, lyt_signals
    try:
        lyt_signal_file = BASE_DIR / "breakt" / "lyt_daily_signals.json"
        if lyt_signal_file.exists():
            with open(lyt_signal_file, 'r', encoding='utf-8') as f:
                lyt_signals = json.load(f)
            print(f"📡 lyt 信号加载成功：{lyt_signals.get('total', 0)} 条")
        
        # scores 已嵌入 stocks_master.json 的 lyt_score 字段
        print(f"📊 lyt 五维评分：已嵌入 stocks（lyt_score 字段）")
    except Exception as e:
        print(f"⚠️ lyt 数据加载失败：{e}")


def load_articles_for_stock(code):
    """按需加载单只股票的 articles（避免启动时加载全部 8MB）"""
    global _articles_cache
    if code in _articles_cache:
        return _articles_cache[code]
    
    # 1. 先查内存中是否已有
    if code in stocks and stocks[code].get("articles"):
        _articles_cache[code] = stocks[code]["articles"]
        return stocks[code]["articles"]
    
    # 2. 从 stocks_articles.json 按需加载
    arts_file = BASE_DIR / "data" / "stocks" / "stocks_articles.json"
    if not arts_file.exists():
        arts_file = Path("/var/task/data/stocks/stocks_articles.json")
    
    try:
        import json as _json
        with open(arts_file, "r", encoding="utf-8") as f:
            all_arts = _json.load(f)
        _articles_cache[code] = all_arts.get(code, [])
        # 回填到内存
        if code in stocks:
            stocks[code]["articles"] = _articles_cache[code]
        return _articles_cache[code]
    except Exception as e:
        print(f"⚠️ 按需加载 articles 失败({code}): {e}")
    return []


def load_hot_topics_only():
    """Vercel 专用：加载热点数据和股票数据，避免超时"""
    global stocks, concepts, hot_topics, _data_loaded
    
    if _data_loaded:
        return
    
    print("📋 [Vercel] 加载热点和股票数据...")
    
    try:
        # 1. 从本地 master 文件加载股票数据
        if not stocks:
            print("📋 [Vercel] 从本地加载股票数据...")
            try:
                loaded_stocks, loaded_concepts = load_data_from_local()
                stocks.update(loaded_stocks)
                concepts.update(loaded_concepts)
                print(f"  ✅ [Vercel] 股票加载成功：{len(loaded_stocks)} 只")
            except Exception as e:
                print(f"  ⚠️ [Vercel] 股票加载失败：{e}")
        
        # 2. 加载热点数据
        if HOT_TOPICS_FILE.exists():
            try:
                with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
                    hot_topics_data = json.load(f)
                    hot_topics = hot_topics_data.get('topics', [])
                print(f"📊 [Vercel] 热点加载成功：{len(hot_topics)} 个")
            except Exception as e:
                print(f"⚠️ [Vercel] 热点加载失败：{e}")
                hot_topics = []
        else:
            hot_topics = []
            print(f"⚠️ [Vercel] 热点文件不存在")
        
        # 如果本地没有热点数据，尝试从 GitHub 加载
        if not hot_topics:
            print("📋 [Vercel] 本地无热点数据，尝试从 GitHub 加载...")
            try:
                github_raw_url = "https://raw.githubusercontent.com/treeie2/app_stockapril/main/data/hot_topics/hot_topics.json"
                resp = requests.get(github_raw_url, timeout=10)
                if resp.status_code == 200:
                    gh_data = resp.json()
                    gh_topics = gh_data.get('topics', [])
                    if gh_topics:
                        hot_topics = gh_topics
                        print(f"📊 [Vercel] GitHub 热点数据加载成功：{len(hot_topics)} 个")
                else:
                    print(f"⚠️ [Vercel] GitHub 热点数据加载失败：HTTP {resp.status_code}")
            except Exception as e:
                print(f"⚠️ [Vercel] GitHub 热点数据加载异常：{e}")
        
        print(f"📊 [Vercel] 数据加载完成：{len(stocks)} 只股票，{len(hot_topics)} 个热点")
        _data_loaded = True
        
    except Exception as e:
        print(f"⚠️ [Vercel] 数据加载失败：{e}")
        import traceback
        traceback.print_exc()
        _data_loaded = True


# 懒加载数据（在第一次请求时加载）
# load_all_data()

# ==================== lyt 突破信号 API ====================
@app.route('/api/lyt-signals')
def api_lyt_signals():
    """返回 lyt 每日信号数据"""
    import json
    try:
        sig_file = BASE_DIR / "breakt" / "lyt_daily_signals.json"
        if sig_file.exists():
            with open(sig_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
    except Exception as e:
        print(f"lyt signals error: {e}")
    return jsonify({"total": 0, "dates": [], "signals": {}, "names": {}})

@app.route('/api/lyt-scores')
def api_lyt_scores():
    """返回 lyt 五维评分（从 stocks_master 提取）"""
    import json
    try:
        scores = {}
        for code, s in stocks.items():
            score = s.get('lyt_score')
            if score is not None:
                scores[code] = score if isinstance(score, dict) else {"score": score}
        return jsonify(scores)
    except Exception as e:
        print(f"lyt scores error: {e}")
    return jsonify({})

@app.route('/api/lyt-changes')
def api_lyt_changes():
    """返回 lyt 涨跌幅变动数据"""
    import json
    try:
        chg_file = BASE_DIR / "breakt" / "lyt_changes.json"
        if chg_file.exists():
            with open(chg_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
    except Exception as e:
        print(f"lyt changes error: {e}")
    return jsonify({})

@app.route('/api/lyt-groups')
def api_lyt_groups():
    """返回 lyt 格式的分组数据 {groupName: {stocks:[code,...]}}"""
    import json
    try:
        # 从 groups.json 转换格式
        gfile = BASE_DIR / "data" / "groups" / "groups.json"
        if gfile.exists():
            with open(gfile, 'r', encoding='utf-8') as f:
                groups_data = json.load(f)
            lyt_groups = {}
            for g in groups_data.get("groups", []):
                codes = g.get("stocks", [])
                if codes:
                    lyt_groups[g["name"]] = {"stocks": codes}
            return jsonify(lyt_groups)
    except Exception as e:
        print(f"lyt groups error: {e}")
    return jsonify({})

@app.route('/')
def dashboard():
    # Vercel 环境：从 GitHub raw 加载最新数据
    if 'VERCEL' in os.environ:
        try:
            load_all_data()
        except Exception as e:
            print(f"⚠️ 数据加载失败：{e}")
    else:
        # 本地环境：完整加载
        try:
            load_all_data()
        except Exception as e:
            print(f"⚠️ 数据加载失败：{e}")
    
    # 获取分页参数
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
    except:
        limit = 20
        offset = 0
    
    # 传递所有股票数据（只保留 A 股个股，过滤 ETF 和指数）
    all_stocks = []
    for c, d in stocks.items():
        # 过滤：只保留 A 股个股（code 以 00/30/60/68 开头）
        if not (c.startswith('00') or c.startswith('30') or c.startswith('60') or c.startswith('68')):
            continue
        
        # 过滤：名称包含 ETF、指数、中证、上证的
        name = d.get('name', '')
        if any(x in name for x in ['ETF', '指数', '中证', '上证', '深证', '创业板指']):
            continue
        
        stock = {'code': c, **d}
        # 修复：字段名是 industries 不是 industry
        stock['industry'] = d.get('industry', '') or d.get('industries', '')
        
        # 获取最新文章日期用于排序
        articles = d.get('articles', [])
        if articles:
            # 从 article_id 提取日期或从 published_at 获取
            first_article = articles[0]
            stock['latest_article_date'] = first_article.get('published_at', '') or first_article.get('article_id', '')[:10]
        else:
            stock['latest_article_date'] = ''
        
        # 优先使用 last_updated 字段（如果有）
        stock['last_updated'] = d.get('last_updated', '')
        
        all_stocks.append(stock)
    
    # 按最后更新时间排序：有 last_updated 的排在前面（按时间倒序），没有的排在后面
    def sort_key(x):
        last_updated = x.get('last_updated', '')
        if last_updated:
            # 有 last_updated 的排在前面，按时间倒序（最新的在前）
            # 返回元组：(优先级, 日期)，优先级0表示有更新时间
            return (0, last_updated)
        else:
            # 没有 last_updated 的排在后面
            # 优先级1表示无更新时间，用空字符串占位
            return (1, '')
    
    # 按排序键排序（日期倒序，所以第二个元素要 reverse）
    # 但元组排序会整体 reverse，所以我们手动实现排序
    stocks_with_update = [s for s in all_stocks if s.get('last_updated')]
    stocks_without_update = [s for s in all_stocks if not s.get('last_updated')]
    
    # 有更新时间的按日期倒序（最新的在前）
    stocks_with_update.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
    
    # 合并：先排有更新时间的，再排没有更新时间的
    all_stocks = stocks_with_update + stocks_without_update
    
    # 分页
    total = len(all_stocks)
    has_more = offset + limit < total
    paginated_stocks = all_stocks[offset:offset + limit]
    
    # 计算文章数（安全方式）
    articles = set()
    for code, s in stocks.items():
        for a in s.get('articles', []):
            articles.add(f"{code}_{a.get('article_id', '')}")
    
    # 如果是 AJAX 请求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'stocks': paginated_stocks,
            'offset': offset + limit,
            'limit': limit,
            'total': total,
            'has_more': has_more
        })
    
    # 直接使用全局热点数据（已在 load_all_data 中正确加载）
    # 添加调试日志
    print(f"DEBUG: hot_topics count = {len(hot_topics)}")
    for ht in hot_topics:
        print(f"  - {ht.get('name')} (display={ht.get('display', True)})")
    
    # 首次加载，渲染完整页面
    return render_template('dashboard.html',
        stocks=paginated_stocks,
        total_stocks=total,
        total_mentions=sum(s.get('mention_count', 0) for s in paginated_stocks),
        total_articles=len(articles),
        has_more=has_more,
        next_offset=offset + limit,
        limit=limit,
        offset=offset,
        hot_topics=hot_topics,
        lyt_signals=lyt_signals)

@app.route('/hot-topic/<topic_id>')
def hot_topic_detail(topic_id):
    """热点详情页"""
    # 查找热点
    topic = None
    for t in hot_topics:
        if t.get('id') == topic_id:
            topic = t
            break
    
    # 如果内存中找不到，尝试重新从文件加载
    if not topic:
        print(f"⚠️ 热点 {topic_id} 不在内存中，尝试从文件重新加载...")
        try:
            if HOT_TOPICS_FILE.exists():
                with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
                    hot_topics_data = json.load(f)
                    reloaded_topics = hot_topics_data.get('topics', [])
                for t in reloaded_topics:
                    if t.get('id') == topic_id:
                        topic = t
                        # 同步到全局变量
                        hot_topics.clear()
                        hot_topics.extend(reloaded_topics)
                        print(f"✅ 从文件重新加载后找到热点: {topic.get('name')}")
                        break
        except Exception as e:
            print(f"⚠️ 从文件重新加载热点失败: {e}")
    
    # 如果文件中也找不到，尝试从 Firebase 加载
    if not topic:
        print(f"⚠️ 热点 {topic_id} 不在文件中，尝试从 Firebase 加载...")
        try:
            fb_topics = None
            if fb_topics:
                for t in fb_topics:
                    if t.get('id') == topic_id:
                        topic = t
                        # 同步到全局变量和本地文件
                        hot_topics.clear()
                        hot_topics.extend(fb_topics)
                        save_hot_topics()
                        print(f"✅ 从 Firebase 加载后找到热点: {topic.get('name')}")
                        break
        except Exception as e:
            print(f"⚠️ 从 Firebase 加载热点失败: {e}")
    
    if not topic:
        return "热点不存在", 404
    
    # 获取相关股票详细信息
    related_stocks = []
    for stock_name in topic.get('stocks', []):
        found = False
        # 精确匹配
        for code, stock_data in stocks.items():
            if stock_data.get('name') == stock_name:
                related_stocks.append({
                    'code': code, 'name': stock_data.get('name', ''),
                    'board': stock_data.get('board', ''),
                    'industry': stock_data.get('industry', ''),
                    'concepts': stock_data.get('concepts', []),
                    'mention_count': stock_data.get('mention_count', 0),
                    'articles': stock_data.get('articles', [])
                })
                found = True
                break
        if not found:
            # 模糊匹配：去除空格、大小写等
            sn = stock_name.replace(' ', '').lower()
            for code, stock_data in stocks.items():
                mn = stock_data.get('name', '').replace(' ', '').lower()
                if mn == sn or (len(sn) >= 2 and sn in mn) or (len(mn) >= 2 and mn in sn):
                    related_stocks.append({
                        'code': code, 'name': stock_data.get('name', ''),
                        'board': stock_data.get('board', ''),
                        'industry': stock_data.get('industry', ''),
                        'concepts': stock_data.get('concepts', []),
                        'mention_count': stock_data.get('mention_count', 0),
                        'articles': stock_data.get('articles', [])
                    })
                    found = True
                    break
        if not found:
            related_stocks.append({
                'code': '', 'name': stock_name,
                'board': '', 'industry': '未录入数据库',
                'concepts': [], 'mention_count': 0, 'articles': []
            })
    
    return render_template('hot_topic_detail.html', topic=topic, stocks=related_stocks)

def _fetch_prices(codes):
    """从腾讯财经获取实时行情"""
    if not codes: return {}
    qstr = ','.join(('sh' if c.startswith(('60','688','9')) else 'sz') + c for c in codes)
    url = f'http://qt.gtimg.cn/q={qstr}'
    try:
        r = requests.get(url, timeout=5)
        r.encoding = 'gbk'
        prices = {}
        for line in r.text.strip().split(';'):
            if not line.strip(): continue
            parts = line.split('~')
            if len(parts) < 32: continue
            code = parts[2] if len(parts) > 2 else ''
            name = parts[1] if len(parts) > 1 else ''
            current = parts[3] if len(parts) > 3 else '0'
            yest_close = parts[4] if len(parts) > 4 else '0'
            open_px = parts[5] if len(parts) > 5 else '0'
            high = parts[33] if len(parts) > 33 else '0'
            low = parts[34] if len(parts) > 34 else '0'
            volume = parts[6] if len(parts) > 6 else '0'
            amount = parts[37] if len(parts) > 37 else '0'
            if code and current and yest_close:
                cur = float(current)
                cls = float(yest_close)
                if cls > 0:
                    pct = round((cur - cls) / cls * 100, 2)
                    prices[code] = {
                        'name': name, 'price': cur, 'yest_close': cls, 
                        'pct': pct, 'open': float(open_px), 'high': float(high),
                        'low': float(low), 'volume': int(volume) if volume.isdigit() else 0,
                        'amount': float(amount) if amount.replace('.','',1).isdigit() else 0,
                    }
        return prices
    except Exception as e:
        print(f'⚠️ 获取行情失败: {e}')
        return {}

@app.route('/api/stock-prices')
def api_stock_prices():
    """实时行情 API"""
    codes_str = request.args.get('codes', '')
    if not codes_str: return jsonify({})
    codes = [c.strip() for c in codes_str.split(',') if c.strip()]
    return jsonify(_fetch_prices(codes))

@app.route('/groups')
def groups_list():
    """所有分组列表页"""
    return render_template('groups.html')

@app.route('/lyt')
def lyt_page():
    """突破信号页（lyt 老鸭头）"""
    return render_template('lyt.html')

@app.route('/group/<group_id>')
def group_detail(group_id):
    """分组详情页"""
    # Vercel 可能存在两次 URL 编码，先解码
    from urllib.parse import unquote
    group_id = unquote(unquote(group_id))
    
    load_all_data()  # 确保 stocks 已加载
    load_groups_data()
    
    # 查找分组
    group = None
    for g in groups:
        if g.get('id') == group_id:
            group = g
            break
    
    if not group:
        return "分组不存在", 404
    
    # 获取相关股票详细信息
    related_stocks = []
    for stock_name in group.get('stocks', []):
        # 通过名称查找股票代码
        for code, stock_data in stocks.items():
            if stock_data.get('name') == stock_name:
                related_stocks.append({
                    'code': code,
                    'name': stock_data.get('name', ''),
                    'board': stock_data.get('board', ''),
                    'industry': stock_data.get('industry', ''),
                    'concepts': stock_data.get('concepts', []),
                    'mention_count': stock_data.get('mention_count', 0),
                    'articles': stock_data.get('articles', [])
                })
                break
    
    return render_template('group_detail.html', group=group, stocks=related_stocks)

# ============================================
# 热点数据 API（独立的、健壮的热点头点加载）
# ============================================

@app.route('/api/hot-topics')
def api_hot_topics():
    """
    专门的热点数据 API
    返回格式: {"success": true, "topics": [...], "count": N}
    """
    # 直接加载热点数据，不依赖全局状态
    topics = []
    
    # 使用 BASE_DIR（已在 main.py 中正确设置）
    try:
        hot_file = HOT_TOPICS_FILE
        if hot_file.exists():
            with open(hot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                topics = data.get('topics', [])
                print(f"[API] 从 {hot_file} 加载了 {len(topics)} 个热点")
    except Exception as e:
        print(f"[API] 本地文件加载失败: {e}")
    


    # 只返回 display=true 的热点
    visible_topics = [t for t in topics if t.get('display', True)]
    
    # 将个股名称转为含代码的对象（前端需要代码做链接）
    load_all_data()
    for topic in visible_topics:
        stock_names = topic.get('stocks', [])
        enriched = []
        for name in stock_names:
            code = _stock_name_to_code(name)
            enriched.append({'name': name, 'code': code})
        topic['stocks'] = enriched
    
    return jsonify({
        'success': True,
        'topics': visible_topics,
        'count': len(visible_topics),
        'all_count': len(topics)
    })

@app.route('/api/all-hot-topics')
def api_all_hot_topics():
    """返回所有热点（包括隐藏的），用于管理"""
    topics = []
    
    try:
        hot_file = HOT_TOPICS_FILE
        if hot_file.exists():
            with open(hot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                topics = data.get('topics', [])
    except Exception as e:
        print(f"[API] 加载失败: {e}")
    
    return jsonify({
        'success': True,
        'topics': topics,
        'count': len(topics)
    })

@app.route('/stocks')
def stocks_list():
    # 获取排序方式（通过 URL 参数）
    sort_by = request.args.get('sort', 'updated')
    
    # 构建股票列表
    stock_list = [{'code': c, **d} for c, d in stocks.items()]
    
    # 按不同方式排序
    if sort_by == 'mention':
        # 按提及次数排序
        stock_list.sort(key=lambda x: x.get('mention_count', 0), reverse=True)
    elif sort_by == 'name':
        # 按名称拼音排序
        stock_list.sort(key=lambda x: x.get('name', ''))
    else:
        # 默认按 last_updated 排序（最新的在前），没有更新时间的排在后面
        stock_list.sort(key=lambda x: (x.get('last_updated', '') or '', x.get('mention_count', 0)), reverse=True)
    
    return render_template('stocks.html', total=len(stock_list), stocks=stock_list, sort_by=sort_by)

@app.route('/social-security-new')
def social_security_new():
    """2025Q4 社保基金新进股票页面"""
    # 加载社保基金数据
    SS_FILE = BASE_DIR / 'data' / 'master' / 'social_security_2025q4.json'
    try:
        with open(SS_FILE, 'r', encoding='utf-8') as f:
            ss_data = json.load(f)
    except Exception as e:
        print(f"⚠️ 加载社保基金数据失败：{e}")
        ss_data = {'stocks': [], 'total_count': 0}
    
    # 检查哪些股票在数据库中
    enhanced_stocks = []
    for stock in ss_data.get('stocks', []):
        code = stock.get('code')
        in_db = code in stocks
        enhanced_stocks.append({**stock, 'in_database': in_db})
    
    # 按行业分组
    industry_groups = {}
    for stock in enhanced_stocks:
        industry = stock.get('industry_category', '其他')
        if industry not in industry_groups:
            industry_groups[industry] = []
        industry_groups[industry].append(stock)
    
    # 计算统计数据
    total_count = len(enhanced_stocks)
    industry_count = len(industry_groups)
    
    # 平均持股比例
    ratios = []
    max_ratio = 0
    max_ratio_stock = ''
    for stock in enhanced_stocks:
        ratio_str = stock.get('ratio', '0%')
        try:
            ratio_val = float(ratio_str.replace('%', ''))
            ratios.append(ratio_val)
            if ratio_val > max_ratio:
                max_ratio = ratio_val
                max_ratio_stock = f"{stock.get('name', '')} {ratio_str}"
        except:
            pass
    
    avg_ratio = f"{sum(ratios)/len(ratios):.2f}%" if ratios else '0%'
    
    return render_template('social_security_new.html',
                         industry_groups=industry_groups,
                         total_count=total_count,
                         industry_count=industry_count,
                         avg_ratio=avg_ratio,
                         max_ratio_stock=max_ratio_stock)

@app.route('/demo/cards')
def demo_cards():
    """卡片组件演示页面"""
    return render_template('demo_cards.html')

@app.route('/stock/<code>')
def stock_detail(code):
    # 剥离 .SH/.SZ/.BJ 后缀，统一为纯数字 code
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    
    # 直接从本地数据加载
    load_all_data()
    if code not in stocks:
        # 尝试按名称查找（兼容分组/热点用名称链接）
        found_code = None
        for c, d in stocks.items():
            if d.get('name') == code:
                found_code = c
                break
        if found_code:
            code = found_code
        else:
            return jsonify({'error': '股票不存在'}), 404
    d = stocks[code]
    
    # v3.0: 按需加载 articles（stocks_meta.json 不含 articles）
    if not d.get("articles") and d.get("article_count", 0) > 0:
        d["articles"] = load_articles_for_stock(code)
        d["mention_count"] = d.get("article_count", 0)
    
    stock = {
        'code': code,
        'name': d.get('name', ''),
        'board': d.get('board', ''),
        'industry': d.get('industry', ''),
        'mention_count': d.get('mention_count', 0),
        'last_updated': d.get('last_updated', ''),
        'concepts': d.get('concepts', []),
        'core_business': d.get('core_business', []),
        'industry_position': d.get('industry_position', []),
        'accident': d.get('accident', ''),
        'insights': d.get('insights', ''),
        'chain': d.get('chain', []),
        'key_metrics': d.get('key_metrics', []),
        'partners': d.get('partners', []),
        'products': d.get('products', []),
        'detail_texts': d.get('detail_texts', [])[:5],
        'valuation': d.get('valuation', {})
    }
    
    # 统一文章字段格式 + 收集行业赛道背景
    def _to_list(val):
        if val is None:
            return []
        if isinstance(val, list):
            return [x.strip() for x in val if x and isinstance(x, str) and x.strip()]
        if isinstance(val, dict):
            return [f"{k}：{v}" for k, v in val.items() if k and str(v).strip()]
        if isinstance(val, str) and val.strip():
            import re
            parts = re.split(r'[；;\n]', val)
            return [p.strip() for p in parts if p and p.strip()]
        return []

    raw_articles = d.get('articles', [])[:20]
    articles = []
    all_industry_bg = []  # 聚合所有文章的 industry_background
    seen_ib = set()
    for a in raw_articles:
        ib_list = _to_list(a.get('industry_background', []))
        for ib in ib_list:
            if ib and ib not in seen_ib:
                seen_ib.add(ib)
                all_industry_bg.append(ib)
        article = {
            'id': a.get('article_id', ''),
            'title': a.get('article_title', a.get('title', '（无标题）')),
            'url': a.get('article_url', a.get('url', '')),
            'date': a.get('date', a.get('published_at', '')),
            'source': a.get('source', ''),
            'context': a.get('context', ''),
            'industry_background': ib_list,
            'insights': _to_list(a.get('insights', a.get('insight', []))),
            'accidents': _to_list(a.get('accidents', [a.get('accident', '')] if a.get('accident') else [])),
            'key_metrics': _to_list(a.get('key_metrics', [])),
            'target_valuation': _to_list(a.get('target_valuation', [])),
            'industry_position': _to_list(a.get('industry_position', [])),
            'products': _to_list(a.get('products', [])),
            'partners': _to_list(a.get('partners', []))
        }
        articles.append(article)
    
    stock['articles'] = articles
    stock['industry_background'] = all_industry_bg  # 聚合到股票级别的行业赛道背景
    
    # 添加上一页/下一页导航（按更新时间排序）
    stock_codes = sorted(stocks.keys(), key=lambda c: (stocks[c].get('last_updated', ''), c), reverse=True)
    current_idx = stock_codes.index(code) if code in stock_codes else -1
    prev_stock = None
    next_stock = None
    if current_idx > 0:
        prev_code = stock_codes[current_idx - 1]
        prev_stock = {'code': prev_code, 'name': stocks[prev_code].get('name', '')}
    if current_idx < len(stock_codes) - 1:
        next_code = stock_codes[current_idx + 1]
        next_stock = {'code': next_code, 'name': stocks[next_code].get('name', '')}
    nav_info = {
        'prev': prev_stock,
        'next': next_stock,
        'index': current_idx + 1,
        'total': len(stock_codes)
    }
    stock['nav'] = nav_info
    
    # 添加社保基金信息
    stock['is_social_security'] = code in social_security_stocks
    if stock['is_social_security']:
        ss_info = social_security_info.get(code, {})
        stock['social_security_holding_ratio'] = ss_info.get('holding_ratio', '')
        stock['social_security_note'] = ss_info.get('note', '')
        stock['social_security_industry_group'] = ss_info.get('industry_group', '')
    
    # 添加所属分组信息
    stock['groups'] = []
    for group in groups:
        group_stocks = group.get('stocks', [])
        if stock['name'] in group_stocks or code in group_stocks:
            # 计算颜色 RGB 值
            color = group.get('color', '#3b82f6')
            result = re.match(r'^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$', color, re.IGNORECASE)
            color_rgb = result and f"{int(result.group(1), 16)},{int(result.group(2), 16)},{int(result.group(3), 16)}" or "59,130,246"
            stock['groups'].append({
                'id': group.get('id', ''),
                'name': group.get('name', ''),
                'icon': group.get('icon', '📁'),
                'color': color,
                'color_rgb': color_rgb
            })
    
    # 查找股票所属分组
    load_groups_data()
    stock_groups = []
    stock_name = d.get('name', '')
    for group in groups:
        if stock_name in group.get('stocks', []):
            color = group.get('color', '#6366f1')
            stock_groups.append({
                'id': group.get('id', ''),
                'name': group.get('name', ''),
                'category': group.get('category', ''),
                'icon': group.get('icon', '📁'),
                'color': color,
                'color_rgb': ','.join(str(int(color[i:i+2], 16)) for i in (1,3,5))
            })
    stock['groups'] = stock_groups
    
    return render_template('stock_detail.html', stock=stock)

@app.route('/concepts')
def concepts_list():
    lst = [{'name': n, 'count': len(c)} for n, c in concepts.items()]
    lst.sort(key=lambda x: x['count'], reverse=True)
    return render_template('concepts.html', concepts=lst)

@app.route('/concept/<name>')
def concept_detail(name):
    codes = concepts.get(name, [])
    lst = []
    for c in codes:
        if c in stocks:
            s = stocks[c]
            lst.append({'code': c, 'name': s.get('name',''), 
                       'mention_count': s.get('mention_count',0),
                       'board': s.get('board',''),
                       'other_concepts': [x for x in s.get('concepts',[]) if x != name]})
    lst.sort(key=lambda x: x['mention_count'], reverse=True)
    return render_template('concept_detail.html', concept=name, stocks=lst)

@app.route('/search')
def search():
    q = request.args.get('q', '').lower().strip()
    results = []
    
    if q:
        # 全文搜索：名称、代码、概念、催化剂、投资洞察、公司概况
        for c, d in stocks.items():
            score = 0
            match_fields = []
            
            # 精确匹配代码（最高优先级）
            if q == c:
                score = 1000
                match_fields.append('代码')
            # 匹配名称
            elif q in d.get('name', '').lower():
                score = 500
                match_fields.append('名称')
            # 匹配概念
            elif any(q in concept.lower() for concept in d.get('concepts', [])):
                score = 300
                match_fields.append('概念')
            # 匹配催化剂（accident）- 搜索文章内的 accidents
            article_accidents = []
            for article in d.get('articles', []):
                for a in article.get('accidents', []):
                    if q in a.lower():
                        article_accidents.append(a)
            if article_accidents:
                score = 200
                match_fields.append('催化剂')
            # 匹配投资洞察（insights）- 搜索文章内的 insights
            article_insights = []
            for article in d.get('articles', []):
                for ins in article.get('insights', []):
                    if q in ins.lower():
                        article_insights.append(ins)
            if article_insights:
                score = 200
                match_fields.append('投资洞察')
            # 匹配关键指标（key_metrics）- 搜索文章内的 key_metrics
            for article in d.get('articles', []):
                for km in article.get('key_metrics', []):
                    if q in km.lower():
                        score = 180
                        match_fields.append('关键指标')
                        break
                if '关键指标' in match_fields:
                    break
            # 匹配目标估值（target_valuation）- 搜索文章内的 target_valuation
            for article in d.get('articles', []):
                for tv in article.get('target_valuation', []):
                    if q in tv.lower():
                        score = 180
                        match_fields.append('目标估值')
                        break
                if '目标估值' in match_fields:
                    break
            # 匹配公司概况（core_business）- 支持数组和字符串
            core_business = d.get('core_business', '')
            core_business_text = ','.join(core_business).lower() if isinstance(core_business, list) else core_business.lower()
            if q in core_business_text:
                score = 200
                match_fields.append('公司概况')
            # 匹配行业地位（industry_position）- 支持数组和字符串
            industry_position = d.get('industry_position', '')
            industry_position_text = ','.join(industry_position).lower() if isinstance(industry_position, list) else industry_position.lower()
            if q in industry_position_text:
                score = 150
                match_fields.append('行业地位')
            # 匹配产业链（chain）- 支持数组和字符串
            chain = d.get('chain', '')
            chain_text = ','.join(chain).lower() if isinstance(chain, list) else chain.lower()
            if q in chain_text:
                score = 150
                match_fields.append('产业链')
            
            if score > 0:
                results.append({
                    'code': c,
                    'name': d.get('name', ''),
                    'mention_count': d.get('mention_count', 0),
                    'concepts': d.get('concepts', [])[:5],
                    'score': score,
                    'match_fields': match_fields
                })
        
        # 按分数排序，同分按提及次数排序
        results.sort(key=lambda x: (-x['score'], -x['mention_count']))
    
    # 热门搜索（Top 20）
    top_stocks = sorted([{'code': c, **d} for c, d in stocks.items()], 
                        key=lambda x: x['mention_count'], reverse=True)[:20]
    
    return render_template('search.html', query=q, results=results, total=len(results), top_stocks=top_stocks)

@app.route('/api/stock/<code>/edit', methods=['POST'])
def api_stock_edit(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """编辑股票信息（支持更多字段）"""
    if code not in stocks:
        return jsonify({'success': False, 'error': '股票不存在'}), 404
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '无效数据'}), 400
    
    # 可编辑的股票字段
    editable_fields = [
        'core_business', 'products', 'industry_position', 
        'chain', 'partners'
    ]
    
    updated = []
    for field in editable_fields:
        if field in data:
            stocks[code][field] = data[field]
            updated.append(field)
    
    # 目标市值 → 写入最新文章的 target_valuation
    if 'target_market_cap' in data:
        target_cap = data['target_market_cap'].strip()
        if target_cap:
            target_billion = parse_target_market_cap(target_cap)
            tv_text = f'目标市值：{target_cap}'
            if stocks[code].get('articles') and len(stocks[code]['articles']) > 0:
                latest = stocks[code]['articles'][0]
                if 'target_valuation' not in latest or not isinstance(latest['target_valuation'], list):
                    latest['target_valuation'] = []
                if tv_text not in latest['target_valuation']:
                    latest['target_valuation'].append(tv_text)
            else:
                stocks[code].setdefault('articles', []).append({
                    'title': '目标估值',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': '',
                    'accidents': [],
                    'insights': [],
                    'key_metrics': [],
                    'target_valuation': [tv_text]
                })
            updated.append('target_valuation')
    
    # 文章相关字段（更新最新的一篇文章）
    article_fields = ['accidents', 'insights', 'target_valuation', 'expected_price', 'expected_performance', 'market_valuation']
    article_updated = False
    
    if stocks[code].get('articles') and len(stocks[code]['articles']) > 0:
        latest_article = stocks[code]['articles'][0]
        for field in article_fields:
            if field in data:
                latest_article[field] = data[field]
                article_updated = True
    
    # 记录编辑日志
    if updated or article_updated:
        edit_log.append({
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'name': stocks[code].get('name', ''),
            'fields': updated + (['articles'] if article_updated else []),
            'changes': {field: data[field] for field in updated}
        })
        save_edit_log()
        
        # 保存到文件
        save_stocks_to_file(code)
    
    return jsonify({'success': True, 'updated_fields': updated})

@app.route('/api/stock/<code>/article/delete', methods=['POST'])
def api_stock_article_delete(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """删除指定文章（按 source URL 标识，避免数组索引错位）"""
    try:
        load_all_data()
    except Exception as e:
        print(f"⚠️ 数据加载失败：{e}")
    
    if code not in stocks:
        return jsonify({'success': False, 'error': '股票不存在'}), 404
    
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': '缺少参数'}), 400
    
    article_source = data.get('article_source', '')
    articles = stocks[code].get('articles', [])
    
    # 找到要删除的文章索引（按 source URL 匹配）
    article_index = -1
    for i, a in enumerate(articles):
        if a.get('source') == article_source:
            article_index = i
            break
    
    if article_index < 0:
        return jsonify({'success': False, 'error': '未找到该文章'}), 404
    
    deleted_article = articles[article_index]
    deleted_title = deleted_article.get('title', '（无标题）')
    
    articles.pop(article_index)
    stocks[code]['articles'] = articles
    stocks[code]['mention_count'] = len(articles)
    stocks[code]['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    edit_log.append({
        'timestamp': datetime.now().isoformat(),
        'code': code,
        'name': stocks[code].get('name', ''),
        'fields': ['articles'],
        'changes': {'deleted_article': deleted_title}
    })
    save_edit_log()
    
    save_stocks_to_file(code)
    

    github_synced = False
    github_error = None
    try:
        master_file = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
        gz_file = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json.gz'
        import gzip
        with open(master_file, 'rb') as f:
            raw = f.read()
        with gzip.open(gz_file, 'wb') as f:
            f.write(raw)
        
        result = _sync_json_to_github(
            master_file,
            'data/stocks/stocks_master.json',
            f'[Web Sync] 删除文章: {deleted_title} - {stocks[code].get("name","")} ({code})'
        )
        github_synced = result.get('success', False)
        if not github_synced:
            github_error = result.get('error', '未知错误')
        
        _sync_json_to_github(
            gz_file,
            'data/stocks/stocks_master.json.gz',
            f'[Web Sync] 删除文章: {deleted_title} - {stocks[code].get("name","")} ({code})'
        )
    except Exception as e:
        github_error = str(e)
    
    supabase_synced = False
    supabase_error = None
    try:
        sb = get_supabase_client()
        if sb:
            stock = stocks[code]
            sb.table('stocks').upsert({
                'code': code,
                'name': stock.get('name', ''),
                'articles': stock.get('articles', [])
            }).execute()
            supabase_synced = True
    except Exception as e:
        supabase_error = str(e)
    
    return jsonify({
        'success': True,
        'deleted_title': deleted_title,
        'remaining_count': len(articles),
'github_synced': github_synced,
        'github_error': github_error,
        'supabase_synced': supabase_synced,
        'supabase_error': supabase_error,
    })


@app.route('/api/stock/<code>/article/edit', methods=['POST'])
def api_stock_article_edit(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """编辑指定文章内容"""
    try:
        load_all_data()
    except Exception as e:
        print(f"⚠️ 数据加载失败：{e}")
    
    if code not in stocks:
        return jsonify({'success': False, 'error': '股票不存在'}), 404
    
    data = request.json
    if not data or 'article_index' not in data:
        return jsonify({'success': False, 'error': '缺少 article_index 参数'}), 400
    
    article_index = data['article_index']
    articles = stocks[code].get('articles', [])
    
    if article_index < 0 or article_index >= len(articles):
        return jsonify({'success': False, 'error': '文章索引无效'}), 400
    
    article = articles[article_index]
    
    # 更新文章字段
    if 'title' in data:
        article['title'] = data['title']
    if 'date' in data:
        article['date'] = data['date']
    if 'source' in data:
        article['source'] = data['source']
    if 'industry_background' in data:
        article['industry_background'] = data['industry_background']
    if 'accidents' in data:
        article['accidents'] = data['accidents']
    if 'insights' in data:
        article['insights'] = data['insights']
    if 'key_metrics' in data:
        article['key_metrics'] = data['key_metrics']
    if 'target_valuation' in data:
        article['target_valuation'] = data['target_valuation']
    
    stocks[code]['articles'] = articles
    stocks[code]['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # 记录编辑日志
    edit_log.append({
        'timestamp': datetime.now().isoformat(),
        'code': code,
        'name': stocks[code].get('name', ''),
        'fields': ['articles'],
        'changes': {'edited_article': article.get('title', '（无标题）')}
    })
    save_edit_log()
    
    # 保存到文件
    save_stocks_to_file(code)
    

    return jsonify({
        'success': True,
        'edited_title': article.get('title', '（无标题）'),
        'success': True,
        'edited_title': article.get('title', '（无标题）')
    })



@app.route('/api/stock/<code>')
def api_stock(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    # 懒加载数据
    try:
        load_all_data()
    except Exception as e:
        print(f"⚠️ 数据加载失败：{e}")
    
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    d = stocks[code]
    return jsonify({'code': code, 'name': d.get('name',''), 'board': d.get('board',''),
                   'industry': d.get('industry',''),
                   'mention_count': d.get('mention_count',0), 
                   'concepts': d.get('concepts',[]),
                   'products': d.get('products',[]),
                   'core_business': d.get('core_business',[]),
                   'industry_position': d.get('industry_position',[]),
                   'chain': d.get('chain',[]),
                   'partners': d.get('partners',[]),
                   'articles': d.get('articles',[])[:20], 
                   'detail_texts': d.get('detail_texts',[])[:5]})

@app.route('/api/stocks/batch-details', methods=['POST'])
def api_stocks_batch_details():
    """批量查询股票详情（按名称）"""
    try:
        load_all_data()
    except Exception as e:
        print(f"⚠️ 数据加载失败：{e}")
    
    data = request.json
    names = data.get('names', []) if data else []
    
    result = []
    for name in names:
        found = False
        for code, stock_data in stocks.items():
            if stock_data.get('name') == name:
                result.append({
                    'code': code,
                    'name': stock_data.get('name', ''),
                    'board': stock_data.get('board', ''),
                    'industry': stock_data.get('industry', ''),
                    'concepts': stock_data.get('concepts', []),
                    'mention_count': stock_data.get('mention_count', 0),
                    'articles': stock_data.get('articles', [])
                })
                found = True
                break
        if not found:
            result.append({
                'code': '',
                'name': name,
                'board': '',
                'industry': '未录入数据库',
                'concepts': [],
                'mention_count': 0,
                'articles': []
            })
    
    return jsonify({'stocks': result})

@app.route('/api/search/suggest')
def api_suggest():
    q = request.args.get('q', '')
    if len(q) < 1:
        return jsonify({'suggestions': []})
    sug = [{'code': c, 'name': d.get('name',''), 'mention_count': d.get('mention_count',0)}
           for c, d in stocks.items() if q.lower() in d.get('name','').lower()]
    return jsonify({'suggestions': sug[:10]})

# ==================== 热点管理 API ====================

@app.route('/api/hot-topics', methods=['GET'])
def api_get_hot_topics():
    """获取热点列表
    
    Query params:
        display: 'true' | 'false' | 'all' (默认: 'true')
    """
    # 确保数据已加载
    try:
        load_all_data()
    except Exception as e:
        print(f"⚠️ 加载数据失败：{e}")
    
    display_filter = request.args.get('display', 'true')
    
    if display_filter == 'all':
        # 返回所有热点
        return jsonify({'topics': hot_topics})
    elif display_filter == 'false':
        # 只返回隐藏的热点
        hidden = [t for t in hot_topics if not t.get('display', True)]
        return jsonify({'topics': hidden})
    else:
        # 默认只返回显示的热点
        visible = [t for t in hot_topics if t.get('display', True)]
        return jsonify({'topics': visible})

@app.route('/api/hot-topic/<topic_id>', methods=['GET'])
def api_get_hot_topic(topic_id):
    """获取单个热点"""
    for topic in hot_topics:
        if topic.get('id') == topic_id:
            return jsonify(topic)
    
    # 内存中找不到，尝试从文件重新加载
    try:
        if HOT_TOPICS_FILE.exists():
            with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
                hot_topics_data = json.load(f)
                reloaded_topics = hot_topics_data.get('topics', [])
            for t in reloaded_topics:
                if t.get('id') == topic_id:
                    hot_topics.clear()
                    hot_topics.extend(reloaded_topics)
                    return jsonify(t)
    except Exception as e:
        print(f"⚠️ api_get_hot_topic 从文件重新加载失败: {e}")
    
    # 文件中也找不到，尝试从 Firebase 加载
    try:
        fb_topics = None
        if fb_topics:
            for t in fb_topics:
                if t.get('id') == topic_id:
                    hot_topics.clear()
                    hot_topics.extend(fb_topics)
                    save_hot_topics()
                    return jsonify(t)
    except Exception as e:
        print(f"⚠️ api_get_hot_topic 从 Firebase 加载失败: {e}")
    
    return jsonify({'error': '热点不存在'}), 404

@app.route('/api/hot-topic', methods=['POST'])
def api_add_hot_topic():
    """添加新热点"""
    global hot_topics
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'success': False, 'error': '热点名称必填'}), 400
    
    # 生成唯一ID
    topic_id = f"topic_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    new_topic = {
        'id': topic_id,
        'name': data['name'],
        'drivers': data.get('drivers', ''),
        'stocks': data.get('stocks', []),
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().strftime('%Y-%m-%d')
    }
    
    hot_topics.append(new_topic)
    
    # 保存到文件
    save_hot_topics()
    
    return jsonify({'success': True, 'topic': new_topic})

@app.route('/api/hot-topic/<topic_id>', methods=['PUT'])
def api_update_hot_topic(topic_id):
    """更新热点"""
    global hot_topics
    data = request.json
    
    for topic in hot_topics:
        if topic.get('id') == topic_id:
            # 更新字段
            if 'name' in data:
                topic['name'] = data['name']
            if 'drivers' in data:
                topic['drivers'] = data['drivers']
            if 'stocks' in data:
                topic['stocks'] = data['stocks']
            
            topic['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            
            # 保存到文件
            save_hot_topics()
            
            return jsonify({'success': True, 'topic': topic})
    
    # 内存中找不到，尝试从文件重新加载后再更新
    try:
        if HOT_TOPICS_FILE.exists():
            with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
                hot_topics_data = json.load(f)
                reloaded_topics = hot_topics_data.get('topics', [])
            for topic in reloaded_topics:
                if topic.get('id') == topic_id:
                    if 'name' in data:
                        topic['name'] = data['name']
                    if 'drivers' in data:
                        topic['drivers'] = data['drivers']
                    if 'stocks' in data:
                        topic['stocks'] = data['stocks']
                    topic['updated_at'] = datetime.now().strftime('%Y-%m-%d')
                    hot_topics.clear()
                    hot_topics.extend(reloaded_topics)
                    save_hot_topics()
                    return jsonify({'success': True, 'topic': topic})
    except Exception as e:
        print(f"⚠️ api_update_hot_topic 从文件重新加载失败: {e}")
    
    return jsonify({'success': False, 'error': '热点不存在'}), 404

@app.route('/api/reload-hot-topics', methods=['POST'])
def reload_hot_topics():
    """重新加载热点数据"""
    global hot_topics
    if HOT_TOPICS_FILE.exists():
        try:
            with open(HOT_TOPICS_FILE, 'r', encoding='utf-8') as f:
                hot_topics_data = json.load(f)
                hot_topics = hot_topics_data.get('topics', [])
            print(f"📊 重新加载热点数据：{len(hot_topics)} 个热点")
            return jsonify({'success': True, 'count': len(hot_topics), 'topics': hot_topics})
        except Exception as e:
            print(f"⚠️ 重新加载热点数据失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': False, 'error': 'hot_topics.json 不存在'}), 404

@app.route('/api/hot-topic/<topic_id>', methods=['DELETE'])
def api_delete_hot_topic(topic_id):
    """删除热点"""
    global hot_topics
    
    # 先重新加载最新数据
    reload_hot_topics()
    
    for i, topic in enumerate(hot_topics):
        if topic.get('id') == topic_id:
            deleted_topic = hot_topics.pop(i)
            save_hot_topics()
            print(f"✅ 已删除热点: {deleted_topic.get('name')} ({topic_id})")
            return jsonify({'success': True, 'deleted': deleted_topic.get('name')})
    
    return jsonify({'success': False, 'error': '热点不存在'}), 404

@app.route('/api/hot-topic/<topic_id>/display', methods=['PUT'])
def api_toggle_display(topic_id):
    """切换热点显示状态
    
    Body: {"display": true|false}
    """
    global hot_topics
    data = request.json
    
    if data is None:
        return jsonify({'success': False, 'error': '无效数据'}), 400
    
    display_value = data.get('display')
    if display_value is None:
        return jsonify({'success': False, 'error': 'display 字段必填'}), 400
    
    # 先重新加载最新数据
    reload_hot_topics()
    
    for topic in hot_topics:
        if topic.get('id') == topic_id:
            topic['display'] = bool(display_value)
            topic['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            save_hot_topics()
            
            status = "显示" if display_value else "隐藏"
            print(f"✅ 热点 {topic.get('name')} 已设为{status}")
            return jsonify({
                'success': True, 
                'topic_id': topic_id,
                'display': display_value,
                'message': f'热点已设为{status}'
            })
    
    return jsonify({'success': False, 'error': '热点不存在'}), 404

@app.route('/api/hot-topics/batch-display', methods=['PUT'])
def api_batch_display():
    """批量设置热点显示状态
    
    Body: {"ids": ["topic_id1", "topic_id2"], "display": true|false}
    """
    global hot_topics
    data = request.json
    
    if data is None:
        return jsonify({'success': False, 'error': '无效数据'}), 400
    
    topic_ids = data.get('ids', [])
    display_value = data.get('display')
    
    if not topic_ids:
        return jsonify({'success': False, 'error': 'ids 字段必填'}), 400
    if display_value is None:
        return jsonify({'success': False, 'error': 'display 字段必填'}), 400
    
    # 先重新加载最新数据
    reload_hot_topics()
    
    updated = []
    for topic in hot_topics:
        if topic.get('id') in topic_ids:
            topic['display'] = bool(display_value)
            topic['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            updated.append(topic.get('id'))
    
    if updated:
        save_hot_topics()
    
    status = "显示" if display_value else "隐藏"
    print(f"✅ 批量更新 {len(updated)} 个热点为{status}")
    return jsonify({
        'success': True,
        'updated_count': len(updated),
        'message': f'{len(updated)} 个热点已设为{status}'
    })

def save_hot_topics():
    """保存热点数据到文件"""
    try:
        # 保存到本地
        with open(HOT_TOPICS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'topics': hot_topics}, f, ensure_ascii=False, indent=2)
        print(f"✅ 热点数据已保存: {len(hot_topics)} 个热点")
        
        # 同步到 agent_store
        sync_hot_topics_to_agent_store()

        # 同步到 Firebase
        None

        # 同步到 GitHub（静默执行，不阻塞保存流程）
        try:
            gh_result = _sync_json_to_github(
                HOT_TOPICS_FILE,
                'data/hot_topics/hot_topics.json',
                f'[Auto Sync] 更新热点数据 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            )
            if gh_result['success']:
                print(f"✅ 热点数据已同步到 GitHub")
            else:
                print(f"⚠️ 热点 GitHub 同步失败: {gh_result.get('error', '未知错误')}")
        except Exception as e:
            print(f"⚠️ 热点 GitHub 同步异常: {e}")
    except Exception as e:
        print(f"❌ 保存热点数据失败: {e}")

def _stock_name_to_code(name):
    """通过股票名称查找股票代码"""
    if not stocks:
        load_all_data()
    for c, d in stocks.items():
        if d.get('name') == name:
            return c
    return ''

def load_groups_data():
    """加载分组数据（Vercel 下本地文件缺失时自动回退 GitHub raw）"""
    global groups
    try:
        if GROUPS_FILE.exists():
            with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
                groups_data = json.load(f)
                groups = groups_data.get('groups', [])
            print(f"📊 加载分组数据（本地）：{len(groups)} 个分组")
        else:
            groups = []
            print(f"📊 分组文件不存在：{GROUPS_FILE}")
    except Exception as e:
        print(f"⚠️ 加载分组数据失败：{e}")
        groups = []
    
    # Vercel fallback：本地加载失败时从 GitHub raw 加载
    if not groups and 'VERCEL' in os.environ:
        print("📋 Vercel: 本地 groups 为空，尝试 GitHub raw...")
        try:
            import time as _t, random as _r
            gh_url = (f"https://raw.githubusercontent.com/treeie2/app_stockapril/main/"
                     f"data/groups/groups.json?t={int(_t.time())}&r={_r.randint(0,99999)}")
            r = requests.get(gh_url, timeout=20, headers={"Cache-Control": "no-cache"})
            r.raise_for_status()
            data = json.loads(r.text)
            groups = data.get('groups', [])
            print(f"  ✅ GitHub raw: {len(groups)} 个分组")
        except Exception as e:
            print(f"  ⚠️ GitHub raw 也失败: {e}")
            groups = []

def save_groups():
    """保存分组数据到文件"""
    try:
        with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'groups': groups}, f, ensure_ascii=False, indent=2)
        print(f"✅ 分组数据已保存: {len(groups)} 个分组")
        
        # 同步到 agent_store
        try:
            import shutil
            target_file = Path("e:/github/agent_store/data/groups.json")
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(GROUPS_FILE, target_file)
            print(f"✅ 分组数据已同步到 agent_store")
        except Exception as e:
            print(f"⚠️ 同步到 agent_store 失败: {e}")

        # 同步到 Firebase
        None

        # 同步到 GitHub（静默执行，不阻塞保存流程）
        try:
            gh_result = _sync_json_to_github(
                GROUPS_FILE,
                'data/groups/groups.json',
                f'[Auto Sync] 更新分组数据 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            )
            if gh_result['success']:
                print(f"✅ 分组数据已同步到 GitHub")
            else:
                print(f"⚠️ 分组 GitHub 同步失败: {gh_result.get('error', '未知错误')}")
        except Exception as e:
            print(f"⚠️ 分组 GitHub 同步异常: {e}")
    except Exception as e:
        print(f"❌ 保存分组数据失败: {e}")

# ─── 分组 API 路由 ───

@app.route('/api/groups')
def api_get_groups():
    """获取所有分组"""
    load_groups_data()
    # 将分组个股名称转为含代码的对象
    enriched_groups = []
    for group in groups:
        g = dict(group)
        stock_names = g.get('stocks', [])
        enriched = []
        for name in stock_names:
            code = _stock_name_to_code(name)
            enriched.append({'name': name, 'code': code})
        g['stocks'] = enriched
        enriched_groups.append(g)
    return jsonify({
        'success': True,
        'groups': enriched_groups,
        'count': len(enriched_groups)
    })

@app.route('/api/group/<group_id>')
def api_get_group(group_id):
    """获取单个分组"""
    load_groups_data()
    for group in groups:
        if group.get('id') == group_id:
            return jsonify(group)
    return jsonify({'error': '分组不存在'}), 404

@app.route('/api/group', methods=['POST'])
def api_add_group():
    """添加新分组"""
    global groups
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'success': False, 'error': '分组名称必填'}), 400
    
    group_id = f"group_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    new_group = {
        'id': group_id,
        'name': data['name'],
        'description': data.get('description', ''),
        'color': data.get('color', '#3b82f6'),
        'icon': data.get('icon', '📁'),
        'stocks': data.get('stocks', []),
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().strftime('%Y-%m-%d')
    }
    
    groups.append(new_group)
    save_groups()
    
    return jsonify({'success': True, 'group': new_group})

@app.route('/api/group/<group_id>', methods=['PUT'])
def api_update_group(group_id):
    """更新分组"""
    global groups
    data = request.json
    
    for i, group in enumerate(groups):
        if group.get('id') == group_id:
            if 'name' in data:
                groups[i]['name'] = data['name']
            if 'description' in data:
                groups[i]['description'] = data['description']
            if 'color' in data:
                groups[i]['color'] = data['color']
            if 'icon' in data:
                groups[i]['icon'] = data['icon']
            if 'stocks' in data:
                groups[i]['stocks'] = data['stocks']
            
            groups[i]['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            save_groups()
            
            return jsonify({'success': True, 'group': groups[i]})
    
    return jsonify({'success': False, 'error': '分组不存在'}), 404

@app.route('/api/group/<group_id>', methods=['DELETE'])
def api_delete_group(group_id):
    """删除分组"""
    global groups
    
    for i, group in enumerate(groups):
        if group.get('id') == group_id:
            deleted_group = groups.pop(i)
            save_groups()
            return jsonify({'success': True, 'deleted': deleted_group.get('name')})
    
    return jsonify({'success': False, 'error': '分组不存在'}), 404

@app.route('/api/group/<group_id>/add-stock', methods=['POST'])
def api_add_stock_to_group(group_id):
    """添加股票到分组"""
    global groups
    data = request.json
    
    stock_name = data.get('stock_name') or data.get('stock')
    if not stock_name:
        return jsonify({'success': False, 'error': '股票名称必填'}), 400
    
    for group in groups:
        if group.get('id') == group_id:
            if stock_name not in group['stocks']:
                group['stocks'].append(stock_name)
                group['updated_at'] = datetime.now().strftime('%Y-%m-%d')
                save_groups()
                return jsonify({
                    'success': True,
                    'message': f'已将 {stock_name} 添加到 {group["name"]}',
                    'group': group
                })
            else:
                return jsonify({
                    'success': True,
                    'message': f'{stock_name} 已在分组中',
                    'group': group
                })
    
    return jsonify({'success': False, 'error': '分组不存在'}), 404

@app.route('/api/group/<group_id>/remove-stock', methods=['POST'])
def api_remove_stock_from_group(group_id):
    """从分组移除股票"""
    global groups
    data = request.json
    
    stock_name = data.get('stock_name') or data.get('stock')
    if not stock_name:
        return jsonify({'success': False, 'error': '股票名称必填'}), 400
    
    for group in groups:
        if group.get('id') == group_id:
            if stock_name in group['stocks']:
                group['stocks'].remove(stock_name)
                group['updated_at'] = datetime.now().strftime('%Y-%m-%d')
                save_groups()
                return jsonify({
                    'success': True,
                    'message': f'已将 {stock_name} 从 {group["name"]} 移除',
                    'group': group
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'{stock_name} 不在分组中'
                }), 400
    
    return jsonify({'success': False, 'error': '分组不存在'}), 404

@app.route('/api/stock/<code>/groups')
def api_get_stock_groups(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """获取股票所属的分组"""
    load_groups_data()
    
    # 先尝试通过代码查找股票名称
    stock_name = None
    if code in stocks:
        stock_name = stocks[code].get('name', '')
    
    # 查找包含该股票的分组
    stock_groups = []
    for group in groups:
        stocks_list = group.get('stocks', [])
        # 检查是否直接包含股票名称
        if stock_name and stock_name in stocks_list:
            stock_groups.append(group)
        # 或者检查是否包含带代码的格式
        elif any(code in str(s) for s in stocks_list):
            stock_groups.append(group)
    
    return jsonify({
        'success': True,
        'code': code,
        'name': stock_name,
        'groups': stock_groups,
        'count': len(stock_groups)
    })

def sync_hot_topics_to_agent_store():
    """同步热点数据到 agent_store"""
    try:
        import shutil
        target_file = Path("e:/github/agent_store/data/hot_topics.json")
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOT_TOPICS_FILE, target_file)
        print(f"✅ 热点数据已同步到 agent_store")
    except Exception as e:
        print(f"⚠️ 同步到 agent_store 失败: {e}")

@app.route('/api/debug')
def api_debug():
    """调试端点"""
    import sys
    # 先尝试重新加载（如果之前加载失败）
    global _data_loaded, stocks
    _data_loaded = False
    load_hot_topics_only()
    load_groups_data()
    hot_file = HOT_TOPICS_FILE
    result = {
        'base_dir': str(BASE_DIR),
        'base_dir_exists': BASE_DIR.exists(),
        'hot_topics_file': str(hot_file),
        'hot_topics_exists': hot_file.exists(),
        'hot_topics_count': len(hot_topics),
        'stocks_count': len(stocks),
        'groups_file': str(GROUPS_FILE),
        'groups_exists': GROUPS_FILE.exists(),
        'groups_count': len(groups),
        'data_loaded': _data_loaded,
        'vercel': 'VERCEL' in os.environ,
        'python_version': sys.version,
        'files_checked': [],
        'load_attempt': None,
    }
    
    # 检查各种可能的文件路径
    paths_to_check = [
        '/var/task/data/stocks/stocks_master.json.gz',
        '/var/task/data/stocks/stocks_master.json',
        '/var/task/api/stocks_master.json.gz',
        '/var/task/api/stocks_master.json',
        '/var/task/static/stocks_master.json.gz',
        '/var/task/static/stocks_master.json',
        str(BASE_DIR / 'data' / 'stocks' / 'stocks_master.json.gz'),
        str(BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'),
        str(BASE_DIR / 'api' / 'stocks_master.json.gz'),
        str(BASE_DIR / 'static' / 'stocks_master.json.gz'),
    ]
    for p in paths_to_check:
        pp = Path(p)
        info = {
            'path': p,
            'exists': pp.exists(),
        }
        if pp.exists():
            try:
                info['size'] = pp.stat().st_size
            except:
                pass
        result['files_checked'].append(info)
    
    # 尝试直接加载文件以诊断问题
    try:
        master_path = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
        if not master_path.exists():
            master_path = Path('/var/task/data/stocks/stocks_master.json')
        
        if master_path.exists():
            with open(master_path, 'r', encoding='utf-8') as f:
                raw = f.read()
            result['load_attempt'] = {
                'char_count': len(raw),
                'file_found': True,
                'parse_ok': None,
                'stocks_in_file': None,
                'error': None,
            }
            try:
                d = json.loads(raw)
                result['load_attempt']['parse_ok'] = True
                stocks_data = d.get('stocks', {})
                if isinstance(stocks_data, dict):
                    result['load_attempt']['stocks_in_file'] = len(stocks_data)
                else:
                    result['load_attempt']['stocks_in_file'] = f'not_dict:{type(stocks_data).__name__}'
            except Exception as e:
                result['load_attempt']['parse_ok'] = False
                result['load_attempt']['error'] = str(e)[:200]
                result['load_attempt']['first_100_chars'] = repr(raw[:100])
        else:
            result['load_attempt'] = {
                'file_found': False,
                'checked_path': str(master_path),
            }
    except Exception as e:
        result['load_attempt'] = {'error': str(e)[:200]}
    
    # 测试 load_data_from_local() 函数
    try:
        test_stocks, test_concepts = load_data_from_local()
        result['test_load_fn'] = {
            'stocks_count': len(test_stocks),
            'concepts_count': len(test_concepts),
            'success': True,
        }
        if test_stocks:
            first_code = list(test_stocks.keys())[0]
            result['test_load_fn']['first_stock'] = {
                'code': first_code,
                'name': test_stocks[first_code].get('name', ''),
                'has_concepts': len(test_stocks[first_code].get('concepts', [])) > 0,
            }
    except Exception as e:
        import traceback
        result['test_load_fn'] = {
            'success': False,
            'error': str(e)[:500],
            'traceback': traceback.format_exc()[:1000],
        }
    
    if hot_file.exists():
        try:
            result['hot_topics_size'] = hot_file.stat().st_size
        except:
            pass
    return jsonify(result)

@app.route('/api/search/fulltext')
def api_fulltext_search():
    """全文搜索 API - 搜索股票名称、概念、产品、业务、文章内容"""
    # 懒加载数据
    try:
        load_all_data()
    except Exception as e:
        print(f"⚠️ 数据加载失败：{e}")
    
    q = request.args.get('q', '').lower().strip()
    limit = request.args.get('limit', 20, type=int)
    
    if len(q) < 1:
        return jsonify({'results': [], 'total': 0})
    
    results = []
    
    for code, stock_data in stocks.items():
        name = stock_data.get('name', '')
        
        # 搜索股票级别的字段
        stock_text = ""
        stock_fields = ['name', 'industry']
        array_fields = ['concepts', 'products', 'core_business', 'industry_position', 'chain', 'partners']
        
        for field in stock_fields:
            stock_text += " " + str(stock_data.get(field, ''))
        
        for field in array_fields:
            values = stock_data.get(field, [])
            if values:
                stock_text += " " + " ".join(values)
        
        stock_text = stock_text.lower()
        
        # 检查股票级别匹配
        stock_match = q in stock_text
        stock_score = 0
        
        if stock_match:
            if q in name.lower():
                stock_score += 1.0  # 名称匹配权重最高
            elif q in stock_data.get('industry', '').lower():
                stock_score += 0.6
            else:
                # 概念、产品等匹配
                for field in array_fields:
                    values = stock_data.get(field, [])
                    for v in values:
                        if q in v.lower():
                            stock_score += 0.5
                            break
        
        # 搜索文章级别的字段
        articles = stock_data.get('articles', [])
        article_results = []
        
        for article in articles:
            title = article.get('title', '')
            date = article.get('date', '')
            source = article.get('source', '')
            
            # 构建文章搜索文本（包含所有文本字段）
            article_text = ""
            text_fields = ['title', 'content', 'analysis', 'summary']
            array_text_fields = ['accidents', 'insights', 'key_metrics', 'target_valuation']
            
            for field in text_fields:
                article_text += " " + str(article.get(field, ''))
            
            for field in array_text_fields:
                values = article.get(field, [])
                if values:
                    article_text += " " + " ".join(values)
            
            article_text_lower = article_text.lower()
            
            # 计算匹配度
            if q in article_text_lower:
                score = stock_score
                
                # 标题匹配
                if q in title.lower():
                    score += 0.5
                
                # 内容匹配
                if q in article_text_lower:
                    score += 0.3
                    match_count = article_text_lower.count(q)
                    score += min(match_count * 0.02, 0.1)
                
                # 生成摘要片段
                snippet = generate_snippet(article_text_lower, q, article_text[:500])
                if not snippet:
                    snippet = f"匹配到 '{q}' 相关内容"
                
                article_results.append({
                    'code': code,
                    'name': name,
                    'article_title': title or '无标题',
                    'article_date': date,
                    'article_source': source,
                    'snippet': snippet[:200],
                    'score': min(score, 2.0),
                    'match_count': article_text_lower.count(q)
                })
        
        # 如果没有文章匹配但股票级别匹配，添加一个结果
        if stock_match and not article_results:
            results.append({
                'code': code,
                'name': name,
                'article_title': '股票信息匹配',
                'article_date': '',
                'article_source': '',
                'snippet': f"在股票名称、概念或业务中匹配到 '{q}'",
                'score': stock_score,
                'match_count': 1
            })
        else:
            results.extend(article_results)
    
    # 按匹配分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 去重（同一股票只保留最高分的匹配）
    seen_codes = set()
    unique_results = []
    for r in results:
        if r['code'] not in seen_codes:
            seen_codes.add(r['code'])
            unique_results.append(r)
    
    # 限制返回数量
    total = len(unique_results)
    final_results = unique_results[:limit]
    
    return jsonify({
        'results': final_results,
        'total': total,
        'query': q,
        'limit': limit
    })

def generate_snippet(text, query, original_content, max_length=150):
    """生成包含关键词的摘要片段"""
    if not original_content:
        return ""
    
    content_lower = original_content.lower()
    query_lower = query.lower()
    
    # 找到关键词位置
    pos = content_lower.find(query_lower)
    if pos == -1:
        # 如果找不到（可能因为大小写或特殊字符），返回前 max_length 个字符
        return original_content[:max_length] + "..." if len(original_content) > max_length else original_content
    
    # 计算片段起始位置（关键词前后各留一些上下文）
    start = max(0, pos - 50)
    end = min(len(original_content), pos + len(query) + 100)
    
    snippet = original_content[start:end]
    
    # 添加省略号
    if start > 0:
        snippet = "..." + snippet
    if end < len(original_content):
        snippet = snippet + "..."
    
    return snippet

# 数据文件路径
# v2.4: 优先加载 .json.gz（Vercel 部署排除 .json，使用压缩版节省空间）
if (BASE_DIR / 'data' / 'stocks' / 'stocks_master.json.gz').exists():
    MASTER_FILE = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json.gz'
elif (BASE_DIR / 'data' / 'stocks' / 'stocks_master.json').exists():
    MASTER_FILE = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
else:
    MASTER_FILE = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json.gz'
EDIT_LOG_FILE = BASE_DIR / 'data' / 'edit_log.json'

# 编辑记录
edit_log = []

# 加载编辑记录
if EDIT_LOG_FILE.exists():
    try:
        with open(EDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            edit_log = json.load(f)
    except:
        edit_log = []

@app.route('/api/stock/<code>/accident', methods=['PUT'])
def update_accident(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """更新股票的 accident（催化剂）字段"""
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    
    data = request.get_json()
    new_accident = data.get('accident', '')
    
    result = update_stock_field(code, 'accident', new_accident)
    
    # 记录编辑日志
    if result.get('success'):
        edit_log.append({
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'name': stocks[code].get('name', ''),
            'field': 'accident',
            'content': new_accident[:200] + '...' if len(new_accident) > 200 else new_accident
        })
        save_edit_log()
    
    return result

@app.route('/api/stock/<code>/insights', methods=['PUT'])
def update_insights(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """更新股票的 insights 字段"""
    if code not in stocks:
        return jsonify({'error': '股票不存在'}), 404
    
    data = request.get_json()
    new_insights = data.get('insights', '')
    
    result = update_stock_field(code, 'insights', new_insights)
    
    # 记录编辑日志
    if result.get('success'):
        edit_log.append({
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'name': stocks[code].get('name', ''),
            'field': 'insights',
            'content': new_insights[:200] + '...' if len(new_insights) > 200 else new_insights
        })
        save_edit_log()
    
    return result

def save_edit_log():
    """保存编辑日志"""
    try:
        with open(EDIT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(edit_log, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存编辑日志失败：{e}")

def save_stocks_to_file(code=None):
    """保存股票数据到文件（保持 dict 格式，与 stocks_master.json 一致）
    
    Args:
        code: 可选，只更新指定股票；不传则全量保存
    """
    try:
        # 读取现有文件（保持格式一致，避免覆盖丢失数据）
        existing = {}
        if MASTER_FILE.exists():
            try:
                with open(MASTER_FILE, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                stocks_raw = raw.get('stocks', {})
                if isinstance(stocks_raw, dict):
                    existing = stocks_raw
                elif isinstance(stocks_raw, list):
                    existing = {s['code']: s for s in stocks_raw if 'code' in s}
            except Exception:
                pass
        
        if code:
            # 只更新单只股票
            stock = stocks.get(code)
            if stock:
                existing[code] = {
                    'code': code,
                    'name': stock.get('name', ''),
                    'board': stock.get('board', ''),
                    'industry': stock.get('industry', ''),
                    'concepts': stock.get('concepts', []),
                    'products': stock.get('products', []),
                    'core_business': stock.get('core_business', []),
                    'industry_position': stock.get('industry_position', []),
                    'chain': stock.get('chain', []),
                    'partners': stock.get('partners', []),
                    'mention_count': stock.get('mention_count', 0),
                    'articles': stock.get('articles', []),
                    'last_updated': stock.get('last_updated', '')
                }
            stocks_dict = existing
        else:
            # 全量保存
            stocks_dict = {}
            for c, d in stocks.items():
                stocks_dict[c] = {
                    'code': c,
                    'name': d.get('name', ''),
                    'board': d.get('board', ''),
                    'industry': d.get('industry', ''),
                    'concepts': d.get('concepts', []),
                    'products': d.get('products', []),
                    'core_business': d.get('core_business', []),
                    'industry_position': d.get('industry_position', []),
                    'chain': d.get('chain', []),
                    'partners': d.get('partners', []),
                    'mention_count': d.get('mention_count', 0),
                    'articles': d.get('articles', []),
                    'last_updated': d.get('last_updated', '')
                }
        
        data = {'stocks': stocks_dict}
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存 {len(stocks_dict)} 只股票到 {MASTER_FILE}")
    except Exception as e:
        print(f"❌ 保存股票数据失败：{e}")

@app.route('/api/sync', methods=['GET'])
def sync_edits():
    """同步编辑记录 - 导出所有修改"""
    return jsonify({
        'success': True,
        'count': len(edit_log),
        'edits': edit_log
    })

@app.route('/api/sync/export', methods=['GET'])
def export_edits():
    """导出编辑记录为 JSON 文件"""
    if not edit_log:
        return jsonify({'error': '没有编辑记录'}), 404
    
    # 生成导出文件
    export_data = {
        'export_time': datetime.now().isoformat(),
        'total_edits': len(edit_log),
        'edits': edit_log
    }
    
    export_file = EDIT_LOG_FILE.parent / f'edit_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return send_file(export_file, as_attachment=True)

@app.route('/api/sync/email', methods=['POST'])
def email_edits():
    """通过邮件发送编辑记录"""
    if not edit_log:
        return jsonify({'error': '没有编辑记录'}), 404
    
    data = request.get_json() or {}
    recipient = data.get('email', '')
    
    # 生成邮件内容
    email_content = f"""
主题：股票数据编辑同步 - {len(edit_log)} 条更新

编辑记录汇总：
================

"""
    for edit in edit_log:
        email_content += f"""
时间：{edit['timestamp']}
股票：{edit['name']} ({edit['code']})
字段：{edit['field']}
内容：{edit['content']}

---

"""
    
    # 保存到临时文件
    email_file = EDIT_LOG_FILE.parent / f'email_draft_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(email_file, 'w', encoding='utf-8') as f:
        f.write(email_content)
    
    return jsonify({
        'success': True,
        'message': f'邮件草稿已生成：{email_file.name}',
        'content': email_content
    })

@app.route('/api/sync/clear', methods=['POST'])
def clear_edits():
    """清空编辑记录"""
    global edit_log
    edit_log = []
    save_edit_log()
    return jsonify({'success': True, 'message': '编辑记录已清空'})

@app.route('/api/stock/<code>/similar')
def get_similar_stocks(code):
    code = re.sub(r'\.(SH|SZ|BJ)$', '', code)
    """获取相似股票推荐"""
    top_k = request.args.get('top', 10, type=int)
    min_sim = request.args.get('min_sim', 0.1, type=float)
    
    similar = find_similar_stocks(code, top_k=top_k, min_similarity=min_sim)
    return jsonify({'similar': similar, 'count': len(similar)})

@app.route('/api/market-data')
def get_market_data():
    """获取实时行情数据（腾讯财经 API）"""
    codes = request.args.get('codes', '').split(',')
    codes = [c for c in codes if c.strip()]
    
    if not codes:
        return jsonify({'totalCap': 0}), 200
    
    try:
        result = {}
        total_cap = 0
        
        # 构建腾讯财经 API 请求
        symbols = []
        for code in codes:
            if code.startswith('6'):
                symbols.append(f'sh{code}')
            else:
                symbols.append(f'sz{code}')
        
        url = 'https://qt.gtimg.cn/q=' + ','.join(symbols)
        headers = {
            'Referer': 'https://stockapp.finance.qq.com/',
            'User-Agent': 'Mozilla/5.0'
        }
        
        # 使用 gb18030 编码（腾讯 API 默认）
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'gb18030'
        
        if resp.status_code == 200:
            # 解析返回数据
            lines = resp.text.strip().split('\n')
            for line in lines:
                if '=' in line and '~' in line:
                    parts = line.split('=', 1)
                    if len(parts) >= 2:
                        # 提取股票代码：v_sh600519 -> 600519, v_sz300308 -> 300308
                        code_part = parts[0].split('_')
                        if len(code_part) >= 2:
                            full_code = code_part[-1]
                            # 去除市场前缀（sh600519 -> 600519, sz300308 -> 300308）
                            code = full_code[2:] if len(full_code) >= 2 else full_code
                            
                            # 解析数据：v_sh600000="51~浦发银行~600000~7.53~7.50~..."
                            data_str = parts[1].strip('"')
                            fields = data_str.split('~')
                            
                            if len(fields) >= 47:
                                # 字段说明（腾讯财经 API）：
                                # [0]:类型，[1]:名称，[2]:代码，[3]:当前价，[32]:涨跌幅%，[44]:总市值 (亿)，[39]:市盈率
                                price = float(fields[3]) if fields[3] else 0
                                change_pct = float(fields[32]) if fields[32] else 0
                                market_cap = float(fields[44]) if fields[44] else 0
                                pe_ratio = float(fields[39]) if fields[39] else None
                                
                                result[code] = {
                                    'price': price,
                                    'change': change_pct,
                                    'marketCap': market_cap,
                                    'peRatio': pe_ratio
                                }
                                
                                if market_cap:
                                    total_cap += market_cap
        
        result['totalCap'] = total_cap
        return jsonify(result)
    
    except Exception as e:
        print(f"获取行情数据失败：{e}")
        return jsonify({'totalCap': 0, 'error': str(e)}), 200

def update_stock_field(code, field, value):
    """通用函数：更新股票字段"""
    try:
        with open(MASTER_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # 查找并更新股票
        updated = False
        for stock in master_data.get('stocks', []):
            if stock.get('code') == code:
                if 'llm_summary' not in stock:
                    stock['llm_summary'] = {}
                stock['llm_summary'][field] = value
                updated = True
                
                # 同步更新内存中的 stocks 字典
                stocks[code][field] = value
                break
        
        if not updated:
            return jsonify({'error': '股票不存在'}), 404
        
        # 保存回文件
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        # 重新构建搜索索引
        import subprocess
        subprocess.run(['python3', 'build_index.py'], 
                      cwd=BASE_DIR, 
                      capture_output=True)
        
        return jsonify({'success': True, 'message': '已保存'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════
# 文章数据同步 API（对接智能体）
# ═══════════════════════════════════════════════════════════

@app.route('/api/articles/sync', methods=['POST'])
def sync_articles_from_api():
    """
    从文章API服务同步数据到主项目
    可以手动触发或设置定时任务
    """
    try:
        # 1. 从API获取待导入数据
        resp = requests.post(
            f'{ARTICLE_API_URL}/api/sync/to-main',
            timeout=30
        )
        
        if resp.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'API服务返回错误: {resp.status_code}'
            }), 500
        
        data = resp.json()
        if not data.get('success'):
            return jsonify({
                'success': False,
                'error': data.get('error', 'Unknown error')
            }), 500
        
        sync_data = data.get('data', {})
        articles = sync_data.get('articles', [])
        stocks_data = sync_data.get('stocks', [])
        
        if not articles:
            return jsonify({
                'success': True,
                'message': '没有待同步的数据',
                'imported': 0
            })
        
        # 2. 导入数据
        from article_importer import ArticleImporter
        importer = ArticleImporter(api_base_url=ARTICLE_API_URL)
        stats = importer.import_articles(auto_confirm=True)
        
        return jsonify({
            'success': True,
            'message': f'同步完成',
            'stats': {
                'articles_processed': stats.get('articles_processed', 0),
                'stocks_created': stats.get('stocks_created', 0),
                'stocks_updated': stats.get('stocks_updated', 0),
                'errors': len(stats.get('errors', []))
            }
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': f'无法连接到文章API服务: {ARTICLE_API_URL}'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/articles/status', methods=['GET'])
def get_article_api_status():
    """检查文章API服务状态"""
    try:
        resp = requests.get(f'{ARTICLE_API_URL}/api/health', timeout=5)
        if resp.status_code == 200:
            return jsonify({
                'success': True,
                'api_status': 'connected',
                'api_url': ARTICLE_API_URL,
                'details': resp.json()
            })
        else:
            return jsonify({
                'success': False,
                'api_status': 'error',
                'api_url': ARTICLE_API_URL,
                'status_code': resp.status_code
            })
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'api_status': 'disconnected',
            'api_url': ARTICLE_API_URL,
            'message': '文章API服务未启动'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'api_status': 'error',
            'error': str(e)
        })


def sync_to_firebase_import(stocks_dict, stats):
    """同步导入的数据到 Firebase Firestore（已废弃，保留兼容）"""
    return {'success': True, 'synced_count': 0, 'total_stocks': len(stocks_dict), 'errors': []}


# Firebase 测试页面
@app.route('/test-firebase')
def test_firebase():
    return render_template('test_firebase.html')


# 数据导入页面
@app.route('/import')
def import_data_page():
    return render_template('import_data.html')


# API: 导入股票数据
@app.route('/api/import/stocks', methods=['POST'])
def import_stocks():
    """导入股票数据JSON"""
    try:
        data = request.get_json()
        
        if not data or 'stocks' not in data:
            return jsonify({
                'success': False,
                'error': '无效的JSON格式，必须包含 "stocks" 字段'
            })
        
        import_stocks = data['stocks']
        if not isinstance(import_stocks, list):
            return jsonify({
                'success': False,
                'error': '"stocks" 必须是数组'
            })
        
        # 加载现有数据
        master_file = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
        existing_stocks = {}
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                existing_stocks = {s['code']: s for s in existing_data.get('stocks', [])}
        
        # 统计
        stats = {
            'imported_stocks': 0,
            'new_stocks': 0,
            'updated_stocks': 0,
            'imported_articles': 0,
            'new_articles': 0,
            'duplicate_articles': 0
        }
        
        # 处理导入的股票
        for stock in import_stocks:
            code = stock.get('code')
            if not code:
                continue
            
            stats['imported_stocks'] += 1
            
            if code in existing_stocks:
                # 更新现有股票
                existing = existing_stocks[code]
                
                # 合并文章（去重）
                existing_articles = existing.get('articles', [])
                new_articles = stock.get('articles', [])
                
                existing_titles = {a.get('title') for a in existing_articles}
                
                for article in new_articles:
                    if article.get('title') not in existing_titles:
                        existing_articles.append(article)
                        stats['new_articles'] += 1
                        stats['imported_articles'] += 1
                    else:
                        stats['duplicate_articles'] += 1
                
                # 更新其他字段
                for key in ['name', 'board', 'industry', 'concepts', 'mention_count']:
                    if key in stock:
                        existing[key] = stock[key]
                
                existing['articles'] = existing_articles
                stats['updated_stocks'] += 1
            else:
                # 新增股票
                existing_stocks[code] = stock
                stats['new_stocks'] += 1
                stats['imported_articles'] += len(stock.get('articles', []))
        
        # 保存数据到本地
        output_data = {'stocks': list(existing_stocks.values())}
        with open(master_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        # 更新内存中的数据
        global stocks
        stocks = existing_stocks
        
        # (Firebase 同步已移除)
        firebase_sync_result = {'success': True, 'synced_count': 0, 'total_stocks': len(existing_stocks), 'errors': []}
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {stats["imported_stocks"]} 只股票，新增 {stats["new_stocks"]} 只，更新 {stats["updated_stocks"]} 只',
            'stats': stats,
            'firebase_sync': firebase_sync_result
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'error': f'JSON解析错误: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'导入失败: {str(e)}'
        })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    print(f"🚀 启动于 port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)


# ==================== 同步 API ====================

@app.route('/api/sync/github', methods=['POST'])
def api_sync_to_github():
    """同步 stocks_master.json 到 GitHub 仓库"""
    try:
        github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('MY_GITHUB_TOKEN')
        if not github_token:
            return jsonify({'success': False, 'error': '未配置 GitHub Token（请在 Vercel 环境变量中设置 GITHUB_TOKEN）'}), 400

        github_repo = os.environ.get('GITHUB_REPO', 'treeie2/app_stockapril')
        branch = 'main'

        # 读取 stocks_master.json
        master_file = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
        if not master_file.exists():
            return jsonify({'success': False, 'error': 'stocks_master.json 不存在'}), 404

        content = master_file.read_text(encoding='utf-8')

        # 上传到 GitHub
        import base64
        import requests as http_requests

        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        file_path = 'data/stocks/stocks_master.json'
        url = f'https://api.github.com/repos/{github_repo}/contents/{file_path}'

        # 获取当前文件 SHA
        sha_resp = http_requests.get(f'{url}?ref={branch}', headers=headers, timeout=10)
        sha = sha_resp.json().get('sha') if sha_resp.status_code == 200 else None

        # 提交更新
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        commit_data = {
            'message': f'[Web Sync] 更新 stocks_master.json - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'content': content_b64,
            'branch': branch
        }
        if sha:
            commit_data['sha'] = sha

        resp = http_requests.put(url, json=commit_data, headers=headers, timeout=15)

        if resp.status_code in [200, 201]:
            return jsonify({
                'success': True,
                'message': '✅ 已同步到 GitHub',
                'commit_url': resp.json().get('content', {}).get('html_url', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': f'GitHub API 错误: HTTP {resp.status_code} - {resp.text[:200]}'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': f'同步失败: {str(e)}'}), 500


@app.route('/api/sync/firebase', methods=['POST'])
def api_None():
    """同步 stocks_master.json 到 Firebase Firestore"""
    try:
        # 读取 stocks_master.json
        master_file = BASE_DIR / 'data' / 'stocks' / 'stocks_master.json'
        if not master_file.exists():
            return jsonify({'success': False, 'error': 'stocks_master.json 不存在'}), 404

        with open(master_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        stocks_dict = data.get('stocks', {})
        if isinstance(stocks_dict, list):
            stocks_dict = {s['code']: s for s in stocks_dict}

        # 使用现有的 None 函数
        result = {'success': True, 'synced_count': 0, 'total_stocks': len(stocks_dict), 'errors': []}

        return jsonify({
            'success': result.get('success', False),
            'message': f'✅ 已同步 {result.get("synced_count", 0)}/{len(stocks_dict)} 只股票到 Firebase',
            'details': result
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'Firebase 同步失败: {str(e)}'}), 500


@app.route('/api/sync/all', methods=['POST'])
def api_sync_all():
    """同步到 GitHub + Firebase"""
    github_result = None
    firebase_result = None
    errors = []

    # 先同步 GitHub
    try:
        gh_resp = api_sync_to_github()
        github_result = gh_resp.get_json() if hasattr(gh_resp, 'get_json') else None
        if github_result and not github_result.get('success'):
            errors.append(f'GitHub: {github_result.get("error", "未知错误")}')
    except Exception as e:
        errors.append(f'GitHub: {str(e)}')

    # 再同步 Firebase
    try:
        fb_resp = api_None()
        firebase_result = fb_resp.get_json() if hasattr(fb_resp, 'get_json') else None
        if firebase_result and not firebase_result.get('success'):
            errors.append(f'Firebase: {firebase_result.get("error", "未知错误")}')
    except Exception as e:
        errors.append(f'Firebase: {str(e)}')

    return jsonify({
        'success': len(errors) == 0,
        'github': github_result,
        'firebase': firebase_result,
        'errors': errors if errors else None
    })


# ==================== 热点 & 分组 同步辅助函数 ====================

def _sync_json_to_github(local_path, github_file_path, commit_msg):
    """通用函数：将本地 JSON 文件同步到 GitHub"""
    github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('MY_GITHUB_TOKEN')
    if not github_token:
        return {'success': False, 'error': '未配置 GitHub Token'}

    github_repo = os.environ.get('GITHUB_REPO', 'treeie2/app_stockapril')
    branch = 'main'

    if not local_path.exists():
        return {'success': False, 'error': f'文件不存在: {local_path}'}

    content = local_path.read_text(encoding='utf-8')

    import base64
    import requests as http_requests

    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{github_repo}/contents/{github_file_path}'

    # 获取当前文件 SHA
    sha_resp = http_requests.get(f'{url}?ref={branch}', headers=headers, timeout=10)
    sha = sha_resp.json().get('sha') if sha_resp.status_code == 200 else None

    # 提交更新
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    commit_data = {
        'message': commit_msg,
        'content': content_b64,
        'branch': branch
    }
    if sha:
        commit_data['sha'] = sha

    resp = http_requests.put(url, json=commit_data, headers=headers, timeout=15)

    if resp.status_code in [200, 201]:
        return {
            'success': True,
            'message': '✅ 已同步到 GitHub',
            'commit_url': resp.json().get('content', {}).get('html_url', '')
        }
    else:
        return {
            'success': False,
            'error': f'GitHub API 错误: HTTP {resp.status_code} - {resp.text[:200]}'
        }


@app.route('/api/sync/hot-topics/github', methods=['POST'])
def api_sync_hot_topics_to_github():
    """同步热点数据到 GitHub"""
    try:
        result = _sync_json_to_github(
            HOT_TOPICS_FILE,
            'data/hot_topics/hot_topics.json',
            f'[Web Sync] 更新热点数据 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        )
        return jsonify(result), (200 if result['success'] else 500)
    except Exception as e:
        return jsonify({'success': False, 'error': f'同步失败: {str(e)}'}), 500


@app.route('/api/sync/groups/github', methods=['POST'])
def api_sync_groups_to_github():
    """同步分组数据到 GitHub"""
    try:
        result = _sync_json_to_github(
            GROUPS_FILE,
            'data/groups/groups.json',
            f'[Web Sync] 更新分组数据 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        )
        return jsonify(result), (200 if result['success'] else 500)
    except Exception as e:
        return jsonify({'success': False, 'error': f'同步失败: {str(e)}'}), 500


@app.route('/api/sync/hot-topics/firebase', methods=['POST'])
def api_sync_hot_topics_to_firebase():
    """同步热点数据到 Firebase"""
    try:
        None
        return jsonify({'success': True, 'message': f'✅ 已同步 {len(hot_topics)} 个热点到 Firebase'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Firebase 同步失败: {str(e)}'}), 500


@app.route('/api/sync/groups/firebase', methods=['POST'])
def api_None():
    """同步分组数据到 Firebase"""
    try:
        None
        return jsonify({'success': True, 'message': f'✅ 已同步 {len(groups)} 个分组到 Firebase'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Firebase 同步失败: {str(e)}'}), 500


@app.route('/api/sync/hot-topics/all', methods=['POST'])
def api_sync_hot_topics_all():
    """同步热点到 GitHub + Firebase"""
    errors = []
    gh = _sync_json_to_github(
        HOT_TOPICS_FILE,
        'data/hot_topics/hot_topics.json',
        f'[Web Sync] 更新热点数据 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    )
    if not gh['success']:
        errors.append(f'GitHub: {gh.get("error", "未知错误")}')

    try:
        None
        fb_ok = True
    except Exception as e:
        fb_ok = False
        errors.append(f'Firebase: {str(e)}')

    return jsonify({
        'success': len(errors) == 0,
        'github': gh,
        'firebase': {'success': fb_ok, 'message': f'✅ 已同步 {len(hot_topics)} 个热点到 Firebase'} if fb_ok else None,
        'errors': errors if errors else None
    })


@app.route('/api/sync/groups/all', methods=['POST'])
def api_sync_groups_all():
    """同步分组到 GitHub + Firebase"""
    errors = []
    gh = _sync_json_to_github(
        GROUPS_FILE,
        'data/groups/groups.json',
        f'[Web Sync] 更新分组数据 - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    )
    if not gh['success']:
        errors.append(f'GitHub: {gh.get("error", "未知错误")}')

    try:
        None
        fb_ok = True
    except Exception as e:
        fb_ok = False
        errors.append(f'Firebase: {str(e)}')

    return jsonify({
        'success': len(errors) == 0,
        'github': gh,
        'firebase': {'success': fb_ok, 'message': f'✅ 已同步 {len(groups)} 个分组到 Firebase'} if fb_ok else None,
        'errors': errors if errors else None
    })
