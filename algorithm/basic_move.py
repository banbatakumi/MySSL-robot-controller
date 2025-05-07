import config
import math


class BasicMove:
    def __init__(self, state):
        self.state = state

    def catch_ball(self):
        robot_angle = self.state.robot_angle
        robot_ball_angle = self.state.robot_ball_angle
        robot_ball_dis = self.state.robot_ball_dis

        move_speed = min(config.MAX_SPEED, robot_ball_dis * 0.01)
        move_speed = max(0.4, move_speed)
        dribble = 0
        if robot_ball_dis < 40 and abs(robot_ball_angle - robot_angle) < 30:
            dribble = 50

        return {
            "cmd": {
                "move_angle": round(robot_ball_angle, 0),
                "move_speed": round(move_speed, 2),
                "move_acce": 1,
                "face_angle": robot_ball_angle,
                "face_speed": 0,
                "face_axis": 0,
                "stop": False,
                "kick": 0,
                "dribble": dribble,
            }
        }

    def move_to_pos(self, target_x, target_y):
        # 目標までのベクトル
        vector = [target_x - self.state.robot_pos[0],
                  target_y - self.state.robot_pos[1]]

        # 目標までの距離
        distance = math.hypot(vector[0], vector[1])

        # 目標とする移動方向 (コート座標系での角度)
        move_angle = math.degrees(math.atan2(vector[1], vector[0])) * -1

        move_acce = 0
        move_max_speed = config.MAX_SPEED
        face_speed = 0
        face_axis = 0
        dribble = 0
        if self.state.photo_front == True:
            move_max_speed = 0.5
            move_acce = 0.1
            face_speed = math.pi * 0.5
            face_axis = 1
            dribble = 100

        speed = min(move_max_speed,
                    0.03 * distance)

        return {
            "cmd": {
                "move_angle": round(move_angle, 0),
                "move_speed": round(speed, 2),
                "move_acce": round(move_acce, 2),
                "face_angle": 0,
                "face_speed": face_speed,
                "face_axis": face_axis,
                "dribble": dribble,
                "kick": 0
            }
        }
