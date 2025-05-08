import socket
import json
import threading
import queue
import config  # config.py から設定を読み込む


class UDPCommunicator:
    """
    UDP通信の送受信を管理するクラス。
    受信は別スレッドで行い、データをキューに入れる。
    複数ロボット (黄色・青色) のセンサーデータ受信とコマンド送信に対応。
    """

    def __init__(self):
        self._vision_sock = None
        self._yellow_sensor_sock = None  # 黄色ロボット用センサーソケット
        self._blue_sensor_sock = None   # 青色ロボット用センサーソケット
        self._command_sock = None
        self._game_command_sock = None  # ゲームコマンド受信用ソケット

        self._vision_data_queue = queue.Queue()
        self._yellow_sensor_data_queue = queue.Queue()  # 黄色ロボット用キュー
        self._blue_sensor_data_queue = queue.Queue()   # 青色ロボット用キュー
        self._game_command_queue = queue.Queue()  # ゲームコマンド用キュー

        self._vision_thread = None
        self._yellow_sensor_thread = None
        self._blue_sensor_thread = None
        self._game_command_thread = None  # ゲームコマンド受信スレッド
        self._running = False  # 受信スレッド実行フラグ

    def init_sockets(self):
        """ソケットを作成し、受信ソケットをバインドする"""
        try:
            # Vision 受信用 (通常は1つ)
            self._vision_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self._vision_sock.bind(
                (config.LISTEN_IP, config.VISION_LISTEN_PORT))
            print(
                f"Vision UDP server bound to {config.LISTEN_IP}:{config.VISION_LISTEN_PORT}")

            # センサーデータ受信用 (ロボットごとにポートを分ける場合)
            if config.ENABLE_YELLOW_ROBOT:
                self._yellow_sensor_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)
                self._yellow_sensor_sock.bind(
                    (config.LISTEN_IP, config.YELLOW_SENSOR_LISTEN_PORT))
                print(
                    f"Yellow Sensor UDP server bound to {config.LISTEN_IP}:{config.YELLOW_SENSOR_LISTEN_PORT}")

            if config.ENABLE_BLUE_ROBOT:
                self._blue_sensor_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)
                self._blue_sensor_sock.bind(
                    (config.LISTEN_IP, config.BLUE_SENSOR_LISTEN_PORT))
                print(
                    f"Blue Sensor UDP server bound to {config.LISTEN_IP}:{config.BLUE_SENSOR_LISTEN_PORT}")

            # ゲームコマンド受信用
            self._game_command_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self._game_command_sock.bind(
                (config.LISTEN_IP, config.GAME_COMMAND_LISTEN_PORT))
            print(
                f"Game Command UDP server bound to {config.LISTEN_IP}:{config.GAME_COMMAND_LISTEN_PORT}")

            # コマンド送信用 (bind は不要) - 送信先はIPとポートで区別
            self._command_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Command UDP client socket created.")

            return True  # 初期化成功
        except socket.error as e:
            print(f"Failed to initialize UDP sockets: {e}")
            self.close_sockets()  # エラー時は開いたソケットを閉じる
            return False  # 初期化失敗

    def start_receiving(self):
        """受信スレッドを開始する"""
        if not self._vision_sock:
            print("Vision UDP socket not initialized. Cannot start receiving.")
            return

        self._running = True
        self._vision_thread = threading.Thread(
            target=self._vision_receiver_thread, daemon=True)
        self._vision_thread.start()
        print("Vision UDP receiver thread started.")

        if config.ENABLE_YELLOW_ROBOT and self._yellow_sensor_sock:
            self._yellow_sensor_thread = threading.Thread(
                target=self._yellow_sensor_receiver_thread, daemon=True)
            self._yellow_sensor_thread.start()
            print("Yellow Sensor UDP receiver thread started.")

        if config.ENABLE_BLUE_ROBOT and self._blue_sensor_sock:
            self._blue_sensor_thread = threading.Thread(
                target=self._blue_sensor_receiver_thread, daemon=True)
            self._blue_sensor_thread.start()
            print("Blue Sensor UDP receiver thread started.")

        if self._game_command_sock:
            self._game_command_thread = threading.Thread(
                target=self._game_command_receiver_thread, daemon=True)
            self._game_command_thread.start()
            print("Game Command UDP receiver thread started.")

    def stop_receiving(self):
        """受信スレッドに停止を指示する (daemon=True の場合は不要なことが多いが明示的に制御する場合)"""
        self._running = False
        # TODO: 必要に応じてソケットをシャットダウンするなどして recvfrom() から抜け出させる

    def _vision_receiver_thread(self):
        """Visionデータを受信するスレッド関数"""
        while self._running:
            try:
                data, addr = self._vision_sock.recvfrom(config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                vision_data = json.loads(json_string)
                # Visionデータには複数のロボット情報が含まれる想定
                self._vision_data_queue.put(vision_data)
                # print(f"Vision data received and queued from {addr}") # デバッグ用
            except socket.timeout:
                pass
            except json.JSONDecodeError:
                # print(f"Vision data: Received invalid JSON from {addr}. Skipping.")
                pass
            except Exception as e:
                if self._running:
                    print(f"Vision receiver error from {addr}: {e}")
                break

    def _yellow_sensor_receiver_thread(self):
        """黄色ロボットのSensorデータを受信するスレッド関数"""
        while self._running and self._yellow_sensor_sock:
            try:
                data, addr = self._yellow_sensor_sock.recvfrom(
                    config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                sensor_data = json.loads(json_string)
                # ロボット色をデータに追加してキューに入れる
                sensor_data['robot_color'] = 'yellow'
                self._yellow_sensor_data_queue.put(sensor_data)
                # print(f"Yellow Sensor data received and queued from {addr}") # デバッグ用
            except socket.timeout:
                pass
            except json.JSONDecodeError:
                # print(f"Yellow Sensor data: Received invalid JSON from {addr}. Skipping.")
                pass
            except Exception as e:
                if self._running:
                    print(f"Yellow Sensor receiver error from {addr}: {e}")
                break

    def _blue_sensor_receiver_thread(self):
        """青色ロボットのSensorデータを受信するスレッド関数"""
        while self._running and self._blue_sensor_sock:
            try:
                data, addr = self._blue_sensor_sock.recvfrom(
                    config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                sensor_data = json.loads(json_string)
                # ロボット色をデータに追加してキューに入れる
                sensor_data['robot_color'] = 'blue'
                self._blue_sensor_data_queue.put(sensor_data)
                # print(f"Blue Sensor data received and queued from {addr}") # デバッグ用
            except socket.timeout:
                pass
            except json.JSONDecodeError:
                # print(f"Blue Sensor data: Received invalid JSON from {addr}. Skipping.")
                pass
            except Exception as e:
                if self._running:
                    print(f"Blue Sensor receiver error from {addr}: {e}")
                break

        # ゲームコマンド受信スレッド関数
    def _game_command_receiver_thread(self):
        """ゲームコマンドデータを受信するスレッド関数"""
        while self._running and self._game_command_sock:
            try:
                data, addr = self._game_command_sock.recvfrom(
                    config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                game_command_data = json.loads(json_string)
                self._game_command_queue.put(game_command_data)
                # コマンド受信はログ出力
                print(
                    f"Game command received and queued from {addr}: {game_command_data}")
            except (socket.timeout, socket.error):
                if not self._running:
                    break
                if self._game_command_sock:
                    print(f"Game command receiver socket error: {e}")
            except json.JSONDecodeError:
                print(
                    f"Game command: Received invalid JSON from {addr}. Skipping.")
            except Exception as e:
                print(f"Game command receiver error from {addr}: {e}")

    def get_latest_vision_data(self):
        """
        キューから最新のVisionデータを全て取り出し、最後のデータを返す。
        データがない場合はNoneを返す。
        """
        latest_data = None
        # キューにあるデータを全て破棄し、最新だけを返す
        while not self._vision_data_queue.empty():
            try:
                latest_data = self._vision_data_queue.get_nowait()
            except queue.Empty:
                break  # 念のため
        return latest_data

    def get_latest_yellow_sensor_data(self):
        """
        黄色ロボットのキューから最新のSensorデータを全て取り出し、最後のデータを返す。
        データがない場合はNoneを返す。
        """
        latest_data = None
        while not self._yellow_sensor_data_queue.empty():
            try:
                latest_data = self._yellow_sensor_data_queue.get_nowait()
            except queue.Empty:
                break
        return latest_data

    def get_latest_blue_sensor_data(self):
        """
        青色ロボットのキューから最新のSensorデータを全て取り出し、最後のデータを返す。
        データがない場合はNoneを返す。
        """
        latest_data = None
        while not self._blue_sensor_data_queue.empty():
            try:
                latest_data = self._blue_sensor_data_queue.get_nowait()
            except queue.Empty:
                break
        return latest_data

    # ゲームコマンドキューから最新データを取得
    def get_latest_game_command(self):
        """キューから最新のゲームコマンドデータを全て取り出し、最後のデータを返す。データがない場合はNoneを返す。"""
        latest_data = None
        while not self._game_command_queue.empty():
            try:
                latest_data = self._game_command_queue.get_nowait()
            except queue.Empty:
                break
        return latest_data

    def send_command(self, command_data, robot_color):
        """
        指定した色のロボットにコマンドデータを送信する。
        command_data はPython辞書形式。robot_color は 'yellow' または 'blue'。
        """
        if not self._command_sock:
            # print("Command socket not initialized. Cannot send.") # 頻繁に出る場合はコメントアウト
            return

        target_ip = None
        target_port = config.COMMAND_SEND_PORT  # 送信ポートは共通とする想定

        if robot_color == 'yellow' and config.ENABLE_YELLOW_ROBOT:
            target_ip = config.YELLOW_ROBOT_IP
        elif robot_color == 'blue' and config.ENABLE_BLUE_ROBOT:
            target_ip = config.BLUE_ROBOT_IP
        else:
            # print(f"Command send skipped: Robot color '{robot_color}' is not enabled.") # 頻繁に出る場合はコメントアウト
            return  # 指定された色のロボットが無効なら送信しない

        if not target_ip:
            # print(f"Command send skipped: No IP configured for robot color '{robot_color}'.") # 頻繁に出る場合はコメントアウト
            return

        try:
            json_command = json.dumps(command_data)
            byte_command = json_command.encode('utf-8')
            self._command_sock.sendto(
                byte_command, (target_ip, target_port))
            # print(f"Sent command to {robot_color} ({target_ip}): {command_data}") # デバッグ用
        except socket.error as e:
            # print(f"Failed to send command to {robot_color} ({target_ip}): {e}") # 頻繁に出る場合はコメントアウト
            pass
        except TypeError as e:
            print(f"Error encoding command data for {robot_color}: {e}")

    def close_sockets(self):
        """全てのソケットを閉じる"""
        self._running = False  # 受信スレッドに終了を知らせる
        # TODO: recvfrom() ブロック解除のためのシャットダウン処理を追加

        if self._vision_sock:
            self._vision_sock.close()
            self._vision_sock = None
            print("Vision UDP socket closed.")
        if self._yellow_sensor_sock:
            self._yellow_sensor_sock.close()
            self._yellow_sensor_sock = None
            print("Yellow Sensor UDP socket closed.")
        if self._blue_sensor_sock:
            self._blue_sensor_sock.close()
            self._blue_sensor_sock = None
            print("Blue Sensor UDP socket closed.")
        if self._game_command_sock:
            self._game_command_sock.close()
            self._game_command_sock = None
            print("Game Command UDP socket closed.")
        if self._command_sock:
            self._command_sock.close()
            self._command_sock = None
            print("Command UDP socket closed.")

        # スレッドの終了を待つ (daemon=True なら必須ではないが、確実に終了させたい場合)
        # if self._vision_thread and self._vision_thread.is_alive(): self._vision_thread.join(timeout=1.0)
        # if self._yellow_sensor_thread and self._yellow_sensor_thread.is_alive(): self._yellow_sensor_thread.join(timeout=1.0)
        # if self._blue_sensor_thread and self._blue_sensor_thread.is_alive(): self._blue_sensor_thread.join(timeout=1.0)
