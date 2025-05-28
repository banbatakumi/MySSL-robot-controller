# --- UDP 通信設定 ---
# Vision からの受信ポート
VISION_LISTEN_PORT = 50007

# ゲームコントローラーからのコマンド受信ポート
GAME_COMMAND_LISTEN_PORT = 50008

# 待ち受けIPアドレス
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

COURT_WIDTH = 6  # m (一般的なSSL Div.Bコートサイズに修正)
COURT_HEIGHT = 4  # m (一般的なSSL Div.Bコートサイズに修正)
# COURT_WIDTH = 1.5  # m
# COURT_HEIGHT = 1  # m


ROBOT_R = 0.09  # m

TEAM_COLOR = 'yellow'  # 'yellow' or 'blue'

TEAM_SIDE = 'left'  # 'left' or 'right'
TEAM_SIDE = -1 if TEAM_SIDE == 'left' else 1  # 計算用係数

# ロボットごとの設定
INITIAI_ROBOT_PORT = 50010
NUM_ROBOTS = 11  # ロボットの数

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

    # simを使う場合は以下をコメントアウト
    # if i == 0:
    #     robot_config["ip"] = "192.168.2.110"  # ロボット0のIP
    # elif i == 1:
    #     robot_config["ip"] = "192.168.2.111"  # ロボット1のIP

    ROBOTS_CONFIG.append(robot_config)

# ソケットタイムアウト設定 (秒)
SOCKET_TIMEOUT = 1.0

# --- GUI 通信設定 ---
# GUIがリッスンするIPアドレスとポート (コントローラーからの送信用)
GUI_TARGET_IP = "127.0.0.1"
GUI_TARGET_PORT = 50040

# コントローラーがGUIからのコマンドをリッスンするIPアドレスとポート (GUIからの送信用)
CONTROLLER_GUI_LISTEN_IP = "0.0.0.0"  # コントローラー側なので LISTEN_IP と同じでも可
CONTROLLER_GUI_LISTEN_PORT = 50041

# GUIの更新間隔 (秒)
GUI_UPDATE_INTERVAL = 0.05  # 50ms
