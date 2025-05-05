import socket
import json
import threading
import queue
import config  # config.py から設定を読み込む


class UDPCommunicator:
    """
    UDP通信の送受信を管理するクラス。
    受信は別スレッドで行い、データをキューに入れる。
    """

    def __init__(self):
        self._vision_sock = None
        self._sensor_sock = None
        self._command_sock = None

        self._vision_data_queue = queue.Queue()
        self._sensor_data_queue = queue.Queue()

        self._vision_thread = None
        self._sensor_thread = None
        self._running = False  # 受信スレッド実行フラグ

    def init_sockets(self):
        """ソケットを作成し、受信ソケットをバインドする"""
        try:
            # Vision 受信用
            self._vision_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self._vision_sock.bind(
                (config.LISTEN_IP, config.VISION_LISTEN_PORT))
            # self._vision_sock.settimeout(1.0) # オプション：タイムアウト設定
            print(
                f"Vision UDP server bound to {config.LISTEN_IP}:{config.VISION_LISTEN_PORT}")

            # センサーデータ受信用
            self._sensor_sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
            self._sensor_sock.bind(
                (config.LISTEN_IP, config.SENSOR_LISTEN_PORT))
            # self._sensor_sock.settimeout(1.0) # オプション：タイムアウト設定
            print(
                f"Sensor UDP server bound to {config.LISTEN_IP}:{config.SENSOR_LISTEN_PORT}")

            # コマンド送信用 (bind は不要)
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
        if not self._vision_sock or not self._sensor_sock:
            print("UDP sockets not initialized. Cannot start receiving.")
            return

        self._running = True
        self._vision_thread = threading.Thread(
            target=self._vision_receiver_thread, daemon=True)
        self._sensor_thread = threading.Thread(
            target=self._sensor_receiver_thread, daemon=True)

        self._vision_thread.start()
        self._sensor_thread.start()
        print("UDP receiver threads started.")

    def stop_receiving(self):
        """受信スレッドに停止を指示する (daemon=True の場合は不要なことが多いが明示的に制御する場合)"""
        self._running = False
        # 必要に応じてソケットをシャットダウンするなどして recvfrom() から抜け出させる
        # 例: self._vision_sock.shutdown(socket.SHUT_RD)
        # ただし、daemonスレッドならメイン終了で一緒に終了するのが一般的

    def _vision_receiver_thread(self):
        """Visionデータを受信するスレッド関数"""
        print("Vision receiver thread started.")
        while self._running:
            try:
                data, addr = self._vision_sock.recvfrom(config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                vision_data = json.loads(json_string)
                self._vision_data_queue.put(vision_data)  # 受信データをキューに入れる
                # print(f"Vision data received and queued from {addr}") # デバッグ用
            except socket.timeout:
                pass  # タイムアウト時
            except json.JSONDecodeError:
                # print("Vision data: Received data is not valid JSON. Skipping.") # 頻繁に出る場合はコメントアウト
                pass
            except Exception as e:
                if self._running:  # running==False の場合はシャットダウン中の可能性
                    print(f"Vision receiver error: {e}")
                break  # エラー発生時はスレッド終了

    def _sensor_receiver_thread(self):
        """Sensorデータを受信するスレッド関数"""
        print("Sensor receiver thread started.")
        while self._running:
            try:
                data, addr = self._sensor_sock.recvfrom(config.BUFFER_SIZE)
                json_string = data.decode('utf-8')
                sensor_data = json.loads(json_string)
                self._sensor_data_queue.put(sensor_data)  # 受信データをキューに入れる
                # print(f"Sensor data received and queued from {addr}") # デバッグ用
            except socket.timeout:
                pass  # タイムアウト時
            except json.JSONDecodeError:
                # print("Sensor data: Received data is not valid JSON. Skipping.") # 頻繁に出る場合はコメントアウト
                pass
            except Exception as e:
                if self._running:  # running==False の場合はシャットダウン中の可能性
                    print(f"Sensor receiver error: {e}")
                break  # エラー発生時はスレッド終了

    def get_latest_vision_data(self):
        """
        キューから最新のVisionデータを全て取り出し、最後のデータを返す。
        データがない場合はNoneを返す。
        """
        latest_data = None
        while not self._vision_data_queue.empty():
            try:
                latest_data = self._vision_data_queue.get_nowait()
            except queue.Empty:
                break  # 念のため
        return latest_data

    def get_latest_sensor_data(self):
        """
        キューから最新のSensorデータを全て取り出し、最後のデータを返す。
        データがない場合はNoneを返す。
        """
        latest_data = None
        while not self._sensor_data_queue.empty():
            try:
                latest_data = self._sensor_data_queue.get_nowait()
            except queue.Empty:
                break  # 念のため
        return latest_data

    def send_command(self, command_data):
        """
        コマンドデータをESP32に送信する。
        command_data はPython辞書形式。
        """
        if not self._command_sock:
            # print("Command socket not initialized. Cannot send.") # 頻繁に出る場合はコメントアウト
            return

        try:
            json_command = json.dumps(command_data)
            byte_command = json_command.encode('utf-8')
            self._command_sock.sendto(
                byte_command, (config.ESP32_IP, config.COMMAND_SEND_PORT))
            # print(f"Sent command: {command_data}") # デバッグ用
        except socket.error as e:
            # print(f"Failed to send command to ESP32: {e}") # 頻繁に出る場合はコメントアウト
            pass
        except TypeError as e:
            print(f"Error encoding command data: {e}")

    def close_sockets(self):
        """全てのソケットを閉じる"""
        self._running = False  # 受信スレッドに終了を知らせる
        # 必要に応じてソケットをシャットダウンして recvfrom() をブロック解除する
        # try:
        #     if self._vision_sock:
        #         self._vision_sock.shutdown(socket.SHUT_RDWR)
        #     if self._sensor_sock:
        #         self._sensor_sock.shutdown(socket.SHUT_RDWR)
        # except OSError: # ソケットが既に閉じているなどの場合
        #     pass

        if self._vision_sock:
            self._vision_sock.close()
            self._vision_sock = None
            print("Vision UDP socket closed.")
        if self._sensor_sock:
            self._sensor_sock.close()
            self._sensor_sock = None
            print("Sensor UDP socket closed.")
        if self._command_sock:
            self._command_sock.close()
            self._command_sock = None
            print("Command UDP socket closed.")

        # スレッドの終了を待つ (daemon=True なら必須ではないが、確実に終了させたい場合)
        # if self._vision_thread and self._vision_thread.is_alive():
        #     self._vision_thread.join(timeout=1.0)
        # if self._sensor_thread and self._sensor_thread.is_alive():
        #      self._sensor_thread.join(timeout=1.0)
