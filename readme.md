# 🖥️ Vision-Controlled Virtual Task Manager

## 📌 Overview

A **camera-based gesture-controlled virtual task manager** that lets you visualize and manage running OS processes using hand gestures. No VR hardware needed — just a standard webcam.

Each running process is displayed as a **colored square** whose size reflects its memory usage. You interact with processes using **hand gestures** captured via your webcam through MediaPipe.

---

## 🎯 Features

- **Real-time process monitoring** — live CPU, memory, and status via `psutil`
- **Gesture-based control** — open palm to track, closed fist to terminate
- **Visual process grid** — squares sized by memory, colored by status
- **Kill confirmation** — hold fist for 1 second (charge bar) to prevent accidental kills
- **Crush animation** — shrink + fade effect when a process is terminated
- **Camera preview** — live webcam feed in the corner showing your hand
- **Protected processes** — system-critical processes cannot be terminated
- **Termination logging** — all kills logged to `terminated_log.txt`

---

## 🧩 Gesture Controls

| Gesture | Action |
|---------|--------|
| 🖐️ Open palm | Start tracking / move cursor |
| ✊ Closed fist (hold 1s) | Terminate highlighted process |
| Move hand | Navigate the process grid |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  main.py         — Entry point & loop   │
├─────────────────────────────────────────┤
│  gesture.py      — MediaPipe hand       │
│                    tracking & gestures   │
├─────────────────────────────────────────┤
│  visualizer.py   — Pygame rendering,    │
│                    grid, animations     │
├─────────────────────────────────────────┤
│  process_mgr.py  — psutil process       │
│                    collection & control │
├─────────────────────────────────────────┤
│  config.py       — All constants        │
│  logger.py       — Termination logging  │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
os_monitor/
├── main.py          ← run this
├── gesture.py       ← hand tracking (MediaPipe)
├── visualizer.py    ← Pygame GUI & animations
├── process_mgr.py   ← process data & termination
├── config.py        ← settings & constants
├── logger.py        ← termination log writer
├── README.md
├── terminated_log.txt  (auto-created)
├── SOW_*.docx
└── SRS_*.docx
```

---

## ⚙️ Requirements

- Python 3.8+
- Webcam

### Install Dependencies

```bash
pip install psutil opencv-python mediapipe pygame
```

---

## 🚀 How to Run

```bash
python main.py
```

1. The app window opens showing a grid of running processes
2. Show your **open palm** to the camera to start tracking
3. Move your hand to hover over a process square
4. **Close your fist** and hold for 1 second to terminate the process
5. Press **ESC** or close the window to exit

---

## 🔐 Safety

- Kernel and system processes (PID 0, 4, csrss, lsass, explorer, etc.) are **protected**
- Termination requires a deliberate 1-second fist hold
- Only user-owned processes can be terminated

---

## 🧠 OS Concepts Demonstrated

- Process Management & States
- CPU Scheduling Observation
- Memory Management (RSS)
- User–Kernel Space Interaction
- Continuous System Monitoring

---

## 📚 Academic Context

Prepared by **Siddharth Deulkar** | VIT, Pune | Roll No. 39 | CS-K | SY

This project demonstrates how operating system concepts can be combined with modern computer vision techniques for an interactive, gesture-based process management experience.
