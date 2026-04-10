#!/usr/bin/env python3
"""
从本地 JSON 合并到 GitHub 的 stocks_master.json
"""
import argparse
import json
import base64
import requests
from pathlib import Path
from datetime import datetime


def fetch_github_json(github_token: str, github_repo: str, branch: str = "main") -> dict:
    """获取 GitHub 上的现有 JSON 数据"""
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    file_path = 'data/master/stocks_master.json'
    url = f"https://api.github.com/repos/{github_repo}/contents/{file_path}?ref={branch}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content_base64 = response.json()['content']
        content = base64.b64decode(content_base64).decode('utf-8')
        return json.loads(content), response.json()['sha']
    elif response.status_code == 404:
        return None, None
    else:
        print(f"⚠️ 获取 GitHub 文件失败: HTTP {response.status_code}")
        return None, None


def merge_stocks(existing_stocks: list, new_stocks: list) -> list:
    """合并股票数据
    
    规则：
    1. 按 code 合并
    2. 如果股票已存在，合并 articles（按 source 去重）
    3. 如果股票不存在，添加新股票
    """
    # 转换为字典，方便查找
    stocks_dict = {s['code']: s for s in existing_stocks}
    
    for new_stock in new_stocks:
        code = new_stock.get('code')
        if not code:
            continue
        
        if code in stocks_dict:
            # 股票已存在，合并文章
            existing_stock = stocks_dict[code]
            existing_articles = existing_stock.get('articles', [])
            new_articles = new_stock.get('articles', [])
            
            # 按 source 去重合并
            existing_sources = {a.get('source') for a in existing_articles}
            for article in new_articles:
                if article.get('source') not in existing_sources:
                    existing_articles.append(article)
                    existing_sources.add(article.get('source'))
            
            # 更新其他字段（如果新数据有值）
            for key in ['name', 'board', 'industry', 'concepts']:
                if new_stock.get(key):
                    existing_stock[key] = new_stock[key]
            
            # 更新 mention_count
            existing_stock['mention_count'] = existing_stock.get('mention_count', 0) + new_stock.get('mention_count', 0)
            
        else:
            # 新股票，直接添加
            stocks_dict[code] = new_stock
    
    return list(stocks_dict.values())


def update_github_json(json_path: str, github_token: str, github_repo: str, branch: str = "main") -> bool:
    """更新 GitHub 的 stocks_master.json"""
    
    # 读取本地 JSON（新数据）
    with open(json_path, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    new_stocks = new_data.get('stocks', [])
    print(f"📥 本地数据: {len(new_stocks)} 只股票")
    
    # 获取 GitHub 上的现有数据
    print(f"🔄 获取 GitHub 现有数据 (分支: {branch})...")
    existing_data, sha = fetch_github_json(github_token, github_repo, branch)
    
    if existing_data:
        existing_stocks = existing_data.get('stocks', [])
        print(f"   GitHub 现有: {len(existing_stocks)} 只股票")
        
        # 合并数据
        merged_stocks = merge_stocks(existing_stocks, new_stocks)
        print(f"   合并后: {len(merged_stocks)} 只股票")
    else:
        print(f"   GitHub 无现有数据，使用本地数据")
        merged_stocks = new_stocks
    
    # 构建最终数据
    final_data = {
        'stocks': merged_stocks,
        'meta': {
            'total': len(merged_stocks),
            'updated_at': datetime.now().isoformat(),
            'source': 'agent_merge'
        }
    }
    
    # 编码为 base64
    content = json.dumps(final_data, ensure_ascii=False, indent=2)
    content_bytes = content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
    
    # GitHub API 配置
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    file_path = 'data/master/stocks_master.json'
    url = f"https://api.github.com/repos/{github_repo}/contents/{file_path}"
    
    # 构建更新数据
    if sha:
        update_data = {
            'message': f'Merge stocks from Agent - {datetime.now().strftime("%Y-%m-%d %H:%M")} (+{len(new_stocks)} stocks, total {len(merged_stocks)})',
            'content': content_base64,
            'sha': sha,
            'branch': branch
        }
    else:
        update_data = {
            'message': f'Create stocks from Agent - {datetime.now().strftime("%Y-%m-%d %H:%M")} ({len(merged_stocks)} stocks)',
            'content': content_base64,
            'branch': branch
        }
    
    # 提交更新
    print(f"🔄 更新 GitHub...")
    response = requests.put(url, headers=headers, json=update_data)
    
    if response.status_code in [200, 201]:
        print(f"✅ GitHub 更新成功!")
        print(f"   新增: {len(new_stocks)} 只")
        print(f"   总计: {len(merged_stocks)} 只")
        print(f"   提交: {response.json()['commit']['html_url']}")
        return True
    else:
        print(f"❌ GitHub 更新失败: HTTP {response.status_code}")
        print(response.text)
        return False


def main():
    parser = argparse.ArgumentParser(description="合并本地 JSON 到 GitHub 的 stocks_master.json")
    parser.add_argument("--json", required=True, help="本地 JSON 文件路径")
    parser.add_argument("--github-token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--github-repo", default="treeie2/models_app", help="GitHub 仓库名")
    parser.add_argument("--branch", default="main", help="GitHub 分支名 (默认: main)")
    
    args = parser.parse_args()
    
    print("🚀 开始合并到 GitHub...")
    success = update_github_json(args.json, args.github_token, args.github_repo, args.branch)
    
    if success:
        print("\n✅ 完成!")
    else:
        print("\n❌ 失败!")
        exit(1)


if __name__ == "__main__":
    main()
