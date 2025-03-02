#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PC Remote Control - Main Entry
アプリケーションのエントリーポイント
"""

from backend.server import run_server
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """アプリケーションのメインエントリーポイント"""
    logger.info("PC Remote Control を起動しています...")
    run_server()

if __name__ == "__main__":
    main()
