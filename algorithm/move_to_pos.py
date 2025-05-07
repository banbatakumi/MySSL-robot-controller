import math
import config


def move_to_pos(robot_pos, target_pos, photo_front=0):
    # 目標までのベクトル
    vector = [target_pos[0] - robot_pos[0], target_pos[1] - robot_pos[1]]

    # 目標までの距離
    distance = math.hypot(vector[0], vector[1])

    # 目標とする移動方向 (コート座標系での角度)
    move_angle = math.degrees(math.atan2(vector[1], vector[0])) * -1

    move_acce = 0
    move_max_speed = config.MAX_LINEAR_SPEED_M_S
    face_speed = 0
    face_axis = 0
    dribble = 0
    face_angle = 0
    if photo_front == True:
        move_max_speed = 0.5
        move_acce = 0.1
        face_speed = math.pi * 0.5
        face_axis = 1
        dribble = 100
        face_angle = move_angle

    # 目標距離に応じた速度を計算
    speed = min(move_max_speed,
                config.CENTER_MOVE_LINEAR_GAIN * distance)

    return {
        "cmd": {
            "move_angle": round(move_angle, 0),
            "move_speed": round(speed, 2),
            "move_acce": round(move_acce, 2),
            "face_angle": face_angle,
            "face_speed": face_speed,
            "face_axis": face_axis,
            "dribble": dribble,
            "kick": 0
        }
    }
