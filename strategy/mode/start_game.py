import math
import params
import config
import strategy.algorithm.alignment as alignment


class StartGame:
    def __init__(self, utils):
        self.utils = utils

    def run(self, id, rc, closest_robot_to_ball):
        if config.NUM_ROBOTS == 2:
            if id == 0:
                x = -params.COURT_WIDTH / 2 + params.ROBOT_D
                y = rc.state.court_ball_pos[1]
                y = max(min(y, params.GOAL_WIDTH / 2), -params.GOAL_WIDTH / 2)
                return rc.basic_move.move_to_pos(x, y)
            else:
                return rc.attack()
        elif config.NUM_ROBOTS <= 6:
            if id == 0:
                x = -params.COURT_WIDTH / 2 + params.ROBOT_D
                y = rc.state.court_ball_pos[1]
                y = max(min(y, params.GOAL_WIDTH / 2), -params.GOAL_WIDTH / 2)
                return rc.basic_move.move_to_pos(x, y)

            elif rc.state.court_ball_pos[0] < 0:
                if id <= 3:
                    x = -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT + 0.2
                    y = rc.state.court_ball_pos[1]
                    y = max(min(y, params.GOAL_WIDTH), -params.GOAL_WIDTH)
                    return alignment.liner_alignment(id, rc, 1, 3, [x, y - 0.2], [x, y + 0.2])
                elif id ==
                elif id == 4:
                    return rc.basic_move.move_to_pos(x, y)
                elif id == 5:
                    x = 0
                    y = -params.COURT_HEIGHT / 2 + 0.5
                    return rc.basic_move.move_to_pos(x, y)
            else:
                # ゴールエリア前に2台整列（id=1,2）
                if id <= 2:
                    x = -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT + 0.2
                    y = rc.state.court_ball_pos[1]
                    y = max(min(y, params.GOAL_WIDTH), -params.GOAL_WIDTH)
                    return alignment.liner_alignment(id, rc, 1, 2, [x, y - 0.1], [x, y + 0.1])
                # 相手ゴール斜めに2台パス待機（id=3,4）
                elif id == 3:
                    x = params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 0.2
                    y = params.GOAL_AREA_WIDTH / 2 + 0.2
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(x, y)
                elif id == 4:
                    x = params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 0.2
                    y = -params.GOAL_AREA_WIDTH / 2 - 0.2
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(x, y)
                elif id == 5:
                    # どちらかの待機ロボットにパス（ここではid=3にパス）
                    target_x = params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 0.2
                    target_y = -params.GOAL_AREA_WIDTH / 2 - 0.2
                    if rc.state.photo_front:
                        return rc.pass_ball.pass_ball(target_x, target_y)
                    else:
                        # ボールを受けに行く
                        return rc.basic_move.catch_ball()
        else:
            pass
