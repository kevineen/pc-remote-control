#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
キーボードコントローラー
PyAutoGUIを使用してキーボード入力を制御する
"""

import pyautogui
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class KeyboardController:
    """キーボード操作を制御するクラス"""
    
    def __init__(self):
        # 利用可能なキーのリスト
        self.available_keys = list(pyautogui.KEYBOARD_KEYS)
        logger.info(f"利用可能なキー数: {len(self.available_keys)}")
    
    def press(self, key):
        """1つのキーを押す
        
        Args:
            key (str): 押すキー
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if key in self.available_keys:
                pyautogui.press(key)
                return True
            else:
                logger.warning(f"サポートされていないキー: {key}")
                return False
        except Exception as e:
            logger.error(f"キー入力エラー: {str(e)}")
            return False
    
    def hotkey(self, *keys):
        """複数のキーを同時に押す（ショートカットキーなど）
        
        Args:
            *keys (str): 押すキーのリスト
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # すべてのキーがサポートされているか確認
            unsupported_keys = [k for k in keys if k not in self.available_keys]
            if unsupported_keys:
                logger.warning(f"サポートされていないキー: {unsupported_keys}")
                return False
            
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"ホットキー入力エラー: {str(e)}")
            return False
    
    def write(self, text):
        """テキストを入力する
        
        Args:
            text (str): 入力するテキスト
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            pyautogui.write(text)
            return True
        except Exception as e:
            logger.error(f"テキスト入力エラー: {str(e)}")
            return False
    
    def key_down(self, key):
        """キーを押し続ける状態にする
        
        Args:
            key (str): 押すキー
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if key in self.available_keys:
                pyautogui.keyDown(key)
                return True
            else:
                logger.warning(f"サポートされていないキー: {key}")
                return False
        except Exception as e:
            logger.error(f"キーダウンエラー: {str(e)}")
            return False
    
    def key_up(self, key):
        """押し続けていたキーを離す
        
        Args:
            key (str): 離すキー
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if key in self.available_keys:
                pyautogui.keyUp(key)
                return True
            else:
                logger.warning(f"サポートされていないキー: {key}")
                return False
        except Exception as e:
            logger.error(f"キーアップエラー: {str(e)}")
            return False
