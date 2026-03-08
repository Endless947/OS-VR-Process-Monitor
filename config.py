# ============================================================
#  config.py — Central configuration for the Virtual Task Manager
# ============================================================

# ------------------- Window / Display -----------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# ------------------- Process Grid ---------------------------
GRID_COLS = 6
CELL_PADDING = 12
MIN_SQUARE_SIZE = 30
MAX_SQUARE_SIZE = 90

# ------------------- Data Refresh ---------------------------
DATA_REFRESH_INTERVAL = 3.0  # seconds between psutil snapshots
MAX_PROCESSES_SHOWN = 30     # cap to keep the grid readable

# ------------------- Gesture --------------------------------
GESTURE_SENSITIVITY = 0.6    # 0.0 – 1.0  (higher = more sensitive)
FIST_HOLD_DURATION = 1.0     # seconds to hold fist to confirm kill
CAMERA_INDEX = 0             # default webcam

# ---- Camera preview size (bottom-left corner) ----
CAM_PREVIEW_W = 240
CAM_PREVIEW_H = 180

# ------------------- Colors (RGB) --------------------------
BG_COLOR = (18, 18, 24)
GRID_BG_COLOR = (28, 28, 38)
TEXT_COLOR = (210, 210, 220)
DIM_TEXT_COLOR = (130, 130, 150)
HIGHLIGHT_COLOR = (100, 180, 255)
KILL_BAR_COLOR = (255, 70, 70)
CURSOR_COLOR = (0, 220, 120)

# Process status → square color
STATUS_COLORS = {
    "running": (40, 200, 100),   # green
    "sleeping": (60, 130, 200),  # blue
    "stopped": (200, 60, 60),    # red
    "zombie": (180, 60, 180),    # purple
    "idle": (100, 100, 120),     # grey
    "default": (180, 180, 60),   # yellow
}

# ------------------- Protected Processes --------------------
PROTECTED_PIDS = {0, 4}
PROTECTED_NAMES = {
    "system", "system idle process", "csrss.exe", "smss.exe",
    "wininit.exe", "services.exe", "lsass.exe", "winlogon.exe",
    "svchost.exe", "dwm.exe", "explorer.exe", "registry",
}

# ------------------- Logging --------------------------------
LOG_FILE = "terminated_log.txt"
