import math
import lib.my_math as mymath


class State:
    def __init__(self):
        # センサ情報
        self.photo_front = None
        self.photo_back = None

        # ビジョン情報
        self.court_ball_pos = None

        self.ball_pos = None
        self.ball_dis = None
        self.ball_angle = None
        self.ball_court_center_angle = None
        self.ball_court_center_dis = None

        self.robot_ball_angle = None
        self.robot_ball_pos = None
        self.robot_pos = None
        self.robot_dir_angle = None
        self.robot_court_center_angle = None
        self.robot_court_center_dis = None

    def update(self, robot_data, ball_data):
        # ロボットの位置と向きを更新
        self.robot_pos = robot_data.get('pos') if robot_data else None
        self.robot_dir_angle = robot_data.get('angle') if robot_data else None

        if self.robot_pos is not None and self.robot_dir_angle is not None:
            # ロボットのコート中心からの角度と距離を計算
            self.robot_court_center_angle = mymath.NormalizeDeg180(
                math.degrees(math.atan2(
                    self.robot_pos[1], self.robot_pos[0])) * -1 + 180
            )
            self.robot_court_center_dis = math.hypot(
                self.robot_pos[0], self.robot_pos[1]
            )
        else:
            return

        # ボールの位置を更新
        self.court_ball_pos = ball_data.get('pos') if ball_data else None

        if self.court_ball_pos is not None and self.robot_pos is not None and self.robot_dir_angle is not None:
            # ロボットを基準としたボールの相対座標を計算
            self.ball_pos = [
                self.court_ball_pos[0] - self.robot_pos[0],
                self.court_ball_pos[1] - self.robot_pos[1],
            ]

            # ボールの角度と距離を計算
            self.ball_angle = math.degrees(
                math.atan2(self.ball_pos[1], self.ball_pos[0])
            ) * -1
            self.robot_ball_angle = mymath.NormalizeDeg180(
                self.ball_angle - self.robot_dir_angle
            )
            self.ball_dis = math.hypot(self.ball_pos[0], self.ball_pos[1])

            # ロボットから見たボールの座標 (向きも考慮)
            self.robot_ball_pos = [
                self.ball_dis * math.sin(math.radians(self.robot_ball_angle)),
                self.ball_dis * math.cos(math.radians(self.robot_ball_angle)),
            ]

            # ボールのコート中心からの角度と距離を計算
            self.ball_court_center_angle = mymath.NormalizeDeg180(
                math.degrees(
                    math.atan2(self.court_ball_pos[1], self.court_ball_pos[0])
                ) * -1 + 180
            )
            self.ball_court_center_dis = math.hypot(
                self.court_ball_pos[0], self.court_ball_pos[1]
            )
