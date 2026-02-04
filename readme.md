🖥️ OS Process Monitor with Gesture-Based Interaction
📌 Project Overview

This project is a Python-based Operating System Process Monitoring and Control System that visualizes and manages running processes in real time.
It combines core OS concepts with a gesture-driven interaction layer, inspired by Virtual Reality (VR) systems, but implemented using a standard camera instead of specialized VR hardware.

The system continuously monitors CPU usage, memory consumption, and process states, and allows users to interact with OS processes using hand gestures captured via a camera.

🎯 Objectives

Monitor OS processes in real time

Observe CPU scheduling and memory usage behavior

Provide a safe user-space interface to the operating system

Enable intuitive, gesture-based process control

Demonstrate practical applications of OS concepts using modern interaction techniques

🧠 Core OS Concepts Covered

Process Management

CPU Scheduling Observation

Memory Management (Resident Set Size)

Process States (running, stopped, etc.)

User–Kernel Interaction (read-only + controlled actions)

Continuous System Monitoring

🏗️ System Architecture
+-----------------------------+
| Interaction Layer           |  (Camera-based hand gestures)
+-----------------------------+
| Visualization Layer         |  (2D / VR-inspired process space)
+-----------------------------+
| Control Layer               |  (Terminate / manage processes)
+-----------------------------+
| Monitoring Layer            |  (Continuous process sampling)
+-----------------------------+
| OS Interface Layer          |  (psutil-based OS access)
+-----------------------------+

⚙️ Current Implementation Status
✅ Step 1: OS Interface Layer

Accesses live OS process information using psutil

Retrieves:

Process ID (PID)

Process name

CPU usage

Memory usage (RSS)

Process state

Safely handles permission issues and terminated processes

✅ Step 2: Continuous Monitoring Layer

Periodically samples OS process data

Sorts processes by CPU usage

Displays real-time changes in scheduling and resource usage

Supports graceful termination using keyboard interrupt

🖐️ Gesture-Based Interaction Layer (Planned / In Progress)

The system uses camera input to track hand gestures for interacting with processes in the visualization space.

🎥 Hand Tracking Behavior

The camera tracks an open palm facing the camera

Movement tracking:

Left

Right

Up

Down

Front/back depth movement is intentionally ignored to simplify interaction

🧩 Gesture-to-Action Mapping
Gesture	Action
Open palm facing camera	Start tracking hand movement
Move palm (left/right/up/down)	Navigate across process grid
Palm reaches a process square	Process gets highlighted
Open palm → closed fist	Terminate highlighted process
Two fingers raised (peace sign ✌️)	Exit monitoring system
🔐 Safety Design

Kernel-critical processes are protected

System processes (e.g., PID 0, PID 4 on Windows) cannot be terminated

Process termination is only enabled when:

A process is explicitly highlighted

A valid fist gesture is detected

This prevents accidental or dangerous OS actions.

🧠 Design Rationale for Gesture Control

Removes dependency on VR headsets

Makes the system accessible using common hardware

Demonstrates future-ready VR interaction principles

Maintains a strong connection to OS fundamentals

Separates interaction logic from OS control logic

📁 Project Structure
os_vr_monitor/
│
├── step1_os_interface.py   # OS access & process data collection
├── step2_monitor.py        # Continuous monitoring loop
├── interaction_layer/      # Camera & gesture logic (planned)
├── visualization_layer/    # Process visualization (planned)
└── README.md

🚀 Future Enhancements

2D visualization using Pygame or PyQt

Pseudo-3D spatial process mapping

Gesture smoothing and stability filtering

Process grouping (user vs system)

Priority modification via gestures

Full VR headset support (optional)

🧪 How to Run (Current Version)

Install dependencies:

pip install psutil


Run the monitoring system:

python step2_monitor.py


Stop monitoring:

Press Ctrl + C

Or (future) show peace sign ✌️ to camera

📚 Academic Justification

This project demonstrates how traditional OS concepts can be combined with modern interaction techniques. It provides a practical, observable model of process scheduling, memory usage, and system monitoring while introducing intuitive, gesture-based control mechanisms inspired by VR systems.

🏁 Conclusion

The OS Process Monitor bridges the gap between theoretical operating system concepts and interactive system design, offering a unique, extensible platform for both learning and experimentation.