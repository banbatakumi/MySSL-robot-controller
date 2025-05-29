import math


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

    def get_closest_robot_to_target(self, target_pos):
        closest_id = None
        min_distance = float('inf')

        for id, rc in self.robot_controllers.items():
            if rc.state.robot_pos is not None:
                dx = rc.state.robot_pos[0] - target_pos[0]
                dy = rc.state.robot_pos[1] - target_pos[1]
                distance = math.hypot(dx, dy)

                if distance < min_distance:
                    min_distance = distance
                    closest_id = id

        return closest_id
