TEAM_COLOR = 'yellow'  # 'yellow' or 'blue'

TEAM_SIDE = 'right'  # 'left' or 'right'
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


# --- UDP 通信設定 ---
LISTEN_IP = "0.0.0.0"
VISION_LISTEN_PORT = 50007

GAME_COMMAND_LISTEN_PORT = 50008

BUFFER_SIZE = 65536

# GUIがリッスンするIPアドレスとポート (コントローラーからの送信用)
GUI_TARGET_IP = "127.0.0.1"
GUI_TARGET_PORT = 50040
CONTROLLER_GUI_LISTEN_PORT = 50041

# GUIの更新間隔 (秒)
GUI_UPDATE_INTERVAL = 0.05  # 50ms

# ソケットタイムアウト設定 (秒)
SOCKET_TIMEOUT = 1.0
