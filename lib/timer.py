import time


class Timer:
    def __init__(self):
        self._start_time = None

    def set(self):
        self._start_time = time.time()

    def read(self):
        """経過秒数を返す。未startなら0"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def readms(self):
        """経過ミリ秒を返す。未startなら0"""
        return int(self.read() * 1000)

    def readus(self):
        """経過マイクロ秒を返す。未startなら0"""
        return int(self.read() * 1000000)
