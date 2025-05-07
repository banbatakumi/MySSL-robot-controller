import config
import math


class BallPlacement:
    def __init__(self, state):
        self.state = state

    def catch_ball(self):
        robot_dir_angle = self.state.robot_dir_angle
        robot_ball_angle = self.state.robot_ball_angle
        ball_dis = self.state.ball_dis

        move_speed = min(config.MAX_SPEED, ball_dis * 0.01)
        move_speed = max(0.4, move_speed)
        dribble = 0
        if ball_dis < 40 and abs(robot_ball_angle - robot_dir_angle) < 30:
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
