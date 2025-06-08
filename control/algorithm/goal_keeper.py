import params
import lib.my_math as mymath
import lib.pid as pid

BALL_KICK_TIME = 1


class GoalKeeper:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def run(self):
        in_goal_area = (
            self.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
            abs(self.state.court_ball_pos[1]) < params.GOAL_AREA_WIDTH * 0.5
        )
        # ゴール中心
        goal_x = -params.COURT_WIDTH * 0.5
        goal_y = 0

        defense_line_x = goal_x + params.ROBOT_D

        ball_x, ball_y = self.state.court_ball_pos
        ball_vx, ball_vy = self.state.ball_vel

        if in_goal_area and self.state.ball_vel_mag > 0.05:
            if abs(ball_vx) > 0:
                t = (defense_line_x - ball_x) / ball_vx
                if t > 0:
                    y_on_defense = ball_y + ball_vy * t
                else:
                    y_on_defense = ball_y
            else:
                y_on_defense = ball_y
            y = mymath.clip(y_on_defense, -params.GOAL_WIDTH *
                            0.5, params.GOAL_WIDTH * 0.5)
            x = defense_line_x
        else:
            if ball_x > goal_x:
                t = (goal_x + params.ROBOT_D - ball_x) / \
                    (goal_x - ball_x + 1e-8)
                y_on_line = ball_y + (goal_y - ball_y) * t
            else:
                y_on_line = ball_y
            y = mymath.clip(y_on_line, -params.GOAL_WIDTH *
                            0.5, params.GOAL_WIDTH * 0.5)
            x = goal_x + params.ROBOT_D

        return self.basic_move.move_to_pos(x, y)
