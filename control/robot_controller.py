import time
import config
import random  # For dummy voltage
import lib.my_math as mymath

from lib.udp_communicator import UDPCommunicator

from control.state import State
from control.algorithm.basic_move import BasicMove
from control.algorithm.ball_placement import BallPlacement
from control.algorithm.attack import Attack
from control.algorithm.pass_ball import PassBall


class RobotController:
    """
    Visionデータとセンサーデータに基づいてロボットの制御指令を生成するクラス。
    特定のロボット (黄色 or 青色) の制御を担当する。
    GUIへの状態情報送信も行う。
    """

    def __init__(self, udp_communicator: UDPCommunicator, robot_id: int = 0):
        self.udp = udp_communicator
        self.robot_id = robot_id
        self.mode = 'stop'

        self.state = State()  # ロボットの状態を管理するインスタンス

        self.basic_move = BasicMove(self.state, self.robot_id)
        self.ball_placement_algo = BallPlacement(  # Renamed to avoid conflict
            self.state, self.basic_move)
        self.attack_algo = Attack(self.state, self.basic_move)  # Renamed
        self.pass_ball = PassBall(self.state, self.basic_move)

        # algorithmのメソッドへのショートカット
        self.ball_placement = self.ball_placement_algo.ball_placement
        self.attack = self.attack_algo.attack

        self.last_gui_send_time = 0
        self.target_move_angle = 0
        self.target_move_speed = 0

    def process_data_and_control(self, vision_data):
        """
        Visionデータとセンサーデータを取得し、制御ロジックを実行し、指令を送信する。
        GUIへも定期的にデータを送信する。
        このメソッドはメインループから定期的に呼び出されることを想定。
        """
        # --- 担当ロボットのVisionデータを見つける ---
        robot_vision_data = None  # Visionから取得する当該ロボットのデータ
        if config.TEAM_COLOR == 'yellow':
            yellow_robots = vision_data.get('yellow_robots', {})
            robot_vision_data = yellow_robots.get(str(self.robot_id))
        elif config.TEAM_COLOR == 'blue':
            blue_robots = vision_data.get('blue_robots', {})
            robot_vision_data = blue_robots.get(str(self.robot_id))
        # print(
        #     f"[Robot {self.robot_id} Controller] Processing vision data: {robot_vision_data}")

        # ボールデータも必要に応じて取得
        orange_balls = vision_data.get('orange_balls', [])
        # Visionから取得するボールのデータ
        ball_vision_data = orange_balls[0] if orange_balls else None

        # 状態を更新
        self.state.update(robot_vision_data, ball_vision_data, True)

        # --- センサーデータの取得と処理 ---
        latest_sensor_data = self.udp.get_latest_robot_sensor_data(
            self.robot_id)

        if latest_sensor_data:
            if latest_sensor_data.get("type") == "sensor_data":
                self.state.photo_front = latest_sensor_data.get(
                    "photo", {}).get("front")
                self.state.photo_back = latest_sensor_data.get(
                    "photo", {}).get("back")
                # self.state.voltage = latest_sensor_data.get(
                #     "voltage", self.state.voltage)
                print(
                    f"[Robot {self.robot_id} Controller] Sensor data received: {latest_sensor_data}")

        # ダミー電圧を少し変動させる (デモ用)
        self.state.voltage = round(11.8 + random.uniform(0, 0.4), 2)

        # --- GUIへのデータ送信 ---
        current_time = time.time()
        if current_time - self.last_gui_send_time >= config.GUI_UPDATE_INTERVAL:
            self.send_data_to_gui(robot_vision_data, ball_vision_data)
            self.last_gui_send_time = current_time

        # --- 制御ロジック (以下は既存のロジックが実行される部分) ---
        if self.state.robot_pos is None or self.state.robot_dir_angle is None:
            # print(
            #     f"[Robot {self.robot_id} Controller] Incomplete vision data for control. Sending stop.")
            self.send_stop_command()
            return

    def send_data_to_gui(self, robot_vision_data, ball_vision_data):
        """Stateオブジェクトの現在の情報とボール情報をGUIに送信する"""
        if robot_vision_data is None:
            return
        # GUIに送るロボットステータス
        robot_status_for_gui = {
            "id": self.robot_id,
            "pos": robot_vision_data.get('pos'),
            "angle": robot_vision_data.get('angle'),
            "target_move_angle": self.target_move_angle,
            "target_move_speed": self.target_move_speed,
            "voltage": self.state.voltage,
            "photo_front": self.state.photo_front,
            "photo_back": self.state.photo_back
        }

        # GUIに送るボール情報
        ball_pos_for_gui = ball_vision_data.get(
            'pos') if ball_vision_data else None

        gui_payload = {
            "type": "gui_update",
            "timestamp": int(time.time() * 1000),
            "robots_status": [robot_status_for_gui],
            "ball_pos": ball_pos_for_gui,
            "team_color": config.TEAM_COLOR
        }
        self.udp.send_to_gui(gui_payload)

    def send_command(self, cmd):
        self.target_move_angle = cmd['cmd']['move_angle']
        self.target_move_speed = cmd['cmd']['move_speed']

        command_data = cmd
        if config.TEAM_SIDE == 'right':
            command_data['cmd']['face_angle'] = mymath.NormalizeDeg180(
                cmd['cmd']['face_angle'] + 180)

        command_data['cmd']['vision_angle'] = self.state.robot_dir_angle
        if self.state.robot_dir_angle is None:
            command_data['cmd']['vision_angle'] = 0

        command_data['cmd']['stop'] = False
        self.udp.send_command(command_data, self.robot_id)

    def send_stop_command(self):
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
        if self.state.robot_dir_angle is not None:
            command_data['cmd']['vision_angle'] = self.state.robot_dir_angle

        self.udp.send_command(command_data, self.robot_id)
