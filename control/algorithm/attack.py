import math
import lib.my_math as mymath
import config
import params
import lib.my_math as mymath


class Attack:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def attack(self):
        if (self.state.photo_front == True):
            face_angle = self.state.opp_goal_angle
            face_axis = 1

            dribble = mymath.GapDeg(
                self.state.robot_dir_angle, self.state.opp_goal_angle) * 1.5
            dribble = min(100, dribble)

            kick = 0

            move_speed = 0
            if mymath.GapDeg(self.state.robot_dir_angle, self.state.opp_goal_angle) < 10:
                move_speed = 1

            if mymath.GapDeg(self.state.robot_dir_angle, self.state.opp_goal_angle) < 5:
                kick = 100
                dribble = 0
            return self.basic_move.move(move_angle=0,
                                        move_speed=move_speed,
                                        move_acce=5,
                                        face_angle=face_angle,
                                        face_axis=face_axis,
                                        face_speed=mymath.PI,
                                        kick=kick,
                                        dribble=dribble
                                        )
        else:
            return self.basic_move.catch_ball()
