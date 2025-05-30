import math


def liner_alignment(id, rc, id_list, start_pos, end_pos):
    """
    id_listに含まれるロボットを、start_posからend_posまで等間隔で整列させる
    """
    if id not in id_list:
        return None
    num_robots = len(id_list)
    index = id_list.index(id)
    pos_x = start_pos[0] + (end_pos[0] - start_pos[0]) * index / \
        (num_robots - 1) if num_robots > 1 else start_pos[0]
    pos_y = start_pos[1] + (end_pos[1] - start_pos[1]) * index / \
        (num_robots - 1) if num_robots > 1 else start_pos[1]
    return rc.basic_move.move_to_pos(pos_x, pos_y)


def circle_alignment(id, rc, initial_id, end_id, num_robots, center_pos, radius):
    num_robots = end_id - initial_id + 1
    if initial_id <= id <= end_id:
        id -= initial_id
        angle = (id * 360 / num_robots) % 360
        target_x = center_pos[0] + radius * math.cos(math.radians(angle))
        target_y = center_pos[1] + radius * math.sin(math.radians(angle))

        command = rc.basic_move.move_to_pos(target_x, target_y)

        return command
