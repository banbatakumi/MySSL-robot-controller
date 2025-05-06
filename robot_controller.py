import time
import math
import config  # config.py から設定を読み込む

from udp_communicator import UDPCommunicator


class RobotController:
    """
    Visionデータとセンサーデータに基づいてロボットの制御指令を生成するクラス。
    特定のロボット (黄色 or 青色) の制御を担当する。
    """

    def __init__(self, udp_communicator: UDPCommunicator, robot_color: str):
        """
        Args:
            udp_communicator: UDPCommunicatorのインスタンス
            robot_color: このコントローラーが担当するロボットの色 ('yellow' or 'blue')
        """
        self.udp = udp_communicator
        self.robot_color = robot_color.lower()  # 'yellow' または 'blue'

        # 元コードにあったパラメータは移動ロジック依存なので、今回はシンプルに共通設定を使用

        # センサーデータ保持用 (このインスタンスが担当するロボットのもの)
        self.photo_front = None
        self.photo_back = None
        self.ball_pos = None
        self.robot_pos = None
        self.robot_angle = None
        self.robot_ball_pos = None
        self.robot_ball_angle = None
        self.robot_ball_dis = None
        # 他のセンサーデータも必要に応じて追加

        # 制御モード ('idle', 'move_to_center', 'move_around_ball' など)
        self.mode = 'move_around_ball'  # 初期モードをコート中心移動とする

        print(f"[{self.robot_color.capitalize()} Robot Controller] Initialized.")

    def process_data_and_control(self):
        """
        Visionデータとセンサーデータを取得し、制御ロジックを実行し、指令を送信する。
        このメソッドはメインループから定期的に呼び出されることを想定。
        担当ロボットが無効化されている場合は何もしない。
        """
        # ロボットが有効化されているかチェック
        if self.robot_color == 'yellow' and not config.ENABLE_YELLOW_ROBOT:
            return
        if self.robot_color == 'blue' and not config.ENABLE_BLUE_ROBOT:
            return

        # --- Vision データの取得 ---
        # Visionデータは全ロボット共通なので、communicatorからまとめて取得
        latest_vision_data = self.udp.get_latest_vision_data()
        # print(
        #     f"[{self.robot_color.capitalize()} Robot Controller] Latest Vision Data: {latest_vision_data}")

        if not latest_vision_data:
            # Visionデータがない場合は制御できない
            return

        # --- 担当ロボットのVisionデータを見つける ---
        robot_data = None
        if self.robot_color == 'yellow':
            yellow_robots = latest_vision_data.get('yellow_robots', [])
            robot_data = yellow_robots[0] if yellow_robots else None
        elif self.robot_color == 'blue':
            blue_robots = latest_vision_data.get('blue_robots', [])
            robot_data = blue_robots[0] if blue_robots else None

        if not robot_data:
            # 担当ロボットのVisionデータが見つからない
            print(
                f"[{self.robot_color.capitalize()} Robot Controller] Own vision data not found.")
            self._send_stop_command()
            return

        # ロボットの位置と向きを取得
        self.robot_pos = robot_data.get('pos')
        self.robot_angle = robot_data.get('angle')

        if self.robot_pos is None or self.robot_angle is None:
            # 位置や向きデータが不完全
            print(
                f"[{self.robot_color.capitalize()} Robot Controller] Incomplete vision data.")
            self._send_stop_command()
            return
        # print(
        #     f"[{self.robot_color.capitalize()} Robot Controller] Position: {self.robot_pos}, Angle: {self.robot_angle}")

        # ボールデータも必要に応じて取得
        orange_balls = latest_vision_data.get('orange_balls', [])
        first_orange_ball = orange_balls[0] if orange_balls else None
        if orange_balls:
            self.ball_pos = first_orange_ball.get('pos')
            self.robot_ball_pos = [
                self.ball_pos[0] - self.robot_pos[0], self.ball_pos[1] - self.robot_pos[1]]
            self.robot_ball_angle = math.degrees(
                math.atan2(self.robot_ball_pos[1], self.robot_ball_pos[0])) * -1

            self.robot_ball_dis = math.hypot(
                self.robot_ball_pos[0], self.robot_ball_pos[1])
            # print(
            #     f"RobotBallPos{self.robot_ball_pos}, RobotBallAngle: {self.robot_ball_angle}, RobotBallDis: {self.robot_ball_dis}")

        # --- センサーデータの取得と処理 ---
        # 担当ロボットの色に対応するキューからセンサーデータを取得
        latest_sensor_data = None
        if self.robot_color == 'yellow':
            latest_sensor_data = self.udp.get_latest_yellow_sensor_data()
        elif self.robot_color == 'blue':
            latest_sensor_data = self.udp.get_latest_blue_sensor_data()

        if latest_sensor_data:
            # 例: ESP32 からエンコーダーデータやIMUデータ、光センサーを受信した場合
            if latest_sensor_data.get("type") == "sensor_data":
                # 自分のインスタンスのセンサーデータを更新
                self.photo_front = latest_sensor_data.get(
                    "photo", {}).get("front")
                self.photo_back = latest_sensor_data.get(
                    "photo", {}).get("back")
                print(
                    f"[{self.robot_color.capitalize()} Robot Controller] Sensor Data: Front={self.photo_front}, Back={self.photo_back}")
            # 他のセンサーデータ処理もここに追加

        # --- 制御ロジック実行 ---
        # 現在のモードに基づいて制御指令を生成
        command_data = None
        if first_orange_ball is None and self.photo_front == False:
            command_data = self._control_move_to_pos(
                -20, 0)
        else:
            command_data = self._control_move_around_ball()
        # 必要に応じて他のモードを追加

        # --- 指令データの送信 ---
        if command_data:
            # 共通の基本情報をコマンドに追加
            command_data['ts'] = int(time.time() * 1000)  # タイムスタンプ (ミリ秒)
            # Visionの自己位置情報はロボット側でも活用できる場合があるので送る
            command_data['cmd']['vision_angle'] = self.robot_angle

            # print(f"[{self.robot_color.capitalize()} Robot Controller] Generated Command: {command_data}") # デバッグ用

            self.udp.send_command(command_data, self.robot_color)
        else:
            # どのモードでも有効なコマンドを生成しなかった場合（例: モードが'idle'など）
            # 安全のため停止コマンドを送ることも検討
            pass  # この例では何もしない

    def _control_move_to_pos(self, target_x, target_y):
        """
        ロボットをコートの中心 (0, 0) へ移動させる制御ロジック。
        Visionデータに基づいて指令を生成する。
        Args:
            robot_pos_cm: ロボットの現在位置 [x, y] (cm)
            robot_angle: ロボットの現在の向き (deg)

        Returns:
            送信するコマンドデータの辞書。移動完了時は停止コマンドを含む。
        """

        # 目標までのベクトル
        dx = target_x - self.robot_pos[0]
        dy = target_y - self.robot_pos[1]

        # 目標までの距離
        distance = math.hypot(dx, dy)  # math.sqrt(dx*dx + dy*dy)

        # 目標とする移動方向 (コート座標系での角度)
        # 角度は+X軸基準(右方向)で反時計回りが正。
        desired_court_angle = math.degrees(math.atan2(dy, dx)) * -1

        # 目標までの距離が閾値以下なら停止
        if distance < config.CENTER_MOVE_DISTANCE_THRESHOLD:
            print(
                f"[{self.robot_color.capitalize()} Robot Controller] Reached center.")
            return {
                "cmd": {
                    "move_angle": 0.0,      # 直進速度 (停止)
                    "move_speed": 0.0,    # 回転速度 (停止)
                    "face_angle": 0.0,    # Faceコマンド無効
                    "face_axis": 0,       # Faceコマンド無効
                    "stop": False,         # 停止フラグ
                    "kick": False,
                    "dribble": False,
                }
            }
        else:
            # 目標距離に応じた速度を計算
            # 線形に速度を上げ、最大速度でクリップ
            speed = min(
                config.MAX_LINEAR_SPEED_M_S,
                config.CENTER_MOVE_LINEAR_GAIN * distance
            )
            # 角度を合わせながら移動する
            # `face_angle` コマンドが指定した絶対角度に向く機能を持つと仮定
            return {
                "cmd": {
                    "move_angle": round(desired_court_angle, 0),
                    "move_speed": round(speed, 2),
                    "face_angle": 0,
                    "face_axis": 0,
                    "stop": False,
                    "kick": False,
                    "dribble": False,
                }
            }

    def _control_move_around_ball(self):
        """
        ボールの周りを移動する制御ロジック。
        ボールの位置に基づいて指令を生成する。

        Returns:
            送信するコマンドデータの辞書。
        """
        if self.robot_ball_dis is None or self.robot_ball_angle is None:
            # ボールデータが不完全な場合は停止
            return

        # ボールの周りを回るための角度と速度を計算
        move_angle = 0
        move_speed = 0.7
        if (self.robot_ball_dis < 40):
            move_speed = 0.5

        kick = None
        dribble = False
        if (self.robot_ball_dis < 25 and abs(self.robot_ball_angle - self.robot_angle) < 20):
            dribble = True
        face_angle = self.robot_ball_angle
        face_axis = 0
        face_speed = 3.14 * 1.5

        target_pos = [100 - self.robot_pos[0], 0 - self.robot_pos[1]]
        target_angle = math.degrees(math.atan2(
            target_pos[1], target_pos[0])) * -1
        if (self.photo_front == True):
            move_speed = 0
            face_angle = target_angle
            face_axis = 1
            if abs(self.robot_angle - target_angle) < 30:
                face_speed = 3.14 * 0.25
            face_speed = 3.14 * 0.5
            dribble = True
        if abs(self.robot_angle - target_angle) < 15:
            kick = 100
            dribble = False

        return {
            "cmd": {
                "move_angle": round(move_angle, 0),
                "move_speed": round(move_speed, 2),
                "face_angle": face_angle,
                "face_axis": face_axis,
                "face_speed": face_speed,
                "stop": False,
                "kick": kick,
                "dribble": dribble,
            }
        }

    def _send_stop_command(self):
        """安全のため、停止コマンドを送信するヘルパーメソッド"""
        command_data = {
            "ts": int(time.time() * 1000),
            "cmd": {
                "move_angle": 0.0,
                "move_speed": 0.0,
                "face_angle": 0.0,
                "face_axis": 0,
                "stop": False,
                "kick": False,
                "dribble": False,
            }
        }
        self.udp.send_command(command_data, self.robot_color)
        # print(f"[{self.robot_color.capitalize()} Robot Controller] Sent Stop Command.")
