import strategy.algorithm.alignment as alignment
import params
import config


def stop_game(id, rc):
    if config.NUM_ROBOTS == 1:
        pass
    elif config.NUM_ROBOTS == 2:
        pass
    else:
        if id == 0:
            return rc.basic_move.move_to_pos(
                params.COURT_WIDTH / -2 + params.ROBOT_D, 0)
        elif id == 1:
            x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 1
            return rc.basic_move.move_to_pos(x, 0)
        elif id == 2:
            x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 1
            y = params.COURT_HEIGHT / 2 - 1
            return rc.basic_move.move_to_pos(x, y)
        elif id == 3:
            x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 1
            y = params.COURT_HEIGHT / -2 + 1
            return rc.basic_move.move_to_pos(x, y)
        elif id <= 7:
            x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 0.2
            return alignment.liner_alignment(
                id, rc, 4, 7, [x, -1], [x, 1])
        else:
            x = -params.CENTEWR_CIRCLE_RADIUS - 0.2
            return alignment.liner_alignment(
                id, rc, 8, 10, [x, -0.5], [x, 0.5])
