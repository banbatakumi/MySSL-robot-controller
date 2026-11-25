import config
import math
import params
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

    def _get_alignment_robot_ids(self):
        return sorted(self.robot_controllers.keys())

    def _get_alignment_command(self, mode, robot_id, rc):
        robot_ids = self._get_alignment_robot_ids()
        if not robot_ids:
            return None

        half_width = params.COURT_WIDTH * 0.5
        half_height = params.COURT_HEIGHT * 0.5
        margin = params.LINE_STOP_OFFSET * 1.5
        center_pos = [0, 0]
        radius = min(half_width, half_height) * 0.35

        if mode == 'align_top_left':
            return alignment.liner_alignment(
                robot_id, rc, robot_ids,
                [-half_width + margin, half_height - margin],
                [-margin, half_height - margin]
            )
        if mode == 'align_top_right':
            return alignment.liner_alignment(
                robot_id, rc, robot_ids,
                [half_width - margin, half_height - margin],
                [margin, half_height - margin]
            )
        if mode == 'align_bottom_left':
            return alignment.liner_alignment(
                robot_id, rc, robot_ids,
                [-half_width + margin, -half_height + margin],
                [-margin, -half_height + margin]
            )
        if mode == 'align_bottom_right':
            return alignment.liner_alignment(
                robot_id, rc, robot_ids,
                [half_width - margin, -half_height + margin],
                [margin, -half_height + margin]
            )
        if mode == 'circle_formation':
            return alignment.circle_alignment(
                robot_id,
                rc,
                robot_ids[0],
                robot_ids[-1],
                len(robot_ids),
                center_pos,
                radius,
            )
        return None

    def handle_game_command(self, command_data):
        cmd_type = command_data.get("type")
        cmd = command_data.get("command")
        self.target_team_color = command_data.get("team_color")
        self.kickoff_team = command_data.get("kickoff_team")
        print(
            f"[StrategyManager] Received command: {cmd_type}, {cmd}, {self.target_team_color}, {self.kickoff_team}")

        if cmd_type == "game_command":
            if cmd == "stop_game":
                self.game_mode = 'stop_game'
                self._placement_target_pos = None
            elif cmd == "start_game":
                if self.kickoff_team == 'force':
                    self.game_mode = 'start_game_force'
                elif self.kickoff_team == config.TEAM_COLOR:
                    self.game_mode = 'start_game_kickoff'
                else:
                    self.game_mode = 'start_game'
                    self.initialize_start_game = True
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
            elif cmd in (
                "align_top_left",
                "align_top_right",
                "align_bottom_left",
                "align_bottom_right",
                "circle_formation",
            ):
                self.game_mode = cmd
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
        closest_robot_to_ball = self.utils.get_closest_robot_to_ball()

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
            elif self.game_mode == 'start_game_kickoff' or self.game_mode == 'start_game_force':
                if (rc.state.court_ball_pos is None):
                    return
                command = self.start_game.run(id, rc)
            elif self.game_mode == 'start_game':
                if (rc.state.court_ball_pos is None):
                    return
                if self.initialize_start_game:
                    self.initial_ball_pos = rc.state.court_ball_pos
                    self.initialize_start_game = False
                ball_pos_diff = [
                    rc.state.court_ball_pos[0] - self.initial_ball_pos[0],
                    rc.state.court_ball_pos[1] - self.initial_ball_pos[1]
                ]
                ball_pos_diff_length = math.hypot(
                    ball_pos_diff[0], ball_pos_diff[1])
                if ball_pos_diff_length > 0.5:
                    self.game_mode = 'start_game_kickoff'
            elif self.game_mode == 'ball_placement':
                if (rc.state.court_ball_pos is None):
                    return
                command = ball_placement(
                    id, rc, self.target_team_color, self._placement_target_pos, closest_robot_to_ball)
            elif self.game_mode in (
                'align_top_left',
                'align_top_right',
                'align_bottom_left',
                'align_bottom_right',
                'circle_formation',
            ):
                command = self._get_alignment_command(self.game_mode, id, rc)

            if command is None:
                rc.send_stop_command()
                continue
            rc.send_command(command)
