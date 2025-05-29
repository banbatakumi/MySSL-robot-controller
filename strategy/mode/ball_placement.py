import math
import lib.my_math as mymath
import params


def ball_placement(id, rc, target_pos, closest_robot_to_ball):
    dx = rc.state.robot_pos[0] - target_pos[0]
    dy = rc.state.robot_pos[1] - target_pos[1]
    placement_dis = math.hypot(dx, dy)
    if id == closest_robot_to_ball:
        return rc.ball_placement(target_pos[0], target_pos[1])
    else:
        if rc.state.ball_dis < 0.5:
            angle = rc.state.ball_angle
            speed = (0.5 - rc.state.ball_dis) * (params.MAX_SPEED / 0.5)
            return rc.basic_move.move(180, speed, face_angle=angle)
        elif placement_dis < 0.5:
            angle = mymath.NormalizeDeg180(
                math.degrees(math.atan2(dy, dx)) * -1 + 180)
            speed = (0.5 - placement_dis) * (params.MAX_SPEED / 0.5)
            return rc.basic_move.move(180, speed, face_angle=angle)
