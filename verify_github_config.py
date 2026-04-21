#!/usr/bin/env python3
"""
验证所有 GitHub 配置是否指向正确的仓库
"""
import json
import re
from pathlib import Path

def check_config():
    """检查所有配置文件"""
    print("🔍 检查 GitHub 配置...\n")
    
    target_repo = "treeie2/app_stockapril"
    all_good = True
    
    # 1. 检查 config.json
    config_file = Path(".trae/skills/wechat-fetch-research-embedded/config.json")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        github_repo = config.get('github', {}).get('repo', '')
        if github_repo == target_repo:
            print(f"✅ config.json: {github_repo}")
        else:
            print(f"❌ config.json: {github_repo} (应该是 {target_repo})")
            all_good = False
    
    # 2. 检查 sync_to_github.py
    sync_file = Path(".trae/skills/wechat-fetch-research-embedded/scripts/sync_to_github.py")
    if sync_file.exists():
        with open(sync_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if f'github_repo: str = "{target_repo}"' in content:
            print(f"✅ sync_to_github.py (default): {target_repo}")
        else:
            print(f"❌ sync_to_github.py (default): 配置不正确")
            all_good = False
        
        if f'--github-repo", default="{target_repo}"' in content:
            print(f"✅ sync_to_github.py (argument): {target_repo}")
        else:
            print(f"❌ sync_to_github.py (argument): 配置不正确")
            all_good = False
    
    # 3. 检查 agent_store git remote
    agent_store_dir = Path("e:/github/agent_store")
    if agent_store_dir.exists():
        import subprocess
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=agent_store_dir,
            capture_output=True,
            text=True
        )
        
        if target_repo in result.stdout:
            print(f"✅ agent_store git remote: {target_repo}")
        else:
            print(f"❌ agent_store git remote: 配置不正确")
            all_good = False
    
    print("\n" + "="*60)
    if all_good:
        print("✅ 所有 GitHub 配置都正确指向：https://github.com/treeie2/app_stockapril")
    else:
        print("❌ 部分配置需要更新")
    print("="*60)
    
    return all_good

if __name__ == "__main__":
    check_config()
