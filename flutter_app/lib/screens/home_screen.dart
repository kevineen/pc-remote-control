import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/device_discovery_service.dart';
import '../services/websocket_service.dart';
import '../models/pc_device.dart';
import 'remote_control_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _ipController = TextEditingController();
  final TextEditingController _portController = TextEditingController(text: '8765');
  bool _autoConnectAttempted = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkPreviousConnection();
    });
  }

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    super.dispose();
  }

  // 前回の接続を確認
  Future<void> _checkPreviousConnection() async {
    if (_autoConnectAttempted) return;
    
    _autoConnectAttempted = true;
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    
    if (wsService.status == ConnectionStatus.disconnected) {
      final connected = await wsService.tryReconnectLast();
      if (connected) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('前回の接続を復元しました')),
        );
        
        // 接続に成功したら、リモート制御画面へ
        if (mounted) {
          _navigateToRemoteControl(wsService.connectedDevice!);
        }
      }
    }
  }

  // デバイススキャンを開始
  void _startScan() {
    final discoveryService = Provider.of<DeviceDiscoveryService>(context, listen: false);
    discoveryService.startScan();
  }

  // 手動でデバイスを追加
  void _addManualDevice() {
    if (_ipController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('IPアドレスを入力してください')),
      );
      return;
    }
    
    int port;
    try {
      port = int.parse(_portController.text);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('ポート番号に有効な数値を入力してください')),
      );
      return;
    }
    
    final discoveryService = Provider.of<DeviceDiscoveryService>(context, listen: false);
    discoveryService.addManualDevice(_ipController.text, port);
    
    // 入力フィールドをクリア
    _ipController.clear();
    _portController.text = '8765';
  }

  // デバイスへの接続
  Future<void> _connectToDevice(PCDevice device) async {
    final wsService = Provider.of<WebSocketService>(context, listen: false);
    
    // 接続中であれば切断
    if (wsService.isConnected) {
      wsService.disconnect();
    }
    
    final host = device.host ?? device.ip;
    final port = device.port ?? 8765;
    
    final connected = await wsService.connect(host, port);
    
    if (connected) {
      if (mounted) {
        // 接続成功
        _navigateToRemoteControl(device);
      }
    } else {
      if (mounted) {
        // 接続失敗
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('接続に失敗しました: ${wsService.errorMessage}')),
        );
      }
    }
  }

  // リモートコントロール画面へ遷移
  void _navigateToRemoteControl(PCDevice device) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => RemoteControlScreen(device: device),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final discoveryService = Provider.of<DeviceDiscoveryService>(context);
    final wsService = Provider.of<WebSocketService>(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('PC Remote Control'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _startScan,
            tooltip: 'デバイスを再スキャン',
          ),
        ],
      ),
      body: Column(
        children: [
          // 接続状態表示
          if (wsService.isConnected)
            Container(
              padding: const EdgeInsets.all(8),
              color: Colors.green.shade100,
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.green),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '接続中: ${wsService.connectedDevice?.displayName ?? "Unknown"}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      wsService.disconnect();
                    },
                    child: const Text('切断'),
                  ),
                ],
              ),
            ),
          
          // 手動接続入力フォーム
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: TextField(
                    controller: _ipController,
                    decoration: const InputDecoration(
                      labelText: 'IPアドレス',
                      hintText: '例: 192.168.1.100',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  flex: 1,
                  child: TextField(
                    controller: _portController,
                    decoration: const InputDecoration(
                      labelText: 'ポート',
                      hintText: '8765',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _addManualDevice,
                  child: const Text('追加'),
                ),
              ],
            ),
          ),
          
          // スキャン中の表示
          if (discoveryService.isScanning)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Center(
                child: Column(
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 8),
                    Text('デバイスをスキャン中...'),
                  ],
                ),
              ),
            ),
            
          // エラーメッセージ
          if (discoveryService.error.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                discoveryService.error,
                style: const TextStyle(color: Colors.red),
              ),
            ),
            
          // 検出されたデバイスのリスト
          Expanded(
            child: discoveryService.discoveredDevices.isEmpty
                ? Center(
                    child: discoveryService.isScanning
                        ? const SizedBox.shrink()
                        : const Text('デバイスが見つかりません。スキャンを実行してください。'),
                  )
                : ListView.builder(
                    itemCount: discoveryService.discoveredDevices.length,
                    itemBuilder: (context, index) {
                      final device = discoveryService.discoveredDevices[index];
                      return ListTile(
                        leading: Text(
                          device.osIcon,
                          style: const TextStyle(fontSize: 24),
                        ),
                        title: Text(device.displayName),
                        subtitle: Text('${device.connectionString} - ${device.resolution}'),
                        trailing: ElevatedButton(
                          onPressed: () => _connectToDevice(device),
                          child: const Text('接続'),
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _startScan,
        tooltip: 'デバイスをスキャン',
        child: const Icon(Icons.search),
      ),
    );
  }
}
