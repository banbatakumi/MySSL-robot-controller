import config
import math
import lib.my_math as mymath
import lib.pid as pid


class PassBall:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move
        self.receive_ball_pid = pid.PID(3, 0, 1)

    def pass_ball(self, target_x, target_y):
        target_dir = math.degrees(math.atan2(
            target_y - self.state.robot_pos[1], target_x - self.state.robot_pos[0])) * -1
        target_dis = math.hypot(
            target_x - self.state.robot_pos[0], target_y - self.state.robot_pos[1])

        kick = 0
        dribble = mymath.GapDeg(target_dir, self.state.robot_dir_angle) * 1.5
        if mymath.GapDeg(target_dir, self.state.robot_dir_angle) < 2:
            kick = target_dis * 60
        return self.basic_move.move(face_angle=target_dir,
                                    face_speed=mymath.PI,
                                    face_axis=1,
                                    dribble=dribble,
                                    kick=kick,)

    def receive_ball(self, target_x, target_y):
        target_dis = math.hypot(
            target_x - self.state.robot_pos[0], target_y - self.state.robot_pos[1])
        if self.state.ball_dis < 0.5 and target_dis < 0.3:
            move_dir = 90 if self.state.robot_ball_pos[0] > 0 else -90
            move_speed = abs(self.receive_ball_pid.update(0,
                                                          self.state.robot_ball_pos[0]))
            return self.basic_move.move(move_angle=move_dir,
                                        move_speed=move_speed,
                                        move_acce=0,
                                        face_angle=self.state.ball_angle,
                                        face_speed=mymath.HALF_PI,
                                        dribble=50)
        else:
            return self.basic_move.move_to_pos(target_x, target_y,
                                               face_angle=self.state.ball_angle)
