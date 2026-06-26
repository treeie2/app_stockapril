#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Centralized logging configuration for server deployment."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "wechat_fetch",
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Setup and return a configured logger.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
        format_string: Optional custom format string
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Global logger instance
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """Get global logger instance."""
    global _logger
    if _logger is None:
        from scripts.config import get_config
        config = get_config()
        _logger = setup_logger(
            level=config.log_level,
            log_file=config.log_file
        )
    return _logger


def reset_logger():
    """Reset global logger (useful for testing)."""
    global _logger
    _logger = None
