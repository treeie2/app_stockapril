#!/usr/bin/env python3
"""
同步数据并推送到 GitHub
"""
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd, description):
    """运行命令"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0:
        print(f"   ❌ {description} 失败: {result.stderr[:200]}")
        return False
    print(f"   ✅ {description} 完成")
    return True


def main():
    """主函数"""
    print("🚀 同步数据并推送到 GitHub...\n")
    
    source_dir = Path("e:/github/stock-research-backup")
    target_dir = Path("e:/github/agent_store")
    
    # 复制数据文件
    print("📂 复制数据文件...")
    src_file = source_dir / "data/master/stocks_master.json"
    dst_file = target_dir / "data/master/stocks_master.json"
    
    try:
        shutil.copy2(src_file, dst_file)
        print(f"   ✅ stocks_master.json 已复制")
    except Exception as e:
        print(f"   ❌ 复制失败: {e}")
        return False
    
    # Git 操作
    print("\n🔄 Git 操作...")
    
    # git add
    if not run_command(["git", "add", "data/master/stocks_master.json"], target_dir, "Git add"):
        return False
    
    # git commit
    result = subprocess.run(["git", "commit", "-m", "添加嘉元科技等9只股票数据，更新铜箔和算力板块"],
                          cwd=target_dir, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode == 0:
        print("   ✅ Git commit 完成")
    else:
        if "nothing to commit" in result.stderr.lower() or "nothing to commit" in result.stdout.lower():
            print("   ⚠️ 没有需要提交的更改")
        else:
            print(f"   ⚠️ Commit: {result.stderr[:100]}")
    
    # git push to github main
    print("\n📤 推送到 GitHub...")
    result = subprocess.run(["git", "push", "github", "HEAD:main", "-f"],
                          cwd=target_dir, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode == 0:
        print("   ✅ Git push 完成")
        print("\n✅ 全部完成!")
        print("   代码已推送到 GitHub")
        print("   Vercel 会自动重新部署")
        return True
    else:
        print(f"   ❌ Git push 失败: {result.stderr[:200]}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
