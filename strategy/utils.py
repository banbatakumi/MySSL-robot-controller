import math
import config
import params
from strategy.state import State


class Utils:
    def __init__(self, rc):
        self.rc = rc
        self.vision_data = None
        self.own_states = State()
        self.enemy_states = State()

    def update_vision_data(self, vision_data):
        self.vision_data = vision_data
        orange_balls = vision_data.get('orange_balls', [])
        ball_data = orange_balls[0] if orange_balls else None
        yellow_robots_data = vision_data.get('yellow_robots', {})
        blue_robots_data = vision_data.get('blue_robots', {})
        if config.TEAM_COLOR == 'yellow':
            self.own_states.update(yellow_robots_data, ball_data)
            self.enemy_states.update(blue_robots_data, ball_data)
        elif config.TEAM_COLOR == 'blue':
            self.own_states.update(blue_robots_data, ball_data)
            self.enemy_states.update(yellow_robots_data, ball_data)

    def is_enemy_on_pass_line(self, passer_pos, receiver_pos):
        for e_pos in self.enemy_states.robot_pos:
            # パスライン上の最近点を計算
            px, py = passer_pos
            rx, ry = receiver_pos
            ex, ey = e_pos
            dx, dy = rx - px, ry - py
            if dx == 0 and dy == 0:
                continue
            t = ((ex - px) * dx + (ey - py) * dy) / (dx*dx + dy*dy)
            t = max(0, min(1, t))
            nearest_x = px + t * dx
            nearest_y = py + t * dy
            dist = math.hypot(ex - nearest_x, ey - nearest_y)
            if dist < params.ROBOT_R:
                return True
        return False

    def find_safe_pass_position(self, passer_pos, base_pos, radius=0.5, angle_step=1):
        dist = math.hypot(base_pos[0] - passer_pos[0],
                          base_pos[1] - passer_pos[1])
        for angle in range(0, 360, angle_step):
            rad = math.radians(angle)
            candidate = [
                base_pos[0] + dist * math.cos(rad),
                base_pos[1] + dist * math.sin(rad)
            ]
            if not self.is_enemy_on_pass_line(passer_pos, candidate):
                return candidate  # 安全な位置が見つかったら返す
        return base_pos  # 見つからなければ基準位置

    def has_possession(self):
        min_own_ball_dis = float('inf')
        for id in range(self.own_states.robot_num):
            if self.own_states.ball_dis[id] is not None and self.own_states.ball_dis[id] < min_own_ball_dis:
                min_own_ball_dis = self.own_states.ball_dis[id]

        min_enemy_ball_dis = float('inf')
        for id in range(self.enemy_states.robot_num):
            if self.enemy_states.ball_dis[id] is not None and self.enemy_states.ball_dis[id] < min_enemy_ball_dis:
                min_enemy_ball_dis = self.enemy_states.ball_dis[id]

        if min_own_ball_dis < min_enemy_ball_dis:
            return True
        else:
            return False

    def get_best_pass_target(self, passer_id, candidate_ids):
        passer_pos = self.own_states[passer_id].robot_pos
        best_score = float('-inf')
        best_id = None
        for id in candidate_ids:
            target_pos = self.own_states[id].robot_pos
            # 敵との最短距離
            min_enemy_dist = min(
                math.hypot(target_pos[0]-e_pos[0], target_pos[1]-e_pos[1])
                for e_pos in self.enemy_states.robot_pos
            ) if self.enemy_states.robot_pos else 0
            # ゴール方向への前進度
            forward_score = target_pos[0] - passer_pos[0]
            # 距離
            dist = math.hypot(target_pos[0]-passer_pos[0],
                              target_pos[1]-passer_pos[1])
            # 総合スコア
            if dist < 0.5 or dist > 3.0:
                continue
            score = min_enemy_dist + 0.5*forward_score
            if score > best_score:
                best_score = score
                best_id = id
        return best_id

    def get_closest_robot_to_ball(self, id_list=None):
        closest_id = None
        min_distance = float('inf')

        if id_list is None:
            for id, rc in self.rc.items():
                if rc.state.ball_dis is not None and rc.state.ball_dis < min_distance:
                    min_distance = rc.state.ball_dis
                    closest_id = id
        else:
            for id in id_list:
                rc = self.rc.get(id)
                if rc is not None and rc.state.ball_dis is not None:
                    if rc.state.ball_dis < min_distance:
                        min_distance = rc.state.ball_dis
                        closest_id = id

        return closest_id

    def get_closest_robot_to_target(self, target_pos, id_list=None):
        closest_id = None
        min_distance = float('inf')
        if id_list is None:
            for id, rc in self.rc.items():
                if rc.state.robot_pos is not None:
                    dx = rc.state.robot_pos[0] - target_pos[0]
                    dy = rc.state.robot_pos[1] - target_pos[1]
                    distance = math.hypot(dx, dy)

                    if distance < min_distance:
                        min_distance = distance
                        closest_id = id
        else:
            for id in id_list:
                rc = self.rc.get(id)
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
            for id, rc in self.rc.items():
                if rc.state.robot_pos is not None and rc.state.robot_pos[0] > max_x:
                    max_x = rc.state.robot_pos[0]
                    frontmost_id = id
        else:
            for id in id_list:
                rc = self.rc.get(id)
                if rc is not None and rc.state.robot_pos is not None:
                    if rc.state.robot_pos[0] > max_x:
                        max_x = rc.state.robot_pos[0]
                        frontmost_id = id

        return frontmost_id

    def get_closest_robot_pos_to_ball(self, id_list=None):
        closest_id = self.get_closest_robot_to_ball(id_list)
        if closest_id is not None:
            rc = self.rc.get(closest_id)
            if rc is not None and rc.state.robot_pos is not None:
                return rc.state.robot_pos
        return None
