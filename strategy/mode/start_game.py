import math
import lib.my_math as mymath
import params
import config
import strategy.algorithm.alignment as alignment
import lib.timer as Timer

DEFENSE_BALL_KICK_TIME = 1


class StartGame:
    def __init__(self, utils):
        self.utils = utils
        self.defense_ball_kick_timer = Timer.Timer()

    def run(self, id, rc):
        if config.NUM_ROBOTS == 2:
            if id == 0:
                in_goal_area = (
                    rc.state.court_ball_pos[0] < -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT and
                    abs(rc.state.court_ball_pos[1]
                        ) < params.GOAL_AREA_WIDTH / 2
                )
                if in_goal_area:
                    if self.defense_ball_kick_timer.read() > DEFENSE_BALL_KICK_TIME:
                        return rc.attack()
                else:
                    self.defense_ball_kick_timer.set()
                x = -params.COURT_WIDTH / 2 + params.ROBOT_D
                y = rc.state.court_ball_pos[1]
                y = max(min(y, params.GOAL_WIDTH / 2), -params.GOAL_WIDTH / 2)
                return rc.basic_move.move_to_pos(x, y, rc.state.ball_angle)
            else:
                return rc.attack()
        elif config.NUM_ROBOTS <= 6:
            avaiable_ids = [0, 1, 2, 3, 4, 5]
            used_ids = []
            used_ids.append(config.GK_ID)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            defense_line_x = -params.COURT_WIDTH * 0.5 + \
                params.GOAL_AREA_HEIGHT + params.LINE_STOP_OFFSET*1.5

            if id == config.GK_ID:
                in_goal_area = (
                    rc.state.court_ball_pos[0] < -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT and
                    abs(rc.state.court_ball_pos[1]
                        ) < params.GOAL_AREA_WIDTH / 2
                )
                if in_goal_area:
                    if self.defense_ball_kick_timer.read() > DEFENSE_BALL_KICK_TIME:
                        return rc.attack()
                else:
                    self.defense_ball_kick_timer.set()
                x = -params.COURT_WIDTH / 2 + params.ROBOT_D
                y = rc.state.court_ball_pos[1]
                y = max(min(y, params.GOAL_WIDTH / 2), -params.GOAL_WIDTH / 2)
                return rc.basic_move.move_to_pos(x, y, rc.state.ball_angle)

            elif rc.state.court_ball_pos[0] < 0:
                # ディフェンス重点配置
                if rc.state.court_ball_pos[0] > -params.COURT_WIDTH / 6:
                    defense_line_x -= -params.COURT_WIDTH / \
                        6 - rc.state.court_ball_pos[0]
                # オフェンシブミドルフィールダー
                omf_pos = [0, 0]
                omf_id = self.utils.get_closest_robot_to_target(
                    omf_pos, remain_ids)
                used_ids.append(omf_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # ディフェンシブミドルフィールダー
                dmf_id = self.utils.get_closest_robot_to_ball(remain_ids)
                used_ids.append(dmf_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # センターバック
                cb_pos = [defense_line_x,
                          mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
                cb_id = self.utils.get_closest_robot_to_target(
                    cb_pos, remain_ids)
                used_ids.append(cb_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # サイドバック
                lsb_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
                           -params.GOAL_WIDTH - params.LINE_STOP_OFFSET*1.5]
                lsb_id = self.utils.get_closest_robot_to_target(
                    lsb_pos, remain_ids)
                used_ids.append(lsb_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rsb_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
                           params.GOAL_WIDTH + params.LINE_STOP_OFFSET*1.5]
                rsb_id = self.utils.get_closest_robot_to_target(
                    rsb_pos, remain_ids)
                used_ids.append(rsb_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == dmf_id:
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > -1:
                            return rc.attack()
                        else:
                            return rc.pass_ball.pass_ball(0, 0)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == omf_id:
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(0, 0)
                elif id == cb_id:
                    return rc.basic_move.move_to_pos(cb_pos[0], cb_pos[1], rc.state.ball_angle)
                elif id == lsb_id:
                    return rc.basic_move.move_to_pos(lsb_pos[0], lsb_pos[1], rc.state.ball_angle)
                elif id == rsb_id:
                    return rc.basic_move.move_to_pos(rsb_pos[0], rsb_pos[1], rc.state.ball_angle)
            else:
                # オフェンス重点配置
                # フォワード
                fw_id = self.utils.get_closest_robot_to_ball(
                    avaiable_ids)
                used_ids.append(fw_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # サイドハーフ
                lsh_pos = [params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT -
                           params.LINE_STOP_OFFSET*1.5, params.GOAL_AREA_WIDTH / 2 + params.LINE_STOP_OFFSET*1.5]
                lsh_id = self.utils.get_closest_robot_to_target(
                    lsh_pos, remain_ids)
                used_ids.append(lsh_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rsh_pos = [params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT -
                           params.LINE_STOP_OFFSET*1.5, -params.GOAL_AREA_WIDTH / 2 - params.LINE_STOP_OFFSET*1.5]
                rsh_id = self.utils.get_closest_robot_to_target(
                    rsh_pos, remain_ids)
                used_ids.append(rsh_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == fw_id:
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > params.COURT_WIDTH / 2 - params.GOAL_AREA_HEIGHT - 1:
                            return rc.attack()
                        else:
                            if rc.state.robot_pos[1] > 0:
                                return rc.pass_ball.pass_ball(*lsh_pos)
                            else:
                                return rc.pass_ball.pass_ball(*rsh_pos)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == lsh_id:
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(*lsh_pos)
                elif id == rsh_id:
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(*rsh_pos)
                else:
                    x = defense_line_x
                    y = rc.state.court_ball_pos[1]
                    y = max(min(y, params.GOAL_WIDTH), -params.GOAL_WIDTH)
                    return alignment.liner_alignment(id, rc, remain_ids, [x, y - 0.1], [x, y + 0.1])

        else:
            pass
