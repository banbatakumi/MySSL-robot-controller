import config


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

    def update_strategy_and_control(self, vision_data):
        for robot_id, rc in self.robot_controllers.items():
            if rc.state.robot_pos is None or rc.state.robot_dir_angle is None:
                print(
                    f"[Robot {robot_id} Maneger] Incomplete vision data.")
                rc.send_stop_command()
                continue
            command = None
            if self.game_mode == 'stop_game':
                command = rc.basic_move.move_to_pos(
                    (0.2 + robot_id * 0.2) * config.TEAM_SIDE, 0)

            elif self.game_mode == 'start_game':
                if (rc.state.court_ball_pos is None):
                    return

                if robot_id == 1:
                    command = rc.basic_move.move_to_pos(-0.5, 0)
                    # if rc.state.photo_front == False:
                    #     command = rc.pass_ball.receive_ball(-0.6, 0)
                    #     if rc.state.court_ball_pos[0] < 0 and rc.state.ball_dis < 0.4:
                    #         command = rc.basic_move.catch_ball()
                    # else:
                    #     command = rc.pass_ball.pass_ball(0.6, 0)
                elif robot_id == 0:
                    command = rc.attack()
                    # if rc.state.photo_front == False:
                    #     command = rc.pass_ball.receive_ball(0.6, 0)
                    #     if rc.state.court_ball_pos[0] > 0 and rc.state.ball_dis < 0.4:
                    #         command = rc.basic_move.catch_ball()
                    # else:
                    #     command = rc.pass_ball.pass_ball(-0.6, 0)

                # if robot_id == 0:
                #     if rc.state.photo_front == False:
                #         command = rc.pass_ball.receive_ball(0.5, 0.3)
                #     else:
                #         command = rc.pass_ball.pass_ball(0.5, -0.3)
                # elif robot_id == 1:
                #     if rc.state.photo_front == False:
                #         command = rc.pass_ball.receive_ball(0.5, -0.3)
                #     else:
                #         command = rc.pass_ball.pass_ball(-0.5, -0.3)
                # elif robot_id == 2:
                #     if rc.state.photo_front == False:
                #         command = rc.pass_ball.receive_ball(-0.5, -0.3)
                #     else:
                #         command = rc.pass_ball.pass_ball(-0.5, 0.3)
                # elif robot_id == 3:
                #     if rc.state.photo_front == False:
                #         command = rc.pass_ball.receive_ball(-0.5, 0.3)
                #     else:
                #         command = rc.pass_ball.pass_ball(0.5, 0.3)

            elif self.game_mode == 'ball_placement':
                if (rc.state.court_ball_pos is None):
                    return
                if robot_id == self.get_closest_robot_to_ball():
                    target_x = self._placement_target_pos[0]
                    target_y = self._placement_target_pos[1]
                    command = rc.ball_placement(target_x, target_y)

            if command is None:
                continue
            rc.send_command(command)

    def get_closest_robot_to_ball(self):
        closest_robot_id = None
        min_distance = float('inf')  # 初期値を無限大に設定

        for robot_id, rc in self.robot_controllers.items():
            # ロボットの状態からボールとの距離を取得
            ball_distance = rc.state.ball_dis

            if ball_distance is not None and ball_distance < min_distance:
                min_distance = ball_distance
                closest_robot_id = robot_id

        return closest_robot_id
