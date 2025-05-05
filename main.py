import time
import config  # config.py から設定を読み込む
from udp_communicator import UDPCommunicator
from robot_controller import RobotController


def main():
    """
    プログラムのエントリーポイント。
    UDP通信、ロボット制御の初期化とメインループを実行する。
    """
    print("Starting Robot Controller Application...")

    # UDP通信クラスの初期化
    udp_comm = UDPCommunicator()
    if not udp_comm.init_sockets():
        print("Failed to initialize UDP communication. Exiting.")
        return

    # ロボット制御クラスの初期化
    controller = RobotController(udp_comm)

    # 受信スレッドの開始
    udp_comm.start_receiving()

    print("Entering main control loop.")
    try:
        while True:
            # 制御ロジックの実行（データ取得、処理、指令送信）
            controller.process_data_and_control()

            # 制御ループのポーリング間隔
            time.sleep(config.CONTROL_LOOP_INTERVAL)

    except KeyboardInterrupt:
        print("Controller stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Shutting down...")
        # ソケットを閉じる
        udp_comm.close_sockets()
        # 必要であれば他のリソース解放処理を追加


if __name__ == "__main__":
    main()
