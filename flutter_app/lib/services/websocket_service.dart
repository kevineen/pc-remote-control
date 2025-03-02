import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/pc_device.dart';

enum ConnectionStatus {
  disconnected,
  connecting,
  connected,
  error,
}

class WebSocketService extends ChangeNotifier {
  WebSocketChannel? _channel;
  ConnectionStatus _status = ConnectionStatus.disconnected;
  String _errorMessage = '';
  PCDevice? _connectedDevice;
  Timer? _pingTimer;
  final Duration _pingInterval = const Duration(seconds: 5);

  // Getters
  ConnectionStatus get status => _status;
  String get errorMessage => _errorMessage;
  PCDevice? get connectedDevice => _connectedDevice;
  bool get isConnected => _status == ConnectionStatus.connected;

  // Connect to WebSocket server
  Future<bool> connect(String host, int port) async {
    if (_status == ConnectionStatus.connecting || _status == ConnectionStatus.connected) {
      return false;
    }

    _status = ConnectionStatus.connecting;
    _errorMessage = '';
    notifyListeners();

    try {
      final uri = Uri.parse('ws://$host:$port');
      _channel = WebSocketChannel.connect(uri);
      
      // Wait for connection to establish
      await _channel!.ready;
      
      _status = ConnectionStatus.connected;
      
      // Save last connected server
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('last_server_host', host);
      await prefs.setInt('last_server_port', port);
      
      // Start listening for messages
      _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
      );
      
      // Start ping timer
      _startPingTimer();
      
      notifyListeners();
      return true;
    } catch (e) {
      _status = ConnectionStatus.error;
      _errorMessage = 'Connection error: ${e.toString()}';
      _channel = null;
      notifyListeners();
      return false;
    }
  }

  // Disconnect from server
  void disconnect() {
    _pingTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
    _connectedDevice = null;
    _status = ConnectionStatus.disconnected;
    notifyListeners();
  }

  // Send a message to the server
  void sendMessage(String type, Map<String, dynamic> data) {
    if (_status != ConnectionStatus.connected || _channel == null) {
      return;
    }

    final message = jsonEncode({
      'type': type,
      'data': data,
    });

    _channel!.sink.add(message);
  }

  // Send mouse movement command
  void sendMouseMove(double x, double y) {
    sendMessage('mouse_move', {'x': x, 'y': y});
  }

  // Send mouse click command
  void sendMouseClick(String button, int count) {
    sendMessage('mouse_click', {'button': button, 'count': count});
  }

  // Send key press command
  void sendKeyPress(String key) {
    sendMessage('key_press', {'key': key});
  }

  // Handle incoming messages
  void _onMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String);
      
      if (data['type'] == 'pc_info') {
        _connectedDevice = PCDevice.fromJson(data['data']);
        notifyListeners();
      }
      
      // Handle other message types as needed
    } catch (e) {
      if (kDebugMode) {
        print('Failed to parse message: $e');
      }
    }
  }

  // Handle WebSocket errors
  void _onError(dynamic error) {
    _status = ConnectionStatus.error;
    _errorMessage = 'WebSocket error: ${error.toString()}';
    _pingTimer?.cancel();
    notifyListeners();
  }

  // Handle WebSocket connection close
  void _onDone() {
    if (_status != ConnectionStatus.disconnected) {
      _status = ConnectionStatus.disconnected;
      _pingTimer?.cancel();
      _channel = null;
      notifyListeners();
    }
  }

  // Start ping timer to keep connection alive
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(_pingInterval, (timer) {
      if (_status == ConnectionStatus.connected) {
        sendMessage('ping', {'timestamp': DateTime.now().millisecondsSinceEpoch});
      } else {
        timer.cancel();
      }
    });
  }

  // Try to restore last connection
  Future<bool> tryReconnectLast() async {
    final prefs = await SharedPreferences.getInstance();
    final host = prefs.getString('last_server_host');
    final port = prefs.getInt('last_server_port');
    
    if (host != null && port != null) {
      return connect(host, port);
    }
    return false;
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
