#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
システム情報取得ユーティリティ
PC情報を取得するための関数群
"""

import socket
import sys
import platform
import os
import pyautogui
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_pc_info():
    """PCの基本情報を取得する
    
    Returns:
        dict: PC情報を含む辞書
    """
    try:
        hostname = socket.gethostname()
        ip = get_local_ip()
        os_name = get_os_name()
        screen_size = pyautogui.size()
        
        info = {
            "hostname": hostname,
            "ip": ip,
            "os": os_name,
            "screen_width": screen_size[0],
            "screen_height": screen_size[1],
            "version": "0.1.0",
            "platform": platform.platform()
        }
        
        return info
    
    except Exception as e:
        logger.error(f"PC情報取得エラー: {str(e)}")
        # 最低限の情報を返す
        return {
            "hostname": "unknown",
            "ip": "127.0.0.1",
            "os": sys.platform,
            "screen_width": 1024,
            "screen_height": 768,
            "version": "0.1.0",
            "error": str(e)
        }

def get_local_ip():
    """ローカルIPアドレスを取得する
    
    Returns:
        str: ローカルIPアドレス
    """
    try:
        # UDPソケットを作成
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 外部に接続しようとする（実際には接続されない）
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.error(f"ローカルIP取得エラー: {str(e)}")
        return "127.0.0.1"

def get_os_name():
    """OS名を取得する
    
    Returns:
        str: OS名
    """
    if sys.platform.startswith('win'):
        return "Windows"
    elif sys.platform.startswith('darwin'):
        return "macOS"
    elif sys.platform.startswith('linux'):
        return "Linux"
    else:
        return sys.platform
