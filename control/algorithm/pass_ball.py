import math
import lib.my_math as mymath
import lib.pid as pid


class PassBall:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move
        self.receive_ball_pid = pid.PID(6, 0, 1)

    def pass_ball(self, target_pos):
        dx = target_pos[0] - self.state.robot_pos[0]
        dy = target_pos[1] - self.state.robot_pos[1]
        target_dir = math.degrees(math.atan2(dy, dx)) * -1
        target_dis = math.hypot(dx, dy)

        kick = 0
        dribble = mymath.GapDeg(target_dir, self.state.robot_dir_angle) * 1.5
        if mymath.GapDeg(target_dir, self.state.robot_dir_angle) < 3:
            kick = target_dis * 60
        return self.basic_move.move(face_angle=target_dir,
                                    face_speed=mymath.PI,
                                    face_axis=1,
                                    dribble=dribble,
                                    kick=kick,)

    def receive_ball(self, origin_pos, target_pos):
        theta = math.radians(self.state.robot_dir_angle)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # ターゲット位置へのベクトル
        dx_t = target_pos[0] - self.state.robot_pos[0]
        dy_t = target_pos[1] - self.state.robot_pos[1]
        target_vec = [dx_t, dy_t]
        target_vec = [
            target_vec[0] * cos_t - target_vec[1] * sin_t,
            target_vec[0] * sin_t + target_vec[1] * cos_t
        ]
        # print(f"target_vec: {target_vec}")

        # ボールへのベクトル
        dx_b = self.state.court_ball_pos[0] - self.state.robot_pos[0]
        dy_b = self.state.court_ball_pos[1] - self.state.robot_pos[1]
        ball_vec = [dx_b, dy_b]
        ball_vec = [
            ball_vec[0] * cos_t - ball_vec[1] * sin_t,
            ball_vec[0] * sin_t + ball_vec[1] * cos_t
        ]
        # print(f"ball_vec: {ball_vec}")

        # ボールまでの距離

        # ボールが近いほどボール方向を重視（例: 0.5m以内ならボール重視, 1m以上ならターゲット重視）
        w_ball = max(0, 1.0 - min(self.state.ball_dis, 1.0))  # 0〜1
        w_target = 1.0 - w_ball

        # 合成ベクトル
        move_vec = [target_vec[0],
                    target_vec[1] * w_target + ball_vec[1] * w_ball]
        # print(f"move_vec: {move_vec}")

        # 角度・距離
        move_angle = math.degrees(math.atan2(move_vec[1], move_vec[0])) * -1
        move_dist = math.hypot(move_vec[0], move_vec[1])
        # print(f"move_angle: {move_angle}, move_dist: {move_dist}")

        # 顔の向きはボール方向
        dx = origin_pos[0] - self.state.robot_pos[0]
        dy = origin_pos[1] - self.state.robot_pos[1]
        face_angle = math.degrees(math.atan2(dy, dx)) * -1

        move_speed = min(1, abs(self.receive_ball_pid.update(0, move_dist)))

        return self.basic_move.move(
            move_angle=move_angle,
            move_speed=move_speed,
            move_acce=0,
            face_angle=face_angle,
            face_speed=mymath.PI,
            dribble=50
        )
