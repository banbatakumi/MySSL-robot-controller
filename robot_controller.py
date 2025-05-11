import time
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

    def process_data_and_control(self, vision_data):
        """
        Visionデータとセンサーデータを取得し、制御ロジックを実行し、指令を送信する。
        このメソッドはメインループから定期的に呼び出されることを想定。
        """
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
            self.send_stop_command()
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

    def send_command(self, cmd):
        command_data = cmd
        command_data['cmd']['vision_angle'] = self.state.robot_dir_angle
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
        self.udp.send_command(command_data, self.robot_id)
        # print(f"[{config.TEAM_COLOR.capitalize()} Robot Controller] Sent Stop Command.")
