#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ブラウザコントローラー
ブラウザーの操作を制御する
"""

import os
import sys
import subprocess
import webbrowser
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class BrowserController:
    """ブラウザー操作を制御するクラス"""
    
    def __init__(self):
        self.browser_path = None
        self.default_browser = True
        self._detect_browser()
    
    def _detect_browser(self):
        """システムのデフォルトブラウザを検出する"""
        try:
            if sys.platform.startswith('win'):
                # Windowsではデフォルトブラウザを検出するロジック
                self.default_browser = True
            elif sys.platform.startswith('darwin'):
                # macOSではデフォルトブラウザを検出するロジック
                self.default_browser = True
            elif sys.platform.startswith('linux'):
                # Linuxではデフォルトブラウザを検出するロジック
                self.default_browser = True
            
            logger.info(f"デフォルトブラウザを使用します")
        except Exception as e:
            logger.error(f"ブラウザ検出エラー: {str(e)}")
            self.default_browser = True
    
    def open_url(self, url):
        """指定したURLをブラウザで開く
        
        Args:
            url (str): 開くURL
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if self.default_browser:
                webbrowser.open(url)
            else:
                # 特定のブラウザパスが設定されている場合はそれを使用
                if sys.platform.startswith('win'):
                    os.startfile(url)
                else:
                    subprocess.Popen([self.browser_path, url])
            
            logger.info(f"ブラウザでURLを開きました: {url}")
            return True
        except Exception as e:
            logger.error(f"URL表示エラー: {str(e)}")
            return False
    
    def open_new_tab(self, url):
        """新しいタブでURLを開く
        
        Args:
            url (str): 開くURL
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open_new_tab(url)
            logger.info(f"新しいタブでURLを開きました: {url}")
            return True
        except Exception as e:
            logger.error(f"新しいタブでのURL表示エラー: {str(e)}")
            return False
    
    def open_new_window(self, url):
        """新しいウィンドウでURLを開く
        
        Args:
            url (str): 開くURL
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open_new(url)
            logger.info(f"新しいウィンドウでURLを開きました: {url}")
            return True
        except Exception as e:
            logger.error(f"新しいウィンドウでのURL表示エラー: {str(e)}")
            return False
    
    def set_browser_path(self, path):
        """使用するブラウザのパスを設定する
        
        Args:
            path (str): ブラウザ実行ファイルのパス
            
        Returns:
            bool: 成功したかどうか
        """
        if os.path.exists(path):
            self.browser_path = path
            self.default_browser = False
            logger.info(f"ブラウザパスを設定しました: {path}")
            return True
        else:
            logger.error(f"指定されたブラウザパスが存在しません: {path}")
            return False
