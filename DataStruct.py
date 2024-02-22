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