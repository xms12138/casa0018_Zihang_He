# CASA0018 DL4SN Assessment Submission

**Author:** Zihang He  
**Module:** CASA0018 Deep Learning for Sensor Networks (DL4SN)

Welcome to my final assessment repository. This folder contains all the documentation, source code, and assets for my coursework, demonstrating the process of taking machine learning out of the cloud and deploying it locally on an edge device.

The centerpiece of this submission is my final project: **EchoLume**.

> **Note:** For more specific details about the project, please visit the [Main Repository](https://github.com/xms12138/casa0018_Zihang_He/tree/main).

---

## 📂 Repository Structure

In accordance with the module guidelines, this assessment repository is organized into two main parts:

### 1. [Report](./Report)
This folder contains the comprehensive documentation of my final project.
* `report.md`: The final project report (approx. 1600 words) detailing the problem context, custom data collection, iterative model testing, and critical reflection.

### 2. [Projects/Final_Project](./Projects/Final_Project)
This folder acts as the technical hub for the EchoLume project. It contains all the code and assets required to replicate the physical build and the machine learning pipeline:
* **`arduino/`**: The deployment firmware in C++ for the Arduino Nano 33 BLE Sense, integrating the Edge Impulse model, the PDM microphone, and the finite state machine (FSM) for the WS2812B LEDs.
* **`edge_impulse/`**: Exported models and configuration files from the Edge Impulse platform.
* **`experiments/`**: Documentation and data analyzing the different model architectures tested (e.g., Conv 8/16 vs. Conv 16/32 vs. Dense).
* **`3D_Printer/`**: CAD files and assets used for the physical enclosure of the smart lamp.
* **`scripts/`**: Python utility scripts used during the data processing and analysis phases.
* **`report_figures/`**: All visual assets, graphs, and hardware photos used in the main report.

---

## 💡 About the Final Project: EchoLume

**EchoLume** is an offline, privacy-preserving smart lamp running an INT8-quantised keyword-spotting model entirely on an Arduino Nano 33 BLE Sense (Cortex-M4F). 

It proves that everyday smart home interactions do not strictly require cloud connectivity. The system captures speech via the on-board PDM microphone, processes it through an MFCC front-end and a lightweight 1D CNN, and drives an addressable LED strip via a finite state machine. It responds reliably to four distinct commands (`turn_on`, `turn_off`, `reading`, `sleep`) while gracefully ignoring background noise and unknown utterances.

---

## 🚀 How to Use / Getting Started

To build and run EchoLume locally, follow these hardware and software setup instructions.

### 🛠️ Hardware Requirements
* 1x **Arduino Nano 33 BLE Sense**
* 1x **WS2812B Addressable LED Strip** (10 LEDs are used in the default configuration)
* Jumper wires and a breadboard
* (Optional) 3D printed enclosure (files available in the `3D_Printer/` folder)

### 🔌 Wiring
Connect the WS2812B LED strip to the Arduino Nano 33 BLE Sense as follows:
* **LED VCC** -> Arduino **3.3V** (Make sure brightness is capped in code to avoid drawing too much current)
* **LED GND** -> Arduino **GND**
* **LED Data (DIN)** -> Arduino **D2**

### 💻 Software Setup & Installation
1. **Install Arduino IDE:** Download and install the [Arduino IDE](https://www.arduino.cc/en/software).
2. **Install Board Core:** Open the Arduino IDE, go to `Tools -> Board -> Boards Manager...`, and install the **Arduino Mbed OS Nano Boards** package.
3. **Install the Edge Impulse Library:**
   * Locate the custom Edge Impulse exported `.zip` library in this repository under `Projects/Final_Project/edge_impulse/`.
   * In the Arduino IDE, navigate to `Sketch -> Include Library -> Add .ZIP Library...` and select the `.zip` file.
4. **Flash the Firmware:**
   * Open the EchoLume firmware sketch located at `Projects/Final_Project/arduino/echolume/echolume.ino`.
   * Connect your Arduino Nano 33 BLE Sense to your computer. Select the correct Board and Port in the `Tools` menu.
   * Click **Upload**.

### 🎙️ Usage
Once the firmware is uploaded and the board is powered on:
1. The on-board PDM microphone will continuously listen to the environment.
2. Speak one of the four action keywords: **"Turn on"**, **"Turn off"**, **"Reading"**, or **"Sleep"**.
3. The LED strip will adapt to the corresponding lighting scene.
   * *Note: The Finite State Machine (FSM) incorporates a 1-second state lock to prevent erratic flickering, and it ignores audio classifications that fall below the 0.60 confidence threshold.*