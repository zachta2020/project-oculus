import math

class Counter:
    def __init__(self, max):
        self.current = 0
        self.max = max

    def inc(self, step=1):
        if self.current < self.max:
            self.current += step

    def reset(self):
        self.current = 0

    def __str__(self):
        digits = math.floor(math.log10(self.max)+1)
        renderedCurrent = str(self.current).zfill(digits)
        return f"({renderedCurrent}/{self.max})"