class Utils:
    def __init__(self, robot_controllers):
        self.robot_controllers = robot_controllers

    def get_closest_robot_to_ball(self):
        closest_id = None
        min_distance = float('inf')

        for id, rc in self.robot_controllers.items():
            if rc.state.ball_dis is not None and rc.state.ball_dis < min_distance:
                min_distance = rc.state.ball_dis
                closest_id = id

        return closest_id
