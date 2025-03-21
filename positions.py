from enum import Enum

class Vertical(Enum):
    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"

    def __str__(self):
        return self.value

class Horizontal(Enum):
    UP = "UP"
    NOTHING = "NOTHING"
    DOWN = "DOWN"

    def __str__(self):
        return self.value
