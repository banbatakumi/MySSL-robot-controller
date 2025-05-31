import math


class Utils:
    def __init__(self, robot_controllers):
        self.robot_controllers = robot_controllers

    def get_closest_robot_to_ball(self, id_list=None):
        """
        指定したid_listの中で最もボールに近いロボットのidを返す
        """
        closest_id = None
        min_distance = float('inf')

        if id_list is None:
            for id, rc in self.robot_controllers.items():
                if rc.state.ball_dis is not None and rc.state.ball_dis < min_distance:
                    min_distance = rc.state.ball_dis
                    closest_id = id
        else:
            for id in id_list:
                rc = self.robot_controllers.get(id)
                if rc is not None and rc.state.ball_dis is not None:
                    if rc.state.ball_dis < min_distance:
                        min_distance = rc.state.ball_dis
                        closest_id = id

        return closest_id

    def get_closest_robot_to_target(self, target_pos, id_list=None):
        closest_id = None
        min_distance = float('inf')
        if id_list is None:
            for id, rc in self.robot_controllers.items():
                if rc.state.robot_pos is not None:
                    dx = rc.state.robot_pos[0] - target_pos[0]
                    dy = rc.state.robot_pos[1] - target_pos[1]
                    distance = math.hypot(dx, dy)

                    if distance < min_distance:
                        min_distance = distance
                        closest_id = id
        else:
            for id in id_list:
                rc = self.robot_controllers.get(id)
                if rc is not None and rc.state.robot_pos is not None:
                    dx = rc.state.robot_pos[0] - target_pos[0]
                    dy = rc.state.robot_pos[1] - target_pos[1]
                    distance = math.hypot(dx, dy)
                    if distance < min_distance:
                        min_distance = distance
                        closest_id = id

        return closest_id

    def get_frontmost_robot(self, id_list=None):
        frontmost_id = None
        max_x = float('-inf')

        if id_list is None:
            for id, rc in self.robot_controllers.items():
                if rc.state.robot_pos is not None and rc.state.robot_pos[0] > max_x:
                    max_x = rc.state.robot_pos[0]
                    frontmost_id = id
        else:
            for id in id_list:
                rc = self.robot_controllers.get(id)
                if rc is not None and rc.state.robot_pos is not None:
                    if rc.state.robot_pos[0] > max_x:
                        max_x = rc.state.robot_pos[0]
                        frontmost_id = id

        return frontmost_id
