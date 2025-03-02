#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
マウスコントローラー
PyAutoGUIを使用してマウスの動作を制御する
"""

import pyautogui
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class MouseController:
    """マウス操作を制御するクラス"""
    
    def __init__(self):
        # 念のため安全モードを有効化（画面の端に行くとエラーになるのを防止）
        pyautogui.FAILSAFE = True
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"画面サイズ: {self.screen_width}x{self.screen_height}")
    
    def move(self, x, y):
        """マウスカーソルを指定座標に移動する
        
        Args:
            x (int): X座標
            y (int): Y座標
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # 座標が画面内に収まるよう調整
            x = max(0, min(x, self.screen_width))
            y = max(0, min(y, self.screen_height))
            
            pyautogui.moveTo(x, y)
            return True
        except Exception as e:
            logger.error(f"マウス移動エラー: {str(e)}")
            return False
    
    def click(self, button="left", clicks=1, x=None, y=None):
        """指定位置でマウスクリックを実行する
        
        Args:
            button (str): クリックするボタン ('left', 'right', 'middle')
            clicks (int): クリック回数
            x (int, optional): クリックするX座標（指定しない場合は現在位置）
            y (int, optional): クリックするY座標（指定しない場合は現在位置）
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            if x is not None and y is not None:
                # 座標指定がある場合はその位置へ移動してからクリック
                x = max(0, min(x, self.screen_width))
                y = max(0, min(y, self.screen_height))
                pyautogui.click(x=x, y=y, button=button, clicks=clicks)
            else:
                # 現在の位置でクリック
                pyautogui.click(button=button, clicks=clicks)
            return True
        except Exception as e:
            logger.error(f"マウスクリックエラー: {str(e)}")
            return False
    
    def scroll(self, amount):
        """マウスホイールをスクロールする
        
        Args:
            amount (int): スクロール量（正の値で上方向、負の値で下方向）
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            pyautogui.scroll(amount)
            return True
        except Exception as e:
            logger.error(f"マウススクロールエラー: {str(e)}")
            return False
    
    def drag(self, start_x, start_y, end_x, end_y, duration=0.5):
        """ドラッグ操作を行う
        
        Args:
            start_x (int): 開始X座標
            start_y (int): 開始Y座標
            end_x (int): 終了X座標
            end_y (int): 終了Y座標
            duration (float): ドラッグにかける時間（秒）
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # 座標が画面内に収まるよう調整
            start_x = max(0, min(start_x, self.screen_width))
            start_y = max(0, min(start_y, self.screen_height))
            end_x = max(0, min(end_x, self.screen_width))
            end_y = max(0, min(end_y, self.screen_height))
            
            pyautogui.moveTo(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=duration)
            return True
        except Exception as e:
            logger.error(f"マウスドラッグエラー: {str(e)}")
            return False
