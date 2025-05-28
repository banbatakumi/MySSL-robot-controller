# 制御ループのポーリング間隔 (秒)
CONTROL_LOOP_INTERVAL = 0.01  # 10ms

# コート中心への移動時の閾値とゲイン
MAX_SPEED = 1

MAX_KICK_POWER = 100
MAX_DRIBBLE_POWER = 100

PLACEMENT_R = 0.1  # m

# --- DivAのパラメータ ---
COURT_WIDTH = 12  # コートの幅 (メートル) - 白線間の距離
COURT_HEIGHT = 9  # コートの高さ (メートル) - 白線間の距離
CENTEWR_CIRCLE_RADIUS = 0.5  # センターサークルの半径 (メートル)
GOAL_AREA_WIDTH = 3.6  # ゴールエリアの幅 (メートル)
GOAL_AREA_HEIGHT = 1.8  # ゴールエリアの高さ (メートル)
GOAL_WIDTH = 1.8
GOAL_HEIGHT = 0.2


# --- DivBのパラメータ ---
# COURT_WIDTH_M = 9  # コートの幅 (メートル) - 白線間の距離
# COURT_HEIGHT_M = 6  # コートの高さ (メートル) - 白線間の距離
# CENTEWR_CIRCLE_RADIUS_M = 0.5  # センターサークルの半径 (メートル)
# GOAL_AREA_WIDTH_M = 2  # ゴールエリアの幅 (メートル)
# GOAL_AREA_HEIGHT_M = 1  # ゴールエリアの高さ (メートル)
# GOAL_WIDTH = 1
# GOAL_HEIGHT = 0.2

ROBOT_D = 0.18
ROBOT_R = ROBOT_D * 0.5
