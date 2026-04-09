import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MODEL_PATH

# ─────────────────────────────────────────
#  UNMUTE.AI — Model Loader (Dual Model)
# ─────────────────────────────────────────

def load_model():
    """
    Load both static and dynamic models from model.p

    Returns:
        dict with keys:
            static_model, static_classes,
            dynamic_model, dynamic_classes,
            static_features, dynamic_features
    """

    if not os.path.exists(MODEL_PATH):
        print(f"""
❌ MODEL NOT FOUND
   Expected : {MODEL_PATH}
   Fix      : Run scripts/train_classifier.py first.
        """)
        sys.exit(1)

    if os.path.getsize(MODEL_PATH) == 0:
        print("❌ model.p is empty. Re-run training.")
        sys.exit(1)

    try:
        with open(MODEL_PATH, "rb") as f:
            data = pickle.load(f)
    except Exception as e:
        print(f"❌ Failed to load model.p: {e}")
        sys.exit(1)

    # Support old single-model format
    if "model" in data and "static_model" not in data:
        print("⚠️  Old model format detected — only static gestures available.")
        print("   Re-run train_classifier.py to enable dynamic gestures.")
        data = {
            "static_model":    data["model"],
            "static_classes":  data["classes"],
            "dynamic_model":   None,
            "dynamic_classes": [],
            "static_features": 63,
            "dynamic_features": 1890,
        }

    # Validate keys
    required = ["static_model", "static_classes", "dynamic_model",
                "dynamic_classes", "static_features", "dynamic_features"]
    for key in required:
        if key not in data:
            print(f"❌ model.p missing key: '{key}'. Re-run training.")
            sys.exit(1)

    print(f"""
╔══════════════════════════════════════════╗
║         ✅  MODEL LOADED                 ║
╠══════════════════════════════════════════╣
║  Static  : {str(data['static_classes']):<30} ║
║  Dynamic : {str(data['dynamic_classes']):<30} ║
╚══════════════════════════════════════════╝
    """)

    return data