import os
import json

PROGRAM_VERSION = "1.0.0"

APP_PATH = os.path.dirname(os.path.realpath(__file__))

RAW = False
SNAP = False
CONFIG_EXIST = False
CONFIG_CHANGED = False

PAGE_SIZE = (595, 842)
POINT_SIZE = 10

MAGICK_NUM = 0x70616765
FILE_VERSION = 1

def getConfigs():
    with open(os.path.join(APP_PATH, "globalConfig.json"), "r") as settings:
        data = json.load(settings)
    return data
