#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PC Remote Control - Server
Python WebSocketサーバー
"""

import asyncio
import json
import logging
import socket
import sys
import websockets
import pyautogui
from argparse import ArgumentParser
from websockets.exceptions import ConnectionClosedError

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# PCの情報を取得
def get_pc_info():
    """PCの基本情報を取得する"""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    screen_size = pyautogui.size()
    
    return {
        "hostname": hostname,
        "ip": ip,
        "os": sys.platform,
        "screen_width": screen_size[0],
        "screen_height": screen_size[1]
    }

# WebSocketハンドラ
async def websocket_handler(websocket):
    """クライアントからのWebSocket接続を処理する"""
    client_address = websocket.remote_address
    logger.info(f"新しいクライアント接続: {client_address}")
    
    try:
        # クライアントに自身の情報を送信
        pc_info = get_pc_info()
        await websocket.send(json.dumps({
            "type": "pc_info",
            "data": pc_info
        }))
        
        # メッセージ受信ループ
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"受信メッセージ: {data}")
                
                # メッセージタイプに応じた処理
                if data["type"] == "ping":
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "data": data.get("data", {})
                    }))
                
                elif data["type"] == "mouse_move":
                    # マウス移動を処理
                    x, y = data["data"]["x"], data["data"]["y"]
                    pyautogui.moveTo(x, y)
                    await websocket.send(json.dumps({
                        "type": "ack",
                        "data": {"action": "mouse_move", "status": "success"}
                    }))
                
                elif data["type"] == "mouse_click":
                    # マウスクリックを処理
                    button = data["data"].get("button", "left")
                    count = data["data"].get("count", 1)
                    pyautogui.click(button=button, clicks=count)
                    await websocket.send(json.dumps({
                        "type": "ack",
                        "data": {"action": "mouse_click", "status": "success"}
                    }))
                
                elif data["type"] == "key_press":
                    # キー入力を処理
                    key = data["data"]["key"]
                    pyautogui.press(key)
                    await websocket.send(json.dumps({
                        "type": "ack",
                        "data": {"action": "key_press", "status": "success"}
                    }))
                
                # その他のコマンドはここに追加
                
                else:
                    logger.warning(f"未知のメッセージタイプ: {data['type']}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "data": {"message": f"不明なコマンド: {data['type']}"}
                    }))
                    
            except json.JSONDecodeError:
                logger.error(f"JSONデコードエラー: {message}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "data": {"message": "無効なJSONフォーマット"}
                }))
    
    except ConnectionClosedError as e:
        logger.info(f"クライアント接続が閉じられました: {client_address} - コード: {e.code}, 理由: {e.reason}")
    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
    finally:
        logger.info(f"クライアント切断: {client_address}")

# メイン関数
async def main(host='0.0.0.0', port=8765):
    """WebSocketサーバーを起動する"""
    logger.info(f"サーバーをスタート: {host}:{port}")
    logger.info(f"PC情報: {get_pc_info()}")
    
    server = await websockets.serve(websocket_handler, host, port)
    logger.info(f"WebSocketサーバーが{host}:{port}で稼働中...")
    
    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("サーバーを停止しています...")
        server.close()
        await server.wait_closed()
        logger.info("サーバーが停止しました")

if __name__ == "__main__":
    # コマンドライン引数
    parser = ArgumentParser(description='PC Remote Control Server')
    parser.add_argument('--host', default='0.0.0.0', help='サーバーのホストアドレス')
    parser.add_argument('--port', type=int, default=8765, help='サーバーのポート番号')
    args = parser.parse_args()
    
    # サーバー起動
    asyncio.run(main(args.host, args.port))
