import time
import config  # config.py から設定を読み込む
from lib.udp_communicator import UDPCommunicator  # libフォルダにあると仮定
from robot_controller import RobotController


def main():
    print("Starting Robot Controller Application...")

    udp_comm = UDPCommunicator()
    if not udp_comm.init_sockets():
        print("Failed to initialize UDP communication. Exiting.")
        return

    # ロボット制御クラスの初期化 (configで有効化されているロボットのみ)
    # robot_id をキーとし、RobotControllerインスタンスを値とする辞書
    robot_controllers = {}
    for robot_cfg in config.ROBOTS_CONFIG:
        if robot_cfg["enabled"]:
            robot_id = robot_cfg["id"]
            # RobotControllerはrobot_idを受け取る想定
            controller = RobotController(udp_comm, robot_id)
            robot_controllers[robot_id] = controller
            print(
                f"Robot {robot_id}  Controller added.")

    if not robot_controllers:
        print("No robots enabled in config. Exiting.")
        udp_comm.close_sockets()
        return

    udp_comm.start_receiving()

    print(
        f"Entering main control loop with {len(robot_controllers)} robot controller(s).")
    try:
        while True:
            game_command_data = udp_comm.get_latest_game_command()
            if game_command_data:
                cmd_type = game_command_data.get("type")
                cmd = game_command_data.get("command")
                target_team = game_command_data.get("team_color")

                if cmd_type == "game_command":
                    if cmd in ("emergency_stop", "start_game", "stop_game"):
                        print(
                            f"'{cmd.replace('_', ' ').title()}' command received! Broadcasting to all controllers.")
                        for controller in robot_controllers.values():
                            controller.handle_game_command(game_command_data)
                    else:  # その他のコマンド (target_team が使われる想定)
                        if target_team:
                            commanded_specific_robot = False
                            for robot_id, controller_instance in robot_controllers.items():
                                # robot_id に対応する設定情報を取得
                                current_robot_cfg = next(
                                    (rcfg for rcfg in config.ROBOTS_CONFIG if rcfg["id"] == robot_id), None)
                                if not current_robot_cfg:
                                    continue

                                # ターゲット名がロボット名と一致する場合にコマンドを送信
                                if config.TEAM_COLOR == target_team:
                                    controller_instance.handle_game_command(
                                        game_command_data)
                                    commanded_specific_robot = True

                            if not commanded_specific_robot:
                                print(
                                    f"No enabled robot found with name '{target_team}' for command '{cmd}'.")
                        else:
                            print(
                                f"Received command '{cmd}' without 'robot_color' (target name) specified.")

            vision_data = udp_comm.get_latest_vision_data()
            for controller in robot_controllers.values():
                # RobotController内で自分のセンサーデータを udp_comm.get_latest_robot_sensor_data(self.robot_id) で取得想定
                controller.process_data_and_control(vision_data)

            time.sleep(config.CONTROL_LOOP_INTERVAL)

    except KeyboardInterrupt:
        print("Controller stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Shutting down...")
        udp_comm.close_sockets()  # これにより受信スレッドも停止準備が整う
        print("Application finished.")


if __name__ == "__main__":
    main()
