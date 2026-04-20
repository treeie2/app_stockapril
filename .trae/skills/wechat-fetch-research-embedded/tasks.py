#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Celery tasks for async processing.

Usage:
    # Start worker
    celery -A tasks worker --loglevel=info
    
    # Start with flower monitoring
    celery -A tasks flower --port=5555
    
    # Submit task
    python -c "from tasks import process_article; process_article.delay('https://mp.weixin.qq.com/s/...')"
"""

import os
from celery import Celery
from celery.signals import task_prerun, task_postrun

# Configure Celery
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

app = Celery('wechat_fetch')
app.conf.update(
    broker_url=broker_url,
    result_backend=result_backend,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    worker_prefetch_multiplier=1,  # Process one task at a time per worker
)


@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **extras):
    """Log task start."""
    from scripts.logger import setup_logger
    logger = setup_logger()
    logger.info(f"[Celery] Task {task.name}[{task_id}] started with args={args}, kwargs={kwargs}")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **extras):
    """Log task completion."""
    from scripts.logger import setup_logger
    logger = setup_logger()
    logger.info(f"[Celery] Task {task.name}[{task_id}] finished with state={state}")


@app.task(bind=True, max_retries=3)
def process_article(self, url: str, sync_firestore: bool = False, sync_github: bool = False):
    """Process a single WeChat article.
    
    Args:
        url: WeChat article URL
        sync_firestore: Whether to sync to Firestore
        sync_github: Whether to sync to GitHub
    
    Returns:
        Result dictionary
    """
    from scripts.pipeline import run_pipeline
    from scripts.config import reset_config
    from scripts.logger import reset_logger
    
    # Reset singletons for clean state
    reset_config()
    reset_logger()
    
    try:
        result = run_pipeline(
            url=url,
            sync_firestore=sync_firestore,
            sync_github=sync_github,
            headless=True,  # Always headless in Celery
            timeout=300
        )
        
        if not result["success"]:
            # Retry on failure
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return result
        
    except Exception as exc:
        # Log and retry
        from scripts.logger import setup_logger
        logger = setup_logger()
        logger.error(f"[Celery] Task failed: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        raise


@app.task
def batch_process(urls: list, sync_firestore: bool = False, sync_github: bool = False):
    """Process multiple URLs in batch.
    
    Args:
        urls: List of WeChat article URLs
        sync_firestore: Whether to sync to Firestore
        sync_github: Whether to sync to GitHub
    
    Returns:
        List of results
    """
    results = []
    for url in urls:
        result = process_article.delay(url, sync_firestore, sync_github)
        results.append(result.id)
    return {"task_ids": results, "count": len(urls)}


@app.task
def cleanup_old_files(days: int = 7):
    """Clean up old raw_material and data files.
    
    Args:
        days: Delete files older than this many days
    """
    import os
    import time
    from datetime import datetime, timedelta
    from pathlib import Path
    from scripts.config import get_config
    from scripts.logger import setup_logger
    
    config = get_config()
    logger = setup_logger()
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    # Cleanup raw_material
    for file_path in Path(config.raw_material_dir).glob("raw_material_*.md"):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"[Cleanup] Deleted {file_path}")
        except Exception as e:
            logger.error(f"[Cleanup] Error deleting {file_path}: {e}")
    
    # Cleanup data files
    for file_path in Path(config.data_dir).glob("stocks_master_*.json"):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"[Cleanup] Deleted {file_path}")
        except Exception as e:
            logger.error(f"[Cleanup] Error deleting {file_path}: {e}")
    
    logger.info(f"[Cleanup] Total deleted: {deleted_count} files")
    return {"deleted": deleted_count}


if __name__ == "__main__":
    app.start()
