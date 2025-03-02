class PCDevice {
  String hostname;
  String ip;
  String os;
  int screenWidth;
  int screenHeight;
  String? host;
  int? port;
  bool isConnected;

  PCDevice({
    required this.hostname,
    required this.ip,
    required this.os,
    required this.screenWidth,
    required this.screenHeight,
    this.host,
    this.port,
    this.isConnected = false,
  });

  factory PCDevice.fromJson(Map<String, dynamic> json) {
    return PCDevice(
      hostname: json['hostname'] ?? 'Unknown',
      ip: json['ip'] ?? '0.0.0.0',
      os: json['os'] ?? 'Unknown',
      screenWidth: json['screen_width'] ?? 0,
      screenHeight: json['screen_height'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'hostname': hostname,
      'ip': ip,
      'os': os,
      'screen_width': screenWidth,
      'screen_height': screenHeight,
      'host': host,
      'port': port,
    };
  }

  @override
  String toString() {
    return 'PCDevice{hostname: $hostname, ip: $ip, os: $os, resolution: ${screenWidth}x$screenHeight}';
  }

  String get connectionString {
    if (host != null && port != null) {
      return '$host:$port';
    }
    return '$ip:8765'; // Default port
  }

  String get osIcon {
    final osLower = os.toLowerCase();
    if (osLower.contains('win')) {
      return '🪟';
    } else if (osLower.contains('mac') || osLower.contains('darwin')) {
      return '🍎';
    } else if (osLower.contains('linux')) {
      return '🐧';
    }
    return '💻';
  }

  String get displayName {
    if (hostname.isNotEmpty && hostname != 'Unknown') {
      return hostname;
    }
    return ip;
  }

  String get resolution {
    if (screenWidth > 0 && screenHeight > 0) {
      return '${screenWidth}x$screenHeight';
    }
    return 'Unknown';
  }
}
