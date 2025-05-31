import strategy.algorithm.alignment as alignment
import params
import config


def stop_game(id, rc):
    if config.NUM_ROBOTS == 1:
        rc.basic_move.move_to_pos(0, 0)
    elif config.NUM_ROBOTS == 2:
        if id == 0:
            x = -params.COURT_WIDTH / 2 + params.ROBOT_D
            return rc.basic_move.move_to_pos(x, 0)
        elif id == 1:
            x = -params.CENTEWR_CIRCLE_RADIUS - params.ROBOT_R
            return rc.basic_move.move_to_pos(x, 0)
    elif config.NUM_ROBOTS <= 6:
        if id == 0:  # ゴールキーパー
            x = -params.COURT_WIDTH / 2 + params.ROBOT_D
            return rc.basic_move.move_to_pos(x, 0)
        elif id == 1:  # センターバック
            x = -params.COURT_WIDTH / 2 + params.GOAL_AREA_HEIGHT + 0.2
            return rc.basic_move.move_to_pos(x, 0)
        elif id == 2:  # オフェンシブミッドフィールダー
            x = -params.CENTEWR_CIRCLE_RADIUS - params.ROBOT_D * 3
            return rc.basic_move.move_to_pos(x, 0)
        elif id <= 4:  # サイドハーフ
            x = -params.ROBOT_D
            y = params.GOAL_WIDTH + params.LINE_STOP_OFFSET * 1.5
            return alignment.liner_alignment(
                id, rc, [3, 4], [x, y], [x, -y])
        elif id == 5:  # フォワード
            x = -params.CENTEWR_CIRCLE_RADIUS - params.ROBOT_D
            return rc.basic_move.move_to_pos(x, 0)
    else:
        if id == 0:  # ゴールキーパー
            x = -params.COURT_WIDTH * 0.5 + params.ROBOT_D
            return rc.basic_move.move_to_pos(x, 0)
        elif id <= 2:  # センターバック
            x = -params.COURT_WIDTH * 0.5 + \
                params.GOAL_AREA_HEIGHT + params.LINE_STOP_OFFSET * 1.5
            return alignment.liner_alignment(
                id, rc, [1, 2], [x, params.ROBOT_R], [x, -params.ROBOT_R])
        elif id <= 4:  # サイドバック
            x = -params.COURT_WIDTH * 0.5 + params.GOAL_AREA_HEIGHT
            y = params.GOAL_WIDTH + params.LINE_STOP_OFFSET * 1.5
            return alignment.liner_alignment(
                id, rc, [3, 4], [x, y], [x, -y])
        elif id <= 6:  # ディフェンシブミッドフィールダー
            x = -params.COURT_WIDTH * 0.25
            y = params.GOAL_WIDTH * 0.5
            return alignment.liner_alignment(
                id, rc, [5, 6], [x, y], [x, -y])
        elif id == 7:  # オフェンシブミッドフィールダー
            x = -params.CENTEWR_CIRCLE_RADIUS - params.ROBOT_D * 3
            return rc.basic_move.move_to_pos(x, 0)
        elif id <= 9:  # サイドハーフ
            x = -params.ROBOT_D
            y = params.GOAL_WIDTH + params.LINE_STOP_OFFSET * 1.5
            return alignment.liner_alignment(
                id, rc, [8, 9], [x, y], [x, -y])
        elif id == 10:  # フォワード
            x = -params.CENTEWR_CIRCLE_RADIUS - params.ROBOT_D
            return rc.basic_move.move_to_pos(x, 0)
