import sys
import time


class ScanProgressBar:
    """터미널 인라인 프로그레스바 (초기 스캔용)"""

    BAR_WIDTH = 35

    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self._last_render_len = 0

    def update(self, filename: str = ""):
        self.current += 1
        self._render(filename)

    def _render(self, filename: str = ""):
        if self.total == 0:
            return
        pct = min(self.current / self.total, 1.0)
        filled = int(self.BAR_WIDTH * pct)
        bar = "█" * filled + "░" * (self.BAR_WIDTH - filled)

        name = filename[-28:] if len(filename) > 28 else filename
        line = f"\r  [{bar}] {self.current}/{self.total} ({pct:.0%})  {name}"

        # 이전 줄보다 짧으면 공백으로 덮어씀
        padding = max(self._last_render_len - len(line), 0)
        sys.stdout.write(line + " " * padding)
        sys.stdout.flush()
        self._last_render_len = len(line)

    def finish(self):
        elapsed = time.time() - self.start_time
        clear = "\r" + " " * (self._last_render_len + 2) + "\r"
        sys.stdout.write(clear)
        sys.stdout.flush()
        return elapsed
