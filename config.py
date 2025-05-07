# --- UDP 通信設定 ---
# Vision からの受信ポート (main.py の UDP_PORT と同じ)
VISION_LISTEN_PORT = 50007

# ESP32 への送信ポート (ESP32 が指令待ち受けするポートと合わせる)
# ロボットごとにポートを分ける、または同じポートだがIPで区別
# ここではIPで区別するのでポートは共通でOKとする場合が多い
COMMAND_SEND_PORT = 50008

# ESP32 からの受信ポート (ESP32 がセンサーデータを送信するポートと合わせる)
# ロボットごとに異なるポートで受信する想定 (設定例)
YELLOW_SENSOR_LISTEN_PORT = 50009
BLUE_SENSOR_LISTEN_PORT = 50010  # 青ロボット用のセンサー受信ポート

# ゲームコントローラーからのコマンド受信ポート (新設)
GAME_COMMAND_LISTEN_PORT = 50011  # << 新しいポート >>

# 待ち受けIPアドレス: 通常は '0.0.0.0'
LISTEN_IP = "0.0.0.0"

# ロボットのローカル IP アドレス
# これは固定にするか、動的に取得する仕組みが必要になる場合があります
YELLOW_ROBOT_IP = "192.168.50.107"  # << 黄ロボットの実際の IP アドレスに変更 >>
BLUE_ROBOT_IP = "192.168.50.108"  # << 青ロボットの実際の IP アドレスに変更 >>
# -------------------

# 有効にするロボットの設定 (True/False で切り替え)
ENABLE_YELLOW_ROBOT = True
ENABLE_BLUE_ROBOT = False  # 必要に応じて True に変更

# 受信バッファサイズ
BUFFER_SIZE = 65536

# 制御ループのポーリング間隔 (秒)
CONTROL_LOOP_INTERVAL = 0.01  # 10ms

# コート中心への移動時の閾値とゲイン
CENTER_MOVE_DISTANCE_THRESHOLD = 5  # この距離以内なら停止
CENTER_MOVE_LINEAR_GAIN = 0.02         # 線形速度ゲイン
MAX_LINEAR_SPEED_M_S = 1        # 最大線形速度 cm/s
