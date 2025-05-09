import config
import math
import lib.my_math as mymath
import lib.pid as pid


class BasicMove:
    def __init__(self, state):
        self.state = state
        self.moveto_pos_pid = pid.PID(0.04, 0, 0.01)

    def move(self, angle, speed, acce):
        return {
            "cmd": {
                "move_angle": round(angle, 0),
                "move_speed": round(speed, 2),
                "move_acce": acce,
                "face_angle": 0,
                "face_speed": 0,
                "face_axis": 0,
                "dribble": 0,
                "kick": 0
            }
        }

    def catch_ball(self):
        move_speed = min(config.MAX_SPEED, self.state.ball_dis * 0.01)
        move_speed = max(0.4, move_speed)
        dribble = 0
        if self.state.ball_dis < 40 and mymath.GapDeg(self.state.ball_angle, self.state.robot_dir_angle) < 30:
            dribble = 50

        return {
            "cmd": {
                "move_angle": 0,
                "move_speed": round(move_speed, 2),
                "move_acce": 1,
                "face_angle": self.state.ball_angle,
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

        move_acce = 3
        move_max_speed = config.MAX_SPEED
        face_speed = 0
        face_axis = 0
        dribble = 0
        if self.state.photo_front == True:
            move_max_speed = 0.5
            if (mymath.GapDeg(0, self.state.robot_dir_angle) > 20):
                move_max_speed = 0
            move_acce = 1
            face_speed = mymath.HALF_PI
            face_axis = 1
            dribble = 100

        speed = abs(self.moveto_pos_pid.update(0, distance))
        speed = min(move_max_speed,
                    speed)

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

    def move_to_ball(self, angle):
        move_angle = 0

        speed = abs(self.state.robot_ball_angle) * \
            0.02 + (self.state.ball_dis - 20) * 0.02

        speed = min(config.MAX_SPEED, speed)
        speed = max(0, speed)

        if self.state.ball_dis < 20:
            theta = 90 + float((20 - self.state.ball_dis) / 20) * 45
            move_angle = self.state.robot_ball_angle
            if self.state.robot_ball_angle > 0:
                move_angle += theta
            else:
                move_angle -= theta
        else:
            ratio = 20 / self.state.ball_dis
            if ratio > 1:
                ratio = 1
            theta = math.asin(ratio) * 180 / mymath.PI
            move_angle = self.state.robot_ball_angle

            if self.state.robot_ball_angle > 0:
                move_angle += theta
            else:
                move_angle -= theta

        return {
            "cmd": {
                "move_angle": round(move_angle, 0),
                "move_speed": round(speed, 2),
                "move_acce": 3,
                "face_angle": angle,
                "face_speed": mymath.PI,
                "face_axis": 0,
                "dribble": 0,
                "kick": 0
            }
        }
