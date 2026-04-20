#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configuration management with environment variable support for server deployment.

优先级（从高到低）：
1. 环境变量
2. config.json 文件
3. 默认值
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def get_env_or_default(key: str, default: Any = None) -> Any:
    """Get value from environment variable or return default."""
    return os.environ.get(key, default)


def load_json_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from config.json file."""
    if config_path is None:
        # 默认在脚本所在目录的父目录查找
        config_path = Path(__file__).parent.parent / "config.json"
    else:
        config_path = Path(config_path)
    
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


class Config:
    """Server-friendly configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.file_config = load_json_config(config_path)
    
    # API Configuration
    @property
    def primary_api_key(self) -> str:
        return get_env_or_default(
            "PRIMARY_API_KEY",
            self.file_config.get("api", {}).get("api_key", "")
        )
    
    @property
    def primary_base_url(self) -> str:
        return get_env_or_default(
            "PRIMARY_BASE_URL",
            self.file_config.get("api", {}).get("base_url", "")
        )
    
    @property
    def primary_model(self) -> str:
        return get_env_or_default(
            "PRIMARY_MODEL",
            self.file_config.get("api", {}).get("model", "deepseek-v3-2-251201")
        )
    
    @property
    def fallback_api_key(self) -> str:
        return get_env_or_default(
            "FALLBACK_API_KEY",
            self.file_config.get("fallback_api", {}).get("api_key", "")
        )
    
    @property
    def fallback_base_url(self) -> str:
        return get_env_or_default(
            "FALLBACK_BASE_URL",
            self.file_config.get("fallback_api", {}).get("base_url", "")
        )
    
    @property
    def fallback_model(self) -> str:
        return get_env_or_default(
            "FALLBACK_MODEL",
            self.file_config.get("fallback_api", {}).get("model", "Qwen/Qwen2.5-72B-Instruct")
        )
    
    # Firebase Configuration
    @property
    def firebase_credentials_path(self) -> str:
        return get_env_or_default(
            "FIREBASE_CREDENTIALS_PATH",
            "/secrets/firebase-credentials.json"
        )
    
    # GitHub Configuration
    @property
    def github_token(self) -> str:
        return get_env_or_default("GITHUB_TOKEN", "")
    
    @property
    def github_repo(self) -> str:
        return get_env_or_default(
            "GITHUB_REPO",
            self.file_config.get("github", {}).get("repo", "")
        )
    
    # Paths
    @property
    def data_dir(self) -> Path:
        return Path(get_env_or_default("DATA_DIR", "data"))
    
    @property
    def raw_material_dir(self) -> Path:
        return Path(get_env_or_default("RAW_MATERIAL_DIR", "raw_material"))
    
    @property
    def stock_xls_path(self) -> Path:
        return Path(get_env_or_default(
            "STOCK_XLS_PATH",
            str(Path(__file__).parent.parent / "assets" / "全部个股.xls")
        ))
    
    # Extraction Settings
    @property
    def extraction_mode(self) -> str:
        return get_env_or_default(
            "EXTRACTION_MODE",
            self.file_config.get("extraction", {}).get("mode", "merge")
        )
    
    # Logging
    @property
    def log_level(self) -> str:
        return get_env_or_default("LOG_LEVEL", "INFO")
    
    @property
    def log_file(self) -> Optional[str]:
        return get_env_or_default("LOG_FILE", None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary (for debugging, excludes secrets)."""
        return {
            "primary_base_url": self.primary_base_url,
            "primary_model": self.primary_model,
            "fallback_base_url": self.fallback_base_url,
            "fallback_model": self.fallback_model,
            "firebase_credentials_path": self.firebase_credentials_path,
            "github_repo": self.github_repo,
            "data_dir": str(self.data_dir),
            "raw_material_dir": str(self.raw_material_dir),
            "stock_xls_path": str(self.stock_xls_path),
            "extraction_mode": self.extraction_mode,
            "log_level": self.log_level,
            "log_file": self.log_file,
        }


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reset_config():
    """Reset global config (useful for testing)."""
    global _config
    _config = None
