# --- UDP 通信設定 ---
# Vision からの受信ポート
VISION_LISTEN_PORT = 50007

# ゲームコントローラーからのコマンド受信ポート
GAME_COMMAND_LISTEN_PORT = 50011

# 待ち受けIPアドレス: 通常は '0.0.0.0'
LISTEN_IP = "0.0.0.0"

# 受信バッファサイズ
BUFFER_SIZE = 65536

# 制御ループのポーリング間隔 (秒)
CONTROL_LOOP_INTERVAL = 0.01  # 10ms

# コート中心への移動時の閾値とゲイン
MAX_SPEED = 1


PLACEMENT_R = 10  # cm

COURT_WIDTH = 150  # cm
COURT_HEIGHT = 100  # cm

ROBOT_R = 9

TEAM_COLOR = 'yellow'  # 'yellow' or 'blue'
TEAM_SIDE = 'right'  # 'left' or 'right'

# ロボットごとの設定
ROBOTS_CONFIG = [
    {
        "id": 0,
        "ip": "127.0.0.1",
        # "ip": "192.168.50.107",
        "send_port": 50008,
        "listen_port": 50009,
        "enabled": True
    },
    {
        "id": 1,
        "ip": "127.0.0.1",
        # "ip": "192.168.50.108",
        "send_port": 50012,
        "listen_port": 50010,
        "enabled": True
    },
]

# ソケットタイムアウト設定 (秒)
SOCKET_TIMEOUT = 1.0
