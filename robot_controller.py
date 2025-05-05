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

            linear_speed = 0.0  # 前後方向の速度 (例: cm/s)
            angular_speed = 0.0  # 回転方向の速度 (例: deg/s)
            kick = False
            dribble = False

            if first_yellow_robot:
                center_relative_cm = first_yellow_robot.get(
                    'center_relative_cm')
                orientation_deg = first_yellow_robot.get('orientation_deg')

                # print(f"Processing Vision Data (Yellow Robot): Pos={center_relative_cm}, Ori={orientation_deg:.1f}") # デバッグ用

                # --- 制御指令の生成 ---
                # ここにロボットをどのように動かすかの制御ロジックを実装
                # Vision データに基づいて速度、角度などを計算

                if center_relative_cm and orientation_deg is not None:
                    current_x_cm = center_relative_cm[0]
                    current_y_cm = center_relative_cm[1]

                    # 目標位置への方向ベクトル (Y上向き正を想定)
                    dx = self.target_x_cm - current_x_cm
                    dy = self.target_y_cm - current_y_cm  # VisionのYは下向き正なので符号反転

                    distance_to_target = math.sqrt(dx**2 + dy**2)

                    if distance_to_target > self.distance_threshold:
                        # 距離に基づいた速度制御（近づくと遅く）
                        linear_speed = min(self.max_linear_speed, max(
                            0.0, distance_to_target * self.linear_speed_gain))

                        # 方向に基づいた回転制御
                        # 目標方向の角度 (ラジアン, -pi to pi)
                        target_angle_rad = math.atan2(dy, dx)  # Y上向き正を仮定
                        target_angle_deg = math.degrees(target_angle_rad)

                        # ロボットの現在の向き orientation_deg (Vision の Y下向き正) との差を計算
                        # Vision角度系と制御系角度系の整合性が必要
                        # 例: Vision (Y下向き正, 0=右, 90=下, 180=左, 270=上) -> 制御系 (Y上向き正, 0=右, 90=上, 180=左, -90=下)
                        # 簡単のため、ここでは Vision の角度をそのまま利用して差を計算
                        # ロボットの向きが target_angle_deg (Y上向き) と合うように回転
                        # Visionの0度が右向きなので、vision_orientationをY上向きの角度に変換（例：90度引く）
                        # 0=上, 90=右, 180=下, 270=左
                        vision_orientation_y_up = (
                            orientation_deg - 90 + 360) % 360
                        # 制御系の角度（例えば右手系、X右、Y上）にさらに変換が必要か検討
                        # ここでは簡易的に、目標方向(Y上向き) と Vision の向き (Y下向き) の差をそのまま使う (要調整)
                        # 例えば、ロボットの鼻先が Vision 0度(右) を向いている時、
                        # 目標が Vision 90度(下) なら、ロボットは時計回りに90度回る必要がある。
                        # target_angle_deg (Vision Y下向き) と orientation_deg (Vision Y下向き) の差
                        # Vision の角度系で差を計算
                        # -180～180度に正規化
                        angle_diff = (target_angle_deg -
                                      orientation_deg + 360 + 180) % 360 - 180

                        angular_speed = max(-self.max_angular_speed, min(
                            self.max_angular_speed, angle_diff * self.angular_speed_gain))
                    else:
                        # 目標に十分近づいたら停止
                        linear_speed = 0.0
                        angular_speed = 0.0

                # キックやドリブルの条件設定 (例: ボールが近くにある場合など)
                if first_orange_ball and first_yellow_robot and center_relative_cm and first_orange_ball.get('center_relative_cm'):
                    ball_relative_cm = first_orange_ball['center_relative_cm']
                    ball_dist_from_robot = math.sqrt(
                        (ball_relative_cm[0] - center_relative_cm[0])**2 + (ball_relative_cm[1] - center_relative_cm[1])**2)

                    if ball_dist_from_robot < self.ball_dribble_distance:
                        dribble = True  # ドリブル開始

                        # キックの条件例：ボールがロボットのすぐ前にあり、ロボットが目標方向を向いている
                        # (より複雑な条件が必要)
                        # kick_condition_met = ... # 例：ボールがロボット座標系で(10, 0)cm以内
                        # if kick_condition_met:
                        #    kick = True

                # --- 指令データの構造化 ---
                # ESP32 がパースしやすい形式でデータを作成
                command_data = {
                    "ts": int(time.time() * 1000),  # タイムスタンプ (ミリ秒)
                    "cmd": {
                        "lin_vel": round(linear_speed, 2),  # 直進速度
                        "ang_vel": round(angular_speed, 2),  # 角速度 (回転)
                        "kick": kick,
                        "dribble": dribble
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
                encoder_counts = latest_sensor_data.get(
                    "encoder", {}).get("counts")
                imu_yaw = latest_sensor_data.get("imu", {}).get("yaw")
                # print(f"Received Sensor Data: Encoder={encoder_counts}, IMU Yaw={imu_yaw}") # デバッグ用

                # センサーデータを使った制御や状態表示などを実装
                pass

        # その他の制御ロジック（状態遷移、戦略決定など）はここに追加
        pass
