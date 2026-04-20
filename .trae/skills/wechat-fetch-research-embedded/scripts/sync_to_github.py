#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub 同步脚本 - 支持分片存储和单文件两种模式

新模式 (推荐): 按日期分片同步
  - 同步当天分片: data/master/stocks/YYYY-MM-DD.json
  - 同步索引: data/master/stocks_index.json
  
旧模式 (兼容): 单一主文件同步  
  - 同步到: data/master/stocks_master.json

使用方式:
    # 分片模式 (推荐)
    python scripts/sync_to_github.py \
      --mode shard \
      --base-dir "data/master" \
      --github-token "$GITHUB_TOKEN"
    
    # 单文件模式 (旧)
    python scripts/sync_to_github.py \
      --mode single \
      --json "data/stocks_master_2026-04-17.json" \
      --github-token "$GITHUB_TOKEN"
    
    # 全量同步 (分片 + 索引 + 主文件)
    python scripts/sync_to_github.py \
      --mode full \
      --base-dir "data/master" \
      --github-token "$GITHUB_TOKEN"
"""

import argparse
import base64
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


class GitHubSyncer:
    """GitHub 分片同步器"""
    
    def __init__(self, github_token: str, github_repo: str = "treeie2/models_app", branch: str = "main"):
        self.github_token = github_token
        self.github_repo = github_repo
        self.branch = branch
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.results = []
    
    def _get_file_sha(self, file_path: str) -> Optional[str]:
        """获取 GitHub 文件的 SHA（用于更新）"""
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{file_path}?ref={self.branch}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('sha')
        elif response.status_code == 404:
            return None
        else:
            print(f"   ⚠️ 获取 SHA 失败 ({file_path}): HTTP {response.status_code}")
            return None
    
    def _upload_file(self, file_path: str, content: str, message: str) -> bool:
        """上传单个文件到 GitHub"""
        sha = self._get_file_sha(file_path)
        
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')
        
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{file_path}"
        
        if sha:
            update_data = {
                'message': message,
                'content': content_base64,
                'sha': sha,
                'branch': self.branch
            }
        else:
            update_data = {
                'message': message,
                'content': content_base64,
                'branch': self.branch
            }
        
        response = requests.put(url, headers=self.headers, json=update_data)
        
        if response.status_code in [200, 201]:
            commit_url = response.json().get('commit', {}).get('html_url', '')
            print(f"   ✅ {file_path} -> {commit_url}")
            self.results.append({"file": file_path, "status": "success", "url": commit_url})
            return True
        else:
            print(f"   ❌ {file_path} 失败: HTTP {response.status_code}")
            self.results.append({"file": file_path, "status": "failed", "error": response.text[:200]})
            return False
    
    def sync_shard_file(self, local_shard_path: str, date: Optional[str] = None) -> bool:
        """同步单个分片文件
        
        Args:
            local_shard_path: 本地分片文件路径
            date: 日期字符串（可选，用于生成远程路径）
            
        Returns:
            是否成功
        """
        shard_path = Path(local_shard_path)
        if not shard_path.exists():
            print(f"❌ 文件不存在: {local_shard_path}")
            return False
        
        if date is None:
            date = shard_path.stem
        
        with open(shard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        remote_path = f"data/master/stocks/{date}.json"
        message = f"Update stock shard {date} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return self._upload_file(remote_path, content, message)
    
    def sync_index_file(self, local_index_path: str) -> bool:
        """同步索引文件
        
        Args:
            local_index_path: 本地索引文件路径
            
        Returns:
            是否成功
        """
        index_path = Path(local_index_path)
        if not index_path.exists():
            print(f"❌ 文件不存在: {local_index_path}")
            return False
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        remote_path = "data/master/stocks_index.json"
        message = f"Update stocks index - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return self._upload_file(remote_path, content, message)
    
    def sync_master_file(self, local_master_path: str) -> bool:
        """同步主文件（完整备份）
        
        Args:
            local_master_path: 本地主文件路径
            
        Returns:
            是否成功
        """
        master_path = Path(local_master_path)
        if not master_path.exists():
            print(f"❌ 文件不存在: {local_master_path}")
            return False
        
        with open(master_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        remote_path = "data/master/stocks_master.json"
        message = f"Update stocks master - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return self._upload_file(remote_path, content, message)
    
    def sync_single_json(self, json_path: str) -> bool:
        """旧模式：同步单一 JSON 到 master 并合并
        
        Args:
            json_path: 本地 JSON 路径
            
        Returns:
            是否成功
        """
        from .merge_stocks import merge_stocks_from_files
        
        print(f"📖 读取本地数据: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        new_stocks = new_data.get('stocks', [])
        if isinstance(new_stocks, dict):
            new_stocks = list(new_stocks.values())
        
        print(f"   本地: {len(new_stocks)} 只股票")
        
        existing_data, sha = self._fetch_remote_master()
        
        if existing_data:
            existing_stocks = existing_data.get('stocks', [])
            merged_stocks = merge_stocks(existing_stocks, new_stocks)
            print(f"   合并后: {len(merged_stocks)} 只")
        else:
            merged_stocks = new_stocks
            print(f"   无现有数据，使用本地数据")
        
        final_data = {
            'stocks': merged_stocks,
            'meta': {
                'total': len(merged_stocks),
                'updated_at': datetime.now().isoformat(),
                'source': 'agent_merge'
            }
        }
        
        content = json.dumps(final_data, ensure_ascii=False, indent=2)
        message = f'Merge stocks from Agent - {datetime.now().strftime("%Y-%m-%d %H:%M")} (+{len(new_stocks)} stocks, total {len(merged_stocks)})'
        
        return self._upload_file("data/master/stocks_master.json", content, message)
    
    def _fetch_remote_master(self) -> Tuple[Optional[Dict], Optional[str]]:
        """获取远程主文件内容"""
        file_path = 'data/master/stocks_master.json'
        url = f"https://api.github.com/repos/{self.github_repo}/contents/{file_path}?ref={self.branch}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            sha = data['sha']
            
            if data.get('encoding') == 'none' or not data.get('content'):
                download_url = data.get('download_url')
                if download_url:
                    print(f"   文件较大，使用 download_url...")
                    content_resp = requests.get(download_url, timeout=60)
                    content_resp.raise_for_status()
                    return json.loads(content_resp.text), sha
                else:
                    return None, None
            
            content = base64.b64decode(data['content']).decode('utf-8')
            return json.loads(content), sha
        elif response.status_code == 404:
            return None, None
        else:
            print(f"⚠️ 获取远程文件失败: HTTP {response.status_code}")
            return None, None
    
    def sync_daily_shards(self, base_dir: str, days: int = 1) -> Dict[str, Any]:
        """同步最近 N 天的分片文件和索引
        
        Args:
            base_dir: 本地 data/master 目录路径
            days: 同步最近几天的分片（默认1=仅今天）
            
        Returns:
            统计信息
        """
        base_path = Path(base_dir)
        stocks_dir = base_path / "stocks"
        index_path = base_path / "stocks_index.json"
        
        today = datetime.now()
        synced_count = 0
        failed_count = 0
        
        print(f"\n🔄 同步最近 {days} 天的分片文件...\n")
        
        for i in range(days):
            d = today.replace(day=today.day - i)
            date_str = d.strftime("%Y-%m-%d")
            shard_file = stocks_dir / f"{date_str}.json"
            
            if shard_file.exists():
                print(f"📅 [{date_str}]")
                if self.sync_shard_file(str(shard_file), date_str):
                    synced_count += 1
                else:
                    failed_count += 1
            else:
                print(f"⏭️ [{date_str}] 无分片文件，跳过")
        
        print(f"\n📋 同步索引文件...")
        if index_path.exists():
            self.sync_index_file(str(index_path))
        else:
            print(f"   ⚠️ 索引文件不存在: {index_path}")
        
        stats = {
            "synced_shards": synced_count,
            "failed_shards": failed_count,
            "results": self.results
        }
        
        print(f"\n✅ 分片同步完成:")
        print(f"   成功: {synced_count}")
        print(f"   失败: {failed_count}")
        
        return stats
    
    def get_results_summary(self) -> str:
        """获取同步结果摘要"""
        success = sum(1 for r in self.results if r['status'] == 'success')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        
        lines = [
            f"\n{'='*50}",
            f"GitHub 同步结果摘要",
            f"{'='*50}",
            f"✅ 成功: {success}",
            f"❌ 失败: {failed}",
            f"总计: {len(self.results)}"
        ]
        
        if failed > 0:
            lines.append("\n失败文件:")
            for r in self.results:
                if r['status'] == 'failed':
                    lines.append(f"  - {r['file']}: {r.get('error', 'unknown')[:100]}")
        
        return '\n'.join(lines)


def merge_stocks(existing_stocks: list, new_stocks: list) -> list:
    """合并股票数据（保留向后兼容）
    
    规则：
    1. 按 code 合并
    2. 如果股票已存在，合并 articles（按 source 去重）
    3. 如果股票不存在，添加新股票
    """
    stocks_dict = {s['code']: s for s in existing_stocks}

    for new_stock in new_stocks:
        code = new_stock.get('code')
        if not code:
            continue

        if code in stocks_dict:
            existing_stock = stocks_dict[code]
            existing_articles = existing_stock.get('articles', [])
            new_articles = new_stock.get('articles', [])

            existing_sources = {a.get('source') for a in existing_articles}
            for article in new_articles:
                if article.get('source') not in existing_sources:
                    existing_articles.append(article)
                    existing_sources.add(article.get('source'))

            for key in ['name', 'board', 'industry', 'concepts']:
                if new_stock.get(key):
                    existing_stock[key] = new_stock[key]

            existing_stock['mention_count'] = existing_stock.get('mention_count', 0) + new_stock.get('mention_count', 0)
        else:
            stocks_dict[code] = new_stock

    return list(stocks_dict.values())


def main():
    parser = argparse.ArgumentParser(
        description="GitHub 同步 - 支持分片存储和单文件模式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 分片模式 (推荐) - 仅同步今天
  python scripts/sync_to_github.py --mode shard --github-token "$TOKEN"
  
  # 分片模式 - 同步最近3天
  python scripts/sync_to_github.py --mode shard --days 3 --github-token "$TOKEN"
  
  # 单文件模式 (旧)
  python scripts/sync_to_github.py --mode single --json "data/stocks_master.json" --github-token "$TOKEN"
  
  # 全量同步 (分片+索引+主文件)
  python scripts/sync_to_github.py --mode full --github-token "$TOKEN"
        """
    )
    
    parser.add_argument("--mode", required=True, choices=["shard", "single", "full"],
                       help="同步模式: shard(分片推荐), single(单文件旧), full(全量)")
    parser.add_argument("--github-token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--github-repo", default="treeie2/models_app", help="GitHub 仓库名")
    parser.add_argument("--branch", default="main", help="分支名 (默认: main)")
    parser.add_argument("--base-dir", default=None, help="基础目录 (默认: skill/data/master)")
    parser.add_argument("--json", default=None, help="JSON 文件路径 (mode=single)")
    parser.add_argument("--days", type=int, default=1, help="同步最近N天分片 (默认: 1)")
    
    args = parser.parse_args()
    
    if args.base_dir is None:
        args.base_dir = str(Path(__file__).parent.parent / "data" / "master")
    
    print("🚀 开始 GitHub 同步...")
    print(f"   模式: {args.mode}")
    print(f"   仓库: {args.github_repo}")
    print(f"   分支: {args.branch}")
    
    syncer = GitHubSyncer(
        github_token=args.github_token,
        github_repo=args.github_repo,
        branch=args.branch
    )
    
    success = False
    
    if args.mode == "shard":
        stats = syncer.sync_daily_shards(args.base_dir, days=args.days)
        success = stats['failed_shards'] == 0
        
    elif args.mode == "single":
        if not args.json:
            print("❌ --mode single 需要 --json 参数")
            sys.exit(1)
        success = syncer.sync_single_json(args.json)
        
    elif args.mode == "full":
        stats = syncer.sync_daily_shards(args.base_dir, days=args.days)
        
        master_path = Path(args.base_dir) / "stocks_master.json"
        if master_path.exists():
            print(f"\n📦 同步主文件备份...")
            syncer.sync_master_file(str(master_path))
        
        success = stats['failed_shards'] == 0
    
    print(syncer.get_results_summary())
    
    if success:
        print("\n✅ 完成!")
    else:
        print("\n❌ 部分失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()