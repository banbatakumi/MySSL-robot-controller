import time
import math
import lib.my_math as mymath
import config

from lib.udp_communicator import UDPCommunicator

from state import State
from algorithm.basic_move import BasicMove
from algorithm.ball_placement import BallPlacement
from algorithm.attack import Attack


class RobotController:
    """
    Visionデータとセンサーデータに基づいてロボットの制御指令を生成するクラス。
    特定のロボット (黄色 or 青色) の制御を担当する。
    """

    def __init__(self, udp_communicator: UDPCommunicator, robot_id: int = 0):
        self.udp = udp_communicator
        self.robot_id = robot_id
        self.mode = 'stop'

        self.state = State()  # ロボットの状態を管理するインスタンス

        self.basic_move = BasicMove(self.state)
        self.ball_placement = BallPlacement(
            self.state, self.basic_move)  # エイリアスを作成
        self.attack = Attack(self.state, self.basic_move)
        self.ball_placement = self.ball_placement.ball_placement
        self.attack = self.attack.attack

    def handle_game_command(self, command_data):
        """
        外部からのゲームコマンドを処理し、ロボットの動作モードを切り替える。
        """
        cmd_type = command_data.get("type")
        cmd = command_data.get("command")
        target_team_color = command_data.get("team_color")

        if target_team_color is not None and target_team_color != config.TEAM_COLOR:
            return

        if cmd_type == "game_command":
            print(
                f"[Robot {self.robot_id} Controller] Processing game command: {cmd}")

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
                self.mode = 'ball_placement'
            else:
                print(
                    f"[Robot {self.robot_id} Controller] Received unknown game command: {cmd}")

    def process_data_and_control(self, vision_data):
        """
        Visionデータとセンサーデータを取得し、制御ロジックを実行し、指令を送信する。
        このメソッドはメインループから定期的に呼び出されることを想定。
        """
        if not vision_data:
            return

        # --- 担当ロボットのVisionデータを見つける ---
        robot_data = None
        if config.TEAM_COLOR == 'yellow':
            yellow_robots = vision_data.get('yellow_robots', {})
            robot_data = yellow_robots.get(str(self.robot_id))  # 安全にキーを取得

        elif config.TEAM_COLOR == 'blue':
            blue_robots = vision_data.get('blue_robots', {})
            robot_data = blue_robots.get(str(self.robot_id))

        # ボールデータも必要に応じて取得
        orange_balls = vision_data.get('orange_balls', [])
        ball_data = orange_balls[0] if orange_balls else None

        # 状態を更新
        self.state.update(robot_data, ball_data)

        if self.state.robot_pos is None or self.state.robot_dir_angle is None:
            print(
                f"[Robot {self.robot_id} Controller] Incomplete vision data.")
            self._send_stop_command()
            return
        # --- センサーデータの取得と処理 ---
        latest_sensor_data = self.udp.get_latest_robot_sensor_data(
            self.robot_id)

        if latest_sensor_data:
            if latest_sensor_data.get("type") == "sensor_data":
                # センサーデータを更新
                self.state.photo_front = latest_sensor_data.get(
                    "photo", {}).get("front")
                self.state.photo_back = latest_sensor_data.get(
                    "photo", {}).get("back")
                # print(
                #     f"[{config.TEAM_COLOR.capitalize()} Robot Controller] Sensor Data: {latest_sensor_data}")

        if self.mode != 'stop' and self.state.court_ball_pos is None:
            return

        # --- 制御ロジック実行 ---
        command_data = None
        if self.mode == 'stop':
            self._send_stop_command()
        elif self.mode == 'start_game':
            command_data = self.attack()

        elif self.mode == 'stop_game':
            # command_data = self.basic_move.move_to_ball(
            #     mymath.NormalizeDeg180(self.state.ball_court_center_angle + 180))
            command_data = self.basic_move.move_to_pos(-30, 0)
        elif self.mode == 'ball_placement':
            command_data = self.ball_placement(self._placement_target_pos[0],
                                               self._placement_target_pos[1])

        # --- 指令データの送信 ---
        if command_data:
            # 共通の基本情報をコマンドに追加
            # command_data['ts'] = int(time.time() * 1000)  # タイムスタンプ (ミリ秒)
            command_data['cmd']['vision_angle'] = self.state.robot_dir_angle
            command_data['cmd']['stop'] = False

            # デバッグ用
            # print(
            #     f"[Robot {self.robot_id} Controller] Generated Command: {command_data}")

            self.udp.send_command(command_data, self.robot_id)
        else:
            pass

    def _send_stop_command(self):
        """安全のため、停止コマンドを送信するヘルパーメソッド"""
        command_data = {
            "ts": int(time.time() * 1000),
            "cmd": {
                "move_angle": 0,
                "move_speed": 0,
                "move_acce": 0,
                "face_angle": 0,
                "face_axis": 0,
                "stop": True,
                "kick": False,
                "dribble": False,
            }
        }
        self.udp.send_command(command_data, self.robot_id)
        # print(f"[{config.TEAM_COLOR.capitalize()} Robot Controller] Sent Stop Command.")
