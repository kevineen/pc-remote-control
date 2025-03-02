#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
システムコントローラー
システムレベルの操作（シャットダウン、再起動など）を実行する
"""

import os
import sys
import subprocess
from typing import Dict, Any, Optional
import platform
import time
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

class SystemController:
    """システム操作を制御するクラス"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        logger.info(f"検出されたOS: {self.os_type}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """システム情報を取得する
        
        Returns:
            Dict[str, Any]: システム情報を含む辞書
        """
        try:
            info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
                "cpu_count": os.cpu_count() or 0
            }
            
            # 系列固有の追加情報
            if self.os_type == 'windows':
                # Windows固有の追加情報
                info["windows_edition"] = platform.win32_edition() if hasattr(platform, 'win32_edition') else ""
            elif self.os_type == 'darwin':
                # macOS固有の追加情報
                info["macos_version"] = platform.mac_ver()[0]
            elif self.os_type == 'linux':
                # Linux固有の追加情報
                info["linux_distribution"] = platform.freedesktop_os_release().get('PRETTY_NAME', "") if hasattr(platform, 'freedesktop_os_release') else ""
            
            return info
        except Exception as e:
            logger.error(f"システム情報取得エラー: {str(e)}")
            return {"error": str(e)}
    
    def shutdown(self, delay: int = 60) -> bool:
        """システムをシャットダウンする
        
        Args:
            delay (int, optional): シャットダウンまでの待機時間（秒）
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            # 安全のため最少で2分以上の待機を設定
            if delay < 120:
                delay = 120
                
            logger.info(f"システムのシャットダウンを{delay}秒後に実行します")
            
            if self.os_type == 'windows':
                # Windowsの場合
                subprocess.run(["shutdown", "/s", "/t", str(delay)], check=True)
            elif self.os_type == 'darwin':
                # macOSの場合
                subprocess.run(["sudo", "shutdown", "-h", f"+{delay//60}"], check=True)
            else:
                # Linuxなどその他のシステムの場合
                subprocess.run(["sudo", "shutdown", "-h", f"+{delay//60}"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"シャットダウンエラー: {str(e)}")
            return False
    
    def restart(self, delay: int = 60) -> bool:
        """システムを再起動する
        
        Args:
            delay (int, optional): 再起動までの待機時間（秒）
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            # 安全のため最少で1分以上の待機を設定
            if delay < 60:
                delay = 60
                
            logger.info(f"システムの再起動を{delay}秒後に実行します")
            
            if self.os_type == 'windows':
                # Windowsの場合
                subprocess.run(["shutdown", "/r", "/t", str(delay)], check=True)
            elif self.os_type == 'darwin':
                # macOSの場合
                subprocess.run(["sudo", "shutdown", "-r", f"+{delay//60}"], check=True)
            else:
                # Linuxなどその他のシステムの場合
                subprocess.run(["sudo", "shutdown", "-r", f"+{delay//60}"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"再起動エラー: {str(e)}")
            return False
    
    def cancel_shutdown(self) -> bool:
        """シャットダウンまたは再起動をキャンセルする
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            logger.info("シャットダウン/再起動をキャンセルします")
            
            if self.os_type == 'windows':
                # Windowsの場合
                subprocess.run(["shutdown", "/a"], check=True)
            elif self.os_type == 'darwin':
                # macOSの場合
                subprocess.run(["sudo", "killall", "shutdown"], check=True)
            else:
                # Linuxなどその他のシステムの場合
                subprocess.run(["sudo", "shutdown", "-c"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"シャットダウンキャンセルエラー: {str(e)}")
            return False
    
    def sleep(self) -> bool:
        """システムをスリープ状態にする
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            logger.info("システムをスリープ状態にします")
            
            if self.os_type == 'windows':
                # Windowsの場合
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
            elif self.os_type == 'darwin':
                # macOSの場合
                subprocess.run(["pmset", "sleepnow"], check=True)
            else:
                # Linuxなどその他のシステムの場合
                subprocess.run(["systemctl", "suspend"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"スリープ状態切替エラー: {str(e)}")
            return False
    
    def lock_screen(self) -> bool:
        """画面をロックする
        
        Returns:
            bool: 成功したかどうか
        """
        try:
            logger.info("画面をロックします")
            
            if self.os_type == 'windows':
                # Windowsの場合
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
            elif self.os_type == 'darwin':
                # macOSの場合
                subprocess.run(["pmset", "displaysleepnow"], check=True)
            else:
                # Linuxなどその他のシステムの場合
                # GNOMEの場合
                try:
                    subprocess.run(["gnome-screensaver-command", "-l"], check=True)
                except:
                    # それ以外の場合は別の方法を試す
                    subprocess.run(["loginctl", "lock-session"], check=True)
            
            return True
        except Exception as e:
            logger.error(f"画面ロックエラー: {str(e)}")
            return False
    
    def get_uptime(self) -> Dict[str, Any]:
        """システムの稼働時間を取得する
        
        Returns:
            Dict[str, Any]: 稼働時間情報を含む辞書
        """
        try:
            if self.os_type == 'windows':
                # Windowsの場合
                output = subprocess.check_output("net statistics server", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if "Statistics since" in line:
                        return {"uptime": line.strip()}
            elif self.os_type == 'darwin' or self.os_type == 'linux':
                # macOS/Linuxの場合
                uptime = subprocess.check_output("uptime", shell=True).decode('utf-8').strip()
                return {"uptime": uptime}
            
            # 適切な方法がない場合は別の情報を返す
            return {"uptime": "Unknown", "os": self.os_type}
            
        except Exception as e:
            logger.error(f"稼働時間取得エラー: {str(e)}")
            return {"error": str(e)}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """メモリ使用量を取得する
        
        Returns:
            Dict[str, Any]: メモリ情報を含む辞書
        """
        try:
            import psutil
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "percent": virtual_memory.percent,
                "swap_total": swap_memory.total,
                "swap_used": swap_memory.used,
                "swap_percent": swap_memory.percent
            }
        except ImportError:
            logger.warning("psutilモジュールが存在しません。メモリ情報は利用できません。")
            return {"error": "psutil module not available"}
        except Exception as e:
            logger.error(f"メモリ情報取得エラー: {str(e)}")
            return {"error": str(e)}
