import params
import math
import lib.my_math as mymath
import lib.pid as pid


class BasicMove:
    def __init__(self, state):
        self.state = state
        self.move_to_pos_pid = pid.PID(3, 0, 0.5)

    def move(self, move_angle=0, move_speed=0, move_acce=0, face_angle=0, face_speed=0, face_axis=0, dribble=0, kick=0):
        move_speed = min(params.MAX_SPEED, move_speed)
        move_speed = max(0, move_speed)
        dribble = min(100, dribble)
        kick = min(100, kick)

        court_move_angle = mymath.NormalizeDeg180(
            move_angle + self.state.robot_dir_angle)
        stop_width = params.COURT_WIDTH * 0.5 - 0.2
        stop_height = params.COURT_HEIGHT * 0.5 - 0.2
        if (self.state.robot_pos[0] > stop_width and abs(court_move_angle) < 90) or (self.state.robot_pos[0] < -stop_width and abs(court_move_angle) > 90) or (self.state.robot_pos[1] > stop_height and court_move_angle < 0) or (self.state.robot_pos[1] < -stop_height and court_move_angle > 0):
            move_speed = 0
            move_acce = 0
        return {
            "cmd": {
                "move_angle": round(move_angle, 0),
                "move_speed": round(move_speed, 2),
                "move_acce": move_acce,
                "face_angle": face_angle,
                "face_speed": face_speed,
                "face_axis": face_axis,
                "dribble": dribble,
                "kick": kick
            }
        }

    def catch_ball(self):
        move_speed = self.state.ball_dis * 1.2
        move_speed = max(0.4, move_speed)
        dribble = 0
        if self.state.ball_dis < 0.4 and mymath.GapDeg(self.state.ball_angle, self.state.robot_dir_angle) < 30:
            dribble = 50

        return self.move(move_angle=0,
                         move_speed=move_speed,
                         move_acce=1,
                         face_angle=self.state.ball_angle,
                         dribble=dribble)

    def move_to_pos(self, target_x, target_y, face_angle=0, with_ball=False):
        # 目標までのベクトル
        vector = [target_x - self.state.robot_pos[0],
                  target_y - self.state.robot_pos[1]]

        # 目標までの距離
        distance = math.hypot(vector[0], vector[1])

        # 目標とする移動方向 (コート座標系での角度)
        move_angle = math.degrees(math.atan2(vector[1], vector[0])) * -1

        move_acce = 3
        move_max_speed = params.MAX_SPEED
        face_speed = 0
        face_axis = 0
        dribble = 0
        if with_ball == True:
            move_max_speed = 0.5
            dribble = distance * 200
            if (mymath.GapDeg(move_angle, self.state.robot_dir_angle) > 20):
                move_max_speed = 0
                dribble = 100
            move_acce = 1.5
            face_speed = mymath.HALF_PI
            face_axis = 1
            face_angle = move_angle
            move_angle = 0
        else:
            move_angle -= self.state.robot_dir_angle

        speed = abs(self.move_to_pos_pid.update(0, distance))
        speed = min(move_max_speed,
                    speed)

        return self.move(move_angle=move_angle,
                         move_speed=speed,
                         move_acce=move_acce,
                         face_angle=face_angle,
                         face_speed=face_speed,
                         face_axis=face_axis,
                         dribble=dribble)

    def move_to_ball(self, face_angle):
        move_angle = 0

        speed = abs(self.state.robot_ball_angle) * \
            0.02 + (self.state.ball_dis - 0.2) * 0.5

        if self.state.ball_dis < 0.2:
            theta = 90 + float((0.2 - self.state.ball_dis) / 0.2) * 45
            move_angle = self.state.robot_ball_angle
            if self.state.robot_ball_angle > 0:
                move_angle += theta
            else:
                move_angle -= theta
        else:
            ratio = 0.2 / self.state.ball_dis
            if ratio > 1:
                ratio = 1
            theta = math.asin(ratio) * 180 / mymath.PI
            move_angle = self.state.robot_ball_angle

            if self.state.robot_ball_angle > 0:
                move_angle += theta
            else:
                move_angle -= theta

        return self.move(move_angle=move_angle,
                         move_speed=speed,
                         move_acce=3,
                         face_angle=face_angle,
                         face_speed=mymath.PI)
