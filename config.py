# --- UDP 通信設定 ---
# Vision からの受信ポート (main.py の UDP_PORT と同じ)
VISION_LISTEN_PORT = 50007
# ESP32 への送信ポート (ESP32 が指令待ち受けするポートと合わせる)
COMMAND_SEND_PORT = 50008
# ESP32 からの受信ポート (ESP32 がセンサーデータを送信するポートと合わせる)
SENSOR_LISTEN_PORT = 50009

# 待ち受けIPアドレス: 通常は '0.0.0.0'
LISTEN_IP = "0.0.0.0"

# ESP32 のローカル IP アドレス (ESP32 が Wi-Fi に接続された際に表示されるもの)
# これは固定にするか、動的に取得する仕組みが必要になる場合があります
ESP32_IP = "192.168.50.107"  # << <-- ここを ESP32 の実際の IP アドレスに変更 >>
# -------------------

# 受信バッファサイズ
BUFFER_SIZE = 65536

# 制御ループのポーリング間隔 (秒)
CONTROL_LOOP_INTERVAL = 0.01  # 10ms
