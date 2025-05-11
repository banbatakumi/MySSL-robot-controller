import socket
import json
import threading
import queue
import config  # config.py から設定を読み込む


class UDPCommunicator:
    """
    UDP通信の送受信を管理するクラス。
    受信は別スレッドで行い、データをキューに入れる。
    設定に基づいて複数のロボットのセンサーデータ受信とコマンド送信に対応。
    """

    def __init__(self):
        self._vision_sock = None
        self._game_command_sock = None
        self._command_sock = None  # コマンド送信用

        # ロボットごとのセンサーソケット、キュー、スレッドを辞書で管理
        # キーはロボットID (config.ROBOTS_CONFIG の "id")
        self._robot_sensor_socks = {}
        self._robot_sensor_data_queues = {}
        self._robot_sensor_threads = {}

        self._vision_data_queue = queue.Queue()
        self._game_command_queue = queue.Queue()

        self._vision_thread = None
        self._game_command_thread = None
        self._running = False  # 受信スレッド実行フラグ

    def init_sockets(self):
        """ソケットを作成し、受信ソケットをバインドする"""
        try:
            # Vision 受信用
            self._vision_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self._vision_sock.bind(
                (config.LISTEN_IP, config.VISION_LISTEN_PORT))
            self._vision_sock.settimeout(config.SOCKET_TIMEOUT)  # タイムアウト設定
            print(
                f"Vision UDP server bound to {config.LISTEN_IP}:{config.VISION_LISTEN_PORT}")

            # ゲームコマンド受信用
            self._game_command_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self._game_command_sock.bind(
                (config.LISTEN_IP, config.GAME_COMMAND_LISTEN_PORT))
            self._game_command_sock.settimeout(
                config.SOCKET_TIMEOUT)  # タイムアウト設定
            print(
                f"Game Command UDP server bound to {config.LISTEN_IP}:{config.GAME_COMMAND_LISTEN_PORT}")

            # ロボットセンサーデータ受信用 (config.ROBOTS_CONFIG に基づく)
            for robot_cfg in config.ROBOTS_CONFIG:
                if robot_cfg["enabled"]:
                    robot_id = robot_cfg["id"]
                    listen_port = robot_cfg["listen_port"]

                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.bind((config.LISTEN_IP, listen_port))
                    sock.settimeout(config.SOCKET_TIMEOUT)  # タイムアウト設定

                    self._robot_sensor_socks[robot_id] = sock
                    self._robot_sensor_data_queues[robot_id] = queue.Queue()
                    print(
                        f"Robot {robot_id}  Sensor UDP server bound to {config.LISTEN_IP}:{listen_port}")

            # コマンド送信用 (bind は不要)
            self._command_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Command UDP client socket created.")

            return True
        except socket.error as e:
            print(f"Failed to initialize UDP sockets: {e}")
            self.close_sockets()
            return False

    def start_receiving(self):
        """受信スレッドを開始する"""
        if not self._vision_sock or not self._game_command_sock:
            print(
                "Core UDP sockets (Vision/GameCommand) not initialized. Cannot start receiving.")
            return

        self._running = True

        self._vision_thread = threading.Thread(
            target=self._vision_receiver_thread, daemon=True)
        self._vision_thread.start()
        print("Vision UDP receiver thread started.")

        self._game_command_thread = threading.Thread(
            target=self._game_command_receiver_thread, daemon=True)
        self._game_command_thread.start()
        print("Game Command UDP receiver thread started.")

        # ロボットセンサー受信スレッド
        for robot_id, sock in self._robot_sensor_socks.items():
            robot_cfg = next(
                # name取得用
                (rc for rc in config.ROBOTS_CONFIG if rc["id"] == robot_id), None)
            thread = threading.Thread(
                target=self._robot_sensor_receiver_thread, args=(robot_id, sock), daemon=True)
            self._robot_sensor_threads[robot_id] = thread
            thread.start()
            print(
                f"Robot {robot_id}  Sensor UDP receiver thread started.")

    def stop_receiving(self):
        """受信スレッドに停止を指示する"""
        self._running = False
        # daemon=True なのでメインスレッド終了時に自動停止するが、
        # 明示的にjoinする場合は、ソケットclose後にjoinする
        # (close_sockets内でソケットを閉じるとrecvfromがエラーで抜けるため)

    def _vision_receiver_thread(self):
        while self._running:
            try:
                data, addr = self._vision_sock.recvfrom(config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                vision_data = json.loads(json_string)
                self._vision_data_queue.put(vision_data)
            except socket.timeout:
                continue  # _running フラグをチェックするためにタイムアウトは正常
            except json.JSONDecodeError:
                # print(f"Vision data: Received invalid JSON from {addr}. Skipping.")
                pass
            except Exception as e:
                if self._running:  # _runningがFalseなら、ソケットクローズによるエラーの可能性
                    print(f"Vision receiver error: {e}")
                break

    def _robot_sensor_receiver_thread(self, robot_id, sock):
        """指定されたロボットIDのセンサーデータを受信する汎用スレッド関数"""
        while self._running:
            try:
                data, addr = sock.recvfrom(config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                sensor_data = json.loads(json_string)
                sensor_data['robot_id'] = robot_id  # どのロボットからのデータかIDを付与
                if robot_id in self._robot_sensor_data_queues:
                    self._robot_sensor_data_queues[robot_id].put(sensor_data)
            except socket.timeout:
                continue
            except json.JSONDecodeError:
                # print(f"Robot {robot_id}  Sensor data: Received invalid JSON from {addr}. Skipping.")
                pass
            except Exception as e:
                if self._running:
                    print(
                        f"Robot {robot_id}  Sensor receiver error: {e}")
                break

    def _game_command_receiver_thread(self):
        while self._running:
            try:
                data, addr = self._game_command_sock.recvfrom(
                    config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                game_command_data = json.loads(json_string)
                self._game_command_queue.put(game_command_data)
                print(
                    f"Game command received and queued from {addr}: {game_command_data}")
            except socket.timeout:
                continue
            except json.JSONDecodeError:
                print(
                    f"Game command: Received invalid JSON from {addr}. Skipping.")
            except socket.error as e:  # recvfrom でソケットが閉じられた場合など
                if self._running:
                    print(f"Game command receiver socket error: {e}")
                break
            except Exception as e:
                if self._running:
                    print(f"Game command receiver error: {e}")
                break

    def get_latest_vision_data(self):
        latest_data = None
        while not self._vision_data_queue.empty():
            try:
                latest_data = self._vision_data_queue.get_nowait()
            except queue.Empty:
                break
        return latest_data

    def get_latest_robot_sensor_data(self, robot_id):
        """指定されたロボットIDのキューから最新のSensorデータを取得する"""
        if robot_id not in self._robot_sensor_data_queues:
            return None

        q = self._robot_sensor_data_queues[robot_id]
        latest_data = None
        while not q.empty():
            try:
                latest_data = q.get_nowait()
            except queue.Empty:
                break
        return latest_data

    def get_latest_game_command(self):
        latest_data = None
        while not self._game_command_queue.empty():
            try:
                latest_data = self._game_command_queue.get_nowait()
            except queue.Empty:
                break
        return latest_data

    def send_command(self, command_data, robot_id):
        """指定したIDのロボットにコマンドデータを送信する"""
        if not self._command_sock:
            return

        robot_config = None
        for cfg in config.ROBOTS_CONFIG:
            if cfg["id"] == robot_id and cfg["enabled"]:
                robot_config = cfg
                break

        if not robot_config:
            # print(f"Command send skipped: Robot ID '{robot_id}' is not enabled or not configured.")
            return

        target_ip = robot_config["ip"]
        target_port = robot_config["send_port"]

        try:
            json_command = json.dumps(command_data)
            byte_command = json_command.encode('utf-8')
            self._command_sock.sendto(byte_command, (target_ip, target_port))
            # print(f"Sent command to Robot ID {robot_id} ({target_ip}:{target_port}): {command_data}")
        except socket.error as e:
            # print(f"Failed to send command to Robot ID {robot_id} ({target_ip}): {e}")
            pass
        except TypeError as e:
            print(f"Error encoding command data for Robot ID {robot_id}: {e}")

    def close_sockets(self):
        self._running = False  # 受信スレッドに終了を指示

        if self._vision_sock:
            self._vision_sock.close()
            self._vision_sock = None
            print("Vision UDP socket closed.")
        if self._game_command_sock:
            self._game_command_sock.close()
            self._game_command_sock = None
            print("Game Command UDP socket closed.")

        for robot_id, sock in self._robot_sensor_socks.items():
            sock.close()
            robot_cfg = next(
                (rc for rc in config.ROBOTS_CONFIG if rc["id"] == robot_id), None)
            print(f"Robot {robot_id} Sensor UDP socket closed.")
        self._robot_sensor_socks.clear()

        if self._command_sock:
            self._command_sock.close()
            self._command_sock = None
            print("Command UDP socket closed.")

        # スレッドの終了を待つ (daemon=True のため必須ではないが、クリーンシャットダウンのため)
        # join にタイムアウトを設定することを推奨
        # if self._vision_thread and self._vision_thread.is_alive(): self._vision_thread.join(timeout=config.SOCKET_TIMEOUT + 0.5)
        # if self._game_command_thread and self._game_command_thread.is_alive(): self._game_command_thread.join(timeout=config.SOCKET_TIMEOUT + 0.5)
        # for thread in self._robot_sensor_threads.values():
        #    if thread.is_alive(): thread.join(timeout=config.SOCKET_TIMEOUT + 0.5)
        # print("All receiver threads signaled to stop.")
