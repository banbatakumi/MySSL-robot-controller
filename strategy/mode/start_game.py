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
        self.target_pos = [0, 0]
        self.photo_front = False


class StartGame:
    def __init__(self, utils):
        self.utils = utils
        self.defense_ball_kick_timer = Timer.Timer()

        if config.NUM_ROBOTS == 2:  # RCJ仕様
            self.df = RollState()
            self.of = RollState()
        elif config.NUM_ROBOTS <= 6:  # DivB仕様
            self.fw = RollState()
            self.sh = RollState()
            self.omf = RollState()
            self.dmf = RollState()
            self.cb = RollState()

            self.lsb = RollState()
            self.rsb = RollState()
            self.lsh = RollState()
            self.rsh = RollState()
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

    def update_roll(self, court_ball_pos):
        if config.NUM_ROBOTS == 2:
            pass

        elif config.NUM_ROBOTS <= 6:
            avaiable_ids = [0, 1, 2, 3, 4, 5]
            used_ids = []
            used_ids.append(config.GK_ID)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            defense_line_x = -params.COURT_WIDTH * 0.5 + \
                params.GOAL_AREA_HEIGHT + params.LINE_STOP_OFFSET*1.5

            # センターバック
            self.cb.target_pos = [defense_line_x,
                                  mymath.clip(court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
            self.cb.id = self.utils.get_closest_robot_to_target(
                self.cb.target_pos, remain_ids)
            used_ids.append(self.cb.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # サイドハーフ
            x = params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - \
                params.LINE_STOP_OFFSET * 1.5
            y = params.GOAL_AREA_WIDTH * 0.5 + params.LINE_STOP_OFFSET*1.5
            if court_ball_pos[1] < 0:
                y *= -1
            self.sh.target_pos = [x, y]
            self.sh.id = self.utils.get_closest_robot_to_target(
                self.sh.target_pos, remain_ids)
            used_ids.append(self.sh.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # フォワード
            self.fw.target_pos = [mymath.clip(court_ball_pos[0], 0, params.COURT_WIDTH * 0.5),
                                  court_ball_pos[1]]
            self.fw.id = self.utils.get_closest_robot_to_target(
                self.fw.target_pos, remain_ids)
            used_ids.append(self.fw.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # オフェンシブミッドフィールダー
            self.omf.target_pos = [mymath.clip(court_ball_pos[0], -params.COURT_WIDTH * 0.5, court_ball_pos[0] * 0.5),
                                   court_ball_pos[1]]
            self.omf.id = self.utils.get_closest_robot_to_target(
                self.omf.target_pos, remain_ids)
            used_ids.append(self.omf.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # ディフェンシブミッドフィールダー
            own_goal_x = -params.COURT_WIDTH * 0.5
            own_goal_y = 0
            # ゴールからボールへのベクトル
            dx = court_ball_pos[0] - own_goal_x
            dy = court_ball_pos[1] - own_goal_y
            angle_rad = math.atan2(dy, dx)
            dis = math.hypot(dx, dy)
            dmf_radius = mymath.clip(dis * 0.75, 2, params.COURT_WIDTH)
            self.dmf.target_pos = [
                own_goal_x + dmf_radius * math.cos(angle_rad),
                own_goal_y + dmf_radius * math.sin(angle_rad)
            ]
            self.dmf.id = self.utils.get_closest_robot_to_target(
                self.dmf.target_pos, remain_ids)
            used_ids.append(self.dmf.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]
        elif config.NUM_ROBOTS <= 11:
            self.fw.pos = court_ball_pos
            self.lsh.pos = court_ball_pos
            self.rsh.pos = court_ball_pos
            self.omf.pos = court_ball_pos
            self.ldmf.pos = court_ball_pos
            self.rdmf.pos = court_ball_pos
            self.lsb.pos = court_ball_pos
            self.rsb.pos = court_ball_pos
            self.lcb.pos = court_ball_pos
            self.rcb.pos = court_ball_pos

    def run(self, id, rc):
        if config.NUM_ROBOTS == 2:
            avaiable_ids = [0, 1]
            used_ids = []

            self.of.id = self.utils.get_frontmost_robot(avaiable_ids)
            used_ids.append(self.of.id)

            if id == self.of.id:
                self.of.pos = rc.state.robot_pos
                self.of.photo_front = rc.state.photo_front
                if self.df.photo_front or rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.25:
                    target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
                                  params.LINE_STOP_OFFSET*1.5, params.GOAL_AREA_WIDTH * 0.5 + params.LINE_STOP_OFFSET*1.5]
                    return rc.pass_ball.receive_ball(self.df.pos, [0.2, 0])
                else:
                    return rc.attack()

            else:
                self.df.pos = rc.state.robot_pos
                self.df.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    return rc.pass_ball.pass_ball(self.of.pos)
                else:
                    if rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.25:
                        if self.defense_ball_kick_timer.read() > 0.5:
                            return rc.basic_move.catch_ball()
                    else:
                        self.defense_ball_kick_timer.set()
                    x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
                    y = mymath.clip(
                        rc.state.court_ball_pos[1], -params.GOAL_WIDTH * 0.5, params.GOAL_WIDTH * 0.5)
                    return rc.basic_move.move_to_pos(x, y)

        elif config.NUM_ROBOTS <= 6:
            if id == self.cb.id:
                return rc.basic_move.move_to_pos(self.cb.target_pos[0], self.cb.target_pos[1], rc.state.ball_angle)
            elif id == self.dmf.id:
                self.dmf.pos = rc.state.robot_pos
                return rc.basic_move.move_to_pos(self.dmf.target_pos[0], self.dmf.target_pos[1], rc.state.ball_angle)
            elif id == self.omf.id:
                self.omf.pos = rc.state.robot_pos
                self.omf.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    return rc.pass_ball.pass_ball(self.fw.pos)
                elif self.fw.photo_front:
                    return rc.basic_move.move_to_pos(0, 0)
                elif self.omf.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.basic_move.move_to_pos(self.omf.target_pos[0], self.omf.target_pos[1], rc.state.ball_angle)
            elif id == self.sh.id:
                self.sh.pos = rc.state.robot_pos
                self.sh.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    return rc.attack()
                else:
                    # self.sh.target_pos = self.utils.find_safe_pass_position(
                    #     self.fw.pos, self.sh.target_pos)
                    return rc.pass_ball.receive_ball(self.fw.pos, self.sh.target_pos)
            elif id == self.fw.id:
                self.fw.pos = rc.state.robot_pos
                self.fw.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if abs(rc.state.robot_pos[1]) < params.GOAL_AREA_WIDTH * 0.5 and rc.state.opp_goal_dis < params.MAX_SHOOT_DIS:
                        return rc.attack()
                    else:
                        return rc.pass_ball.pass_ball(self.sh.pos)
                elif self.sh.photo_front:
                    return rc.basic_move.move_to_pos(params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - params.LINE_STOP_OFFSET*1.5, 0, rc.state.ball_angle)
                elif self.fw.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    # self.fw.target_pos = self.utils.find_safe_pass_position(
                    #     self.omf.pos, self.fw.target_pos)
                    return rc.pass_ball.receive_ball(self.omf.pos, self.fw.target_pos)
            elif id == config.GK_ID:
                # in_goal_area = (
                #     rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
                #     abs(rc.state.court_ball_pos[1]
                #         ) < params.GOAL_AREA_WIDTH * 0.5
                # )
                # if in_goal_area:
                #     if self.defense_ball_kick_timer.read() > DEFENSE_BALL_KICK_TIME:
                #         return rc.attack()
                # else:
                #     self.defense_ball_kick_timer.set()
                # x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
                # y = mymath.clip(
                #     rc.state.court_ball_pos[1], -params.GOAL_WIDTH * 0.5, params.GOAL_WIDTH * 0.5)
                # return rc.basic_move.move_to_pos(x, y)
                return rc.goal_keeper.run()

            # if id == config.GK_ID:
            #     in_goal_area = (
            #         rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
            #         abs(rc.state.court_ball_pos[1]
            #             ) < params.GOAL_WIDTH * 0.5
            #     )
            #     if in_goal_area:
            #         if self.defense_ball_kick_timer.read() > DEFENSE_BALL_KICK_TIME:
            #             return rc.attack()
            #     else:
            #         self.defense_ball_kick_timer.set()
            #     x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
            #     y = mymath.clip(
            #         rc.state.court_ball_pos[1], -params.GOAL_WIDTH * 0.5, params.GOAL_WIDTH * 0.5)
            #     return rc.basic_move.move_to_pos(x, y)
            # elif rc.state.court_ball_pos[0] < 0:
            #     # ディフェンス重点配置
            #     # センターバック
            #     self.cb.target_pos = [defense_line_x,
            #                      mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
            #     self.cb.id = self.utils.get_closest_robot_to_target(
            #         self.cb.target_pos, remain_ids)
            #     used_ids.append(self.cb.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     # オフェンシブミッドフィールダー
            #     omf_pos = [0, 0]
            #     self.omf.id = self.utils.get_closest_robot_to_target(
            #         omf_pos, remain_ids)
            #     used_ids.append(self.omf.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     # ディフェンシブミッドフィールダー
            #     self.dmf.id = self.utils.get_closest_robot_to_ball(remain_ids)
            #     used_ids.append(self.dmf.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     # サイドバック
            #     if rc.state.court_ball_pos[0] > -params.COURT_WIDTH / 6:
            #         defense_line_x -= -params.COURT_WIDTH / \
            #             6 - rc.state.court_ball_pos[0]
            #     lsb_target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
            #                       -params.GOAL_WIDTH - params.LINE_STOP_OFFSET*1.5]
            #     self.lsb.id = self.utils.get_closest_robot_to_target(
            #         lsb_target_pos, remain_ids)
            #     used_ids.append(self.lsb.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     rsb_target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, defense_line_x),
            #                       params.GOAL_WIDTH + params.LINE_STOP_OFFSET*1.5]
            #     self.rsb.id = self.utils.get_closest_robot_to_target(
            #         rsb_target_pos, remain_ids)
            #     used_ids.append(self.rsb.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     if id == self.dmf.id:
            #         self.dmf.pos = rc.state.robot_pos
            #         if rc.state.photo_front:
            #             if rc.state.robot_pos[0] > -1:
            #                 return rc.attack()
            #             else:
            #                 return rc.pass_ball.pass_ball(self.omf.pos)
            #         else:
            #             return rc.basic_move.catch_ball()
            #     elif id == self.omf.id:
            #         self.omf.pos = rc.state.robot_pos
            #         if rc.state.photo_front:
            #             return rc.attack()
            #         else:
            #             return rc.pass_ball.receive_ball(self.dmf.pos, [0, 0])
            #     elif id == self.cb.id:
            #         return rc.basic_move.move_to_pos(self.cb.target_pos[0], self.cb.target_pos[1], rc.state.ball_angle)
            #     elif id == self.lsb.id:
            #         return rc.basic_move.move_to_pos(lsb_target_pos[0], lsb_target_pos[1], rc.state.ball_angle)
            #     elif id == self.rsb.id:
            #         return rc.basic_move.move_to_pos(rsb_target_pos[0], rsb_target_pos[1], rc.state.ball_angle)
            # else:
            #     # オフェンス重点配置
            #     # フォワード
            #     fw_id = self.utils.get_closest_robot_to_ball(
            #         avaiable_ids)
            #     used_ids.append(fw_id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     # サイドハーフ
            #     lself.sh.target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
            #                       params.LINE_STOP_OFFSET*1.5, params.GOAL_AREA_WIDTH * 0.5 + params.LINE_STOP_OFFSET*1.5]
            #     self.lsh.id = self.utils.get_closest_robot_to_target(
            #         lself.sh.target_pos, remain_ids)
            #     used_ids.append(self.lsh.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     rself.sh.target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
            #                       params.LINE_STOP_OFFSET*1.5, -params.GOAL_AREA_WIDTH * 0.5 - params.LINE_STOP_OFFSET*1.5]
            #     self.rsh.id = self.utils.get_closest_robot_to_target(
            #         rself.sh.target_pos, remain_ids)
            #     used_ids.append(self.rsh.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     # センターバック
            #     self.cb.target_pos = [defense_line_x,
            #                      mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
            #     self.cb.id = self.utils.get_closest_robot_to_target(
            #         self.cb.target_pos, remain_ids)
            #     used_ids.append(self.cb.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     # ディフェンスミッドフィールダー
            #     self.dmf.target_pos = [rc.state.court_ball_pos[0] - params.COURT_WIDTH / 4,
            #                       rc.state.court_ball_pos[1] * 0.5]
            #     self.dmf.id = self.utils.get_closest_robot_to_target(
            #         self.dmf.target_pos, remain_ids)
            #     used_ids.append(self.dmf.id)
            #     remain_ids = [i for i in avaiable_ids if i not in used_ids]

            #     if id == fw_id:
            #         self.fw.pos = rc.state.robot_pos
            #         if rc.state.photo_front:
            #             if rc.state.robot_pos[0] > params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - 1:
            #                 return rc.attack()
            #             else:
            #                 if rc.state.robot_pos[1] > 0:
            #                     return rc.pass_ball.pass_ball(self.lsh.pos)
            #                 else:
            #                     return rc.pass_ball.pass_ball(self.rsh.pos)
            #         else:
            #             return rc.basic_move.catch_ball()
            #     elif id == self.lsh.id:
            #         self.lsh.pos = rc.state.robot_pos
            #         if rc.state.photo_front:
            #             return rc.attack()
            #         else:
            #             return rc.pass_ball.receive_ball(self.fw.pos, lself.sh.target_pos)
            #     elif id == self.rsh.id:
            #         self.rsh.pos = rc.state.robot_pos
            #         if rc.state.photo_front:
            #             return rc.attack()
            #         else:
            #             return rc.pass_ball.receive_ball(self.fw.pos, rself.sh.target_pos)
            #     elif id == self.cb.id:
            #         return rc.basic_move.move_to_pos(self.cb.target_pos[0], self.cb.target_pos[1], rc.state.ball_angle)
            #     elif id == self.dmf.id:
            #         return rc.basic_move.move_to_pos(self.dmf.target_pos[0], self.dmf.target_pos[1], rc.state.ball_angle)

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
                lself.cb.target_pos = [defense_line_x,
                                       mymath.clip(rc.state.court_ball_pos[1] - params.ROBOT_R, -params.GOAL_WIDTH - params.ROBOT_R, params.GOAL_WIDTH - params.ROBOT_R)]
                self.lcb.id = self.utils.get_closest_robot_to_target(
                    lself.cb.target_pos, remain_ids)
                used_ids.append(self.lcb.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                rself.cb.target_pos = [defense_line_x,
                                       mymath.clip(rc.state.court_ball_pos[1] + params.ROBOT_R, -params.GOAL_WIDTH + params.ROBOT_R, params.GOAL_WIDTH + params.ROBOT_R)]
                self.rcb.id = self.utils.get_closest_robot_to_target(
                    rself.cb.target_pos, remain_ids)
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

                # ディフェンシブミッドフィールダー
                lself.dmf.target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, 0),
                                        mymath.clip(rc.state.court_ball_pos[1], params.GOAL_AREA_WIDTH * 0.5, params.COURT_HEIGHT * 0.5)]
                self.ldmf.id = self.utils.get_closest_robot_to_target(
                    lself.dmf.target_pos, remain_ids)
                used_ids.append(self.ldmf.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
                rself.dmf.target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, 0),
                                        mymath.clip(rc.state.court_ball_pos[1], -params.COURT_HEIGHT * 0.5, -params.GOAL_AREA_WIDTH * 0.5)]
                self.rdmf.id = self.utils.get_closest_robot_to_target(
                    rself.dmf.target_pos, remain_ids)
                used_ids.append(self.rdmf.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # オフェンシブミッドフィールダー
                self.omf.target_pos = [mymath.clip(rc.state.court_ball_pos[0], -params.COURT_WIDTH * 0.5, 0),
                                       mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_AREA_HEIGHT * 0.5, params.GOAL_AREA_HEIGHT * 0.5)]
                self.omf.id = self.utils.get_closest_robot_to_target(
                    self.omf.target_pos, remain_ids)
                used_ids.append(self.omf.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # サイドハーフ
                lself.sh.target_pos = [0, params.GOAL_AREA_WIDTH *
                                       0.5 + params.LINE_STOP_OFFSET*1.5]
                self.lsh.id = self.utils.get_closest_robot_to_target(
                    lself.sh.target_pos, remain_ids)
                used_ids.append(self.lsh.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]
                rself.sh.target_pos = [0, -params.GOAL_AREA_WIDTH *
                                       0.5 - params.LINE_STOP_OFFSET*1.5]
                self.rsh.id = self.utils.get_closest_robot_to_target(
                    rself.sh.target_pos, remain_ids)
                used_ids.append(self.rsh.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                # フォワード
                self.fw.target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
                                      params.LINE_STOP_OFFSET*1.5, 0]
                self.fw.id = self.utils.get_closest_robot_to_target(
                    self.fw.target_pos, remain_ids)
                used_ids.append(self.fw.id)
                remain_ids = [i for i in avaiable_ids if i not in used_ids]

                if id == self.lcb.id:
                    self.lcb.pos = rc.state.robot_pos
                    return rc.basic_move.move_to_pos(lself.cb.target_pos[0], lself.cb.target_pos[1], rc.state.ball_angle)
                elif id == self.rcb.id:
                    self.rcb.pos = rc.state.robot_pos
                    return rc.basic_move.move_to_pos(rself.cb.target_pos[0], rself.cb.target_pos[1], rc.state.ball_angle)
                elif id == self.lsb.id:
                    self.lsb.pos = rc.state.robot_pos
                    return rc.basic_move.move_to_pos(lsb_target_pos[0], lsb_target_pos[1], rc.state.ball_angle)
                elif id == self.rsb.id:
                    self.rsb.pos = rc.state.robot_pos
                    return rc.basic_move.move_to_pos(rsb_target_pos[0], rsb_target_pos[1], rc.state.ball_angle)
                elif id == self.ldmf.id:
                    self.ldmf.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        return rc.pass_ball.pass_ball(self.lsh.pos)
                    elif lself.dmf.target_pos == rc.state.court_ball_pos:
                        return rc.basic_move.catch_ball()
                    else:
                        return rc.basic_move.move_to_pos(lself.dmf.target_pos[0], lself.dmf.target_pos[1], rc.state.ball_angle)
                elif id == self.rdmf.id:
                    self.rdmf.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        return rc.pass_ball.pass_ball(self.rsh.pos)
                    elif rself.dmf.target_pos == rc.state.court_ball_pos:
                        return rc.basic_move.catch_ball()
                    else:
                        return rc.basic_move.move_to_pos(rself.dmf.target_pos[0], rself.dmf.target_pos[1], rc.state.ball_angle)
                elif id == self.omf.id:
                    self.omf.pos = rc.state.robot_pos
                    if rc.state.photo_front:
                        return rc.pass_ball.pass_ball(self.fw.pos)
                    elif self.omf.target_pos == rc.state.court_ball_pos:
                        return rc.basic_move.catch_ball()
                    else:
                        return rc.basic_move.move_to_pos(self.omf.target_pos[0], self.omf.target_pos[1], rc.state.ball_angle)
                elif id == self.lsh.id:
                    self.lsh.pos = rc.state.robot_pos
                    return rc.pass_ball.receive_ball(self.utils.get_closest_robot_pos_to_ball(), lself.sh.target_pos)
                elif id == self.rsh.id:
                    self.rsh.pos = rc.state.robot_pos
                    return rc.pass_ball.receive_ball(self.utils.get_closest_robot_pos_to_ball(), rself.sh.target_pos)
                # elif id == self.fw.id:
                    # self.fw.pos = rc.state.robot_pos
                    # if rc.state.photo_front:
                    #     if rc.state.robot_pos[0] > params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - 1:
                    #         return rc.attack()
                    #     else:
                    #         if rc.state.robot_pos[1] > 0:
                    #             return rc.pass_ball.pass_ball(self.lsh.pos)
                    #         else:
                    #             return rc.pass_ball.pass_ball(self.rsh.pos)
                    # else:
                    #     return rc.basic_move.catch_ball()
            else:
                # オフェンス重点配置
                # センターバック
                lself.cb.target_pos = [defense_line_x,
                                       mymath.clip(rc.state.court_ball_pos[1], -params.GOAL_WIDTH, params.GOAL_WIDTH)]
                self.lcb.id = self.utils.get_closest_robot_to_target(
                    lself.cb.target_pos, remain_ids)
                used_ids.append(self.lcb.id)
                remain_ids = [
                    i for i in avaiable_ids if i not in used_ids]
