import config
import strategy.algorithm.funny as funny
import strategy.algorithm.alignment as alignment
from strategy.mode.stop_game import stop_game
from strategy.mode.ball_placement import ball_placement
from strategy.utils import Utils


class StrategyManager:
    def __init__(self, robot_controllers):
        self.robot_controllers = robot_controllers
        self.utils = Utils(robot_controllers)

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
                if target_team_color == config.TEAM_COLOR:
                    target_x = command_data.get("x")
                    target_y = command_data.get("y")
                    self._placement_target_pos = [target_x, target_y]
                    self.game_mode = 'ball_placement'
                else:
                    rc.send_stop_command()
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
        closest_robot_to_ball = self.utils.get_closest_robot_to_ball()
        for id, rc in self.robot_controllers.items():
            if rc.state.robot_pos is None or rc.state.robot_dir_angle is None:
                print(
                    f"[Robot {id} Maneger] Incomplete vision data.")
                rc.send_stop_command()
                continue
            command = None
            if self.game_mode == 'stop_game':
                command = stop_game(id, rc)
            elif self.game_mode == 'start_game':
                if (rc.state.court_ball_pos is None):
                    return
                # command = funny.circle_passing(id, rc, [0, 0], 3)
                if id == closest_robot_to_ball:
                    command = rc.attack()

            elif self.game_mode == 'ball_placement':
                if (rc.state.court_ball_pos is None):
                    return
                command = ball_placement(
                    id, rc, self._placement_target_pos, closest_robot_to_ball)

            if command is None:
                continue
            rc.send_command(command)
