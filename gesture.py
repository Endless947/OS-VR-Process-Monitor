# ============================================================
#  gesture.py — MediaPipe hand tracking & gesture classification
#  Uses the new MediaPipe Tasks API (0.10.30+)
#  Optimised: single inference per frame with result caching
# ============================================================

import os
import cv2
import mediapipe as mp

from config import GESTURE_SENSITIVITY, WINDOW_WIDTH, WINDOW_HEIGHT

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Downscale camera frames before inference for speed
_INFER_WIDTH = 320
_INFER_HEIGHT = 240


class GestureDetector:
    """Wraps MediaPipe HandLandmarker (Tasks API) for single-hand gesture recognition."""

    # MediaPipe landmark indices for finger tips and their PIP joints
    FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky
    FINGER_PIPS = [6, 10, 14, 18]
    THUMB_TIP = 4
    THUMB_IP = 3

    # Hand connection pairs for drawing
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
        (0, 5), (5, 6), (6, 7), (7, 8),        # index
        (0, 9), (9, 10), (10, 11), (11, 12),   # middle
        (0, 13), (13, 14), (14, 15), (15, 16), # ring
        (0, 17), (17, 18), (18, 19), (19, 20), # pinky
        (5, 9), (9, 13), (13, 17),              # palm
    ]

    def __init__(self):
        # Locate the .task model file next to this script
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "hand_landmarker.task")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Hand landmarker model not found at {model_path}. "
                "Download it from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            )

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=GESTURE_SENSITIVITY,
            min_tracking_confidence=0.5,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self._frame_timestamp_ms = 0
        # Cache the latest detection result so draw_landmarks can reuse it
        self._last_landmarks = None

    # ----------------------------------------------------------
    def detect(self, frame):
        """
        Process a BGR frame.  Returns dict:
          gesture  : "open_palm" | "fist" | "none"
          position : (screen_x, screen_y) | None
          landmarks: list of (x, y) normalised landmarks | None
        """
        # Downscale for faster inference
        small = cv2.resize(frame, (_INFER_WIDTH, _INFER_HEIGHT))
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Timestamps must be monotonically increasing for VIDEO mode
        self._frame_timestamp_ms += 33  # ~30 fps
        result = self.landmarker.detect_for_video(mp_image, self._frame_timestamp_ms)

        if not result.hand_landmarks:
            self._last_landmarks = None
            return {"gesture": "none", "position": None, "landmarks": None}

        hand = result.hand_landmarks[0]   # list of NormalizedLandmark
        self._last_landmarks = hand       # cache for draw_landmarks

        # --- finger state (up / down) ---
        fingers_up = self._fingers_up(hand)

        # Classify gesture
        if sum(fingers_up) >= 4:
            gesture = "open_palm"
        elif sum(fingers_up) <= 1:
            gesture = "fist"
        else:
            gesture = "none"

        # Map landmark 9 (middle finger MCP, more stable) to screen
        cx = hand[9].x   # 0..1
        cy = hand[9].y   # 0..1

        # Mirror X so moving hand right moves cursor right on screen
        screen_x = int((1 - cx) * WINDOW_WIDTH)
        screen_y = int(cy * WINDOW_HEIGHT)

        return {
            "gesture": gesture,
            "position": (screen_x, screen_y),
            "landmarks": [(l.x, l.y) for l in hand],
        }

    # ----------------------------------------------------------
    def draw_landmarks(self, frame):
        """Draw cached hand landmarks on the raw camera frame (no re-inference)."""
        if self._last_landmarks is None:
            return frame

        h, w, _ = frame.shape
        hand = self._last_landmarks

        # Draw connections
        for c0, c1 in self.HAND_CONNECTIONS:
            x1 = int(hand[c0].x * w)
            y1 = int(hand[c0].y * h)
            x2 = int(hand[c1].x * w)
            y2 = int(hand[c1].y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw landmark dots
        for lm in hand:
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

        return frame

    # ----------------------------------------------------------
    def _fingers_up(self, lm):
        """Return list of 5 booleans (thumb, index, middle, ring, pinky)."""
        fingers = []

        # Thumb — compare tip.x vs IP.x  (works for right hand facing camera)
        if lm[self.THUMB_TIP].x < lm[self.THUMB_IP].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 fingers — tip above PIP means finger is up
        for tip, pip in zip(self.FINGER_TIPS, self.FINGER_PIPS):
            if lm[tip].y < lm[pip].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    # ----------------------------------------------------------
    def release(self):
        """Clean up MediaPipe resources."""
        self.landmarker.close()
