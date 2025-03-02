#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
アプリケーションランチャー
リモートからPC上のアプリケーションを起動する
"""

import os
import sys
import subprocess
from typing import Dict, List, Optional
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class AppLauncher:
    """アプリケーションを起動するためのクラス"""
    
    def __init__(self):
        # 共通アプリケーションのリスト
        self.common_apps = {
            "notepad": self._get_notepad_path(),
            "calculator": self._get_calculator_path(),
            "explorer": self._get_file_explorer_path(),
        }
        
        # ユーザー定義アプリケーション
        self.user_apps: Dict[str, str] = {}
    
    def _get_notepad_path(self) -> Optional[str]:
        """メモ帳アプリのパスを取得する"""
        if sys.platform.startswith('win'):
            return "notepad.exe"
        elif sys.platform.startswith('darwin'):
            return "open -a TextEdit"
        elif sys.platform.startswith('linux'):
            # Linuxでは複数の選択肢を試す
            editors = ["gedit", "kate", "leafpad", "mousepad", "nano"]
            for editor in editors:
                try:
                    result = subprocess.run(["which", editor], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        return editor
                except:
                    pass
        return None
    
    def _get_calculator_path(self) -> Optional[str]:
        """電卓アプリのパスを取得する"""
        if sys.platform.startswith('win'):
            return "calc.exe"
        elif sys.platform.startswith('darwin'):
            return "open -a Calculator"
        elif sys.platform.startswith('linux'):
            # Linuxでは複数の選択肢を試す
            calculators = ["gnome-calculator", "kcalc", "xcalc"]
            for calc in calculators:
                try:
                    result = subprocess.run(["which", calc], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        return calc
                except:
                    pass
        return None
    
    def _get_file_explorer_path(self) -> Optional[str]:
        """ファイルエクスプローラーのパスを取得する"""
        if sys.platform.startswith('win'):
            return "explorer.exe"
        elif sys.platform.startswith('darwin'):
            return "open ."
        elif sys.platform.startswith('linux'):
            # Linuxでは複数の選択肢を試す
            explorers = ["nautilus", "dolphin", "thunar", "pcmanfm"]
            for explorer in explorers:
                try:
                    result = subprocess.run(["which", explorer], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        return explorer
                except:
                    pass
        return None
    
    def launch_app(self, app_name: str, args: List[str] = None) -> bool:
        """指定された名前のアプリを起動する
        
        Args:
            app_name (str): 起動するアプリの名前またはパス
            args (List[str], optional): アプリに渡す引数のリスト
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            app_path = None
            
            # 共通アプリケーションから探す
            if app_name.lower() in self.common_apps:
                app_path = self.common_apps[app_name.lower()]
            
            # ユーザー定義アプリケーションから探す
            elif app_name.lower() in self.user_apps:
                app_path = self.user_apps[app_name.lower()]
            
            # それ以外はそのままパスとして使用
            else:
                app_path = app_name
            
            if not app_path:
                logger.error(f"アプリケーションパスが見つかりません: {app_name}")
                return False
            
            # OSに応じた起動処理
            if sys.platform.startswith('win'):
                # Windowsの場合
                if args:
                    subprocess.Popen([app_path] + args)
                else:
                    subprocess.Popen(app_path)
            elif sys.platform.startswith('darwin'):
                # macOSの場合
                if app_path.startswith('open'):
                    # すでにopenコマンドが含まれている場合
                    cmd = app_path
                    if args:
                        cmd += ' ' + ' '.join(args)
                    subprocess.Popen(cmd, shell=True)
                else:
                    # 通常のアプリケーション
                    if args:
                        subprocess.Popen(["open", "-a", app_path] + args)
                    else:
                        subprocess.Popen(["open", "-a", app_path])
            else:
                # Linuxなどその他のOSの場合
                if args:
                    subprocess.Popen([app_path] + args)
                else:
                    subprocess.Popen(app_path)
            
            logger.info(f"アプリケーションを起動しました: {app_path}")
            return True
            
        except Exception as e:
            logger.error(f"アプリケーション起動エラー: {str(e)}")
            return False
    
    def register_app(self, name: str, path: str) -> bool:
        """ユーザー定義アプリケーションを登録する
        
        Args:
            name (str): アプリの名前（識別子）
            path (str): アプリのパス
        
        Returns:
            bool: 成功したかどうか
        """
        if not path:
            logger.error("無効なアプリケーションパスです")
            return False
        
        self.user_apps[name.lower()] = path
        logger.info(f"アプリケーションを登録しました: {name} -> {path}")
        return True
    
    def unregister_app(self, name: str) -> bool:
        """登録されたアプリケーションを削除する
        
        Args:
            name (str): 削除するアプリの名前
        
        Returns:
            bool: 成功したかどうか
        """
        lower_name = name.lower()
        if lower_name in self.user_apps:
            path = self.user_apps[lower_name]
            del self.user_apps[lower_name]
            logger.info(f"アプリケーション登録を削除しました: {name} -> {path}")
            return True
        else:
            logger.warning(f"アプリケーションが登録されていません: {name}")
            return False
    
    def get_registered_apps(self) -> Dict[str, str]:
        """登録されている全てのアプリケーションを取得する
        
        Returns:
            Dict[str, str]: アプリ名とパスの辞書
        """
        return {**self.common_apps, **self.user_apps}
