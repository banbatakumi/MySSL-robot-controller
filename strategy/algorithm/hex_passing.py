import math
import config


def hex_passing(rc, robot_id):
    """
    六角形の頂点を通過する戦略
    """
    RADIUS = 1.5  # 六角形の半径（中心から頂点までの距離、適宜調整）
    CENTER_X = 0
    CENTER_Y = 0

    # 六角形の頂点座標を計算
    hex_points = [
        (
            CENTER_X + RADIUS * math.cos(math.radians(30 * i)),
            CENTER_Y + RADIUS * math.sin(math.radians(30 * i))
        )
        for i in range(config.NUM_ROBOTS)
    ]

    my_pos = hex_points[robot_id % config.NUM_ROBOTS]
    next_pos = hex_points[(robot_id + 1) % config.NUM_ROBOTS]

    if rc.state.photo_front == False:
        command = rc.pass_ball.receive_ball(*my_pos)
    else:
        command = rc.pass_ball.pass_ball(*next_pos)
    return command
