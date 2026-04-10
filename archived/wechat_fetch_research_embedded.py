#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wechat-fetch-research-embedded runner

把微信公众号文章链接转成可结构化投研素材，并（可选）同步到 Firestore。

本脚本是对 skill 包（.skill）解包后的 **Python 脚本化版本** 的入口。

## 目录结构（与本文件同级）
- wechat-fetch-research-embedded/
  - scripts/
    - fetch_wechat_via_browser_dom.py
    - fetch_wechat_to_raw_material.py
    - extract_stocks_from_raw_material.py
    - sync_to_firestore.py
  - assets/全部个股.xls
  - references/数据结构规范_v2.md

## 依赖
- Python 3.10+
- playwright（已安装浏览器：`playwright install chromium`）
- firebase-admin（仅 sync_to_firestore 需要）

## 使用示例

1) 抓取正文 → raw_material

```bash
python wechat_fetch_research_embedded.py fetch \
  --url "https://mp.weixin.qq.com/s/xxx" \
  --out_raw "./raw_material/raw_material_YYYY-MM-DD.md"
```

2) 抽取结构化 → data/stocks_master

```bash
python wechat_fetch_research_embedded.py extract \
  --raw "./raw_material/raw_material_YYYY-MM-DD.md" \
  --out_json "./data/stocks_master_YYYY-MM-DD.json"
```

3) 同步到 Firestore（建议把凭证放在 workspace/secrets）

```bash
python wechat_fetch_research_embedded.py sync \
  --json "./data/stocks_master_YYYY-MM-DD.json" \
  --credentials "/home/user/workspace/secrets/firebase-credentials.json" \
  --on_exists merge
```
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL_DIR = ROOT / "wechat-fetch-research-embedded"
SCRIPTS_DIR = SKILL_DIR / "scripts"
ASSET_STOCK_XLS = SKILL_DIR / "assets" / "全部个股.xls"


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd)
    if p.returncode != 0:
        raise SystemExit(p.returncode)


def cmd_fetch(args: argparse.Namespace) -> None:
    tmp_txt = Path(args.tmp_txt).resolve()
    tmp_txt.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "fetch_wechat_via_browser_dom.py"),
            "--url",
            args.url,
            "--out_text",
            str(tmp_txt),
            "--user_data_dir",
            args.user_data_dir,
            "--timeout",
            str(args.timeout),
        ]
    )

    out_raw = Path(args.out_raw).resolve()
    out_raw.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "fetch_wechat_to_raw_material.py"),
            "--url",
            args.url,
            "--out",
            str(out_raw),
            "--manual_text_file",
            str(tmp_txt),
        ]
    )


def cmd_extract(args: argparse.Namespace) -> None:
    out_json = Path(args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "extract_stocks_from_raw_material.py"),
            "--raw",
            str(Path(args.raw).resolve()),
            "--stock_xls",
            str(ASSET_STOCK_XLS),
            "--out_json",
            str(out_json),
            "--mode",
            args.mode,
        ]
    )


def cmd_sync(args: argparse.Namespace) -> None:
    run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "sync_to_firestore.py"),
            "--credentials",
            args.credentials,
            "--json",
            str(Path(args.json).resolve()),
            "--collection",
            args.collection,
            "--article_subcollection",
            args.article_subcollection,
            "--on_exists",
            args.on_exists,
        ]
    )


def cmd_sync_github(args: argparse.Namespace) -> None:
    """同步到 Firebase 后，同时更新 GitHub"""
    # 先执行 Firestore 同步
    cmd_sync(args)
    
    # 然后更新 GitHub
    run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "sync_to_github.py"),
            "--json",
            str(Path(args.json).resolve()),
            "--github-token",
            args.github_token,
            "--github-repo",
            args.github_repo,
            "--branch",
            args.branch,
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_fetch = sub.add_parser("fetch", help="抓取公众号正文并落盘 raw_material")
    ap_fetch.add_argument("--url", required=True)
    ap_fetch.add_argument("--out_raw", required=True)
    ap_fetch.add_argument("--tmp_txt", default=str(ROOT / "tmp_article.txt"))
    ap_fetch.add_argument("--user_data_dir", default=str(ROOT / ".browser_profile_headless"))
    ap_fetch.add_argument("--timeout", type=int, default=300)
    ap_fetch.set_defaults(func=cmd_fetch)

    ap_ext = sub.add_parser("extract", help="从 raw_material 抽取个股结构化并 merge JSON")
    ap_ext.add_argument("--raw", required=True)
    ap_ext.add_argument("--out_json", required=True)
    ap_ext.add_argument("--mode", choices=["merge", "overwrite"], default="merge")
    ap_ext.set_defaults(func=cmd_extract)

    ap_sync = sub.add_parser("sync", help="把 stocks_master JSON 增量同步到 Firestore")
    ap_sync.add_argument("--json", required=True)
    ap_sync.add_argument("--credentials", required=True)
    ap_sync.add_argument("--collection", default="stocks")
    ap_sync.add_argument("--article_subcollection", default="articles")
    ap_sync.add_argument("--on_exists", choices=["skip", "update", "merge"], default="merge")
    ap_sync.set_defaults(func=cmd_sync)

    ap_sync_gh = sub.add_parser("sync-github", help="同步到 Firestore 并更新 GitHub")
    ap_sync_gh.add_argument("--json", required=True)
    ap_sync_gh.add_argument("--credentials", required=True)
    ap_sync_gh.add_argument("--collection", default="stocks")
    ap_sync_gh.add_argument("--article_subcollection", default="articles")
    ap_sync_gh.add_argument("--on_exists", choices=["skip", "update", "merge"], default="merge")
    ap_sync_gh.add_argument("--github-token", required=True, help="GitHub Personal Access Token")
    ap_sync_gh.add_argument("--github-repo", default="treeie2/models_app", help="GitHub 仓库名")
    ap_sync_gh.add_argument("--branch", default="main", help="GitHub 分支名 (默认: main)")
    ap_sync_gh.set_defaults(func=cmd_sync_github)

    return ap


def main() -> None:
    ap = build_parser()
    args = ap.parse_args()

    if not SKILL_DIR.exists():
        raise SystemExit(f"Missing directory: {SKILL_DIR}")
    if not ASSET_STOCK_XLS.exists():
        raise SystemExit(f"Missing embedded stock list: {ASSET_STOCK_XLS}")

    args.func(args)


if __name__ == "__main__":
    main()
