#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main pipeline orchestrator for wechat-fetch-research-embedded skill.

This module provides a unified interface for the complete workflow:
1. Fetch article content
2. Extract stock information
3. (NEW) Incremental merge to date-based shards
4. Sync to Firestore (optional)
5. Sync to GitHub shards (optional)

Usage:
    python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..."
    python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --sync-firestore --sync-github
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.config import get_config, reset_config
from scripts.logger import get_logger, reset_logger, setup_logger


def run_pipeline(
    url: str,
    sync_firestore: bool = False,
    sync_github: bool = False,
    headless: bool = True,
    timeout: int = 300,
    use_shards: bool = True
) -> dict:
    """Run the complete pipeline for a single URL.
    
    Args:
        url: WeChat article URL
        sync_firestore: Whether to sync to Firestore
        sync_github: Whether to sync to GitHub
        headless: Run browser in headless mode
        timeout: Browser timeout in seconds
        use_shards: Use new date-based shard storage (default: True)
    
    Returns:
        Result dictionary with status and details
    """
    config = get_config()
    logger = get_logger()
    
    result = {
        "url": url,
        "success": False,
        "stocks_found": 0,
        "errors": [],
        "output_files": {},
        "shard_info": None
    }
    
    try:
        # Step 1: Fetch article content
        logger.info(f"[Pipeline] Step 1: Fetching article from {url}")
        
        from scripts.fetch_wechat_via_browser_dom import main_async
        import asyncio
        
        tmp_file = config.raw_material_dir / "tmp_article.txt"
        profile_dir = config.raw_material_dir / ".browser_profile"
        
        asyncio.run(main_async(
            url=url,
            out_text=str(tmp_file),
            user_data_dir=str(profile_dir),
            timeout=timeout,
            headless=headless
        ))
        
        if not tmp_file.exists():
            raise RuntimeError("Failed to fetch article content")
        
        logger.info(f"[Pipeline] Article fetched successfully")
        
        # Step 2: Convert to raw_material format
        logger.info(f"[Pipeline] Step 2: Converting to raw_material format")
        
        from scripts.fetch_wechat_to_raw_material import main as raw_material_main
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        raw_material_file = config.raw_material_dir / f"raw_material_{today}.md"
        
        class Args:
            url = url
            out = str(raw_material_file)
            mcp_server = None
            mcp_tool = None
            manual_text_file = str(tmp_file)
        
        raw_material_main(Args())
        
        if not raw_material_file.exists():
            raise RuntimeError("Failed to create raw_material file")
        
        result["output_files"]["raw_material"] = str(raw_material_file)
        logger.info(f"[Pipeline] Raw material saved to {raw_material_file}")
        
        # Step 3: Extract stock information
        logger.info(f"[Pipeline] Step 3: Extracting stock information")
        
        from scripts.extract_stocks_from_raw_material import main as extract_main
        
        stocks_file = config.data_dir / f"stocks_master_{today}.json"
        
        class ExtractArgs:
            raw = str(raw_material_file)
            stock_xls = str(config.stock_xls_path)
            out_json = str(stocks_file)
            mode = config.extraction_mode
            config = None
        
        extract_main(ExtractArgs())
        
        if not stocks_file.exists():
            raise RuntimeError("Failed to extract stock information")
        
        result["output_files"]["stocks_json"] = str(stocks_file)
        logger.info(f"[Pipeline] Stock data saved to {stocks_file}")
        
        # Count stocks
        import json
        with open(stocks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            result["stocks_found"] = len(data.get("stocks", []))
        
        # Step 3.5: Incremental merge to date-based shards (NEW)
        if use_shards:
            logger.info(f"[Pipeline] Step 3.5: Incremental merge to shards")
            
            from scripts.incremental_update import IncrementalUpdater
            
            master_base_dir = Path(config.data_dir).parent / "master"
            updater = IncrementalUpdater(base_dir=str(master_base_dir))
            
            shard_stats = updater.merge_from_json(str(stocks_file))
            result["shard_info"] = shard_stats
            result["output_files"]["daily_shard"] = shard_stats.get("daily_file")
            result["output_files"]["index_file"] = shard_stats.get("index_file")
            
            logger.info(f"[Pipeline] Shard merge completed: +{shard_stats['new_stocks']} new, ~{shard_stats['updated_stocks']} updated")
        
        # Step 4: Sync to Firestore (optional)
        if sync_firestore:
            logger.info(f"[Pipeline] Step 4: Syncing to Firestore")
            
            from scripts.sync_to_firestore import main as firestore_main
            
            class FirestoreArgs:
                credentials = config.firebase_credentials_path
                json = str(stocks_file)
                collection = "stocks"
                article_subcollection = "articles"
                on_exists = "merge"
            
            firestore_main(FirestoreArgs())
            logger.info(f"[Pipeline] Firestore sync completed")
        
        # Step 5: Sync to GitHub (optional) - now supports shard mode
        if sync_github:
            logger.info(f"[Pipeline] Step 5: Syncing to GitHub")
            
            from scripts.sync_to_github import main as github_main
            
            if use_shards:
                master_base_dir = str(Path(config.data_dir).parent / "master")
                
                class GithubArgs:
                    mode = "shard"
                    github_token = config.github_token
                    github_repo = config.github_repo
                    branch = "main"
                    base_dir = master_base_dir
                    days = 1
                    json = None
            else:
                class GithubArgs:
                    mode = "single"
                    json = str(stocks_file)
                    github_token = config.github_token
                    github_repo = config.github_repo
                    branch = "main"
                    base_dir = None
                    days = 1
            
            github_main(GithubArgs())
            logger.info(f"[Pipeline] GitHub sync completed")
        
        result["success"] = True
        mode_str = "shard" if use_shards else "single-file"
        logger.info(f"[Pipeline] Pipeline completed successfully ({mode_str} mode). Found {result['stocks_found']} stocks.")
        
        if tmp_file.exists():
            tmp_file.unlink()
        
    except Exception as e:
        error_msg = str(e)
        result["errors"].append(error_msg)
        logger.error(f"[Pipeline] Error: {error_msg}")
    
    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="WeChat Article Research Pipeline (v2 - 支持分片存储)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (默认使用分片存储)
  python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..."
  
  # With Firestore sync
  python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --sync-firestore
  
  # With GitHub sync (分片模式)
  python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --sync-github
  
  # Full pipeline with all syncs
  python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --sync-firestore --sync-github
  
  # Non-headless mode (for first-time login)
  python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --no-headless
  
  # Legacy single-file mode (不使用分片)
  python scripts/pipeline.py --url "https://mp.weixin.qq.com/s/..." --no-shards --sync-github
        """
    )
    
    parser.add_argument("--url", required=True, help="WeChat article URL")
    parser.add_argument("--sync-firestore", action="store_true", help="Sync to Firestore")
    parser.add_argument("--sync-github", action="store_true", help="Sync to GitHub")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    parser.add_argument("--timeout", type=int, default=300, help="Browser timeout (seconds)")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    parser.add_argument("--log-file", help="Log file path")
    parser.add_argument("--no-shards", action="store_true", 
                       help="Use legacy single-file mode instead of date-based shards")
    
    args = parser.parse_args()
    
    reset_config()
    reset_logger()
    setup_logger(level=args.log_level, log_file=args.log_file)
    
    result = run_pipeline(
        url=args.url,
        sync_firestore=args.sync_firestore,
        sync_github=args.sync_github,
        headless=not args.no_headless,
        timeout=args.timeout,
        use_shards=not args.no_shards
    )
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()