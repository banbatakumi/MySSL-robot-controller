import math
import config
from catch_ball import catch_ball


def atack(self, robot_pos):
    target_pos = [config.COURT_WIDTH - robot_pos[0], 0 - robot_pos[1]]
    target_angle = math.degrees(math.atan2(
        target_pos[1], target_pos[0])) * -1
    if (self.photo_front == True):
        face_angle = target_angle
        face_axis = 1
    if abs(self.robot_angle - target_angle) < 30:
        face_speed = 3.14 * 0.25
    face_speed = 3.14 * 0.5
    dribble = 50
    kick = None

    if abs(self.robot_angle - target_angle) < 15:
        kick = 100
        dribble = 0
        return {
            "cmd": {
                "move_angle": 0,
                "move_speed": 0,
                "move_acce": 1,
                "face_angle": face_angle,
                "face_axis": face_axis,
                "face_speed": face_speed,
                "kick": kick,
                "dribble": dribble,
            }
        }
    else:
        return catch_ball(self.robot_angle, self.robot_ball_angle, self.robot_ball_dis)
