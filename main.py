import time
import params
import config  # config.py から設定を読み込む
from lib.udp_communicator import UDPCommunicator  # libフォルダにあると仮定
from control.robot_controller import RobotController
from strategy.strategy_maneger import StrategyManager


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

    # StrategyManagerを初期化
    strategy_mgr = StrategyManager(robot_controllers)
    print(
        f"StrategyManager initialized with {len(robot_controllers)} robot(s).")

    udp_comm.start_receiving()

    print("Entering main control loop...")
    try:
        while True:
            # 1. ゲームコマンドの処理
            game_command_data = udp_comm.get_latest_game_command()
            if game_command_data:
                strategy_mgr.handle_game_command(game_command_data)

            # 1.1 GUIからのコマンド処理 (StrategyManagerで処理)
            gui_command_data = udp_comm.get_latest_gui_command()
            if gui_command_data:
                strategy_mgr.handle_gui_command(gui_command_data)
                print(
                    f"[Main Loop] GUI command processed: {gui_command_data}")

            # 2. Visionデータの取得と戦略に基づく制御
            vision_data = udp_comm.get_latest_vision_data()
            if not vision_data:
                continue
            # print(vision_data)

            for rc in robot_controllers.values():
                rc.process_data_and_control(vision_data)

            strategy_mgr.update_strategy_and_control(vision_data)
            # print(vision_data)

            time.sleep(params.CONTROL_LOOP_INTERVAL)

    except KeyboardInterrupt:
        print("Controller stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Shutting down...")
        for rc in robot_controllers.values():
            rc.send_stop_command()  # 終了時にロボットを停止
        udp_comm.stop_receiving()  # 受信スレッドに停止を通知
        udp_comm.close_sockets()  # これにより受信スレッドも停止準備が整う
        print("Application finished.")


if __name__ == "__main__":
    main()
