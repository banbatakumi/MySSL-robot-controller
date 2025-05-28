import math
import config


def circle_passing(id, rc, center_pos=[0, 0], radius=1.5):
    circle_points = [
        (
            center_pos[0] + radius *
            math.cos(math.radians(360 * i / config.NUM_ROBOTS)),
            center_pos[1] + radius *
            math.sin(math.radians(360 * i / config.NUM_ROBOTS))
        )
        for i in range(config.NUM_ROBOTS)
    ]

    my_pos = circle_points[id % config.NUM_ROBOTS]
    next_pos = circle_points[(id + 1) % config.NUM_ROBOTS]

    if rc.state.photo_front == False:
        command = rc.pass_ball.receive_ball(*my_pos)
    else:
        command = rc.pass_ball.pass_ball(*next_pos)
    return command
