import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_loader import load_model

# ─────────────────────────────────────────
#  UNMUTE.AI — Dual Predictor
#  static_predict  → single frame (63 features)
#  dynamic_predict → 30-frame sequence (1890 features)
# ─────────────────────────────────────────

model_data      = load_model()
static_model    = model_data["static_model"]
static_classes  = model_data["static_classes"]
dynamic_model   = model_data["dynamic_model"]
dynamic_classes = model_data["dynamic_classes"]
STATIC_FEATURES  = model_data["static_features"]
DYNAMIC_FEATURES = model_data["dynamic_features"]


def predict_static(features: list):
    """Single frame prediction — for A, B, L, 1."""
    if not features or len(features) != STATIC_FEATURES:
        return "Error", 0.0
    try:
        arr   = np.array(features, dtype=np.float32).reshape(1, -1)
        if not np.isfinite(arr).all():
            return "Error", 0.0
        probs = static_model.predict_proba(arr)[0]
        idx   = int(np.argmax(probs))
        return str(static_classes[idx]), round(float(probs[idx]) * 100, 2)
    except Exception as e:
        print(f"⚠️  Static predict error: {e}")
        return "Error", 0.0


def predict_dynamic(sequence: list):
    """
    30-frame sequence prediction — for CONGRATULATIONS.
    sequence: flat list of 1890 floats (30 × 63)
    """
    if dynamic_model is None:
        return None, 0.0
    if not sequence or len(sequence) != DYNAMIC_FEATURES:
        return None, 0.0
    try:
        arr   = np.array(sequence, dtype=np.float32).reshape(1, -1)
        if not np.isfinite(arr).all():
            return None, 0.0
        probs = dynamic_model.predict_proba(arr)[0]
        idx   = int(np.argmax(probs))
        return str(dynamic_classes[idx]), round(float(probs[idx]) * 100, 2)
    except Exception as e:
        print(f"⚠️  Dynamic predict error: {e}")
        return None, 0.0