import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:network_info_plus/network_info_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import '../models/pc_device.dart';

class DeviceDiscoveryService extends ChangeNotifier {
  final List<PCDevice> _discoveredDevices = [];
  bool _isScanning = false;
  String _error = '';
  final int _defaultPort = 8765;
  final Duration _scanTimeout = const Duration(seconds: 3);
  final Duration _connectionTimeout = const Duration(milliseconds: 500);

  // Getters
  List<PCDevice> get discoveredDevices => List.unmodifiable(_discoveredDevices);
  bool get isScanning => _isScanning;
  String get error => _error;

  // Start scanning for devices
  Future<void> startScan() async {
    if (_isScanning) return;
    
    _isScanning = true;
    _error = '';
    _discoveredDevices.clear();
    notifyListeners();

    try {
      // Request location permission (required for network info on Android)
      if (Platform.isAndroid) {
        final status = await Permission.location.request();
        if (status.isDenied || status.isPermanentlyDenied) {
          _error = 'Location permission is required for network scanning';
          _isScanning = false;
          notifyListeners();
          return;
        }
      }

      // Get current network info
      final networkInfo = NetworkInfo();
      final wifiIP = await networkInfo.getWifiIP();
      
      if (wifiIP == null || wifiIP.isEmpty) {
        _error = 'Failed to get local IP address';
        _isScanning = false;
        notifyListeners();
        return;
      }

      // Extract network prefix for scanning
      final ipParts = wifiIP.split('.');
      if (ipParts.length != 4) {
        _error = 'Invalid IP address format';
        _isScanning = false;
        notifyListeners();
        return;
      }

      final subnet = '${ipParts[0]}.${ipParts[1]}.${ipParts[2]}';
      
      // Scan all IPs in the subnet
      final futures = <Future>[];
      for (int i = 1; i <= 254; i++) {
        final ip = '$subnet.$i';
        // Skip own IP
        if (ip == wifiIP) continue;
        
        futures.add(_checkDevice(ip, _defaultPort));
      }

      // Wait for all checks to complete or timeout
      await Future.wait(futures).timeout(_scanTimeout, onTimeout: () {
        if (kDebugMode) {
          print('Scan timeout reached');
        }
        return [];
      });
    } catch (e) {
      _error = 'Error during scanning: ${e.toString()}';
    } finally {
      _isScanning = false;
      notifyListeners();
    }
  }

  // Check if a device at the given IP and port is a PC Remote Control server
  Future<void> _checkDevice(String ip, int port) async {
    try {
      // Try to connect to the server
      final socket = await Socket.connect(ip, port, timeout: _connectionTimeout)
          .catchError((e) => null);
      
      if (socket == null) return;
      
      // Send a ping message to check if it's our server
      final message = jsonEncode({
        'type': 'ping',
        'data': {'source': 'discovery'}
      });
      
      socket.write(message);
      
      // Wait for response
      final response = await socket.timeout(_connectionTimeout).first
          .catchError((e) => null);
      
      socket.destroy();
      
      if (response == null) return;
      
      // Parse response
      final data = jsonDecode(utf8.decode(response));
      if (data['type'] == 'pong' || data['type'] == 'pc_info') {
        PCDevice device;
        
        if (data['type'] == 'pc_info') {
          device = PCDevice.fromJson(data['data']);
        } else {
          // Create basic device if no detailed info
          device = PCDevice(
            hostname: 'Unknown',
            ip: ip,
            os: 'Unknown',
            screenWidth: 0,
            screenHeight: 0,
          );
        }
        
        device.host = ip;
        device.port = port;
        
        if (!_discoveredDevices.any((d) => d.ip == device.ip)) {
          _discoveredDevices.add(device);
          notifyListeners();
        }
      }
    } catch (e) {
      // Silently ignore connection errors - expected for most IPs
    }
  }

  // Manual device addition
  void addManualDevice(String ip, int port) {
    if (!_discoveredDevices.any((d) => d.ip == ip)) {
      final device = PCDevice(
        hostname: 'Manual Entry',
        ip: ip,
        os: 'Unknown',
        screenWidth: 0,
        screenHeight: 0,
        host: ip,
        port: port,
      );
      
      _discoveredDevices.add(device);
      notifyListeners();
    }
  }

  // Remove a device from the list
  void removeDevice(String ip) {
    _discoveredDevices.removeWhere((device) => device.ip == ip);
    notifyListeners();
  }

  // Clear all discovered devices
  void clearDevices() {
    _discoveredDevices.clear();
    notifyListeners();
  }
}
