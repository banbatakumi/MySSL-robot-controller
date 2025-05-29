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
        if placement_dis < params.PLACEMENT_AVOID_R:
            angle = math.degrees(math.atan2(dy, dx)) * -1
            return rc.basic_move.move(angle, 0.5, 0.5)
        elif rc.state.ball_dis < 0.5:
            angle = mymath.NormalizeDeg180(rc.state.robot_ball_angle + 180)
            return rc.basic_move.move(angle, 0.5, 0.5)
