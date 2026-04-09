import cv2
import mediapipe as mp
import numpy as np
from config import MAX_HANDS, MIN_DETECTION_CONF, MIN_TRACKING_CONF

# ─────────────────────────────────────────
#  UNMUTE.AI — Landmark Extractor
#  Normalization MUST match training scripts
#  Method: per-axis min-max normalization
# ─────────────────────────────────────────

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=MAX_HANDS,
    min_detection_confidence=MIN_DETECTION_CONF,
    min_tracking_confidence=MIN_TRACKING_CONF
)

def extract_landmarks(frame):
    """
    Extract and normalize 21 hand landmarks from a BGR frame.
    Returns a flat list of 63 features [x0,y0,z0, x1,y1,z1, ...]
    or None if no hand detected.
    """
    frame_flipped = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        return None

    hand = results.multi_hand_landmarks[0]

    # Collect raw coordinates
    x_ = [lm.x for lm in hand.landmark]
    y_ = [lm.y for lm in hand.landmark]
    z_ = [lm.z for lm in hand.landmark]

    # Per-axis min-max normalization — matches create_A/B/L_dataset.py exactly
    x_min, x_max = min(x_), max(x_)
    y_min, y_max = min(y_), max(y_)
    z_min, z_max = min(z_), max(z_)

    x_norm = [(v - x_min) / (x_max - x_min + 1e-6) for v in x_]
    y_norm = [(v - y_min) / (y_max - y_min + 1e-6) for v in y_]
    z_norm = [(v - z_min) / (z_max - z_min + 1e-6) for v in z_]

    # Interleave as [x0,y0,z0, x1,y1,z1, ...] — 63 features total
    features = []
    for i in range(21):
        features.extend([x_norm[i], y_norm[i], z_norm[i]])

    return features