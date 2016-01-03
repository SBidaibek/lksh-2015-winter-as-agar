time_step = 0.05
INITIAL_MASS = 60

FIELD_X = 1000
FIELD_Y = 1000

WINDOW_HEIGHT = 600
WINDOW_WIDTH = 1000

MAX_LENGTH = 4096

FOOD_NUM = 500
FOOD_MASS = 5

FAIL_COUNT = 50

DEBUG_ON = False
DEBUG_OFF = False

def debug(D):
    return (D | DEBUG_ON) & (not DEBUG_OFF)

DEBUG_PROTOCOL = debug(False)
DEBUG_PROTOCOL_PRINT = debug(False)
