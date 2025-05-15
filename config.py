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

MAX_KICK_POWER = 100
MAX_DRIBBLE_POWER = 100

PLACEMENT_R = 0.1  # m

COURT_WIDTH = 1.5  # m
COURT_HEIGHT = 1  # m

ROBOT_R = 0.09  # m

TEAM_COLOR = 'yellow'  # 'yellow' or 'blu

TEAM_SIDE = 'left'  # 'left' or 'right'
TEAM_SIDE = -1 if TEAM_SIDE == 'left' else 1

# ロボットごとの設定
INITIAI_ROBOT_PORT = 50010
NUM_ROBOTS = 2  # ロボットの数

# ロボットごとの設定
ROBOTS_CONFIG = []

for i in range(NUM_ROBOTS):
    robot_config = {
        "id": i,
        "ip": "127.0.0.1",  # すべてのロボットに共通のIP
        "send_port": INITIAI_ROBOT_PORT + i * 2,
        "listen_port": INITIAI_ROBOT_PORT + i * 2 + 1,
        "enabled": True
    }

    # # 特定のロボットに個別の設定を追加
    if i == 0:
        robot_config["ip"] = "192.168.2.110"  # ロボット0のIP
    elif i == 1:
        robot_config["ip"] = "192.168.2.111"  # ロボット1のIP

    ROBOTS_CONFIG.append(robot_config)

# ソケットタイムアウト設定 (秒)
SOCKET_TIMEOUT = 1.0
