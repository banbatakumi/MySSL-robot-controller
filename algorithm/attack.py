import math
import lib.my_math as mymath
import config
import lib.my_math as mymath


class Attack:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def attack(self):
        target_pos = [config.COURT_WIDTH * -0.5 * config.TEAM_SIDE - self.state.robot_pos[0],
                      0 - self.state.robot_pos[1]]

        target_angle = math.degrees(math.atan2(
            target_pos[1], target_pos[0])) * -1
        if (self.state.photo_front == True):
            face_angle = target_angle
            face_axis = 1

            dribble = mymath.GapDeg(
                self.state.robot_dir_angle, target_angle) * 1.5
            dribble = min(100, dribble)

            kick = None

            face_speed = mymath.GapDeg(
                self.state.robot_dir_angle, target_angle) * 0.01

            face_speed = min(mymath.PI, face_speed)
            face_speed = max(mymath.PI * 0.2, face_speed)

            move_speed = 0
            if mymath.GapDeg(self.state.robot_dir_angle, target_angle) < 10:
                move_speed = 1

            if mymath.GapDeg(self.state.robot_dir_angle, target_angle) < 5:
                kick = 100
                dribble = 0
            return self.basic_move.move(move_angle=0,
                                        move_speed=move_speed,
                                        move_acce=5,
                                        face_angle=face_angle,
                                        face_speed=face_speed,
                                        kick=kick,
                                        dribble=dribble
                                        )
        else:
            return self.basic_move.catch_ball()
