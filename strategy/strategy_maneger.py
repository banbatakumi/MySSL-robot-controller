import config
import params
import strategy.algorithm.funny as funny
import strategy.algorithm.alignment as alignment


class StrategyManager:
    def __init__(self, robot_controllers):
        self.robot_controllers = robot_controllers

        self.game_mode = 'stop'

    def handle_game_command(self, command_data):
        """
        外部からのゲームコマンドを処理し、ロボットの動作モードを切り替える。
        """
        cmd_type = command_data.get("type")
        cmd = command_data.get("command")
        target_team_color = command_data.get("team_color")
        print(
            f"[StrategyManager] Received command: {cmd_type}, {cmd}, {target_team_color}")

        if target_team_color is not None and target_team_color != config.TEAM_COLOR:
            return

        if cmd_type == "game_command":
            if cmd == "stop_game":
                self.game_mode = 'stop_game'
                self._placement_target_pos = None
            elif cmd == "start_game":
                self.game_mode = 'start_game'
                self._placement_target_pos = None
            elif cmd == "emergency_stop":
                self.game_mode = 'stop'
                self._placement_target_pos = None
                for rc in self.robot_controllers.values():
                    rc.send_stop_command()
            elif cmd == "place_ball":
                target_x = command_data.get("x")
                target_y = command_data.get("y")
                self._placement_target_pos = [target_x, target_y]
                self.game_mode = 'ball_placement'
            else:
                for rc in self.robot_controllers.values():
                    rc.send_stop_command()
                return

    def handle_gui_command(self, command_data):
        """
        GUIからのコマンド
        """
        cmd_type = command_data.get("type")
        cmd = command_data.get("command")
        print(
            f"[StrategyManager] Received GUI command: {cmd_type}, {cmd}")

        if cmd_type == "gui_command":
            if cmd == "stop_all_robots":
                for rc in self.robot_controllers.values():
                    rc.send_stop_command()
                self.game_mode = 'emergency_stop'
            elif cmd == "place_ball":
                target_x = command_data.get("x")
                target_y = command_data.get("y")
                self._placement_target_pos = [target_x, target_y]
                self.game_mode = 'ball_placement'
            else:
                for rc in self.robot_controllers.values():
                    rc.send_stop_command()

    def update_strategy_and_control(self, vision_data):
        """
        メインの戦略プログラム
        """
        closest_robot_id = self.get_closest_robot_to_ball()
        for id, rc in self.robot_controllers.items():
            if rc.state.robot_pos is None or rc.state.robot_dir_angle is None:
                print(
                    f"[Robot {id} Maneger] Incomplete vision data.")
                rc.send_stop_command()
                continue
            command = None
            if self.game_mode == 'stop_game':
                if id == 0:
                    command = rc.basic_move.move_to_pos(
                        params.COURT_WIDTH / -2 + params.ROBOT_D, 0)
                elif id == 1:
                    x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 1
                    command = rc.basic_move.move_to_pos(x, 0)
                elif id == 2:
                    x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 1
                    y = params.COURT_HEIGHT / 2 - 1
                    command = rc.basic_move.move_to_pos(x, y)
                elif id == 3:
                    x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 1
                    y = params.COURT_HEIGHT / -2 + 1
                    command = rc.basic_move.move_to_pos(x, y)
                elif id <= 7:
                    x = params.COURT_WIDTH / -2 + params.GOAL_AREA_HEIGHT + 0.2
                    command = alignment.liner_alignment(
                        id, rc, 4, 7, [x, -1], [x, 1])
                else:
                    x = -params.CENTEWR_CIRCLE_RADIUS - 0.2
                    command = alignment.liner_alignment(
                        id, rc, 8, 10, [x, -0.5], [x, 0.5])
            elif self.game_mode == 'start_game':
                if (rc.state.court_ball_pos is None):
                    return
                # command = funny.circle_passing(id, rc, [0, 0], 3)
                if id == closest_robot_id:
                    command = rc.attack()

            elif self.game_mode == 'ball_placement':
                if (rc.state.court_ball_pos is None):
                    return
                if id == closest_robot_id:
                    target_x = self._placement_target_pos[0]
                    target_y = self._placement_target_pos[1]
                    command = rc.ball_placement(target_x, target_y)

            if command is None:
                continue
            rc.send_command(command)

    def get_closest_robot_to_ball(self):
        closest_id = None
        min_distance = float('inf')

        for id, rc in self.robot_controllers.items():
            if rc.state.ball_dis is not None and rc.state.ball_dis < min_distance:
                min_distance = rc.state.ball_dis
                closest_id = id

        return closest_id
