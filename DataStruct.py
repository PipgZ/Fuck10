# data_struct.py

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def center(self):
        return int(self.x + self.w / 2), int(self.y + self.h / 2)


class OCRResult:
    def __init__(self, rect, v):
        self.rect = rect
        self.v = v


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class DragEvent:
    def __init__(self, start_x, start_y, end_x, end_y, duration_ms):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.duration_ms = duration_ms
