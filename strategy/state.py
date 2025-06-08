import math
import lib.my_math as mymath
import config


class State:
    def __init__(self):
        self.robot_num = 0
        self.robot_pos = []
        self.robot_dir_angle = []
        self.ball_pos = []
        self.ball_dis = []

    def update(self, robots_data, ball_data):
        court_ball_pos = list(ball_data.get('pos')) if ball_data else None
        if config.TEAM_SIDE == 'right':
            # 右側チームの場合、ボール位置を反転
            court_ball_pos[0] *= -1
            court_ball_pos[1] *= -1

        self.robot_num = len(robots_data) if robots_data else 0
        self.robot_pos = []
        self.robot_dir_angle = []
        self.ball_pos = []
        self.ball_dis = []

        for id in range(self.robot_num):
            robot_data = robots_data.get(str(id))
            if robot_data is None:
                self.robot_pos.append([0, 0])
                self.robot_dir_angle.append(0)
                self.ball_pos.append([0, 0])
                self.ball_dis.append(float('inf'))
                continue

            pos = list(robot_data.get('pos')) if robot_data.get(
                'pos') else [0, 0]
            angle = robot_data.get('angle') if robot_data.get(
                'angle') is not None else 0
            if config.TEAM_SIDE == 'right':
                # 右側チームの場合、位置と角度を反転
                pos[0] *= -1
                pos[1] *= -1
                angle = mymath.NormalizeDeg180(angle + 180)

            self.robot_pos.append(pos)
            self.robot_dir_angle.append(angle)

            if court_ball_pos is None:
                rel_ball_pos = [0, 0]
                self.ball_pos.append(rel_ball_pos)
                self.ball_dis.append(float('inf'))
                continue
            rel_ball_pos = [court_ball_pos[0] -
                            pos[0], court_ball_pos[1] - pos[1]]
            self.ball_pos.append(rel_ball_pos)
            self.ball_dis.append(math.hypot(rel_ball_pos[0], rel_ball_pos[1]))
