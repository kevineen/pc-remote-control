import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/pc_device.dart';
import '../services/websocket_service.dart';

class RemoteControlScreen extends StatefulWidget {
  final PCDevice device;

  const RemoteControlScreen({
    super.key,
    required this.device,
  });

  @override
  State<RemoteControlScreen> createState() => _RemoteControlScreenState();
}

class _RemoteControlScreenState extends State<RemoteControlScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _textInputController = TextEditingController();
  late PCDevice _device;
  
  // トラックパッドの状態管理用
  double _lastX = 0;
  double _lastY = 0;
  bool _isDragging = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _device = widget.device;
  }

  @override
  void dispose() {
    _tabController.dispose();
    _textInputController.dispose();
    super.dispose();
  }

  // マウス移動処理
  void _handlePanUpdate(DragUpdateDetails details) {
    if (!_isDragging) {
      setState(() {
        _isDragging = true;
      });
    }
    
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    if (!wsService.isConnected) return;
    
    // 相対移動量を計算
    final dx = details.delta.dx;
    final dy = details.delta.dy;
    
    // 現在のマウス位置を更新（画面上の絶対位置ではなく相対移動量を積算）
    _lastX += dx;
    _lastY += dy;
    
    // PCの画面サイズが不明な場合、デフォルト値を使用
    final screenWidth = _device.screenWidth > 0 ? _device.screenWidth : 1920;
    final screenHeight = _device.screenHeight > 0 ? _device.screenHeight : 1080;
    
    // 現在の位置に相対移動量を適用し、PCの画面サイズに合わせて調整
    double newX = _lastX;
    double newY = _lastY;
    
    // 画面範囲を超えないようにする
    newX = newX.clamp(0, screenWidth.toDouble());
    newY = newY.clamp(0, screenHeight.toDouble());
    
    // 更新された位置を送信
    wsService.sendMouseMove(newX, newY);
  }

  void _handlePanEnd(DragEndDetails details) {
    setState(() {
      _isDragging = false;
    });
  }

  // マウスクリック処理
  void _handleTap() {
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    if (!wsService.isConnected) return;
    
    wsService.sendMouseClick('left', 1);
  }

  void _handleDoubleTap() {
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    if (!wsService.isConnected) return;
    
    wsService.sendMouseClick('left', 2);
  }

  void _handleRightTap() {
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    if (!wsService.isConnected) return;
    
    wsService.sendMouseClick('right', 1);
  }

  // キー入力処理
  void _sendText() {
    if (_textInputController.text.isEmpty) return;
    
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    if (!wsService.isConnected) return;
    
    // 1文字ずつキー入力として送信
    for (var i = 0; i < _textInputController.text.length; i++) {
      final char = _textInputController.text[i];
      wsService.sendKeyPress(char);
    }
    
    // 入力フィールドをクリア
    _textInputController.clear();
  }

  // ショートカットキー送信
  void _sendSpecialKey(String key) {
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    if (!wsService.isConnected) return;
    
    wsService.sendKeyPress(key);
  }

  @override
  Widget build(BuildContext context) {
    final wsService = Provider.of<WebSocketService>(context);
    
    // 接続が切れた場合、前の画面に戻る
    if (!wsService.isConnected) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('接続が切断されました')),
        );
      });
    }
    
    return Scaffold(
      appBar: AppBar(
        title: Text('${_device.displayName} をコントロール'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.mouse), text: 'マウス'),
            Tab(icon: Icon(Icons.keyboard), text: 'キーボード'),
            Tab(icon: Icon(Icons.settings), text: '設定'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // マウスコントロール画面
          Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'マウスコントロール',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
              ),
              
              Expanded(
                child: Container(
                  margin: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: GestureDetector(
                    onPanUpdate: _handlePanUpdate,
                    onPanEnd: _handlePanEnd,
                    onTap: _handleTap,
                    onDoubleTap: _handleDoubleTap,
                    onLongPress: _handleRightTap,
                    child: Center(
                      child: _isDragging
                          ? const Icon(Icons.touch_app, size: 32)
                          : const Text('トラックパッド\n\nドラッグ: マウス移動\nタップ: 左クリック\nダブルタップ: ダブルクリック\n長押し: 右クリック'),
                    ),
                  ),
                ),
              ),
              
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(
                      onPressed: () => _handleTap(),
                      child: const Text('左クリック'),
                    ),
                    ElevatedButton(
                      onPressed: () => _handleRightTap(),
                      child: const Text('右クリック'),
                    ),
                    ElevatedButton(
                      onPressed: () => _handleDoubleTap(),
                      child: const Text('ダブルクリック'),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          // キーボード画面
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'キーボード入力',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 16),
                
                TextField(
                  controller: _textInputController,
                  decoration: InputDecoration(
                    labelText: 'テキスト入力',
                    hintText: 'テキストを入力してEnterを押してください',
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: _sendText,
                    ),
                  ),
                  onSubmitted: (_) => _sendText(),
                ),
                
                const SizedBox(height: 24),
                const Text('特殊キー'),
                
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    ElevatedButton(
                      onPressed: () => _sendSpecialKey('enter'),
                      child: const Text('Enter'),
                    ),
                    ElevatedButton(
                      onPressed: () => _sendSpecialKey('esc'),
                      child: const Text('Esc'),
                    ),
                    ElevatedButton(
                      onPressed: () => _sendSpecialKey('tab'),
                      child: const Text('Tab'),
                    ),
                    ElevatedButton(
                      onPressed: () => _sendSpecialKey('space'),
                      child: const Text('Space'),
                    ),
                    ElevatedButton(
                      onPressed: () => _sendSpecialKey('backspace'),
                      child: const Text('Backspace'),
                    ),
                    ElevatedButton(
                      onPressed: () => _sendSpecialKey('delete'),
                      child: const Text('Delete'),
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                const Text('矢印キー'),
                
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: ElevatedButton(
                        onPressed: () => _sendSpecialKey('up'),
                        child: const Icon(Icons.arrow_upward),
                      ),
                    ),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: ElevatedButton(
                        onPressed: () => _sendSpecialKey('left'),
                        child: const Icon(Icons.arrow_back),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: ElevatedButton(
                        onPressed: () => _sendSpecialKey('down'),
                        child: const Icon(Icons.arrow_downward),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: ElevatedButton(
                        onPressed: () => _sendSpecialKey('right'),
                        child: const Icon(Icons.arrow_forward),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // 設定画面
          SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '接続情報',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 16),
                
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ListTile(
                          title: const Text('ホスト名'),
                          subtitle: Text(_device.hostname),
                        ),
                        ListTile(
                          title: const Text('IPアドレス'),
                          subtitle: Text(_device.ip),
                        ),
                        ListTile(
                          title: const Text('OS'),
                          subtitle: Text('${_device.osIcon} ${_device.os}'),
                        ),
                        ListTile(
                          title: const Text('画面解像度'),
                          subtitle: Text(_device.resolution),
                        ),
                        ListTile(
                          title: const Text('接続URL'),
                          subtitle: Text(_device.connectionString),
                        ),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                ElevatedButton.icon(
                  onPressed: () {
                    wsService.disconnect();
                    Navigator.of(context).pop();
                  },
                  icon: const Icon(Icons.logout),
                  label: const Text('切断'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
