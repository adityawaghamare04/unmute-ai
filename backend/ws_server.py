import base64
import cv2
import numpy as np
import time
from collections import deque
from fastapi import WebSocket
from landmark_extractor import extract_landmarks
from predictor import predict_static, predict_dynamic
from config import CONF_THRESHOLD, SMOOTHING_FRAMES, DYNAMIC_FEATURES

# ─────────────────────────────────────────
#  UNMUTE.AI — WebSocket Server
#  Runs static + dynamic prediction
#  every frame, shows best result
# ─────────────────────────────────────────

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🟢 Client connected")

    prev_time    = time.time()
    pred_buffer  = deque(maxlen=SMOOTHING_FRAMES)
    frame_buffer = deque(maxlen=30)   # 30-frame rolling window for dynamic

    try:
        while True:
            data = await websocket.receive_text()

            # ── Decode frame ─────────────────────
            try:
                img_bytes = base64.b64decode(data)
                np_arr    = np.frombuffer(img_bytes, np.uint8)
                frame     = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            except Exception:
                continue

            if frame is None:
                continue

            # ── FPS ──────────────────────────────
            curr_time = time.time()
            fps       = round(1 / (curr_time - prev_time + 1e-6), 1)
            prev_time = curr_time

            # ── Extract landmarks ─────────────────
            landmarks = extract_landmarks(frame)

            if landmarks is None:
                pred_buffer.clear()
                frame_buffer.clear()
                await websocket.send_json({
                    "gesture":    "No Hand",
                    "confidence": 0,
                    "fps":        fps,
                    "low_conf":   False,
                    "type":       "none"
                })
                continue

            # ── Push to frame buffer ─────────────
            frame_buffer.append(landmarks)

            # ── Static prediction (every frame) ──
            static_gesture, static_conf = predict_static(landmarks)

            # ── Dynamic prediction (every 30 frames)
            dynamic_gesture, dynamic_conf = None, 0.0
            if len(frame_buffer) == 30:
                flat_sequence = []
                for frame_landmarks in frame_buffer:
                    flat_sequence.extend(frame_landmarks)
                dynamic_gesture, dynamic_conf = predict_dynamic(flat_sequence)

            # ── Pick best prediction ─────────────
            # Dynamic wins only if its confidence beats static
            if dynamic_gesture and dynamic_conf > static_conf:
                gesture    = dynamic_gesture
                confidence = dynamic_conf
                pred_type  = "dynamic"
            else:
                gesture    = static_gesture
                confidence = static_conf
                pred_type  = "static"

            # ── Smoothing (static only) ──────────
            if pred_type == "static":
                pred_buffer.append(gesture)
                gesture = max(set(pred_buffer), key=pred_buffer.count)
            else:
                pred_buffer.clear()  # reset on dynamic detection

            low_conf = confidence < (CONF_THRESHOLD * 100)

            await websocket.send_json({
                "gesture":    gesture,
                "confidence": confidence,
                "fps":        fps,
                "low_conf":   low_conf,
                "type":       pred_type
            })

    except Exception as e:
        print(f"🔴 WebSocket closed: {e}")