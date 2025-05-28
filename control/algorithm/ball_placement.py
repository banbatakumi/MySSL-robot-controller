import config
import math


class BallPlacement:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def ball_placement(self, target_x, target_y):
        if (abs(self.state.court_ball_pos[0] - target_x) < config.PLACEMENT_R and abs(self.state.court_ball_pos[1] - target_y) < config.PLACEMENT_R):
            if self.state.ball_dis < config.PLACEMENT_R:
                return self.basic_move.move(move_angle=180,
                                            move_speed=0.5,
                                            move_acce=0.5,
                                            face_angle=self.state.ball_angle)
            else:
                return self.basic_move.move(face_angle=self.state.ball_angle)

        else:
            if (self.state.photo_front == False):
                return self.basic_move.catch_ball()
            else:
                # ターゲット
                # 座標をボールの角度だけ回転
                rotate_origin = [target_x, target_y]
                rotate_coord = [rotate_origin[0] - (target_x - config.ROBOT_R),
                                rotate_origin[1] - target_y]
                angle_rad = -math.radians(self.state.ball_angle) + 180
                rotated_x = rotate_origin[0] + (rotate_coord[0]) * \
                    math.cos(angle_rad) - rotate_coord[1] * math.sin(angle_rad)
                rotated_y = rotate_origin[1] + (rotate_coord[0]) * \
                    math.sin(angle_rad) + rotate_coord[1] * math.cos(angle_rad)
                return self.basic_move.move_to_pos(rotated_x, rotated_y, with_ball=True)
