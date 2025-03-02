#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ロガー設定
アプリケーション全体で一貫したログ出力を提供する
"""

import logging
import sys
from typing import Optional

# ログレベルの設定
DEFAULT_LOG_LEVEL = logging.INFO

# ロガー辞書（モジュールごとのロガーをキャッシュ）
_loggers = {}

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """指定した名前でロガーを設定する
    
    すでに同名のロガーが存在する場合はそれを返す。
    存在しない場合は新しく作成する。
    
    Args:
        name (str): ロガー名
        level (int, optional): ログレベル
        
    Returns:
        logging.Logger: 設定されたロガー
    """
    # すでに作成済みのロガーがあればそれを返す
    if name in _loggers:
        return _loggers[name]
    
    # 新しいロガーを作成
    logger = logging.getLogger(name)
    
    # ログレベルの設定
    if level is None:
        level = DEFAULT_LOG_LEVEL
    logger.setLevel(level)
    
    # すでにハンドラーが設定されていなければ新たに追加
    if not logger.handlers:
        # コンソール出力用のハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)
    
    # 作成したロガーをキャッシュして返す
    _loggers[name] = logger
    return logger
