import time
import math
# config はudp_communicator経由でアクセスされることが多いが、
# 制御ロジック自体で設定を使うならここでもインポート
# import config

from udp_communicator import UDPCommunicator


class RobotController:
    """
    Visionデータとセンサーデータに基づいてロボットの制御指令を生成するクラス。
    """

    def __init__(self, udp_communicator: UDPCommunicator):
        """
        Args:
            udp_communicator: UDPCommunicatorのインスタンス
        """
        self.udp = udp_communicator
        # 制御パラメータなどを初期化
        self.target_x_cm = 0.0
        self.target_y_cm = 0.0
        self.linear_speed_gain = 0.5  # 線形速度ゲイン
        self.angular_speed_gain = 2.0  # 角速度ゲイン
        self.max_linear_speed = 50.0  # 最大線形速度 cm/s
        self.max_angular_speed = 100.0  # 最大角速度 deg/s
        self.distance_threshold = 5.0  # 目標に近づいたと判断する距離 cm
        self.ball_dribble_distance = 20.0  # ボールをドリブル開始する距離 cm

    def process_data_and_control(self):
        """
        Visionデータとセンサーデータを取得し、制御ロジックを実行し、指令を送信する。
        このメソッドはメインループから定期的に呼び出されることを想定。
        """
        # --- Vision データの取得と処理 ---
        latest_vision_data = self.udp.get_latest_vision_data()

        if latest_vision_data:
            # 例: 最初の黄色ロボットの情報を取得
            yellow_robots = latest_vision_data.get('yellow_robots', [])
            orange_balls = latest_vision_data.get('orange_balls', [])

            first_yellow_robot = yellow_robots[0] if yellow_robots else None
            first_orange_ball = orange_balls[0] if orange_balls else None
            ball_xy = [0.0, 0.0]  # ボールの座標 (初期値)
            if (first_orange_ball):
                ball_xy = first_orange_ball.get('center_relative_cm')

            move_dir = 0.0  # 前後方向の速度 (例: cm/s)
            move_speed = 0.0  # 回転方向の速度 (例: deg/s)
            face_angle = 0.0  # 向く角度 (例: deg)
            kick = False
            do_dribble = False
            stop = False
            face_axis = 0

            if first_yellow_robot:
                center_relative_cm = first_yellow_robot.get(
                    'center_relative_cm')
                orientation_deg = first_yellow_robot.get('orientation_deg')

                if center_relative_cm[0] > ball_xy[0] - 20:
                    # ボールがロボットの前方にある場合
                    if center_relative_cm[1] > ball_xy[1]:
                        move_dir = 135
                    else:
                        move_dir = -135
                else:
                    if center_relative_cm[1] > ball_xy[1]:
                        move_dir = 45
                    else:
                        move_dir = -45
                move_speed = abs(
                    center_relative_cm[0] - (ball_xy[0] - 20)) * 0.025 + abs(center_relative_cm[1] - ball_xy[1]) * 0.025
                if (move_speed > 0.5):
                    move_speed = 0.5

                # デバッグ用
            #     print(
            #         f"Processing Vision Data (Yellow Robot): Pos={center_relative_cm}, Ori={orientation_deg:.1f}")

                print(f"ball_xy: {ball_xy}")
                # --- 指令データの構造化 ---
                # ESP32 がパースしやすい形式でデータを作成
                command_data = {
                    "ts": int(time.time() * 1000),  # タイムスタンプ (ミリ秒)
                    "cmd": {
                        "move_dir": move_dir,  # 直進速度
                        "move_speed": move_speed,  # 角速度 (回転)
                        "face_angle": face_angle,
                        "face_axis": face_axis,
                        "vision_own_dir": orientation_deg,  # 自分の向き
                        "stop": stop,  # 停止フラグ
                        "kick": kick,
                        "dribble": do_dribble
                        # 必要に応じて他のコマンドも追加 (例: 目標座標など)
                    }
                }

                # print(f"Generated Command: {command_data}") # デバッグ用

                # --- 指令データの送信 ---
                self.udp.send_command(command_data)

        # --- センサーデータの取得と処理 ---
        latest_sensor_data = self.udp.get_latest_sensor_data()

        if latest_sensor_data:
            # 例: ESP32 からエンコーダーデータやIMUデータを受信した場合の処理
            if latest_sensor_data.get("type") == "sensor_data":
                self.photo_front = latest_sensor_data.get(
                    "photo", {}).get("front")
                self.photo_back = latest_sensor_data.get(
                    "photo", {}).get("back")
            #     print(
            #         f"Processing Sensor Data: Front={self.photo_front}, Back={self.photo_back}")

                # センサーデータを使った制御や状態表示などを実装
                pass

        # その他の制御ロジック（状態遷移、戦略決定など）はここに追加
        pass
