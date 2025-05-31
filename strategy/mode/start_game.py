import math
import lib.my_math as mymath
import params
import config
import strategy.algorithm.alignment as alignment
import lib.timer as Timer

DEFENSE_BALL_KICK_TIME = 1


class RollState:
    def __init__(self):
        self.id = None
        self.pos = [0, 0]
        self.photo_front = False


class StartGame:
    def __init__(self, utils):
        self.utils = utils
        self.defense_ball_kick_timer = Timer.Timer()

        if config.NUM_ROBOTS == 2:  # RCJ仕様
            self.df = RollState()
            self.of = RollState()
            self.mf = RollState()
        elif config.NUM_ROBOTS <= 6:  # DivB仕様
            self.fw = RollState()
            self.lsh = RollState()
            self.rsh = RollState()
            self.omf = RollState()
            self.dmf = RollState()
            self.lsb = RollState()
            self.rsb = RollState()
            self.cb = RollState()
        elif config.NUM_ROBOTS <= 11:  # DivA仕様
            self.fw = RollState()
            self.lsh = RollState()
            self.rsh = RollState()
            self.omf = RollState()
            self.ldmf = RollState()
            self.rdmf = RollState()
            self.lsb = RollState()
            self.rsb = RollState()
            self.lcb = RollState()
            self.rcb = RollState()

    def run(self, id, rc):
        if config.NUM_ROBOTS == 2:
            avaiable_ids = [0, 1]
            used_ids = []

            if rc.state.court_ball_pos[0] < 0:
                # ディフェンス重点配置
                self.of.id = self.utils.get_closest_robot_to_ball(avaiable_ids)
                used_ids.append(self.of.id)

                self.df.id = [i for i in avaiable_ids if i not in used_ids]

                if id == self.df.id:
                    self.df.pos = rc.state.robot_pos
                    x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
                    y = mymath.clip(
                        rc.state.court_ball_pos[1], -params.GOAL_WIDTH * 0.5, params.GOAL_WIDTH * 0.5)
                    return rc.basic_move.move_to_pos(x, y)
                elif id == self.of.id:
                    self.of.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > -1:
                            return rc.attack()
                        else:
                            return rc.pass_ball.pass_ball(self.df.pos)
                    else:
                        return rc.basic_move.catch_ball()
            else:
                self.of.id = self.utils.get_frontmost_robot(avaiable_ids)
                used_ids.append(self.of.id)

                self.mf.id = [i for i in avaiable_ids if i not in used_ids]
                if id == self.of.id:
                    self.of.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - 1:
                            return rc.attack()
                        else:
                            return rc.pass_ball.pass_ball(self.mf.pos)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == self.mf.id:

        elif config.NUM_ROBOTS <= 6:
            avaiable_ids = [0, 1, 2, 3, 4, 5]
            used_ids = []
            used_ids.append(config.GK_ID)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            defense_line_x = -params.COURT_WIDTH * 0.5 + \
                params.GOAL_AREA_HEIGHT + params.LINE_STOP_OFFSET*1.5

            if id == config.GK_ID:
                in_goal_area = (
                    rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
                    abs(rc.state.court_ball_pos[1]
                        ) < params.GOAL_AREA_WIDTH * 0.5
                )
                if in_goal_area:
                    if self.defense_ball_kick_timer.read() > DEFENSE_BALL_KICK_TIME:
                        return rc.attack()
                else:
                    self.defense_ball_kick_timer.set()
                x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
                y = mymath.clip(
                    rc.state.court_ball_pos[1], -params.GOAL_WIDTH * 0.5, params.GOAL_WIDTH * 0.5)
                return rc.basic_move.move_to_pos(x, y)

            elif rc.state.court_ball_pos[0] < 0:
                # ディフェンス重点配置
                # センターバック
                cb_target_pos = [defense_line_x,
                                 mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
                self.cb.id = self.utils.get_closest_robot_to_target(
                    cb_target_pos, remain_ids)
                used_ids.append(self.cb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # オフェンシブミドルフィールダー
                omf_pos = [0, 0]
                self.omf.id = self.utils.get_closest_robot_to_target(
                    omf_pos, remain_ids)
                used_ids.append(self.omf.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # ディフェンシブミドルフィールダー
                self.dmf.id = self.utils.get_closest_robot_to_ball(remain_ids)
                used_ids.append(self.dmf.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # サイドバック
                if rc.state.court_ball_pos[0] > -params.COURT_WIDTH / 6:
                    defense_line_x -= -params.COURT_WIDTH / \
                        6 - rc.state.court_ball_pos[0]
                lsb_target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
                                  -params.GOAL_WIDTH - params.LINE_STOP_OFFSET*1.5]
                self.lsb.id = self.utils.get_closest_robot_to_target(
                    lsb_target_pos, remain_ids)
                used_ids.append(self.lsb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rsb_target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
                                  params.GOAL_WIDTH + params.LINE_STOP_OFFSET*1.5]
                self.rsb.id = self.utils.get_closest_robot_to_target(
                    rsb_target_pos, remain_ids)
                used_ids.append(self.rsb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == self.dmf.id:
                    self.dmf.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > -1:
                            return rc.attack()
                        else:
                            return rc.pass_ball.pass_ball(self.omf.pos)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == self.omf.id:
                    self.omf.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(self.dmf.pos, [0, 0])
                elif id == self.cb.id:
                    return rc.basic_move.move_to_pos(cb_target_pos[0], cb_target_pos[1], rc.state.ball_angle)
                elif id == self.lsb.id:
                    return rc.basic_move.move_to_pos(lsb_target_pos[0], lsb_target_pos[1], rc.state.ball_angle)
                elif id == self.rsb.id:
                    return rc.basic_move.move_to_pos(rsb_target_pos[0], rsb_target_pos[1], rc.state.ball_angle)
            else:
                # オフェンス重点配置
                # フォワード
                fw_id = self.utils.get_closest_robot_to_ball(
                    avaiable_ids)
                used_ids.append(fw_id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # サイドハーフ
                lsh_target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
                                  params.LINE_STOP_OFFSET*1.5, params.GOAL_AREA_WIDTH * 0.5 + params.LINE_STOP_OFFSET*1.5]
                self.lsh.id = self.utils.get_closest_robot_to_target(
                    lsh_target_pos, remain_ids)
                used_ids.append(self.lsh.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rsh_target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
                                  params.LINE_STOP_OFFSET*1.5, -params.GOAL_AREA_WIDTH * 0.5 - params.LINE_STOP_OFFSET*1.5]
                self.rsh.id = self.utils.get_closest_robot_to_target(
                    rsh_target_pos, remain_ids)
                used_ids.append(self.rsh.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # センターバック
                cb_target_pos = [defense_line_x,
                                 mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
                self.cb.id = self.utils.get_closest_robot_to_target(
                    cb_target_pos, remain_ids)
                used_ids.append(self.cb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # ディフェンスミドルフィールダー
                dmf_target_pos = [rc.state.court_ball_pos[0] - params.COURT_WIDTH / 4,
                                  rc.state.court_ball_pos[1] * 0.5]
                self.dmf.id = self.utils.get_closest_robot_to_target(
                    dmf_target_pos, remain_ids)
                used_ids.append(self.dmf.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == fw_id:
                    self.fw.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        if rc.state.robot_pos[0] > params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - 1:
                            return rc.attack()
                        else:
                            if rc.state.robot_pos[1] > 0:
                                return rc.pass_ball.pass_ball(self.lsh.pos)
                            else:
                                return rc.pass_ball.pass_ball(self.rsh.pos)
                    else:
                        return rc.basic_move.catch_ball()
                elif id == self.lsh.id:
                    self.lsh.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(self.fw.pos, lsh_target_pos)
                elif id == self.rsh.id:
                    self.rsh.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        return rc.attack()
                    else:
                        return rc.pass_ball.receive_ball(self.fw.pos, rsh_target_pos)
                elif id == self.cb.id:
                    return rc.basic_move.move_to_pos(cb_target_pos[0], cb_target_pos[1], rc.state.ball_angle)
                elif id == self.dmf.id:
                    return rc.basic_move.move_to_pos(dmf_target_pos[0], dmf_target_pos[1], rc.state.ball_angle)

        elif config.NUM_ROBOTS <= 11:
            avaiable_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            used_ids = []
            used_ids.append(config.GK_ID)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            defense_line_x = -params.COURT_WIDTH * 0.5 + \
                params.GOAL_AREA_HEIGHT + params.LINE_STOP_OFFSET*1.5

            if id == config.GK_ID:
                in_goal_area = (
                    rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
                    abs(rc.state.court_ball_pos[1]
                        ) < params.GOAL_AREA_WIDTH * 0.5
                )
                if in_goal_area:
                    if self.defense_ball_kick_timer.read() > DEFENSE_BALL_KICK_TIME:
                        return rc.attack()
                else:
                    self.defense_ball_kick_timer.set()
                x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
                y = rc.state.court_ball_pos[1]
                y = max(min(y, params.GOAL_WIDTH * 0.5), -
                        params.GOAL_WIDTH * 0.5)
                return rc.basic_move.move_to_pos(x, y)

            elif rc.state.court_ball_pos[0] < 0:
                # ディフェンス重点配置
                # センターバック
                lcb_target_pos = [defense_line_x,
                                  mymath.clip(rc.state.court_ball_pos[1] - params.ROBOT_R, -params.GOAL_WIDTH - params.ROBOT_R, params.GOAL_WIDTH - params.ROBOT_R)]
                self.lcb.id = self.utils.get_closest_robot_to_target(
                    lcb_target_pos, remain_ids)
                used_ids.append(self.lcb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rcb_target_pos = [defense_line_x,
                                  mymath.clip(rc.state.court_ball_pos[1] + params.ROBOT_R, -params.GOAL_WIDTH + params.ROBOT_R, params.GOAL_WIDTH + params.ROBOT_R)]
                self.rcb.id = self.utils.get_closest_robot_to_target(
                    rcb_target_pos, remain_ids)
                used_ids.append(self.rcb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # サイドバック
                if rc.state.court_ball_pos[0] > -params.COURT_WIDTH / 6:
                    defense_line_x -= -params.COURT_WIDTH / \
                        6 - rc.state.court_ball_pos[0]
                lsb_target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
                                  -params.GOAL_WIDTH - params.LINE_STOP_OFFSET*1.5]
                self.lsb.id = self.utils.get_closest_robot_to_target(
                    lsb_target_pos, remain_ids)
                used_ids.append(self.lsb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rsb_target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
                                  params.GOAL_WIDTH + params.LINE_STOP_OFFSET*1.5]
                self.rsb.id = self.utils.get_closest_robot_to_target(
                    rsb_target_pos, remain_ids)
                used_ids.append(self.rsb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
            else:
                # オフェンス重点配置
                # センターバック
                lcb_target_pos = [defense_line_x,
                                  mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
                self.lcb.id = self.utils.get_closest_robot_to_target(
                    lcb_target_pos, remain_ids)
                used_ids.append(self.lcb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
