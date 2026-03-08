# ============================================================
#  main.py — Entry point for Vision-Controlled Virtual Task Manager
# ============================================================

import sys
import time
import cv2
import pygame

from config import CAMERA_INDEX, DATA_REFRESH_INTERVAL, FIST_HOLD_DURATION
from gesture import GestureDetector
from process_mgr import get_processes, terminate_process, is_protected
from visualizer import Visualizer
from logger import log_termination


def main():
    # ---- Initialise components ----
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam. Check CAMERA_INDEX in config.py.")
        sys.exit(1)

    detector = GestureDetector()
    viz = Visualizer()

    # ---- State variables ----
    processes = []
    last_data_refresh = 0
    gesture_info = {"gesture": "none", "position": None, "landmarks": None}
    highlighted_pid = None
    fist_start_time = None      # timestamp when fist started on a highlighted proc
    fist_target_pid = None      # pid being targeted by fist hold
    process_rects = {}          # pid → pygame.Rect  (from visualizer)

    running = True

    # Prime psutil CPU counters (first call is always 0)
    _ = get_processes()

    print("Vision-Controlled Virtual Task Manager is running.")
    print("Show your open palm to the camera to begin.")
    print("Close fist over a process to terminate it.")
    print("Press ESC or close the window to quit.\n")

    while running:
        # ---- Pygame events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not running:
            break

        # ---- Capture camera frame ----
        ret, frame = cap.read()
        if not ret:
            frame = None

        # ---- Gesture detection ----
        if frame is not None:
            gesture_info = detector.detect(frame)
            # Draw landmarks on camera preview
            frame = detector.draw_landmarks(frame)

        # ---- Refresh process data (slow, throttled) ----
        now = time.time()
        if now - last_data_refresh > DATA_REFRESH_INTERVAL:
            processes = get_processes()
            last_data_refresh = now

        # ---- Hit-test: which process is the cursor over? ----
        pos = gesture_info.get("position")
        gesture = gesture_info.get("gesture", "none")
        old_highlighted = highlighted_pid
        highlighted_pid = None

        if pos and gesture != "none":
            for pid, rect in process_rects.items():
                if rect.collidepoint(pos):
                    highlighted_pid = pid
                    break

        # ---- Fist-hold termination logic ----
        if gesture == "fist" and highlighted_pid is not None:
            if fist_target_pid != highlighted_pid:
                # started fist on a new target
                fist_start_time = time.time()
                fist_target_pid = highlighted_pid
            else:
                # continuing fist on same target — check if hold complete
                if fist_start_time and (time.time() - fist_start_time) >= FIST_HOLD_DURATION:
                    _do_terminate(highlighted_pid, processes, process_rects, viz)
                    fist_start_time = None
                    fist_target_pid = None
                    highlighted_pid = None
        else:
            # reset fist hold if gesture changed or moved off target
            fist_start_time = None
            fist_target_pid = None

        # ---- Draw everything ----
        process_rects = viz.draw(
            processes, gesture_info, frame,
            fist_start_time, highlighted_pid
        )

    # ---- Cleanup ----
    detector.release()
    cap.release()
    viz.quit()
    cv2.destroyAllWindows()
    print("Application closed.")


# ------------------------------------------------------------------
def _do_terminate(pid, processes, process_rects, viz):
    """Execute the termination of a process with visual feedback."""
    proc = next((p for p in processes if p["pid"] == pid), None)
    if proc is None:
        return

    name = proc["name"]
    if is_protected(pid, name):
        viz.set_status(f"⛔ Protected process: {name}")
        return

    success, msg = terminate_process(pid, name)
    if success:
        log_termination(pid, name, msg)
        viz.set_status(f"✅ {msg}")

        # trigger crush animation
        rect = process_rects.get(pid)
        if rect:
            viz.add_crush_effect(rect, proc["color"])
    else:
        viz.set_status(f"❌ {msg}")


# ------------------------------------------------------------------
if __name__ == "__main__":
    main()
