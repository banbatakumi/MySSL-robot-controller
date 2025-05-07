class State:
    def __init__(self):
        # センサ情報
        self.photo_front = None
        self.photo_back = None

        # ビジョン情報
        self.court_ball_pos = None

        self.ball_pos = None
        self.ball_dis = None
        self.ball_angle = None
        self.robot_ball_angle = None
        self.robot_ball_pos = None

        self.robot_pos = None
        self.robot_dir_angle = None
