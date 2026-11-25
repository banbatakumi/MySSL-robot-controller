import math
import lib.my_math as mymath
import params
import config
import strategy.algorithm.alignment as alignment
import lib.timer as timer

GK_BALL_KICK_TIME = 1


class RollState:
    def __init__(self):
        self.id = None
        self.pos = [0, 0]
        self.target_pos = [0, 0]
        self.photo_front = False


class StartGame:
    def __init__(self, utils):
        self.utils = utils
        self.gk_ball_kick_timer = timer.Timer()

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
            self.lfw = RollState()
            self.rfw = RollState()
            self.lsh = RollState()
            self.rsh = RollState()
            self.lch = RollState()
            self.rch = RollState()
            self.lsb = RollState()
            self.rsb = RollState()
            self.lcb = RollState()
            self.rcb = RollState()
            self.gk = RollState()

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
                params.LINE_STOP_OFFSET * 2.5
            y = params.GOAL_AREA_WIDTH * 0.5 + params.LINE_STOP_OFFSET*2.5
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
            avaiable_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            used_ids = []
            used_ids.append(config.GK_ID)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            defense_line_x = -params.COURT_WIDTH * 0.5 + \
                params.GOAL_AREA_HEIGHT + params.LINE_STOP_OFFSET*1.5

            # センターバック
            own_goal_x = -params.COURT_WIDTH * 0.5
            own_goal_y = 0
            # ゴールからボールへのベクトル
            dx = court_ball_pos[0] - own_goal_x
            dy = court_ball_pos[1] - own_goal_y
            angle_rad = math.atan2(dy, dx)
            dis = math.hypot(dx, dy)
            lcb_radius = mymath.clip(dis * 0.5, 1.6, params.COURT_WIDTH)
            x = own_goal_x + lcb_radius * math.cos(angle_rad - math.pi / 50)
            y = own_goal_y + lcb_radius * math.sin(angle_rad - math.pi / 50)

            self.lcb.target_pos = [x, y]
            self.lcb.id = self.utils.get_closest_robot_to_target(
                self.lcb.target_pos, remain_ids)
            used_ids.append(self.lcb.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            x = own_goal_x + lcb_radius * math.cos(angle_rad + math.pi / 50)
            y = own_goal_y + lcb_radius * math.sin(angle_rad + math.pi / 50)
            self.rcb.target_pos = [x, y]
            self.rcb.id = self.utils.get_closest_robot_to_target(
                self.rcb.target_pos, remain_ids)
            used_ids.append(self.rcb.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # レフトサイドバック
            if self.utils.has_possession():
                x = mymath.clip(
                    court_ball_pos[0], params.COURT_WIDTH * -0.5, 0)
                y = mymath.clip(
                    court_ball_pos[1], 0, params.COURT_HEIGHT * 0.5)
            else:
                x = own_goal_x + lcb_radius * \
                    math.cos(angle_rad + math.pi / 25)
                y = own_goal_y + lcb_radius * \
                    math.sin(angle_rad + math.pi / 25)

            if self.lsh.photo_front:
                x -= params.COURT_WIDTH * 0.1
            self.lsb.target_pos = [x, y]
            self.lsb.id = self.utils.get_closest_robot_to_target(
                self.lsb.target_pos, remain_ids)
            used_ids.append(self.lsb.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # ライトサイドバック
            if self.utils.has_possession():
                x = mymath.clip(
                    court_ball_pos[0], params.COURT_WIDTH * -0.5, 0)
                y = mymath.clip(
                    court_ball_pos[1], params.COURT_HEIGHT * -0.5, 0)
            else:
                x = own_goal_x + lcb_radius * \
                    math.cos(angle_rad - math.pi / 25)
                y = own_goal_y + lcb_radius * \
                    math.sin(angle_rad - math.pi / 25)
            if self.rch.photo_front:
                x -= params.COURT_WIDTH * 0.1
            self.rsb.target_pos = [x, y]
            self.rsb.id = self.utils.get_closest_robot_to_target(
                self.rsb.target_pos, remain_ids)
            used_ids.append(self.rsb.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # レフトフォワード
            if court_ball_pos[1] > params.COURT_HEIGHT * 0.25 or court_ball_pos[1] < 0:
                x = params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - params.LINE_STOP_OFFSET*1.5
                y = params.COURT_HEIGHT * 0.1
            else:
                x = mymath.clip(
                    court_ball_pos[0], params.COURT_WIDTH * 0.2, params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT)
                y = mymath.clip(
                    court_ball_pos[1], 0, params.COURT_HEIGHT * 0.25)
            self.lfw.target_pos = [x, y]
            self.lfw.id = self.utils.get_closest_robot_to_target(
                self.lfw.target_pos, remain_ids)
            used_ids.append(self.lfw.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # ライトフォワード
            if court_ball_pos[1] < params.COURT_HEIGHT * -0.25 or court_ball_pos[1] > 0:
                x = params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT - params.LINE_STOP_OFFSET*1.5
                y = params.COURT_HEIGHT * -0.1
            else:
                x = mymath.clip(
                    court_ball_pos[0], params.COURT_WIDTH * 0.2, params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT)
                y = mymath.clip(
                    court_ball_pos[1], -params.COURT_HEIGHT * 0.25, 0)
            self.rfw.target_pos = [x, y]
            self.rfw.id = self.utils.get_closest_robot_to_target(
                self.rfw.target_pos, remain_ids)
            used_ids.append(self.rfw.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # レフトサイドハーフ
            if court_ball_pos[1] < params.COURT_HEIGHT * 0.25:
                x = params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT
                y = params.COURT_HEIGHT * 0.3
            else:
                x = mymath.clip(
                    court_ball_pos[0], 0, params.COURT_WIDTH * 0.5)
                y = mymath.clip(
                    court_ball_pos[1], params.COURT_HEIGHT * 0.25, params.COURT_HEIGHT * 0.5)
            self.lsh.target_pos = [x, y]
            self.lsh.id = self.utils.get_closest_robot_to_target(
                self.lsh.target_pos, remain_ids)
            used_ids.append(self.lsh.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # ライトサイドハーフ
            if court_ball_pos[1] > params.COURT_HEIGHT * -0.25:
                x = params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT
                y = params.COURT_HEIGHT * -0.3
            else:
                x = mymath.clip(
                    court_ball_pos[0], 0, params.COURT_WIDTH * 0.5)
                y = mymath.clip(
                    court_ball_pos[1], params.COURT_HEIGHT * -0.5, params.COURT_HEIGHT * -0.25)
            self.rsh.target_pos = [x, y]
            self.rsh.id = self.utils.get_closest_robot_to_target(
                self.rsh.target_pos, remain_ids)
            used_ids.append(self.rsh.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # レフトセンターハーフ
            x = mymath.clip(
                court_ball_pos[0], params.COURT_WIDTH * -0.25, params.COURT_WIDTH * 0.25)
            y = mymath.clip(
                court_ball_pos[1], 0, params.COURT_HEIGHT * 0.25)
            if self.lch.photo_front:
                x -= params.COURT_WIDTH * 0.1
            self.lch.target_pos = [x, y]
            self.lch.id = self.utils.get_closest_robot_to_target(
                self.lch.target_pos, remain_ids)
            used_ids.append(self.lch.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

            # ライトセンターハーフ
            x = mymath.clip(
                court_ball_pos[0], params.COURT_WIDTH * -0.25, params.COURT_WIDTH * 0.25)
            y = mymath.clip(
                court_ball_pos[1], params.COURT_HEIGHT * -0.25, 0)
            if self.rsh.photo_front:
                x -= params.COURT_WIDTH * 0.1
            self.rch.target_pos = [x, y]
            self.rch.id = self.utils.get_closest_robot_to_target(
                self.rch.target_pos, remain_ids)
            used_ids.append(self.rch.id)
            remain_ids = [i for i in avaiable_ids if i not in used_ids]

    def run(self, id, rc):
        if config.NUM_ROBOTS == 2:
            avaiable_ids = [0, 1]
            used_ids = []

            self.of.id = 1
            used_ids.append(self.of.id)

            if id == self.of.id:
                self.of.pos = rc.state.robot_pos
                self.of.photo_front = rc.state.photo_front
                if self.df.photo_front or rc.state.court_ball_pos[0] < 0:
                    target_pos = [params.COURT_WIDTH * 0.5 - params.GOAL_AREA_HEIGHT -
                                  params.LINE_STOP_OFFSET*1.5, params.GOAL_AREA_WIDTH * 0.5 + params.LINE_STOP_OFFSET*1.5]
                    return rc.pass_ball.receive_ball(self.df.pos, [0.4, 0.2])
                else:
                    return rc.attack()

            else:
                self.df.pos = rc.state.robot_pos
                self.df.photo_front = rc.state.photo_front
                in_goal_area = (
                    rc.state.court_ball_pos[0] < 0
                )
                if in_goal_area:
                    if self.gk_ball_kick_timer.read() > GK_BALL_KICK_TIME:
                        if rc.state.photo_front:
                            return rc.pass_ball.pass_ball(self.of.pos)
                        else:
                            return rc.basic_move.catch_ball()
                else:
                    self.gk_ball_kick_timer.set()
                return rc.goal_keeper.run()

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
                    return rc.pass_ball.receive_ball(self.omf.pos, self.fw.target_pos)
            elif id == config.GK_ID:
                in_goal_area = (
                    rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
                    abs(rc.state.court_ball_pos[1]
                        ) < params.GOAL_AREA_WIDTH * 0.5
                )
                if in_goal_area:
                    if self.gk_ball_kick_timer.read() > GK_BALL_KICK_TIME:
                        if rc.state.photo_front:
                            return rc.pass_ball.pass_ball(self.dmf.pos)
                        else:
                            return rc.basic_move.catch_ball()
                else:
                    self.gk_ball_kick_timer.set()
                return rc.goal_keeper.run()
        elif config.NUM_ROBOTS <= 11:
            if id == self.lfw.id:
                self.lfw.pos = rc.state.robot_pos
                self.lfw.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if rc.state.opp_goal_dis < params.MAX_SHOOT_DIS:
                        return rc.attack()
                    else:
                        return rc.pass_ball.pass_ball(self.lsh.pos)

                elif self.lfw.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.pass_ball.receive_ball(self.lsh.pos, self.lfw.target_pos)
            elif id == self.rfw.id:
                self.rfw.pos = rc.state.robot_pos
                self.rfw.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if rc.state.opp_goal_dis < params.MAX_SHOOT_DIS:
                        return rc.attack()
                    else:
                        return rc.pass_ball.pass_ball(self.rsh.pos)
                elif self.rfw.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.pass_ball.receive_ball(self.rsh.pos, self.rfw.target_pos)
            elif id == self.lsh.id:
                self.lsh.pos = rc.state.robot_pos
                self.lsh.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if rc.state.opp_goal_dis < params.MAX_SHOOT_DIS:
                        return rc.attack()
                    else:
                        return rc.pass_ball.pass_ball(self.lfw.pos)
                elif self.lsh.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                elif rc.state.court_ball_pos[0] > 0:
                    return rc.pass_ball.receive_ball(self.lfw.pos, self.lsh.target_pos)
                else:
                    return rc.pass_ball.receive_ball(self.lsb.pos, self.lsh.target_pos)
            elif id == self.rsh.id:
                self.rsh.pos = rc.state.robot_pos
                self.rsh.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if rc.state.opp_goal_dis < params.MAX_SHOOT_DIS:
                        return rc.attack()
                    else:
                        return rc.pass_ball.pass_ball(self.rfw.pos)
                elif self.rsh.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                elif rc.state.court_ball_pos[0] > 0:
                    return rc.pass_ball.receive_ball(self.rfw.pos, self.rsh.target_pos)
                else:
                    return rc.pass_ball.receive_ball(self.rsb.pos, self.rsh.target_pos)
            elif id == self.lch.id:
                self.lch.pos = rc.state.robot_pos
                self.lch.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    return rc.pass_ball.pass_ball(self.lsh.pos)
                elif self.lch.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.pass_ball.receive_ball(self.gk.pos, self.lch.target_pos)
            elif id == self.rch.id:
                self.rch.pos = rc.state.robot_pos
                self.rch.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    return rc.pass_ball.pass_ball(self.rsh.pos)
                elif self.rch.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.pass_ball.receive_ball(self.gk.pos, self.rch.target_pos)
            elif id == self.lsb.id:
                self.lsb.pos = rc.state.robot_pos
                self.lsb.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if rc.state.robot_pos[0] < params.COURT_WIDTH * -0.25:
                        return rc.pass_ball.pass_ball(self.lch.pos)
                    else:
                        return rc.pass_ball.pass_ball(self.lsh.pos)
                elif self.lsb.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.basic_move.move_to_pos(self.lsb.target_pos[0], self.lsb.target_pos[1], rc.state.ball_angle)
            elif id == self.rsb.id:
                self.rsb.pos = rc.state.robot_pos
                self.rsb.photo_front = rc.state.photo_front
                if rc.state.photo_front:
                    if rc.state.robot_pos[0] < params.COURT_WIDTH * -0.25:
                        return rc.pass_ball.pass_ball(self.rch.pos)
                    else:
                        return rc.pass_ball.pass_ball(self.rsh.pos)
                elif self.rsb.target_pos == rc.state.court_ball_pos:
                    return rc.basic_move.catch_ball()
                else:
                    return rc.basic_move.move_to_pos(self.rsb.target_pos[0], self.rsb.target_pos[1], rc.state.ball_angle)
            elif id == self.lcb.id:
                self.lcb.pos = rc.state.robot_pos
                self.lcb.photo_front = rc.state.photo_front
                return rc.basic_move.move_to_pos(self.lcb.target_pos[0], self.lcb.target_pos[1], rc.state.ball_angle)
            elif id == self.rcb.id:
                self.rcb.pos = rc.state.robot_pos
                self.rcb.photo_front = rc.state.photo_front
                return rc.basic_move.move_to_pos(self.rcb.target_pos[0], self.rcb.target_pos[1], rc.state.ball_angle)
            elif id == config.GK_ID:
                self.gk.pos = rc.state.robot_pos
                self.gk.photo_front = rc.state.photo_front
                in_goal_area = (
                    rc.state.court_ball_pos[0] < -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT and
                    abs(rc.state.court_ball_pos[1]
                        ) < params.GOAL_AREA_WIDTH * 0.5
                )
                if in_goal_area:
                    if self.gk_ball_kick_timer.read() > GK_BALL_KICK_TIME:
                        if rc.state.photo_front:
                            if rc.state.court_ball_pos[0] < 0:
                                return rc.pass_ball.pass_ball(self.rsb.pos)
                            else:
                                return rc.pass_ball.pass_ball(self.lsb.pos)
                        else:
                            return rc.basic_move.catch_ball()
                else:
                    self.gk_ball_kick_timer.set()
                return rc.goal_keeper.run()
