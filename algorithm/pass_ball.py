import config
import math
import lib.my_math as mymath


class PassBall:
    def __init__(self, state, basic_move):
        self.state = state
        self.basic_move = basic_move

    def pass_ball(self, target_x, target_y):
        target_dir = math.degrees(math.atan2(
            target_y - self.state.robot_pos[1], target_x - self.state.robot_pos[0])) * -1
        target_dis = math.hypot(
            target_x - self.state.robot_pos[0], target_y - self.state.robot_pos[1])

        dribble = 100
        kick = 0
        if mymath.GapDeg(target_dir, self.state.robot_dir_angle) < 10:
            dribble = 0
        if mymath.GapDeg(target_dir, self.state.robot_dir_angle) < 5:
            kick = target_dis * 75
        print(
            f"robot_dir: {self.state.robot_dir_angle}, target_dir: {target_dir}, target_dis: {target_dis}, dribble: {dribble}, kick: {kick}")
        return self.basic_move.move(face_angle=target_dir,
                                    face_speed=mymath.HALF_PI,
                                    face_axis=1,
                                    dribble=dribble,
                                    kick=kick,)

    def receive_ball(self, target_x, target_y):
        cmd = self.basic_move.move_to_pos(target_x, target_y,
                                          face_angle=self.state.ball_angle)
        if self.state.ball_dis < 0.5:
            cmd['cmd']['dribble'] = 50
        return cmd
