from enum import IntEnum


class EdgeFaceEnum(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class CornerFaceEnum(IntEnum):
    UPLEFT = 0
    UPRIGHT = 1
    DOWNRIGHT = 2
    DOWNLEFT = 3
