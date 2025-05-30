import math
import params
import config
import strategy.algorithm.alignment as alignment


class StartGame:
    def __init__(self, utils):
        self.utils = utils

    def run(self, id, rc):
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
                avaiable_ids = [1, 2, 3, 4, 5]
                used_ids = []

                # 1. ボールに最も近いロボット
                ball_pickup_id = self.utils.get_closest_robot_to_ball_from_list(
                    avaiable_ids)
                used_ids.append(ball_pickup_id)

                # 2. センターに一番近いロボット
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
                receive_pass_id = self.utils.get_closest_robot_to_target_from_list(
                    remain_ids, [0, 0])
                used_ids.append(receive_pass_id)

                # 3. その他のロボット
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == ball_pickup_id:
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > -1:
                            return rc.attack()
                        else:
                            return rc.pass_ball.pass_ball(0, 0)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == receive_pass_id:
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(0, 0)
                else:
                    x = -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT + 0.2
                    y = rc.state.court_ball_pos[1]
                    y = max(min(y, params.GOAL_WIDTH), -params.GOAL_WIDTH)
                    return alignment.liner_alignment(id, rc, remain_ids, [x, y - 0.2], [x, y + 0.2])
            else:
                avaiable_ids = [1, 2, 3, 4, 5]
                used_ids = []

                # 1. ボールに最も近いロボット
                ball_pickup_id = self.utils.get_closest_robot_to_ball_from_list(
                    avaiable_ids)
                used_ids.append(ball_pickup_id)

                # 2. ゴール上側に最も近いロボット
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
                top_target = [params.COURT_WIDTH / 2 -
                              params.GOAL_AREA_HEIGHT - 0.2, params.GOAL_AREA_WIDTH / 2 + 0.2]
                top_id = self.utils.get_closest_robot_to_target_from_list(
                    remain_ids, top_target)
                used_ids.append(top_id)

                # 3. ゴール下側に最も近いロボット
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
                bottom_target = [params.COURT_WIDTH / 2 -
                                 params.GOAL_AREA_HEIGHT - 0.2, -params.GOAL_AREA_WIDTH / 2 - 0.2]
                bottom_id = self.utils.get_closest_robot_to_target_from_list(
                    remain_ids, bottom_target)
                used_ids.append(bottom_id)

                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == ball_pickup_id:
                    target_x = params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 0.2
                    target_y = -params.GOAL_AREA_WIDTH / 2 - 0.2
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 1:
                            return rc.attack()
                        else:
                            return rc.pass_ball.pass_ball(target_x, target_y)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == top_id:
                    x = params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 0.2
                    y = params.GOAL_AREA_WIDTH / 2 + 0.2
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(x, y)
                elif id == bottom_id:
                    x = params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 0.2
                    y = -params.GOAL_AREA_WIDTH / 2 - 0.2
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(x, y)
                else:
                    x = -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT + 0.2
                    y = rc.state.court_ball_pos[1]
                    y = max(min(y, params.GOAL_WIDTH), -params.GOAL_WIDTH)
                    return alignment.liner_alignment(id, rc, remain_ids, [x, y - 0.1], [x, y + 0.1])

        else:
            pass
