import pygame
import sys
import time
from systeminfo import collect_process_snapshot
from normalization import normalize_process_data

# ---------------- CONFIG ----------------
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
FPS = 60

GRID_COLS = 8
CELL_PADDING = 10
MIN_SIZE = 20
MAX_SIZE = 80

DATA_REFRESH_INTERVAL = 1.5
SIZE_SMOOTHING = 0.15  # 0.1–0.2 is good

BACKGROUND_COLOR = (20, 20, 20)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT_COLOR = (255, 255, 255)

COLOR_MAP = {
    "green": (0, 200, 0),
    "red": (200, 50, 50),
    "yellow": (200, 200, 0)
}
# ----------------------------------------


def map_size(mem_norm):
    return MIN_SIZE + mem_norm * (MAX_SIZE - MIN_SIZE)


def lerp(a, b, t):
    return a + (b - a) * t


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("OS Process Visualizer (Stable Interaction)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 14)

    running = True
    last_refresh = 0

    # ---- PERSISTENT STATE ----
    process_slots = {}   # pid → slot index
    process_rects = {}   # pid → rect data
    slot_counter = 0

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_pos = pygame.mouse.get_pos()

        # ---- DATA UPDATE (SLOW) ----
        now = time.time()
        if now - last_refresh > DATA_REFRESH_INTERVAL:
            raw = collect_process_snapshot()
            processes = normalize_process_data(raw)

            for proc in processes:
                pid = proc["pid"]

                # Assign fixed slot if new process
                if pid not in process_slots:
                    process_slots[pid] = slot_counter
                    slot_counter += 1

                # Initialize rect state if needed
                if pid not in process_rects:
                    process_rects[pid] = {
                        "size": map_size(proc["mem_norm"]),
                        "target_size": map_size(proc["mem_norm"]),
                        "proc": proc
                    }
                else:
                    process_rects[pid]["target_size"] = map_size(proc["mem_norm"])
                    process_rects[pid]["proc"] = proc

            last_refresh = now

        screen.fill(BACKGROUND_COLOR)

        selected_process = None
        cell_width = WINDOW_WIDTH // GRID_COLS
        cell_height = 120

        # ---- DRAW (FAST, STABLE) ----
        for pid, slot in process_slots.items():
            if pid not in process_rects:
                continue

            data = process_rects[pid]
            proc = data["proc"]

            row = slot // GRID_COLS
            col = slot % GRID_COLS

            x = col * cell_width + CELL_PADDING
            y = row * cell_height + CELL_PADDING

            # Smooth size transition
            data["size"] = lerp(data["size"], data["target_size"], SIZE_SMOOTHING)
            size = int(data["size"])

            color = COLOR_MAP.get(proc["visual"]["color"], (150, 150, 150))

            rect = pygame.Rect(
                x + (cell_width - size) // 2,
                y + 30,
                size,
                size
            )

            pygame.draw.rect(screen, color, rect)

            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, 3)
                selected_process = proc

            name_text = font.render(proc["name"][:12], True, TEXT_COLOR)
            cpu_text = font.render(f"CPU: {proc['cpu']}%", True, TEXT_COLOR)

            screen.blit(name_text, (x, y))
            screen.blit(cpu_text, (x, y + size + 40))

        if selected_process:
            info = f"Selected: {selected_process['name']} (PID {selected_process['pid']})"
            screen.blit(font.render(info, True, (180, 180, 255)), (10, WINDOW_HEIGHT - 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
