def ball_placement(id, rc, target_pos, closest_robot_to_ball):
    if id == closest_robot_to_ball:
        return rc.ball_placement(target_pos[0], target_pos[1])
