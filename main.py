import time
import config  # config.py から設定を読み込む
from udp_communicator import UDPCommunicator
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
            # 各ロボットコントローラーの制御ロジックを実行
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
