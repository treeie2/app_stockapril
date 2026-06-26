#!/usr/bin/env python3
"""Save industry knowledge to markdown + optionally push to GitHub."""
import json, re, sys, subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent.parent.parent
IND_DIR = BASE / 'raw_material' / 'industry'
IND_DIR.mkdir(parents=True, exist_ok=True)

def save_industry_knowledge(name, content):
    """Save a knowledge file."""
    title = re.sub(r'[\\/:*?"<>|]', '_', name)[:50]
    fp = IND_DIR / f'{title}.md'
    fp.write_text(content, encoding='utf-8')
    print(f'[OK] Saved {fp}')
    return str(fp)

def git_push(files, message='chore: update industry knowledge'):
    """Push saved files to GitHub."""
    try:
        subprocess.run(['git', 'add'] + files, cwd=str(BASE), capture_output=True, timeout=15)
        subprocess.run(['git', 'commit', '-m', message], cwd=str(BASE), capture_output=True, timeout=15)
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=str(BASE), capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print('[OK] Pushed to GitHub')
            return True
        else:
            print('[WARN] Push failed (will need manual push):', result.stderr.strip()[:200])
            return False
    except subprocess.TimeoutExpired:
        print('[WARN] Git push timed out')
        return False
    except FileNotFoundError:
        print('[WARN] Git not available')
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python save_knowledge.py <name> <content> [--push]')
        print('  --push   Also attempt git add/commit/push to GitHub')
        sys.exit(1)

    name = sys.argv[1]
    content = sys.argv[2]
    do_push = '--push' in sys.argv

    fp = save_industry_knowledge(name, content)

    if do_push:
        git_push([fp])
