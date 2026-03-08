# ============================================================
#  gesture.py — MediaPipe hand tracking & gesture classification
# ============================================================

import cv2
import mediapipe as mp
from config import GESTURE_SENSITIVITY, WINDOW_WIDTH, WINDOW_HEIGHT


class GestureDetector:
    """Wraps MediaPipe Hands for single-hand gesture recognition."""

    # MediaPipe landmark indices for finger tips and their PIP joints
    FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky
    FINGER_PIPS = [6, 10, 14, 18]
    THUMB_TIP = 4
    THUMB_IP = 3

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=GESTURE_SENSITIVITY,
            min_tracking_confidence=0.5,
        )
        self.mp_draw = mp.solutions.drawing_utils

    # ----------------------------------------------------------
    def detect(self, frame):
        """
        Process a BGR frame.  Returns dict:
          gesture  : "open_palm" | "fist" | "none"
          position : (screen_x, screen_y) | None
          landmarks: list of (x, y) normalised landmarks | None
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if not result.multi_hand_landmarks:
            return {"gesture": "none", "position": None, "landmarks": None}

        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark

        # --- finger state (up / down) ---
        fingers_up = self._fingers_up(lm)

        # Classify gesture
        if sum(fingers_up) >= 4:
            gesture = "open_palm"
        elif sum(fingers_up) <= 1:
            gesture = "fist"
        else:
            gesture = "none"

        # Map wrist (landmark 9 = middle finger MCP is more stable) to screen
        cx = lm[9].x   # 0..1  (left of camera image → right of screen)
        cy = lm[9].y   # 0..1

        # Mirror X so moving hand right moves cursor right on screen
        screen_x = int((1 - cx) * WINDOW_WIDTH)
        screen_y = int(cy * WINDOW_HEIGHT)

        return {
            "gesture": gesture,
            "position": (screen_x, screen_y),
            "landmarks": [(l.x, l.y) for l in lm],
        }

    # ----------------------------------------------------------
    def draw_landmarks(self, frame, landmarks_list=None):
        """Optionally draw landmarks on the raw camera frame."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        if result.multi_hand_landmarks:
            for hlm in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hlm, self.mp_hands.HAND_CONNECTIONS)
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
        self.hands.close()
