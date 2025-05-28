import config
import math


def liner_alignment(id, rc, initial_id, end_id, start_pos, end_pos):
    num_robots = end_id - initial_id + 1
    if initial_id <= id <= end_id:
        id -= initial_id
        pos = start_pos[0] + \
            (id * (end_pos[0] - start_pos[0]) / (num_robots - 1)), \
            start_pos[1] + (id * (end_pos[1] - start_pos[1]) /
                            (num_robots - 1))

        command = rc.basic_move.move_to_pos(pos[0], pos[1])

        return command


def circle_alignment(id, rc, initial_id, end_id, num_robots, center_pos, radius):
    num_robots = end_id - initial_id + 1
    if initial_id <= id <= end_id:
        id -= initial_id
        angle = (id * 360 / num_robots) % 360
        target_x = center_pos[0] + radius * math.cos(math.radians(angle))
        target_y = center_pos[1] + radius * math.sin(math.radians(angle))

        command = rc.basic_move.move_to_pos(target_x, target_y)

        return command
