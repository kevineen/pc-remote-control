# PC Remote Control

同一ネットワーク内のPC機器に接続し、ブラウザーなどを遠隔操作するアプリケーション

## プロジェクト概要

このプロジェクトは、同一ネットワーク内にある他のPC機器に接続し、ブラウザーなどを遠隔で操作するアプリケーションです。

- **フロントエンド**: Flutter（Android）
- **バックエンド**: Python（uv）
- **通信方式**: WebSocket

## システム構成

```
[Android端末(Flutter)] ⟷ WebSocket通信 ⟷ [PC(Python)]
```

## 主な機能（予定）

- 同一ネットワーク内のPC検出
- リモートブラウザ操作
- マウス・キーボード入力制御
- 画面共有

## 開発ステータス

現在、基本的な通信機能の実装中です。このREADMEは通信確認のために更新されました。

## セットアップ方法

### PC側（バックエンド）
```bash
# 依存関係のインストール
uv install

# サーバー起動
python server.py
```

### Android側（フロントエンド）
```bash
# Flutterプロジェクトのセットアップ
flutter pub get

# デバッグ実行
flutter run
```

## 通信テスト

このプロジェクトではWebSocketを使用して端末間の通信を行います。
初期段階では、単純なPing-Pongテストを実装して通信の確認を行います。

## ライセンス

[LICENSE](./LICENSE)ファイルをご覧ください。