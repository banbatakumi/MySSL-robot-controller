import config
import math


def liner_alignment(id, rc, start_pos, end_pos):
    pos = start_pos[0] + \
        (id * (end_pos[0] - start_pos[0]) / (config.NUM_ROBOTS - 1)), \
        start_pos[1] + (id * (end_pos[1] - start_pos[1]) /
                        (config.NUM_ROBOTS - 1))

    command = rc.basic_move.move_to_pos(pos[0], pos[1])

    return command


def circle_alignment(id, rc, center_pos, radius):
    angle = (id * 360 / config.NUM_ROBOTS) % 360
    target_x = center_pos[0] + radius * math.cos(math.radians(angle))
    target_y = center_pos[1] + radius * math.sin(math.radians(angle))

    command = rc.basic_move.move_to_pos(target_x, target_y)

    return command
