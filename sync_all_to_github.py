#!/usr/bin/env python3
"""
同步所有分片数据文件到 GitHub
"""
import shutil
import subprocess
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
    print("🚀 同步所有分片数据到 agent_store 并推送到 GitHub...\n")
    
    source_dir = Path("e:/github/stock-research-backup")
    target_dir = Path("e:/github/agent_store")
    
    # 获取所有 stocks 分片文件
    stocks_dir = source_dir / "data" / "master" / "stocks"
    all_stock_files = list(stocks_dir.glob("*.json"))
    
    print(f"📂 发现 {len(all_stock_files)} 个分片文件")
    print("\n📂 复制所有分片文件...")
    
    copied = 0
    for src_file in all_stock_files:
        rel_path = src_file.relative_to(source_dir)
        dst_file = target_dir / rel_path
        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied += 1
        except Exception as e:
            print(f"   ❌ {rel_path}: {e}")
    
    print(f"   ✅ 已复制 {copied} 个文件")
    
    # 复制索引文件
    index_file = source_dir / "data" / "master" / "stocks_index.json"
    if index_file.exists():
        dst_index = target_dir / "data" / "master" / "stocks_index.json"
        dst_index.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(index_file, dst_index)
        print(f"   ✅ stocks_index.json")
    
    # 复制热点文件
    hot_topics_file = source_dir / "data" / "hot_topics.json"
    if hot_topics_file.exists():
        dst_hot = target_dir / "data" / "hot_topics.json"
        dst_hot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(hot_topics_file, dst_hot)
        print(f"   ✅ hot_topics.json")
    
    # 复制模板文件
    template_items = [
        "templates/hot_topic_detail.html",
        "templates/dashboard.html",
    ]
    print("\n📂 复制模板文件...")
    for item in template_items:
        src = source_dir / item
        dst = target_dir / item
        if src.exists():
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"   ✅ {item}")
            except Exception as e:
                print(f"   ❌ {item}: {e}")
    
    # Git 操作
    print("\n🔄 Git 操作...")
    
    # git add
    if not run_command(["git", "add", "-A"], target_dir, "Git add"):
        return False
    
    # git commit
    result = subprocess.run(["git", "commit", "-m", f"同步所有分片数据: {copied}个文件, 3164只个股"],
                          cwd=target_dir, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode == 0:
        print("   ✅ Git commit 完成")
    else:
        print(f"   ⚠️ Commit: {result.stderr[:100] if result.stderr else '无变化或已提交'}")
    
    # git push to github main
    print("\n📤 推送到 GitHub...")
    result = subprocess.run(["git", "push", "github", "HEAD:main", "-f"],
                          cwd=target_dir, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode == 0:
        print("   ✅ Git push 完成")
        print("\n✅ 全部完成!")
        print(f"   已同步 {copied} 个分片文件到 GitHub")
        print("   包含 3164 只个股的完整数据")
    else:
        print(f"   ❌ Git push 失败: {result.stderr}")


if __name__ == "__main__":
    main()
