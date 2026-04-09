import os

# config.py — replace the first two lines with:
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.p")

MAX_HANDS         = 1
MIN_DETECTION_CONF = 0.6
MIN_TRACKING_CONF  = 0.6

EXPECTED_FEATURES  = 63
DYNAMIC_FEATURES   = 1890    

CONF_THRESHOLD     = 0.75
SMOOTHING_FRAMES   = 5

FRAME_WIDTH        = 640
FRAME_HEIGHT       = 480

HOST               = "127.0.0.1"
PORT               = 8000
