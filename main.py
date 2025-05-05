# robot_controller.py

import socket
import json
import time  # オプション：タイムスタンプ確認用

# --- UDP 通信設定 ---
# 待ち受けポート番号: main.py の UDP_PORT と同じにする必要があります
UDP_LISTEN_PORT = 50007
# 待ち受けIPアドレス: 通常は自分のPCの全てのインターフェースで受け付けるために '0.0.0.0' を指定
# 特定のIPアドレスのみで受け付ける場合はそのIPを指定
UDP_LISTEN_IP = "0.0.0.0"
# -------------------

# UDPソケットを作成
try:
    # AF_INET は IPv4 を使用することを示す
    # SOCK_DGRAM は UDP (データグラム) を使用することを示す
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP socket created.")
except socket.error as e:
    print(f"Failed to create UDP socket: {e}")
    sock = None  # ソケット作成に失敗した場合
    exit()  # プログラム終了

# 指定したIPアドレスとポートにソケットをバインド（紐付け）し、待ち受け状態にする
try:
    sock.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))
    print(
        f"UDP socket bound to {UDP_LISTEN_IP}:{UDP_LISTEN_PORT}, waiting for data...")
except socket.error as e:
    print(f"Failed to bind UDP socket: {e}")
    sock.close()  # ソケットを閉じる
    exit()  # プログラム終了

# 受信バッファサイズ (任意、適宜調整)
# 一度に受信できる最大データ量
BUFFER_SIZE = 65536  # 標準的なUDPパケットサイズより十分に大きく

print("Starting vision data reception loop...")

while True:
    try:
        # データを受信 (ブロッキング受信)
        # data: 受信したバイト列
        # addr: 送信元アドレス (IP, ポート)
        data, addr = sock.recvfrom(BUFFER_SIZE)

        # 受信したバイト列をデコードして文字列に戻す
        json_string = data.decode('utf-8')

        # JSON文字列をPythonの辞書に変換
        vision_data = json.loads(json_string)

        # --- 受信したビジョン情報の利用 ---
        # ここで vision_data (Python辞書) を使ってロボットを制御します

        # 例として、受信したデータをプリント
      #   print(f"Received data from {addr}:")
      #   print(f"  Timestamp: {vision_data.get('timestamp')}")
      #   print(f"  FPS: {vision_data.get('fps')}")
      #   print(f"  Orange Balls: {vision_data.get('orange_balls', [])}")
      #   print(f"  Yellow Robots: {vision_data.get('yellow_robots', [])}")
      #   print(f"  Blue Robots: {vision_data.get('blue_robots', [])}")

        # ロボット制御の例: 黄色ロボットの位置と向きを取得
        yellow_robots = vision_data.get('yellow_robots', [])
        if yellow_robots:
            # 最初の黄色ロボットの情報を取得
            first_yellow_robot = yellow_robots[0]
            orientation_deg = first_yellow_robot.get('orientation_deg')

        # オレンジボールの位置を取得
        orange_balls = vision_data.get('orange_balls', [])
        if orange_balls:
            # 最初のオレンジボールの情報を取得
            first_orange_ball = orange_balls[0]
            ball_center_relative_cm = first_orange_ball.get(
                'center_relative_cm')
        # ---------------------------------

    except json.JSONDecodeError:
        print("Received data is not valid JSON. Skipping.")
    except socket.timeout:
        # recvfromがタイムアウトした場合 (ノンブロッキングまたは短いタイムアウト設定時)
        # ブロッキング設定 (デフォルト) の場合はここは実行されない
        pass
    except socket.error as e:
        print(f"Socket error receiving data: {e}")
        # エラーによっては再接続などを検討
        break  # エラー発生時はループを抜ける
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break  # その他のエラー発生時もループを抜ける

print("Stopping vision data reception loop.")
sock.close()  # プログラム終了時にソケットを閉じる
print("UDP socket closed.")
