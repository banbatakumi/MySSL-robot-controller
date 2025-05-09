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
MAX_SPEED = 1        # 最大線形速度 m/s
PLACEMENT_R = 10  # cm

COURT_WIDTH = 150  # cm
COURT_HEIGHT = 100  # cm

ROBOT_R = 9

# チームカラー (ゲームコマンドのターゲット指定などで利用)
TEAM_COLOR = 'yellow'  # 'yellow' or 'blue'

# ロボットごとの設定
# id: ユニークな整数ID
# name: ロボットの識別名 (例: "yellow", "blue", "robot_A")。ゲームコマンドの "robot_color" と照合される想定。
# ip: ロボットのIPアドレス
# send_port: このPCからロボットへコマンドを送信する際の、ロボット側の待ち受けポート
# listen_port: このPCがロボットからのセンサーデータを受信するポート
# enabled: このロボット設定を有効にするか
ROBOTS_CONFIG = [
    {
        "id": 0,
        "ip": "127.0.0.1",  # 以前の ROBOT_0_ROBOT_IP
        # "ip": "192.168.50.107",
        "send_port": 50008,  # 以前の ROBOT_0_SEND_PORT
        "listen_port": 50009,  # 以前の ROBOT_0_SENSOR_LISTEN_PORT
        "enabled": True
    },
    {
        "id": 1,
        "ip": "127.0.0.1",  # 以前の ROBOT_1_ROBOT_IP
        # "ip": "192.168.50.108",
        "send_port": 50012,  # 以前の ROBOT_1_SEND_PORT
        "listen_port": 50010,  # 以前の ROBOT_1_SENSOR_LISTEN_PORT
        "enabled": True
    },
]

# ソケットタイムアウト設定 (秒)
SOCKET_TIMEOUT = 1.0
