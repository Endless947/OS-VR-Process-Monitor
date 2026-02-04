# 🖥️ OS Process Monitor with Gesture-Based Interaction

## 📌 Project Overview

This project is a **Python-based Operating System Process Monitoring and Control System** that visualizes and manages running processes in real time.

It combines core OS concepts with a **gesture-driven interaction layer**, inspired by Virtual Reality (VR) systems, but implemented using a **standard camera instead of specialized VR hardware**.

The system continuously monitors **CPU usage, memory consumption, and process states**, and allows users to interact with OS processes using **hand gestures captured via a camera**.

---

## 🎯 Objectives

- Monitor OS processes in real time  
- Observe CPU scheduling and memory usage behavior  
- Provide a safe user-space interface to the operating system  
- Enable intuitive, gesture-based process control  
- Demonstrate practical applications of OS concepts using modern interaction techniques  

---

## 🧠 Core OS Concepts Covered

- Process Management  
- CPU Scheduling Observation  
- Memory Management (Resident Set Size)  
- Process States (running, stopped, etc.)  
- User–Kernel Interaction (read-only + controlled actions)  
- Continuous System Monitoring  

---

## 🏗️ System Architecture

```
+-----------------------------+
| Interaction Layer | Camera-based hand gestures
+-----------------------------+
| Visualization Layer | 2D / VR-inspired process space
+-----------------------------+
| Control Layer | Terminate / manage processes
+-----------------------------+
| Monitoring Layer | Continuous process sampling
+-----------------------------+
| OS Interface Layer | psutil-based OS access
+-----------------------------+
```

---

## ⚙️ Current Implementation Status

### ✅ Step 1: OS Interface Layer

- Accesses live OS process information using `psutil`
- Retrieves:
  - Process ID (PID)
  - Process name
  - CPU usage
  - Memory usage (RSS)
  - Process state

### ✅ Step 2: Continuous Monitoring Layer

- Periodically samples OS process data  
- Sorts processes by CPU usage  
- Displays real-time scheduling behavior  
- Supports graceful termination  

---

## 🖐️ Gesture-Based Interaction Layer (Planned)

### 🎥 Hand Tracking Behavior

- Open palm facing camera → tracking starts  
- Hand movement tracked in:
  - Left
  - Right
  - Up
  - Down  
- Front/back depth movement is intentionally ignored  

---

### 🧩 Gesture-to-Action Mapping

| Gesture | Action |
|------|------|
| Open palm facing camera | Start tracking hand movement |
| Move palm | Navigate process grid |
| Palm over process square | Highlight process |
| Open palm → closed fist | Terminate highlighted process |
| Two fingers raised (✌️) | Exit monitoring system |

---

## 🔐 Safety Design

- Kernel-critical processes are protected  
- System processes cannot be terminated  
- Process termination only occurs after explicit gesture confirmation  

---

## 📁 Project Structure

```
os_monitor/
├── systeminfo.py
├── monitor.py
└── README.md
```

---

## 🧪 How to Run

```bash
pip install psutil
python monitor.py
```

To stop monitoring, press `Ctrl + C`

(Future) Show ✌️ gesture to camera

---

## 📚 Academic Justification

This project demonstrates how operating system concepts can be integrated with modern interaction techniques, providing a practical, observable system for understanding process scheduling, memory usage, and system monitoring.

---

## 🏁 Conclusion

The OS Process Monitor bridges the gap between theoretical OS concepts and interactive system design, offering a future-ready, extensible platform for experimentation.
