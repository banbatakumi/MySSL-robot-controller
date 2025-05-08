import config


class BallPlacement:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def ball_placement(self, target_x, target_y):
        if (abs(self.state.court_ball_pos[0] - target_x) < config.PLACEMENT_R and abs(self.state.court_ball_pos[1] - target_y) < config.PLACEMENT_R):
            if self.state.photo_front == True:
                cmd = self.basic_move.move_to_pos(
                    target_x - config.ROBOT_R, target_y)
                cmd['cmd']['kick'] = 10
                cmd['cmd']['dribble'] = 30
                return cmd
            else:
                cmd = self.basic_move.move_to_pos(target_x - 30, target_y)
                cmd['cmd']['kick'] = 0
                return cmd

        else:
            if (self.state.photo_front == False):
                return self.basic_move.catch_ball()
            else:
                return self.basic_move.move_to_pos(target_x - config.ROBOT_R, target_y)
