# --- UDP 通信設定 ---
# Vision からの受信ポート
VISION_LISTEN_PORT = 50007

# ゲームコントローラーからのコマンド受信ポート
GAME_COMMAND_LISTEN_PORT = 50008

# 待ち受けIPアドレス: 通常は '0.0.0.0'
LISTEN_IP = "0.0.0.0"

# 受信バッファサイズ
BUFFER_SIZE = 65536

# 制御ループのポーリング間隔 (秒)
CONTROL_LOOP_INTERVAL = 0.01  # 10ms

# コート中心への移動時の閾値とゲイン
MAX_SPEED = 1


PLACEMENT_R = 0.2  # m

COURT_WIDTH = 1.5  # m
COURT_HEIGHT = 1  # m

ROBOT_R = 0.09  # m

TEAM_COLOR = 'yellow'  # 'yellow' or 'blu

TEAM_SIDE = 'left'  # 'left' or 'right'
TEAM_SIDE = -1 if TEAM_SIDE == 'left' else 1

# ロボットごとの設定
ROBOTS_CONFIG = [
    {
        "id": 0,
        "ip": "127.0.0.1",
        # "ip": "192.168.50.107",
        "send_port": 50010,
        "listen_port": 50011,
        "enabled": True
    },
    {
        "id": 1,
        "ip": "127.0.0.1",
        # "ip": "192.168.50.108",
        "send_port": 50012,
        "listen_port": 50013,
        "enabled": False
    },
]

# ソケットタイムアウト設定 (秒)
SOCKET_TIMEOUT = 1.0
