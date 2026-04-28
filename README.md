# 💡 EchoLume: An Offline Voice-Controlled Adaptive Smart Lamp on the Edge

![Edge Impulse](https://img.shields.io/badge/Edge%20Impulse-Enabled-brightgreen)
![Arduino](https://img.shields.io/badge/Arduino-Nano%2033%20BLE%20Sense-00979D)
![TensorFlow Lite Micro](https://img.shields.io/badge/TFLite-Micro-orange)
![C++](https://img.shields.io/badge/C++-Embedded-blue)


## 📖 Overview

Smart lamps that respond to voice are everywhere, but the dominant pattern sends audio off-device for cloud inference—trading user privacy and network dependency for accuracy. **EchoLume asks whether that trade is necessary for a simple four-command desk lamp.**

EchoLume is a fully offline, privacy-preserving smart lamp running an INT8-quantised keyword-spotting model entirely on an **Arduino Nano 33 BLE Sense (Cortex-M4F, 64 MHz)**. It processes audio locally, utilizes a lightweight 1D CNN to recognize commands (`turn_on`, `turn_off`, `reading`, `sleep`), and uses a Finite State Machine (FSM) to drive an addressable LED strip.

> **Note:** This repository is forked from the UCL CASA0018 module. All of my final project code, models, and comprehensive documentation are located in the [`Assessment`](./Assessment) directory.

---

## 🛠️ Repository Navigation & Reproduction

To replicate this project or view the source files, navigate to the [`Assessment/Projects/Final_Project`](./Assessment/Projects/Final_Project) directory.

### Directory Structure

* 📄 **[`Report/`](./Assessment/Report)**: The final academic report (`report.md`) detailing problem context, datasets, and critical reflections.
* 💻 **[`arduino/`](./Assessment/Projects/Final_Project/arduino)**: The deployment firmware (`.ino`) containing the FSM and LED control logic.
* 🧠 **[`edge_impulse/`](./Assessment/Projects/Final_Project/edge_impulse)**: Exported INT8 C++ libraries from the training pipeline.
* 📊 **[`experiments/`](./Assessment/Projects/Final_Project/experiments)**: Detailed experiment logs and JSON configs.
* 🖨️ **[`3D_Printer/`](./Assessment/Projects/Final_Project/3D_Printer)**: Enclosure CAD/STL files.

### Hardware Setup

1. **Board:** Arduino Nano 33 BLE Sense
2. **Actuator:** WS2812B Addressable LED strip (Data pin wired to `D2`, powered via the 3.3V rail).
3. **Dependencies:** Install the Edge Impulse `.zip` library (found in the `edge_impulse/` folder) into your Arduino IDE.

------

## ⚙️ System Architecture

The signal path is a highly optimized five-stage pipeline designed to fit within the stringent 100 ms real-time budget and 256 KB RAM of the Cortex-M4F.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/system_overview.png" width="800" alt="System Signal Path Overview">
</p>

1. **Audio Capture:** On-board MP34DT05 PDM microphone (16 kHz mono).
2. **DSP (MFCC):** Extracts 13 cepstral coefficients per 1 s sliding window. 
   * *Engineering Decision:* EI Autotune suggested an FFT length of 512, which cost 416 ms (unusable for real-time). **I manually reduced the FFT length to 256, dropping DSP time to 296 ms (−29%)** with no visible loss of feature separability.
3. **1D CNN (INT8):** A sub-50 KB convolutional network processes the features.
4. **Finite State Machine:** A 1-second state-lock acts as a low-pass filter, preventing erratic flickering. Predictions below a 0.60 confidence threshold are safely ignored.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/state_machine.png" width="800" alt="FSM Diagram">
</p>


---

## 🔬 Experiments & Model Selection

The goal was not merely to chase headline accuracy, but to find a model that fails *safely*. Three architectures were rigorously tested.

| Metric                            | baseline (Conv 8/16)               | exp_wider (Conv 16/32)          | exp_dense (No Conv)    |
| --------------------------------- | ---------------------------------- | ------------------------------- | ---------------------- |
| **Test Acc (INT8 @ 0.6)**         | **81.95%**                         | 82.93%                          | 61.95% ❌               |
| **`turn_on` -> `turn_off` Error** | **10.0%**                          | 33.3% ❌                         | 23.3% ❌                |
| **Peak RAM (KB)**                 | 12.5                               | 14.0                            | 1.8                    |
| **Flash (KB)**                    | 46.4                               | 49.4                            | 34.1                   |
| **Inference Time (ms)**           | 4                                  | 7                               | 1                      |
| **Verdict**                       | **Deployed (Safest Failure Mode)** | Rejected (Wrong-action failure) | Rejected (Noise blind) |

### 🔍 Key Findings
* **Capacity is not the bottleneck (Wider != Better):** Doubling the convolutional channels (`exp_wider`) increased overall accuracy by +1 pp, but caused a **3.3x rise in confidently-wrong triggers** (confusing `turn_on` for `turn_off`). The baseline model politely fails into "uncertainty" (no action), making it strictly better for an FSM application.
* **Convolutions are load-bearing:** Replacing the CNN with a Dense head (`exp_dense`) collapsed accuracy by 20 pp and made the model essentially blind to background noise (40% accuracy on `noise`). 

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/03_experiments/baseline/model_test_int8.png" width="500" alt="Baseline Confusion Matrix">
  <br>
  <em>Figure: Baseline INT8 Test-Set Confusion Matrix. Note the safe concentration of errors in the UNCERTAIN column.</em>
</p>

---

## 📊 Real-World Performance (Live Testing)

The shipped baseline firmware was deployed on-device and tested via **100 live spoken trials** in a real-world desk environment (varying distances 0.05m–0.5m, with occasional background music).

* **Aggregate Correct Transitions:** **88.0%**
* Live recall actually *exceeded* the static Edge Impulse test set because the FSM's 1-second state lock successfully collapses uncertain acoustic frames into benign "no actions".

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/04_testing/live_test_per_keyword.png" width="500" alt="Live Testing per Keyword">
</p>
---
*Authored by **Zihang He** for CASA0018: Deep Learning for Sensor Networks.*
