import math
import config


class Attack:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def attack(self):
        target_pos = [0, 0]
        if (config.TEAM_SIDE == "left"):
            target_pos = [config.COURT_WIDTH * 0.5 - self.state.robot_pos[0],
                          0 - self.state.robot_pos[1]]
        elif (config.TEAM_SIDE == "right"):
            target_pos = [config.COURT_WIDTH * -0.5 - self.state.robot_pos[0],
                          0 - self.state.robot_pos[1]]

        target_angle = math.degrees(math.atan2(
            target_pos[1], target_pos[0])) * -1
        if (self.state.photo_front == True):
            face_angle = target_angle
            face_axis = 1
            if abs(self.state.robot_dir_angle - target_angle) < 30:
                face_speed = 3.14 * 0.3
            else:
                face_speed = 3.14 * 0.6
            dribble = 100
            kick = None

            if abs(self.state.robot_dir_angle - target_angle) < 15:
                kick = 100
                dribble = 0
            return {
                "cmd": {
                    "move_angle": 0,
                    "move_speed": 0,
                    "move_acce": 3,
                    "face_angle": face_angle,
                    "face_axis": face_axis,
                    "face_speed": face_speed,
                    "stop": False,
                    "kick": kick,
                    "dribble": dribble,
                }
            }
        else:
            return self.basic_move.catch_ball()
