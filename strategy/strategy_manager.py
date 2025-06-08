import config
import strategy.algorithm.funny as funny
import strategy.algorithm.alignment as alignment
from strategy.mode.stop_game import stop_game
from strategy.mode.ball_placement import ball_placement
from strategy.mode.start_game import StartGame
from strategy.utils import Utils


class StrategyManager:
    def __init__(self, robot_controllers):
        self.robot_controllers = robot_controllers
        self.utils = Utils(robot_controllers)
        self.start_game = StartGame(self.utils)

        self.game_mode = 'stop'

    def handle_game_command(self, command_data):
        cmd_type = command_data.get("type")
        cmd = command_data.get("command")
        self.target_team_color = command_data.get("team_color")
        print(
            f"[StrategyManager] Received command: {cmd_type}, {cmd}, {self.target_team_color}")

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
        orange_balls = vision_data.get('orange_balls', [])
        ball_data = orange_balls[0] if orange_balls else None
        court_ball_pos = list(ball_data.get('pos')) if ball_data else None
        if config.TEAM_SIDE == 'right' and not court_ball_pos == None:
            # 右側チームの場合、ボール位置を反転
            court_ball_pos[0] *= -1
            court_ball_pos[1] *= -1
        self.utils.update_vision_data(vision_data)
        closest_robot_to_ball = self.utils.get_closest_robot_to_ball(
            court_ball_pos)

        self.start_game.update_roll(court_ball_pos)
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
                command = self.start_game.run(id, rc)
                # command = funny.circle_passing(
                #     id, rc, [0, 0], radius=2)

            elif self.game_mode == 'ball_placement':
                if (rc.state.court_ball_pos is None):
                    return
                command = ball_placement(
                    id, rc, self.target_team_color, self._placement_target_pos, closest_robot_to_ball)

            if command is None:
                rc.send_stop_command()
                continue
            rc.send_command(command)
