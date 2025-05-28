import time
import config
import random  # For dummy voltage

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

        self.basic_move = BasicMove(self.state)
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

        # ボールデータも必要に応じて取得
        orange_balls = vision_data.get('orange_balls', [])
        # Visionから取得するボールのデータ
        ball_vision_data = orange_balls[0] if orange_balls else None

        # 状態を更新
        self.state.update(robot_vision_data, ball_vision_data)

        # --- センサーデータの取得と処理 ---
        latest_sensor_data = self.udp.get_latest_robot_sensor_data(
            self.robot_id)

        if latest_sensor_data:
            if latest_sensor_data.get("type") == "sensor_data":
                self.state.photo_front = latest_sensor_data.get(
                    "photo", {}).get("front")
                self.state.photo_back = latest_sensor_data.get(
                    "photo", {}).get("back")
                # ここで電圧も取得できれば更新する。今回はStateのダミー値を使用。
                # self.state.voltage = latest_sensor_data.get("voltage", self.state.voltage)

        # ダミー電圧を少し変動させる (デモ用)
        self.state.voltage = round(11.8 + random.uniform(0, 0.4), 2)

        # --- GUIへのデータ送信 ---
        current_time = time.time()
        if current_time - self.last_gui_send_time >= config.GUI_UPDATE_INTERVAL:
            self.send_data_to_gui(ball_vision_data)  # ball_vision_data を渡す
            self.last_gui_send_time = current_time

        # --- 制御ロジック (以下は既存のロジックが実行される部分) ---
        if self.state.robot_pos is None or self.state.robot_dir_angle is None:
            # print(
            #     f"[Robot {self.robot_id} Controller] Incomplete vision data for control. Sending stop.")
            self.send_stop_command()
            return

        # ここに実際の戦略に基づいたコマンド生成ロジックが入る
        # 例: if self.mode == 'attack': cmd = self.attack() ...
        # 現状は process_data_and_control が直接コマンドを生成・送信していないため、
        # StrategyManager から各アルゴリズムが呼ばれてコマンドが生成される想定。
        # そのため、このメソッドでは主に状態更新とGUIへのデータ送信に注力する。

    def send_data_to_gui(self, ball_vision_data):
        """Stateオブジェクトの現在の情報とボール情報をGUIに送信する"""
        # GUIに送るロボットステータス
        robot_status_for_gui = {
            "id": self.robot_id,
            "pos": self.state.robot_pos,
            "angle": self.state.robot_dir_angle,
            "target_move_angle": self.target_move_angle,
            "target_move_speed": self.target_move_speed,
            "voltage": self.state.voltage,
            "photo_front": self.state.photo_front,
            "photo_back": self.state.photo_back,
            "ball_relative_angle": -self.state.robot_ball_angle if self.state.robot_ball_angle is not None else None,
            "ball_relative_distance": self.state.ball_dis
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
        if self.state.robot_dir_angle is not None:
            command_data['cmd']['vision_angle'] = self.state.robot_dir_angle
        else:
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
        # vision_angle は stop コマンドでは重要でない場合が多いが、
        # 必要であれば最新の観測値を付与することも考えられる
        if self.state.robot_dir_angle is not None:
            command_data['cmd']['vision_angle'] = self.state.robot_dir_angle

        self.udp.send_command(command_data, self.robot_id)
