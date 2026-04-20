#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""增量更新机制 - 将抽取结果按日期分片存储并维护索引

数据架构:
  data/master/
  ├── stocks_index.json           # 索引文件（股票代码列表和最后更新时间）
  ├── stocks_master.json          # 主文件（完整数据，可选备份）
  └── stocks/
      ├── 2026-04-17.json        # 按日期分片存储
      ├── 2026-04-16.json
      └── ...

使用方式:
    # 从 stocks_master_YYYY-MM-DD.json 增量合并到分片
    python scripts/incremental_update.py \
      --json "data/stocks_master_2026-04-17.json" \
      --mode merge
    
    # 直接更新单只股票
    python scripts/incremental_update.py \
      --stock-code "688227" \
      --stock-data '{"name": "品高股份", ...}' \
      --mode single
    
    # 构建索引（从现有分片重建）
    python scripts/incremental_update.py --mode rebuild-index
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class IncrementalUpdater:
    """增量更新管理器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent.parent / "data" / "master"
        
        self.stocks_dir = self.base_dir / "stocks"
        self.index_file = self.base_dir / "stocks_index.json"
        self.master_file = self.base_dir / "stocks_master.json"
    
    def _load_index(self) -> Dict[str, Any]:
        """加载索引文件"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "2.0", "last_updated": "", "total_stocks": 0, "stocks": {}}
    
    def _save_index(self, index: Dict[str, Any]):
        """保存索引文件"""
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def _load_daily_file(self, date: str) -> Dict[str, Any]:
        """加载指定日期的分片文件"""
        file_path = self.stocks_dir / f"{date}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"date": date, "update_count": 0, "stocks": {}}
    
    def _save_daily_file(self, date: str, data: Dict[str, Any]):
        """保存指定日期的分片文件"""
        self.stocks_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.stocks_dir / f"{date}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _deduplicate_articles(self, existing_articles: List[Dict], new_articles: List[Dict]) -> List[Dict]:
        """文章去重（按 source + title 去重）"""
        seen = set()
        result = []
        
        for article in existing_articles + new_articles:
            key = (article.get('source', ''), article.get('title', ''))
            if key not in seen and key != ('', ''):
                seen.add(key)
                result.append(article)
        
        return result
    
    def _merge_stock_data(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """合并单只股票的数据（带去重逻辑）"""
        merged = existing.copy()
        
        for key in ['name', 'code', 'board', 'industry']:
            if new_data.get(key):
                merged[key] = new_data[key]
        
        for set_field in ['core_business', 'industry_position', 'chain', 'partners', 'concepts', 'products']:
            existing_set = set(existing.get(set_field, []))
            new_set = set(new_data.get(set_field, []))
            merged[set_field] = list(existing_set | new_set)
        
        if new_data.get('target_valuation'):
            merged['target_valuation'] = {**existing.get('target_valuation', {}), **new_data['target_valuation']}
        
        if new_data.get('insights'):
            existing_insights = set(existing.get('insights', []))
            new_insights = set(new_data['insights'])
            merged['insights'] = list(existing_insights | new_insights)
        
        new_articles = new_data.get('articles', [])
        if new_articles:
            existing_articles = existing.get('articles', [])
            merged['articles'] = self._deduplicate_articles(existing_articles, new_articles)
        
        merged['mention_count'] = existing.get('mention_count', 0) + new_data.get('mention_count', 0)
        merged['last_updated'] = new_data.get('last_updated', datetime.now().strftime("%Y-%m-%d"))
        
        return merged
    
    def merge_from_json(self, json_path: str) -> Dict[str, Any]:
        """从 stocks_master JSON 文件增量合并到分片
        
        Args:
            json_path: 抽取生成的 stocks_master JSON 路径
            
        Returns:
            统计信息字典
        """
        print(f"📖 读取源文件: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        source_stocks = source_data.get('stocks', [])
        if isinstance(source_stocks, dict):
            source_stocks = list(source_stocks.values())
        
        print(f"   源文件包含 {len(source_stocks)} 只股票")
        
        today = datetime.now().strftime("%Y-%m-%d")
        index = self._load_index()
        daily_data = self._load_daily_file(today)
        
        updated_count = 0
        new_count = 0
        
        for stock in source_stocks:
            code = stock.get('code')
            if not code:
                continue
            
            stock['last_updated'] = today
            
            if code in daily_data['stocks']:
                daily_data['stocks'][code] = self._merge_stock_data(daily_data['stocks'][code], stock)
                updated_count += 1
            else:
                daily_data['stocks'][code] = stock
                new_count += 1
            
            index['stocks'][code] = {
                "name": stock.get('name', ''),
                "last_updated": today,
                "file": f"{today}.json"
            }
        
        daily_data['update_count'] = len(daily_data['stocks'])
        daily_data['date'] = today
        
        self._save_daily_file(today, daily_data)
        
        index['total_stocks'] = len(index['stocks'])
        index['last_updated'] = today
        self._save_index(index)
        
        stats = {
            "date": today,
            "new_stocks": new_count,
            "updated_stocks": updated_count,
            "total_in_day": len(daily_data['stocks']),
            "total_indexed": len(index['stocks']),
            "daily_file": str(self.stocks_dir / f"{today}.json"),
            "index_file": str(self.index_file)
        }
        
        print(f"\n✅ 增量合并完成:")
        print(f"   📅 日期: {today}")
        print(f"   ➕ 新增: {new_count} 只")
        print(f"   🔄 更新: {updated_count} 只")
        print(f"   📊 当日总计: {stats['total_in_day']} 只")
        print(f"   📚 索引总计: {stats['total_indexed']} 只")
        print(f"   💾 分片文件: {stats['daily_file']}")
        
        return stats
    
    def update_single_stock(self, stock_code: str, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """增量更新单只股票
        
        Args:
            stock_code: 股票代码（6位数字）
            stock_data: 股票数据字典
            
        Returns:
            统计信息字典
        """
        today = datetime.now().strftime("%Y-%m-%d")
        stock_data['code'] = stock_code
        stock_data['last_updated'] = today
        
        index = self._load_index()
        daily_data = self._load_daily_file(today)
        
        if stock_code in daily_data['stocks']:
            daily_data['stocks'][stock_code] = self._merge_stock_data(daily_data['stocks'][stock_code], stock_data)
            action = "updated"
        else:
            daily_data['stocks'][stock_code] = stock_data
            action = "added"
        
        daily_data['update_count'] = len(daily_data['stocks'])
        daily_data['date'] = today
        self._save_daily_file(today, daily_data)
        
        index['stocks'][stock_code] = {
            "name": stock_data.get('name', ''),
            "last_updated": today,
            "file": f"{today}.json"
        }
        index['total_stocks'] = len(index['stocks'])
        index['last_updated'] = today
        self._save_index(index)
        
        print(f"✅ 已{action}: {stock_data.get('name', stock_code)} ({stock_code}) -> {today}.json")
        
        return {"action": action, "stock_code": stock_code, "date": today}
    
    def rebuild_index(self) -> Dict[str, Any]:
        """从所有分片文件重建索引"""
        print("🔄 重建索引...")
        
        stock_index = {}
        total_files = 0
        total_stocks = 0
        
        if not self.stocks_dir.exists():
            print("⚠️ stocks 目录不存在")
            return {"total_files": 0, "total_stocks": 0}
        
        for file_path in sorted(self.stocks_dir.glob("*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                date = data.get('date', file_path.stem)
                stocks = data.get('stocks', {})
                
                for code, stock in stocks.items():
                    stock_index[code] = {
                        "name": stock.get('name', ''),
                        "last_updated": stock.get('last_updated', date),
                        "file": f"{date}.json"
                    }
                
                total_files += 1
                total_stocks += len(stocks)
            except Exception as e:
                print(f"   ⚠️ 跳过 {file_path.name}: {e}")
        
        index_data = {
            "version": "2.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_stocks": len(stock_index),
            "stocks": stock_index
        }
        
        self._save_index(index_data)
        
        print(f"✅ 索引重建完成:")
        print(f"   📁 分片文件: {total_files}")
        print(f"   📚 总股票数: {len(stock_index)}")
        
        return {"total_files": total_files, "total_stocks": len(stock_index)}
    
    def load_recent_stocks(self, days: int = 7) -> Dict[str, Any]:
        """加载最近 N 天的股票数据"""
        index = self._load_index()
        today = datetime.now()
        
        recent_dates = []
        for i in range(days):
            d = today.replace(day=today.day - i)
            recent_dates.append(d.strftime("%Y-%m-%d"))
        
        all_stocks = {}
        for date in recent_dates:
            file_path = self.stocks_dir / f"{date}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_stocks.update(data.get('stocks', {}))
        
        return all_stocks
    
    def build_master_from_shards(self) -> bool:
        """从所有分片构建主文件（可选的完整备份）"""
        print("🔄 从分片构建主文件...")
        
        all_stocks = {}
        
        if not self.stocks_dir.exists():
            print("⚠️ stocks 目录不存在")
            return False
        
        for file_path in sorted(self.stocks_dir.glob("*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                all_stocks.update(data.get('stocks', {}))
            except Exception as e:
                print(f"   ⚠️ 跳过 {file_path.name}: {e}")
        
        master_data = {
            "stocks": list(all_stocks.values()),
            "meta": {
                "total": len(all_stocks),
                "updated_at": datetime.now().isoformat(),
                "source": "shard_merge",
                "version": "2.0"
            }
        }
        
        with open(self.master_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 主文件已构建: {self.master_file}")
        print(f"   总计: {len(all_stocks)} 只股票")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="增量更新 - 按日期分片存储股票数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 合并抽取结果到分片
  python scripts/incremental_update.py --json "data/stocks_master_2026-04-17.json" --mode merge
  
  # 更新单只股票
  python scripts/incremental_update.py --stock-code "688227" --mode single
  
  # 重建索引
  python scripts/incremental_update.py --mode rebuild-index
  
  # 构建主文件
  python scripts/incremental_update.py --mode build-master
        """
    )
    
    parser.add_argument("--mode", required=True, choices=["merge", "single", "rebuild-index", "build-master"],
                       help="运行模式")
    parser.add_argument("--json", help="要合并的 JSON 文件路径 (mode=merge)")
    parser.add_argument("--stock-code", help="股票代码 (mode=single)")
    parser.add_argument("--stock-data", help="股票 JSON 数据 (mode=single)")
    parser.add_argument("--base-dir", help="基础目录路径 (默认: skill/data/master)")
    parser.add_argument("--days", type=int, default=7, help="加载数据的天数 (默认: 7)")
    
    args = parser.parse_args()
    
    updater = IncrementalUpdater(base_dir=args.base_dir)
    
    if args.mode == "merge":
        if not args.json:
            print("❌ --mode merge 需要 --json 参数")
            sys.exit(1)
        result = updater.merge_from_json(args.json)
        
    elif args.mode == "single":
        if not args.stock_code:
            print("❌ --mode single 需要 --stock-code 参数")
            sys.exit(1)
        
        if args.stock_data:
            stock_data = json.loads(args.stock_data)
        else:
            stock_data = {"name": "", "articles": [], "mention_count": 1}
        
        result = updater.update_single_stock(args.stock_code, stock_data)
        
    elif args.mode == "rebuild-index":
        result = updater.rebuild_index()
        
    elif args.mode == "build-master":
        success = updater.build_master_from_shards()
        result = {"success": success}
    
    print("\n✅ 完成!")
    return result


if __name__ == "__main__":
    main()