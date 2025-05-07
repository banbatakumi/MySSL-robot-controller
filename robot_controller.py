import time
import math
import config

from udp_communicator import UDPCommunicator
from algorithm.move_to_pos import move_to_pos
from algorithm.catch_ball import catch_ball


class RobotController:
    """
    Visionデータとセンサーデータに基づいてロボットの制御指令を生成するクラス。
    特定のロボット (黄色 or 青色) の制御を担当する。
    """

    def __init__(self, udp_communicator: UDPCommunicator, robot_color: str):
        self.udp = udp_communicator
        self.robot_color = robot_color.lower()  # 'yellow' または 'blue'

        # センサーデータ保持用 (このインスタンスが担当するロボットのもの)
        self.photo_front = None
        self.photo_back = None
        self.ball_pos = None
        self.robot_pos = None
        self.robot_angle = None
        self.robot_ball_pos = None
        self.robot_ball_angle = None
        self.robot_ball_dis = None

        self.mode = 'stop'

        print(f"[{self.robot_color.capitalize()} Robot Controller] Initialized.")

    def handle_game_command(self, command_data):
        """
        外部からのゲームコマンドを処理し、ロボットの動作モードを切り替える。
        """
        cmd_type = command_data.get("type")
        cmd = command_data.get("command")
        target_robot_color = command_data.get("robot_color")

        if target_robot_color is not None and target_robot_color != self.robot_color:
            return

        if cmd_type == "game_command":
            print(
                f"[{self.robot_color.capitalize()} Robot Controller] Processing game command: {cmd}")

            if cmd == "stop_game":
                self.mode = 'stop_game'
                self._placement_target_pos = None
            elif cmd == "start_game":
                self.mode = 'start_game'
                self._placement_target_pos = None
            elif cmd == "emergency_stop":
                self.mode = 'stop'
                self._placement_target_pos = None
                self._send_stop_command()  # 受信ループとは別に即座に停止コマンドを送信
            elif cmd == "place_ball":
                target_x = command_data.get("x")
                target_y = command_data.get("y")
                self._placement_target_pos = [target_x, target_y]
                self.mode = 'ball_placement'  # ボール配置移動モードへ
            else:
                print(
                    f"[{self.robot_color.capitalize()} Robot Controller] Received unknown game command: {cmd}")

    def process_data_and_control(self):
        """
        Visionデータとセンサーデータを取得し、制御ロジックを実行し、指令を送信する。
        このメソッドはメインループから定期的に呼び出されることを想定。
        """
        # ロボットが有効化されているかチェック
        if self.robot_color == 'yellow' and not config.ENABLE_YELLOW_ROBOT:
            return
        if self.robot_color == 'blue' and not config.ENABLE_BLUE_ROBOT:
            return

        # --- Vision データの取得 ---
        latest_vision_data = self.udp.get_latest_vision_data()
        # print(
        #     f"[{self.robot_color.capitalize()} Robot Controller] Latest Vision Data: {latest_vision_data}")

        if not latest_vision_data:
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
            print(
                f"[{self.robot_color.capitalize()} Robot Controller] Own vision data not found.")
            self._send_stop_command()
            return

        # ロボットの位置と向きを取得
        self.robot_pos = robot_data.get('pos')
        self.robot_angle = robot_data.get('angle')

        if self.robot_pos is None or self.robot_angle is None:
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
        latest_sensor_data = None
        if self.robot_color == 'yellow':
            latest_sensor_data = self.udp.get_latest_yellow_sensor_data()
        elif self.robot_color == 'blue':
            latest_sensor_data = self.udp.get_latest_blue_sensor_data()

        if latest_sensor_data:
            if latest_sensor_data.get("type") == "sensor_data":
                # 自分のインスタンスのセンサーデータを更新
                self.photo_front = latest_sensor_data.get(
                    "photo", {}).get("front")
                self.photo_back = latest_sensor_data.get(
                    "photo", {}).get("back")
                print(
                    f"[{self.robot_color.capitalize()} Robot Controller] Sensor Data: Front={self.photo_front}, Back={self.photo_back}")

        # --- 制御ロジック実行 ---
        command_data = None
        if self.mode == 'stop':
            self._send_stop_command()
        elif self.mode == 'start_game':
            command_data = self._control_move_around_ball()
        elif self.mode == 'stop_game':
            command_data = move_to_pos(self.robot_pos, [0, 0])
        elif self.mode == 'ball_placement':
            command_data = self._control_ball_placement()

        # --- 指令データの送信 ---
        if command_data:
            # 共通の基本情報をコマンドに追加
            # command_data['ts'] = int(time.time() * 1000)  # タイムスタンプ (ミリ秒)
            command_data['cmd']['vision_angle'] = self.robot_angle
            command_data["cmd"]["move_angle"] -= self.robot_angle
            command_data['cmd']['stop'] = False

            # print(f"[{self.robot_color.capitalize()} Robot Controller] Generated Command: {command_data}") # デバッグ用

            self.udp.send_command(command_data, self.robot_color)
        else:
            pass

    def _control_ball_placement(self):
        target_x, target_y = self._placement_target_pos

        if (abs(self.ball_pos[0] - self._placement_target_pos[0]) < 15 and abs(self.ball_pos[1] - self._placement_target_pos[1]) < 15):
            if self.photo_front == True:
                cmd = move_to_pos(
                    self.robot_pos, [target_x - 10, target_y], self.photo_front)
                cmd['cmd']['kick'] = 10
                cmd['cmd']['dribble'] = 30
                return cmd
            else:
                cmd = move_to_pos(
                    self.robot_pos, [target_x - 30, target_y], self.photo_front)
                cmd['cmd']['kick'] = 0
                return cmd

        else:
            if (self.photo_front == False):
                return catch_ball(self.robot_angle, self.robot_ball_angle, self.robot_ball_dis)
            else:
                return move_to_pos(self.robot_pos, [target_x - 10, target_y], self.photo_front)

    def _control_move_around_ball(self):
        target_pos = [100 - self.robot_pos[0], 0 - self.robot_pos[1]]
        target_angle = math.degrees(math.atan2(
            target_pos[1], target_pos[0])) * -1
        if (self.photo_front == True):
            face_angle = target_angle
            face_axis = 1
            if abs(self.robot_angle - target_angle) < 30:
                face_speed = 3.14 * 0.25
            face_speed = 3.14 * 0.5
            dribble = 50
            kick = None

            if abs(self.robot_angle - target_angle) < 15:
                kick = 100
                dribble = 0
            return {
                "cmd": {
                    "move_angle": 0,
                    "move_speed": 0,
                    "move_acce": 1,
                    "face_angle": face_angle,
                    "face_axis": face_axis,
                    "face_speed": face_speed,
                    "stop": False,
                    "kick": kick,
                    "dribble": dribble,
                }
            }
        else:
            return catch_ball(self.robot_angle, self.robot_ball_angle, self.robot_ball_dis)

    def _send_stop_command(self):
        """安全のため、停止コマンドを送信するヘルパーメソッド"""
        command_data = {
            "ts": int(time.time() * 1000),
            "cmd": {
                "move_angle": 0.0,
                "move_speed": 0.0,
                "move_acce": 0,
                "face_angle": 0.0,
                "face_axis": 0,
                "stop": True,
                "kick": False,
                "dribble": False,
            }
        }
        self.udp.send_command(command_data, self.robot_color)
        # print(f"[{self.robot_color.capitalize()} Robot Controller] Sent Stop Command.")
