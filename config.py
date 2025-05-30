TEAM_COLOR = 'blue'  # 'yellow' or 'blue'

TEAM_SIDE = 'right'  # 'left' or 'right'

INITIAI_ROBOT_PORT = 50020
VISION_LISTEN_PORT = 50007
GAME_COMMAND_LISTEN_PORT = 50009
GUI_TARGET_PORT = 50011
GUI_LISTEN_PORT = 50012
if TEAM_COLOR == 'blue':
    INITIAI_ROBOT_PORT = 50050
    VISION_LISTEN_PORT = 50008
    GAME_COMMAND_LISTEN_PORT = 50010
    GUI_TARGET_PORT = 50013
    GUI_LISTEN_PORT = 50014


NUM_ROBOTS = 6  # ロボットの数

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

    # if i == 0:
    #     robot_config["ip"] = "192.168.2.110"  # ロボット0のIP
    # elif i == 1:
    #     robot_config["ip"] = "192.168.2.111"  # ロボット1のIP

    ROBOTS_CONFIG.append(robot_config)


# --- UDP 通信設定 ---
LISTEN_IP = "0.0.0.0"

BUFFER_SIZE = 65536

# GUIのポート
GUI_TARGET_IP = "127.0.0.1"

# ソケットタイムアウト
SOCKET_TIMEOUT = 1.0  # s

# GUIの更新間隔 (秒)
GUI_UPDATE_INTERVAL = 0.05  # s
