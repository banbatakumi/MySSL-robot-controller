import time  # 時間計測用


class PID:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = None  # 前回の更新時刻を記録

    def update(self, target, input):
        current_time = time.time()  # 現在の時刻を取得（秒単位）
        if self.last_time is None:
            # 初回呼び出し時は dt を 0 に設定
            dt = 0.0
        else:
            # 前回の時刻との差分を計算
            dt = current_time - self.last_time

        self.last_time = current_time  # 現在の時刻を次回のために記録

        # PID 制御の計算
        error = target - input
        self.integral += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0

        output = (self.Kp * error) + (self.Ki * self.integral) + \
            (self.Kd * derivative)

        self.last_error = error

        return output
