"""仓库大清理 - 删除冗余文件"""
import os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'e:\github\stock-research-backup'
os.chdir(ROOT)
saved = 0

def rm(path):
    """安全删除，统计节省空间"""
    global saved
    if os.path.isdir(path):
        size = sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(path) for f in fs)
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        size = os.path.getsize(path)
        os.remove(path)
    else:
        return
    saved += size
    print(f'  - {path} ({size//1024}KB)')

# ============================================================
# 1. 过期 stocks_master_YYYY-MM-DD.json（保留 stocks_master_friday 和主文件）
# ============================================================
print('[1] Deleting stale intermediate JSON...')
for d in ['data', '.trae/skills/wechat-fetch-research-embedded/data']:
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.startswith('stocks_master_202') and f.endswith('.json'):
                # 保留 friday 备份
                if 'friday' in f:
                    continue
                rm(os.path.join(d, f))

# 2. 多余 .gz 副本
print('[2] Deleting duplicate .gz files...')
for path in ['api/stocks_master.json.gz', 'static/stocks_master.json.gz']:
    if os.path.exists(path):
        rm(path)

# 3. 重复 wind-mcp-skill 目录（保留 .agents/ 下的）
print('[3] Deleting duplicate wind-mcp-skill dirs...')
for path in [
    '.codeartsdoer/skills/wind-mcp-skill',
    '.codebuddy/skills/wind-mcp-skill',
    '.trae/skills/wind-mcp-skill',
    'skills/wind-mcp-skill'
]:
    if os.path.exists(path):
        rm(path)

# 4. Site-packages, __pycache__, node_modules in unexpected places
print('[4] Deleting local Python site-packages and caches...')
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root:
        continue
    for d in dirs:
        if d in ('__pycache__', 'site-packages'):
            rm(os.path.join(root, d))
    for f in files:
        if f.endswith('.pyc') or f.endswith('.pyo'):
            rm(os.path.join(root, f))

# 5. archived/data_backups 中的旧备份
print('[5] Deleting archived stock backups (keeping only archived/同花顺/所属概念)...')
backup_dir = 'archived/data_backups'
if os.path.isdir(backup_dir):
    for f in os.listdir(backup_dir):
        rm(os.path.join(backup_dir, f))

# 6. raw_material 中的过期文章（保留 6月13日 batch100）
print('[6] Deleting stale raw_material files...')
for d in ['raw_material', '.trae/skills/wechat-fetch-research-embedded/raw_material']:
    if os.path.isdir(d):
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if os.path.isdir(fp):
                continue
            # 只保留 2026-06-13 batch100 和 tmp_article.txt
            if '2026-06-13' in f or f == 'tmp_article.txt':
                continue
            if f.endswith('.md') or f.startswith('test_') or f.startswith('tmp_'):
                rm(fp)

# 7. .trae/skills 下的过期 lark 技能（已删除）
print('[7] Deleting stale skill temp files...')
skill_dir = '.trae/skills/wechat-fetch-research-embedded'
for f in ['tmp_article.txt', 'tmp_article1.txt', 'tmp_article2.txt',
          'tmp_article3.txt', 'tmp_article4.txt', 'tmp_article5.txt',
          'tmp_article6.txt']:
    fp = os.path.join(skill_dir, f)
    if os.path.exists(fp):
        rm(fp)

# 8. 删除大文件 stocks_master_friday.json (已合并到主文件)
print('[8] Deleting redundant large backups...')
for f in ['data/stocks_master_friday.json', 'data/stocks_master_friday.json.gz',
          'data/stocks/stocks_master.min.json']:
    if os.path.exists(f):
        rm(f)

# ============================================================
# 汇总
# ============================================================
print(f'\n{"="*40}')
print(f'Total saved: {saved//1024//1024}MB')
print('Done.')
