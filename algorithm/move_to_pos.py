import math
import config


def move_to_pos(robot_pos, target_pos, max_speed=1, face_speed=6.28, face_axis=0, dribble=0, kick=0):
    # 目標までのベクトル
    vector = [target_pos[0] - robot_pos[0], target_pos[1] - robot_pos[1]]

    # 目標までの距離
    distance = math.hypot(vector[0], vector[1])

    # 目標とする移動方向 (コート座標系での角度)
    desired_court_angle = math.degrees(math.atan2(vector[1], vector[0])) * -1

    # 目標距離に応じた速度を計算
    speed = min(config.MAX_LINEAR_SPEED_M_S,
                config.CENTER_MOVE_LINEAR_GAIN * distance)
    if speed > max_speed:
        speed = max_speed

    return {
        "cmd": {
            "move_angle": round(desired_court_angle, 0),
            "move_speed": round(speed, 2),
            "move_acce": 5,
            "face_angle": 0,
            "face_speed": face_speed,
            "face_axis": face_axis,
            "stop": False,
            "kick": kick,
            "dribble": dribble,
        }
    }
