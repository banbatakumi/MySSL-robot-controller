import time
import config  # config.py から設定を読み込む
from lib.udp_communicator import UDPCommunicator
from robot_controller import RobotController


def main():
    """
    プログラムのエントリーポイント。
    UDP通信、ロボット制御の初期化とメインループを実行する。
    複数のロボットコントローラーを管理する。
    """
    print("Starting Robot Controller Application...")

    # UDP通信クラスの初期化
    udp_comm = UDPCommunicator()
    if not udp_comm.init_sockets():
        print("Failed to initialize UDP communication. Exiting.")
        return

    # ロボット制御クラスの初期化 (configで有効化されているロボットのみ)
    controllers = []
    yellow_controller = None  # 後でゲームコマンド処理で参照するため変数として保持
    blue_controller = None   # 同様
    if config.ENABLE_YELLOW_ROBOT:
        yellow_controller = RobotController(udp_comm, 'yellow')
        controllers.append(yellow_controller)
        print("Yellow Robot Controller added.")

    if config.ENABLE_BLUE_ROBOT:
        blue_controller = RobotController(udp_comm, 'blue')
        controllers.append(blue_controller)
        print("Blue Robot Controller added.")

    if not controllers:
        print("No robots enabled in config. Exiting.")
        udp_comm.close_sockets()
        return

    # 受信スレッドの開始
    udp_comm.start_receiving()

    print(
        f"Entering main control loop with {len(controllers)} robot controller(s).")
    try:
        while True:
            game_command_data = udp_comm.get_latest_game_command()
            if game_command_data:
                # コマンドの内容に応じて処理を分岐
                cmd_type = game_command_data.get("type")
                cmd = game_command_data.get("command")
                target_robot_color = game_command_data.get("robot_color")

                if cmd_type == "game_command":
                    # print(f"Processing game command: {cmd} (Target: {target_robot_color})") # デバッグ用ログ

                    # 緊急停止は全てのロボットに伝える
                    if cmd == "emergency_stop":
                        print(
                            "Emergency Stop command received! Broadcasting to all controllers.")
                        for controller in controllers:
                            controller.handle_game_command(game_command_data)
                    elif cmd == "start_game":
                        print(
                            "Start Game command received! Broadcasting to all controllers.")
                        for controller in controllers:
                            controller.handle_game_command(game_command_data)
                    elif cmd == "stop_game":
                        print(
                            "Stop Game command received! Broadcasting to all controllers.")
                        for controller in controllers:
                            controller.handle_game_command(game_command_data)
                    else:
                        if target_robot_color in ('yellow', 'blue'):
                            if target_robot_color == 'yellow' and yellow_controller:
                                yellow_controller.handle_game_command(
                                    game_command_data)
                            elif target_robot_color == 'blue' and blue_controller:
                                blue_controller.handle_game_command(
                                    game_command_data)
                            else:
                                print(
                                    f"Target robot '{target_robot_color}' for command '{cmd}' not found or not enabled.")
                        else:
                            print(
                                f"Received command '{cmd}' without valid target_robot_color.")

            # --- 各ロボットコントローラーの制御ロジック実行 ---
            for controller in controllers:
                controller.process_data_and_control()

            # 制御ループのポーリング間隔
            time.sleep(config.CONTROL_LOOP_INTERVAL)

    except KeyboardInterrupt:
        print("Controller stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Shutting down...")
        # ソケットを閉じる (受信スレッドも停止される)
        udp_comm.close_sockets()
        print("Application finished.")
        # 必要であれば他のリソース解放処理を追加


if __name__ == "__main__":
    main()
