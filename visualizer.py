# ============================================================
#  visualizer.py — Pygame rendering: process grid, cursor,
#                  camera preview, kill-bar, animations
# ============================================================

import pygame
import cv2
import numpy as np
import time

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    GRID_COLS, CELL_PADDING, MIN_SQUARE_SIZE, MAX_SQUARE_SIZE,
    BG_COLOR, GRID_BG_COLOR, TEXT_COLOR, DIM_TEXT_COLOR,
    HIGHLIGHT_COLOR, KILL_BAR_COLOR, CURSOR_COLOR,
    CAM_PREVIEW_W, CAM_PREVIEW_H,
    FIST_HOLD_DURATION, STATUS_COLORS,
)


# ───────────────── helpers ──────────────────────────────────
def _lerp(a, b, t):
    return a + (b - a) * t


def _map_size(mem_mb, max_mem):
    """Map memory (MB) to square pixel size."""
    if max_mem <= 0:
        return MIN_SQUARE_SIZE
    ratio = min(mem_mb / max_mem, 1.0)
    return int(MIN_SQUARE_SIZE + ratio * (MAX_SQUARE_SIZE - MIN_SQUARE_SIZE))


def _cv2_frame_to_pygame(frame, target_w, target_h):
    """Convert an OpenCV BGR frame to a Pygame surface."""
    small = cv2.resize(frame, (target_w, target_h))
    small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    return pygame.surfarray.make_surface(np.transpose(small, (1, 0, 2)))


# ───────────────── Crush animation state ────────────────────
class _CrushEffect:
    def __init__(self, rect, color):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.start = time.time()
        self.duration = 0.45  # seconds

    @property
    def alive(self):
        return (time.time() - self.start) < self.duration

    def draw(self, surface):
        t = (time.time() - self.start) / self.duration  # 0→1
        # shrink
        w = int(self.rect.width * (1 - t))
        h = int(self.rect.height * (1 - t))
        if w < 2 or h < 2:
            return
        cx, cy = self.rect.center
        r = pygame.Rect(0, 0, w, h)
        r.center = (cx, cy)
        alpha = int(255 * (1 - t))
        col = tuple(min(c + 60, 255) for c in self.color)  # flash brighter
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((*col, alpha))
        surface.blit(s, r.topleft)


# ───────────────── Visualizer ───────────────────────────────
class Visualizer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vision-Controlled Virtual Task Manager")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font = pygame.font.SysFont("Consolas", 14)
        self.font_big = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 22, bold=True)

        # State
        self.process_rects = {}    # pid → pygame.Rect
        self.smooth_sizes = {}     # pid → current interpolated size
        self.crush_effects = []    # list of _CrushEffect
        self.status_msg = ""
        self.status_msg_time = 0

    # ----------------------------------------------------------
    #  Main draw call
    # ----------------------------------------------------------
    def draw(self, processes, gesture_info, cam_frame,
             fist_start_time, highlighted_pid):
        """Render one frame.  Returns dict of pid → Rect for hit-testing."""
        self.screen.fill(BG_COLOR)

        # ---- title bar ----
        title = self.font_title.render(
            "Vision-Controlled Virtual Task Manager", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (20, 12))

        # ---- process grid ----
        rects = self._draw_grid(processes, highlighted_pid,
                                fist_start_time)

        # ---- fist kill-charge bar ----
        if fist_start_time and highlighted_pid is not None:
            self._draw_kill_bar(fist_start_time)

        # ---- gesture cursor ----
        pos = gesture_info.get("position")
        gesture = gesture_info.get("gesture", "none")
        if pos:
            self._draw_cursor(pos, gesture)

        # ---- camera preview (bottom-left) ----
        if cam_frame is not None:
            self._draw_cam_preview(cam_frame)

        # ---- status bar ----
        self._draw_status_bar(highlighted_pid, processes, gesture)

        # ---- crush animations ----
        self.crush_effects = [e for e in self.crush_effects if e.alive]
        for e in self.crush_effects:
            e.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(FPS)

        return rects

    # ----------------------------------------------------------
    #  Grid
    # ----------------------------------------------------------
    def _draw_grid(self, processes, highlighted_pid, fist_start_time):
        rects = {}
        if not processes:
            return rects

        max_mem = max((p["memory"] for p in processes), default=1) or 1

        cell_w = (WINDOW_WIDTH - 2 * CELL_PADDING) // GRID_COLS
        cell_h = 130
        top_offset = 55  # below title

        for idx, proc in enumerate(processes):
            col = idx % GRID_COLS
            row = idx // GRID_COLS

            x = CELL_PADDING + col * cell_w
            y = top_offset + row * cell_h

            target_size = _map_size(proc["memory"], max_mem)
            pid = proc["pid"]

            # smooth interpolation
            current = self.smooth_sizes.get(pid, target_size)
            current = _lerp(current, target_size, 0.12)
            self.smooth_sizes[pid] = current
            size = int(current)

            # --- draw cell background ---
            cell_rect = pygame.Rect(x + 2, y + 2, cell_w - 4, cell_h - 4)
            pygame.draw.rect(self.screen, GRID_BG_COLOR, cell_rect,
                             border_radius=6)

            # --- draw process square (centered in cell) ---
            sq_x = x + (cell_w - size) // 2
            sq_y = y + 22 + (cell_h - 22 - size) // 2 - 5
            sq_rect = pygame.Rect(sq_x, sq_y, size, size)

            color = proc["color"]

            # highlight
            is_hl = (pid == highlighted_pid)
            if is_hl:
                # glow border
                glow = pygame.Rect(sq_x - 3, sq_y - 3, size + 6, size + 6)
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, glow,
                                 border_radius=4)

            pygame.draw.rect(self.screen, color, sq_rect, border_radius=3)

            # --- text labels ---
            name_lbl = self.font.render(proc["name"][:14], True,
                                        TEXT_COLOR if is_hl else DIM_TEXT_COLOR)
            self.screen.blit(name_lbl, (x + 6, y + 4))

            cpu_lbl = self.font.render(
                f"CPU {proc['cpu']}%  MEM {proc['memory']}MB",
                True, DIM_TEXT_COLOR)
            self.screen.blit(cpu_lbl, (x + 6, y + cell_h - 20))

            rects[pid] = sq_rect

        return rects

    # ----------------------------------------------------------
    #  Kill charge bar (top center)
    # ----------------------------------------------------------
    def _draw_kill_bar(self, fist_start_time):
        elapsed = time.time() - fist_start_time
        progress = min(elapsed / FIST_HOLD_DURATION, 1.0)
        bar_w = 300
        bar_h = 14
        bx = (WINDOW_WIDTH - bar_w) // 2
        by = 44

        # background
        pygame.draw.rect(self.screen, (60, 30, 30),
                         (bx, by, bar_w, bar_h), border_radius=7)
        # fill
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(self.screen, KILL_BAR_COLOR,
                             (bx, by, fill_w, bar_h), border_radius=7)

        lbl = self.font.render(
            f"Terminating... {int(progress * 100)}%", True, (255, 200, 200))
        self.screen.blit(lbl, (bx + bar_w + 10, by - 1))

    # ----------------------------------------------------------
    #  Gesture cursor
    # ----------------------------------------------------------
    def _draw_cursor(self, pos, gesture):
        x, y = pos
        radius = 18 if gesture == "open_palm" else 10
        col = CURSOR_COLOR if gesture == "open_palm" else KILL_BAR_COLOR

        # outer ring
        pygame.draw.circle(self.screen, col, (x, y), radius, 3)
        # small center dot
        pygame.draw.circle(self.screen, col, (x, y), 4)

        # label
        lbl = self.font.render(gesture.replace("_", " ").title(),
                               True, col)
        self.screen.blit(lbl, (x + radius + 6, y - 8))

    # ----------------------------------------------------------
    #  Camera preview  (bottom-left, with border)
    # ----------------------------------------------------------
    def _draw_cam_preview(self, frame):
        try:
            surf = _cv2_frame_to_pygame(frame, CAM_PREVIEW_W, CAM_PREVIEW_H)
            px = 10
            py = WINDOW_HEIGHT - CAM_PREVIEW_H - 10

            # border
            border = pygame.Rect(px - 2, py - 2,
                                 CAM_PREVIEW_W + 4, CAM_PREVIEW_H + 4)
            pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, border,
                             border_radius=4, width=2)

            self.screen.blit(surf, (px, py))

            cam_lbl = self.font.render("CAMERA", True, HIGHLIGHT_COLOR)
            self.screen.blit(cam_lbl, (px + 4, py - 18))
        except Exception:
            pass  # skip if frame conversion fails

    # ----------------------------------------------------------
    #  Status bar  (bottom)
    # ----------------------------------------------------------
    def _draw_status_bar(self, highlighted_pid, processes, gesture):
        bar_y = WINDOW_HEIGHT - 32
        pygame.draw.rect(self.screen, (30, 30, 40),
                         (0, bar_y, WINDOW_WIDTH, 32))

        parts = []
        if highlighted_pid is not None:
            proc = next((p for p in processes if p["pid"] == highlighted_pid), None)
            if proc:
                parts.append(
                    f"Selected: {proc['name']} (PID {proc['pid']})  "
                    f"CPU {proc['cpu']}%  MEM {proc['memory']}MB  "
                    f"Status: {proc['status']}")

        if gesture != "none":
            parts.append(f"Gesture: {gesture.replace('_',' ').title()}")

        # Show status message if recent
        if self.status_msg and (time.time() - self.status_msg_time) < 3.0:
            parts.append(self.status_msg)

        text = "   |   ".join(parts) if parts else "Show open palm to start tracking"
        lbl = self.font.render(text, True, TEXT_COLOR)
        self.screen.blit(lbl, (CAM_PREVIEW_W + 30, bar_y + 8))

    # ----------------------------------------------------------
    #  Public helpers
    # ----------------------------------------------------------
    def add_crush_effect(self, rect, color):
        self.crush_effects.append(_CrushEffect(rect, color))

    def set_status(self, msg):
        self.status_msg = msg
        self.status_msg_time = time.time()

    def quit(self):
        pygame.quit()
