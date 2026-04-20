#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cloudflare R2 同步脚本 - 用于 raw_material 云端存储

R2 特点:
- 10GB 免费存储
- 无出口流量费 (下载免费)
- S3 兼容 API
- 国内访问速度快

使用方式:
    # 上传单个文件
    python scripts/sync_to_r2.py \
      --mode upload \
      --file "raw_material/raw_material_2026-04-17.md"
    
    # 上传整个目录
    python scripts/sync_to_r2.py \
      --mode upload-dir \
      --dir "raw_material"
    
    # 下载单个文件
    python scripts/sync_to_r2.py \
      --mode download \
      --key "raw_material_2026-04-17.md" \
      --output "raw_material/raw_material_2026-04-17.md"
    
    # 列出所有文件
    python scripts/sync_to_r2.py \
      --mode list
    
    # 同步本地目录到 R2 (增量)
    python scripts/sync_to_r2.py \
      --mode sync-up \
      --dir "raw_material"
    
    # 从 R2 同步到本地 (增量)
    python scripts/sync_to_r2.py \
      --mode sync-down \
      --dir "raw_material"

环境变量配置 (.env):
    R2_ACCOUNT_ID=your_account_id
    R2_ACCESS_KEY_ID=your_access_key
    R2_SECRET_ACCESS_KEY=your_secret_key
    R2_BUCKET_NAME=stock-research
    R2_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_r2_config():
    """加载 R2 配置（支持环境变量和 config.json）"""
    config = {}
    
    # 1. 尝试从环境变量读取
    config['account_id'] = os.environ.get('R2_ACCOUNT_ID')
    config['access_key'] = os.environ.get('R2_ACCESS_KEY_ID')
    config['secret_key'] = os.environ.get('R2_SECRET_ACCESS_KEY')
    config['bucket'] = os.environ.get('R2_BUCKET_NAME', 'stock-research')
    config['endpoint_url'] = os.environ.get('R2_ENDPOINT_URL')
    
    # 2. 如果环境变量不完整，尝试从 config.json 读取
    if not all([config['account_id'], config['access_key'], config['secret_key']]):
        config_path = Path(__file__).parent.parent / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                r2_config = json_config.get('r2', {})
                config['account_id'] = config['account_id'] or r2_config.get('account_id')
                config['access_key'] = config['access_key'] or r2_config.get('access_key_id')
                config['secret_key'] = config['secret_key'] or r2_config.get('secret_access_key')
                config['bucket'] = config['bucket'] or r2_config.get('bucket_name', 'stock-research')
                config['endpoint_url'] = config['endpoint_url'] or r2_config.get('endpoint_url')
                config['verify_ssl'] = r2_config.get('verify_ssl', True)
            except Exception:
                pass
    
    return config


def get_r2_client():
    """创建 R2 客户端"""
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("❌ 请先安装 boto3: pip install boto3")
        sys.exit(1)
    
    config = load_r2_config()
    
    account_id = config['account_id']
    access_key = config['access_key']
    secret_key = config['secret_key']
    
    if not all([account_id, access_key, secret_key]):
        print("❌ 缺少 R2 配置")
        print("   方式1: 设置环境变量 R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY")
        print("   方式2: 在 config.json 中添加 r2 配置")
        sys.exit(1)
    
    # 检查是否需要禁用 SSL 验证（Windows 开发环境可能需要）
    verify_ssl = config.get('verify_ssl', True)
    
    # 始终使用 HTTPS，但可以选择禁用证书验证
    endpoint_url = config['endpoint_url'] or f"https://{account_id}.r2.cloudflarestorage.com"
    
    boto_config = Config(
        retries={'max_attempts': 3, 'mode': 'standard'},
        connect_timeout=10,
        read_timeout=30
    )
    
    client_kwargs = {
        'service_name': 's3',
        'endpoint_url': endpoint_url,
        'aws_access_key_id': access_key,
        'aws_secret_access_key': secret_key,
        'config': boto_config,
        'region_name': 'auto',
        'use_ssl': True
    }
    
    # 如果禁用 SSL 验证
    if not verify_ssl:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        client_kwargs['verify'] = False
        print("⚠️  SSL 证书验证已禁用（仅用于开发测试）")
    
    client = boto3.client(**client_kwargs)
    
    return client


def get_bucket_name() -> str:
    """获取 bucket 名称"""
    config = load_r2_config()
    return config.get('bucket', 'stock-research')


class R2Syncer:
    """R2 同步器"""
    
    def __init__(self):
        self.client = get_r2_client()
        self.bucket = get_bucket_name()
        self.stats = {"uploaded": 0, "downloaded": 0, "skipped": 0, "errors": 0}
    
    def upload_file(self, local_path: str, key: Optional[str] = None, 
                    prefix: str = "raw_material") -> bool:
        """上传单个文件到 R2
        
        Args:
            local_path: 本地文件路径
            key: R2 中的 key (默认使用文件名)
            prefix: key 前缀
            
        Returns:
            是否成功
        """
        file_path = Path(local_path)
        if not file_path.exists():
            print(f"❌ 文件不存在: {local_path}")
            self.stats["errors"] += 1
            return False
        
        if key is None:
            key = f"{prefix}/{file_path.name}"
        
        # 获取本地文件大小
        local_size = file_path.stat().st_size
        
        # 检查文件是否已存在且相同
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=key)
            remote_size = response.get('ContentLength', 0)
            
            if remote_size == local_size:
                print(f"⏭️ 跳过 (相同): {key}")
                self.stats["skipped"] += 1
                return True
        except self.client.exceptions.ClientError:
            pass  # 文件不存在，继续上传
        
        # 上传文件
        try:
            content_type = self._get_content_type(file_path.suffix)
            
            with open(file_path, 'rb') as f:
                self.client.put_object(
                    Bucket=self.bucket,
                    Key=key,
                    Body=f,
                    ContentType=content_type,
                    Metadata={
                        'uploaded_at': datetime.now().isoformat(),
                        'original_name': file_path.name
                    }
                )
            
            print(f"✅ 上传成功: {key} ({local_size} bytes)")
            self.stats["uploaded"] += 1
            return True
            
        except Exception as e:
            print(f"❌ 上传失败: {key} - {e}")
            self.stats["errors"] += 1
            return False
    
    def download_file(self, key: str, output_path: str) -> bool:
        """从 R2 下载文件
        
        Args:
            key: R2 中的 key
            output_path: 本地保存路径
            
        Returns:
            是否成功
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read()
            
            with open(output_file, 'wb') as f:
                f.write(content)
            
            print(f"✅ 下载成功: {key} -> {output_path} ({len(content)} bytes)")
            self.stats["downloaded"] += 1
            return True
            
        except self.client.exceptions.NoSuchKey:
            print(f"❌ 文件不存在: {key}")
            self.stats["errors"] += 1
            return False
        except Exception as e:
            print(f"❌ 下载失败: {key} - {e}")
            self.stats["errors"] += 1
            return False
    
    def list_files(self, prefix: str = "raw_material/") -> List[Dict[str, Any]]:
        """列出 R2 中的文件
        
        Args:
            prefix: 前缀过滤
            
        Returns:
            文件列表
        """
        files = []
        
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'etag': obj['ETag']
                    })
            
            return files
            
        except Exception as e:
            print(f"❌ 列出文件失败: {e}")
            return []
    
    def upload_directory(self, local_dir: str, prefix: str = "raw_material") -> bool:
        """上传整个目录到 R2
        
        Args:
            local_dir: 本地目录路径
            prefix: R2 中的前缀
            
        Returns:
            是否全部成功
        """
        dir_path = Path(local_dir)
        if not dir_path.exists():
            print(f"❌ 目录不存在: {local_dir}")
            return False
        
        md_files = list(dir_path.glob("*.md"))
        print(f"📁 发现 {len(md_files)} 个 .md 文件\n")
        
        success_count = 0
        for file_path in md_files:
            key = f"{prefix}/{file_path.name}"
            if self.upload_file(str(file_path), key):
                success_count += 1
        
        print(f"\n📊 上传完成: {success_count}/{len(md_files)} 成功")
        return success_count == len(md_files)
    
    def sync_up(self, local_dir: str, prefix: str = "raw_material") -> bool:
        """增量同步本地到 R2
        
        Args:
            local_dir: 本地目录
            prefix: R2 前缀
            
        Returns:
            是否成功
        """
        dir_path = Path(local_dir)
        if not dir_path.exists():
            print(f"❌ 目录不存在: {local_dir}")
            return False
        
        # 获取 R2 上的文件列表
        print("🔄 获取 R2 文件列表...")
        remote_files = {f['key']: f for f in self.list_files(prefix + "/")}
        print(f"   R2 上已有 {len(remote_files)} 个文件")
        
        # 扫描本地文件
        local_files = list(dir_path.glob("*.md"))
        print(f"   本地有 {len(local_files)} 个文件\n")
        
        # 上传新文件或修改过的文件
        for file_path in local_files:
            key = f"{prefix}/{file_path.name}"
            local_mtime = file_path.stat().st_mtime
            local_size = file_path.stat().st_size
            
            if key in remote_files:
                remote_size = remote_files[key]['size']
                if local_size == remote_size:
                    print(f"⏭️ 跳过 (相同): {file_path.name}")
                    self.stats["skipped"] += 1
                    continue
            
            self.upload_file(str(file_path), key)
        
        print(f"\n📊 同步完成:")
        print(f"   上传: {self.stats['uploaded']}")
        print(f"   跳过: {self.stats['skipped']}")
        print(f"   错误: {self.stats['errors']}")
        
        return self.stats["errors"] == 0
    
    def sync_down(self, local_dir: str, prefix: str = "raw_material") -> bool:
        """增量同步 R2 到本地
        
        Args:
            local_dir: 本地目录
            prefix: R2 前缀
            
        Returns:
            是否成功
        """
        dir_path = Path(local_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # 获取 R2 文件列表
        print("🔄 获取 R2 文件列表...")
        remote_files = self.list_files(prefix + "/")
        print(f"   R2 上有 {len(remote_files)} 个文件\n")
        
        # 下载每个文件
        for file_info in remote_files:
            key = file_info['key']
            filename = Path(key).name
            local_path = dir_path / filename
            
            # 检查本地是否已存在且相同
            if local_path.exists():
                local_size = local_path.stat().st_size
                if local_size == file_info['size']:
                    print(f"⏭️ 跳过 (相同): {filename}")
                    self.stats["skipped"] += 1
                    continue
            
            self.download_file(key, str(local_path))
        
        print(f"\n📊 同步完成:")
        print(f"   下载: {self.stats['downloaded']}")
        print(f"   跳过: {self.stats['skipped']}")
        print(f"   错误: {self.stats['errors']}")
        
        return self.stats["errors"] == 0
    
    def delete_file(self, key: str) -> bool:
        """删除 R2 上的文件
        
        Args:
            key: 文件 key
            
        Returns:
            是否成功
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            print(f"🗑️ 已删除: {key}")
            return True
        except Exception as e:
            print(f"❌ 删除失败: {key} - {e}")
            return False
    
    def get_public_url(self, key: str) -> Optional[str]:
        """获取文件的公开访问 URL
        
        Args:
            key: 文件 key
            
        Returns:
            公开 URL 或 None
        """
        try:
            # 生成预签名 URL (7天有效)
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=604800  # 7天
            )
            return url
        except Exception as e:
            print(f"❌ 生成 URL 失败: {e}")
            return None
    
    def _get_content_type(self, suffix: str) -> str:
        """根据文件后缀获取 Content-Type"""
        mime_types = {
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.html': 'text/html',
            '.csv': 'text/csv'
        }
        return mime_types.get(suffix.lower(), 'application/octet-stream')
    
    def print_stats(self):
        """打印统计信息"""
        print(f"\n{'='*50}")
        print("R2 同步统计")
        print(f"{'='*50}")
        print(f"上传: {self.stats['uploaded']}")
        print(f"下载: {self.stats['downloaded']}")
        print(f"跳过: {self.stats['skipped']}")
        print(f"错误: {self.stats['errors']}")


def main():
    parser = argparse.ArgumentParser(
        description="Cloudflare R2 同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 上传单个文件
  python scripts/sync_to_r2.py --mode upload --file "raw_material/2026-04-17.md"
  
  # 上传整个目录
  python scripts/sync_to_r2.py --mode upload-dir --dir "raw_material"
  
  # 下载单个文件
  python scripts/sync_to_r2.py --mode download --key "raw_material/2026-04-17.md" \
    --output "raw_material/2026-04-17.md"
  
  # 列出所有文件
  python scripts/sync_to_r2.py --mode list
  
  # 增量同步本地到 R2 (推荐日常使用)
  python scripts/sync_to_r2.py --mode sync-up --dir "raw_material"
  
  # 增量同步 R2 到本地
  python scripts/sync_to_r2.py --mode sync-down --dir "raw_material"
  
  # 获取文件公开 URL
  python scripts/sync_to_r2.py --mode url --key "raw_material/2026-04-17.md"
        """
    )
    
    parser.add_argument("--mode", required=True,
                       choices=["upload", "upload-dir", "download", "list", 
                               "sync-up", "sync-down", "delete", "url"],
                       help="操作模式")
    parser.add_argument("--file", help="本地文件路径 (upload/download)")
    parser.add_argument("--dir", help="本地目录路径 (upload-dir/sync-up/sync-down)")
    parser.add_argument("--key", help="R2 中的文件 key")
    parser.add_argument("--output", help="下载保存路径 (download)")
    parser.add_argument("--prefix", default="raw_material", help="R2 前缀 (默认: raw_material)")
    
    args = parser.parse_args()
    
    syncer = R2Syncer()
    
    print(f"🚀 R2 同步工具 - 模式: {args.mode}\n")
    
    success = False
    
    if args.mode == "upload":
        if not args.file:
            print("❌ --mode upload 需要 --file 参数")
            sys.exit(1)
        key = args.key or f"{args.prefix}/{Path(args.file).name}"
        success = syncer.upload_file(args.file, key)
        
    elif args.mode == "upload-dir":
        if not args.dir:
            print("❌ --mode upload-dir 需要 --dir 参数")
            sys.exit(1)
        success = syncer.upload_directory(args.dir, args.prefix)
        
    elif args.mode == "download":
        if not args.key or not args.output:
            print("❌ --mode download 需要 --key 和 --output 参数")
            sys.exit(1)
        success = syncer.download_file(args.key, args.output)
        
    elif args.mode == "list":
        files = syncer.list_files(args.prefix + "/")
        print(f"\n📋 R2 文件列表 ({len(files)} 个):\n")
        for f in files:
            size_kb = f['size'] / 1024
            print(f"   {f['key']} ({size_kb:.1f} KB) - {f['last_modified'][:10]}")
        success = True
        
    elif args.mode == "sync-up":
        if not args.dir:
            print("❌ --mode sync-up 需要 --dir 参数")
            sys.exit(1)
        success = syncer.sync_up(args.dir, args.prefix)
        
    elif args.mode == "sync-down":
        if not args.dir:
            print("❌ --mode sync-down 需要 --dir 参数")
            sys.exit(1)
        success = syncer.sync_down(args.dir, args.prefix)
        
    elif args.mode == "delete":
        if not args.key:
            print("❌ --mode delete 需要 --key 参数")
            sys.exit(1)
        success = syncer.delete_file(args.key)
        
    elif args.mode == "url":
        if not args.key:
            print("❌ --mode url 需要 --key 参数")
            sys.exit(1)
        url = syncer.get_public_url(args.key)
        if url:
            print(f"\n🔗 预签名 URL (7天有效):\n   {url}")
            success = True
    
    syncer.print_stats()
    
    if success:
        print("\n✅ 完成!")
    else:
        print("\n❌ 失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
