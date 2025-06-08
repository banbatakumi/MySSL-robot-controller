import math
import lib.my_math as mymath
import lib.timer as timer
import config
import params


class State:
    def __init__(self):
        # センサ情報
        self.photo_front = None
        self.photo_back = None

        # ビジョン情報
        self.court_ball_pos = None

        self.prev_ball_pos = None
        self.ball_pos = None
        self.ball_dis = None
        self.ball_angle = None
        self.ball_vel = None
        self.ball_vel_angle = None
        self.ball_vel_mag = None
        self.robot_ball_angle = None
        self.robot_ball_pos = None

        self.robot_pos = None
        self.robot_dir_angle = None
        self.robot_court_center_angle = None
        self.robot_court_center_dis = None
        self.own_goal_angle = None
        self.own_goal_dis = None
        self.opp_goal_angle = None
        self.opp_goal_dis = None

        self.dt_timer = timer.Timer()

        self.ball_lost_timer = timer.Timer()
        self.robot_lost_timer = timer.Timer()
        self.ball_lost_timeout = 0.3  # 秒
        self.robot_lost_timeout = 0.3  # 秒

    def update(self, robot_data, ball_data, enable_point_symmetry=True):
        # ロボットの位置と向きを更新
        if robot_data and robot_data.get('pos') is not None and robot_data.get('angle') is not None:
            self.robot_pos = list(robot_data.get('pos'))
            self.robot_dir_angle = robot_data.get('angle')
            self.robot_lost_timer.set()
            self.robot_data_valid = True
        else:
            # データが来ていない場合、一定時間は前回値を保持
            if self.robot_lost_timer.read() < self.robot_lost_timeout:
                self.robot_data_valid = True
            else:
                self.robot_pos = None
                self.robot_dir_angle = None
                self.robot_data_valid = False

        if self.robot_pos is not None and self.robot_dir_angle is not None:
            if config.TEAM_SIDE == 'right' and enable_point_symmetry:
                # 右側チームの場合、角度を180度回転
                self.robot_dir_angle = mymath.NormalizeDeg180(
                    self.robot_dir_angle + 180
                )
                self.robot_pos[0] *= -1
                self.robot_pos[1] *= -1

            # ロボットのコート中心からの角度と距離を計算
            self.robot_court_center_angle = mymath.NormalizeDeg180(
                math.degrees(math.atan2(
                    self.robot_pos[1], self.robot_pos[0])) * -1 + 180
            )
            self.robot_court_center_dis = math.hypot(
                self.robot_pos[0], self.robot_pos[1]
            )

            # 両ゴールの位置と角度を計算
            own_goal_pos = [-params.COURT_WIDTH * 0.5 - self.robot_pos[0],
                            0 - self.robot_pos[1]]

            self.own_goal_angle = math.degrees(
                math.atan2(own_goal_pos[1], own_goal_pos[0])
            ) * -1
            self.own_goal_dis = math.hypot(own_goal_pos[0], own_goal_pos[1])

            opp_goal_pos = [params.COURT_WIDTH * 0.5 - self.robot_pos[0],
                            0 - self.robot_pos[1]]
            self.opp_goal_angle = math.degrees(
                math.atan2(opp_goal_pos[1], opp_goal_pos[0])
            ) * -1
            self.opp_goal_dis = math.hypot(opp_goal_pos[0], opp_goal_pos[1])
        else:
            return

        # ボールの位置を更新
        if ball_data and ball_data.get('pos') is not None:
            self.court_ball_pos = list(ball_data.get('pos'))
            self.ball_lost_timer.set()
            self.ball_data_valid = True
        else:
            if self.ball_lost_timer.read() < self.ball_lost_timeout:
                self.ball_data_valid = True
            else:
                self.court_ball_pos = None
                self.ball_data_valid = False

        if self.court_ball_pos is not None:
            if config.TEAM_SIDE == 'right' and enable_point_symmetry:
                # 右側チームの場合、ボールの位置を反転
                self.court_ball_pos[0] *= -1
                self.court_ball_pos[1] *= -1

            # ボール速度の計算
            if self.prev_ball_pos is not None:
                dt = self.dt_timer.read()
                if dt > 0:
                    dx = self.court_ball_pos[0] - self.prev_ball_pos[0]
                    dy = self.court_ball_pos[1] - self.prev_ball_pos[1]
                    self.ball_vel = [dx / dt, dy / dt]
                    self.ball_vel_mag = math.hypot(
                        self.ball_vel[0], self.ball_vel[1])
                    self.ball_vel_angle = math.degrees(
                        math.atan2(self.ball_vel[1], self.ball_vel[0]))
                else:
                    self.ball_vel = [0.0, 0.0]
                    self.ball_vel_mag = 0.0
                    self.ball_vel_angle = 0.0
            self.prev_ball_pos = self.court_ball_pos.copy()
            self.dt_timer.set()

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
