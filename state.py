class State:
    def __init__(self):
        # センサ情報
        self.photo_front = None
        self.photo_back = None

        # ビジョン情報
        self.ball_pos = None
        self.robot_pos = None
        self.robot_angle = None
        self.robot_ball_pos = None
        self.robot_ball_angle = None
        self.robot_ball_dis = None
