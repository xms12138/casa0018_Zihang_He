# 💡 EchoLume: An Offline Voice-Controlled Adaptive Smart Lamp on the Edge

![Edge Impulse](https://img.shields.io/badge/Edge%20Impulse-Enabled-brightgreen)
![Arduino](https://img.shields.io/badge/Arduino-Nano%2033%20BLE%20Sense-00979D)
![C++](https://img.shields.io/badge/C++-Embedded-blue)
![License](https://img.shields.io/badge/License-MIT-gray)

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/05_hardware/light.jpg" width="600" alt="EchoLume in Reading State">
</p>

> **Note to Reviewers:** This repository is forked from the UCL CASA0018 module template. **All of my original work, including the full report, firmware, and model training data, is located in the [`Assessment`](./Assessment) directory.**

## 📖 About The Project

Smart lamps that respond to voice are everywhere, but the dominant pattern sends your audio off-device for cloud inference—trading user privacy and network dependency for accuracy. **EchoLume asks whether that trade is necessary for a simple four-command desk lamp.**

EchoLume is an offline, privacy-preserving smart lamp running an INT8-quantized keyword-spotting model entirely on an **Arduino Nano 33 BLE Sense (Cortex-M4F, 64 MHz)**. Audio never leaves the board. It listens for 4 distinct commands (`turn_on`, `turn_off`, `reading`, `sleep`) while actively filtering out background noise and unknown speech.

### Key Features
- **100% Offline Inference:** No Wi-Fi, no cloud processing.
- **Graceful Failure Mode:** Driven by a Finite State Machine (FSM), the lamp ignores low-confidence audio, translating "uncertainty" into a benign "no action" rather than a wrong action.
- **Resource Optimized:** Fits neatly within 256KB RAM and 1MB Flash, with custom-tuned DSP to meet real-time processing constraints.

---

## 🧭 Repository Navigation

* 📄 **[Assessment/Report](./Assessment/Report)**: The comprehensive final project report detailing problem context, datasets, and critical reflections.
* 🛠️ **[Assessment/Projects/Final_Project](./Assessment/Projects/Final_Project)**: The core technical workspace containing:
  * `arduino/`: The C++ `.ino` firmware deployment.
  * `edge_impulse/`: Exported `.zip` models and config files.
  * `experiments/`: Experiment logs and model comparisons.
  * `3D_Printer/`: CAD files for the lamp enclosure.
  * `report_figures/`: All diagrams, charts, and photos.

---

## ⚙️ System Architecture

The signal path is a highly optimized five-stage pipeline designed for the Cortex-M4F architecture. 

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/system_overview.png" width="700" alt="System Overview">
</p>

1. **Audio Capture:** The on-board MP34DT05 PDM microphone samples audio at 16 kHz mono.
2. **DSP (MFCC):** Extracts 13 cepstral coefficients. *Note: FFT length was manually aggressively tuned from 512 to 256, slashing DSP time from 416ms down to 296ms to meet real-time budgets.*
3. **1D CNN Inference:** A lightweight Convolutional Neural Network (Conv 8 -> Conv 16 -> Dense) classifies the 1-second sliding window into 6 classes.
4. **FSM Logic:** A 1-second state-lock prevents erratic flickering, ensuring smooth transitions.
5. **Actuation:** Drives a 10-pixel WS2812B RGB LED strip via the 3.3V rail.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/state_machine.png" width="460" alt="FSM Diagram">
</p>

---

## 🚀 Getting Started & Reproduction

To build and run EchoLume locally, you will need the following hardware and software.

### Hardware BOM (Bill of Materials)
- 1x Arduino Nano 33 BLE Sense
- 1x WS2812B Addressable LED Strip (10 LEDs used)
- Jumper wires and breadboard
- (Optional) 3D printed enclosure (files in `3D_Printer/`)

### Installation
1. Install the [Arduino IDE](https://www.arduino.cc/en/software).
2. Install the **Arduino Mbed OS Nano Boards** package via the Board Manager.
3. Download the custom Edge Impulse Library `.zip` from [`edge_impulse/`](./Assessment/Projects/Final_Project/edge_impulse) and install it in Arduino IDE via `Sketch -> Include Library -> Add .ZIP Library...`
4. Open the firmware sketch located at [`arduino/echolume/echolume.ino`](./Assessment/Projects/Final_Project/arduino/echolume).
5. Connect the WS2812B Data pin to **D2** on the Arduino.
6. Compile and upload to the board.

---

## 📊 Model Evaluation & Live Performance

### Architectural Trade-offs
Instead of just chasing "headline accuracy", this project rigorously evaluated the *failure modes* of different architectures:
* **Baseline (Conv 8/16 - Deployed):** Provided the safest failure mode. If it mishears `turn_on`, it defaults to "uncertain" (no action).
* **exp_wider (Conv 16/32):** Achieved slightly higher aggregate accuracy but dangerously increased confident `turn_on` -> `turn_off` misclassifications by **3.3x**. 
* **exp_dense (No Conv):** Collapsed test accuracy by 20%, proving that Convolutional layers are load-bearing for this spectro-temporal task.

### Live Real-World Testing
The baseline INT8 firmware was tested live with **100 spoken trials** in a real-world desk environment (varying distances from 0.05m to 0.5m, with occasional background music).

* **Aggregate Accuracy:** **88.0%** correct physical state transitions.
* The physical FSM's 1-second state lock successfully smoothed out frame-by-frame uncertainty, allowing the real-world recall to exceed the static Edge Impulse test-set metrics.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/04_testing/live_test_per_keyword.png" width="600" alt="Live Testing Graph">
</p>

---

## 📝 Acknowledgments
* This project was developed as part of the **CASA0018: Deep Learning for Sensor Networks** module at the Bartlett Centre for Advanced Spatial Analysis, University College London (UCL).
* Datasets utilized include self-collected samples, the MS-SNSD noisy-speech dataset, and a subset of Google Speech Commands V2.
