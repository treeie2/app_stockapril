#!/usr/bin/env python3
"""
同步代码到 agent_store 并推送到 GitHub
"""
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd, description):
    """运行命令"""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ❌ {description} 失败: {result.stderr}")
        return False
    print(f"   ✅ {description} 完成")
    return True


def main():
    """主函数"""
    print("🚀 同步代码到 agent_store 并推送到 GitHub...\n")
    
    source_dir = Path("e:/github/stock-research-backup")
    target_dir = Path("e:/github/agent_store")
    
    # 要复制的文件
    files_to_copy = [
        "main.py",
        "utils.py",
        "concept_extractor.py",
        "industry_mapper.py",
        "requirements.txt",
        "Dockerfile",
        "vercel.json",
        "templates/dashboard.html",
    ]
    
    print("📂 复制文件...")
    for file in files_to_copy:
        src = source_dir / file
        dst = target_dir / file
        if src.exists():
            try:
                if src.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"   ✅ {file}")
            except Exception as e:
                print(f"   ❌ {file}: {e}")
        else:
            print(f"   ⚠️ {file} 不存在")
    
    # Git 操作
    print("\n🔄 Git 操作...")
    
    # git add
    if not run_command(["git", "add", "-A"], target_dir, "Git add"):
        return False
    
    # git commit
    result = subprocess.run(["git", "commit", "-m", "添加全文搜索功能，清理项目文件"],
                          cwd=target_dir, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git commit 完成")
    else:
        print(f"   ⚠️ Commit: {result.stderr}")
    
    # git push to github main
    print("\n📤 推送到 GitHub...")
    result = subprocess.run(["git", "push", "github", "HEAD:main", "-f"],
                          cwd=target_dir, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Git push 完成")
        print("\n✅ 全部完成!")
        print("   代码已推送到 GitHub")
        print("   Vercel 会自动重新部署")
        return True
    else:
        print(f"   ❌ Git push 失败: {result.stderr}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
