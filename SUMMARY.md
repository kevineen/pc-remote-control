# PC Remote Control - 実装サマリー

## プロジェクト概要

「PC Remote Control」は、同一ネットワーク内にある他のPC機器に接続し、ブラウザーなどを遠隔で操作するアプリケーションです。

- **フロントエンド**: Flutter（Android）
- **バックエンド**: Python（uvを利用）
- **通信方式**: WebSocket

## 実装されている機能

### バックエンド（Python）

1. **WebSocketサーバー**
   - 同一ネットワーク内でのデバイス検出に対応
   - PCの基本情報（ホスト名、IP、OS、画面サイズ）の提供
   - クライアントからのリモートコマンド処理

2. **入力制御機能**
   - マウス移動制御
   - マウスクリック処理（左クリック、右クリック、ダブルクリック）
   - キーボード入力処理

3. **接続管理**
   - Ping-Pongによる接続維持
   - 接続状態監視

### フロントエンド（Flutter）

1. **デバイス検出画面**
   - 同一ネットワーク内のPC自動検出
   - 手動IPアドレス入力による接続
   - 前回接続したデバイスへの自動再接続

2. **リモートコントロール機能**
   - マウス操作（トラックパッド式）
   - キーボード入力
   - 特殊キー送信（Enterキー、矢印キーなど）

3. **接続管理機能**
   - WebSocket接続状態監視
   - 通信エラー処理

## ファイル構成

### バックエンド

- `server.py` - WebSocketサーバーとマウス/キーボード制御
- `requirements.txt` - 依存パッケージ一覧

### フロントエンド

- `flutter_app/lib/main.dart` - アプリケーションのエントリーポイント
- `flutter_app/lib/models/pc_device.dart` - PCデバイスモデル
- `flutter_app/lib/services/`
  - `websocket_service.dart` - WebSocket通信サービス
  - `device_discovery_service.dart` - デバイス検出サービス
- `flutter_app/lib/screens/`
  - `home_screen.dart` - デバイス検出・接続画面
  - `remote_control_screen.dart` - リモート操作画面

## セットアップ手順

### バックエンド（PC側）

```bash
# 依存関係のインストール
uv install

# サーバー起動
python server.py
```

### フロントエンド（Android側）

```bash
# Flutterプロジェクトのセットアップ
cd flutter_app
flutter pub get

# デバッグ実行
flutter run
```

## 今後の拡張予定

1. **画面共有機能**
   - PCの画面をリアルタイムでAndroidに表示

2. **ファイル転送機能**
   - PC⇔Android間のファイル転送

3. **マルチPC管理**
   - 複数PCの同時接続・切り替え

4. **カスタムショートカット**
   - よく使うコマンドのカスタマイズ
