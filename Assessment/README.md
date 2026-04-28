# CASA0018 DL4SN Assessment Submission

**Author:** Zihang He  
**Module:** CASA0018 Deep Learning for Sensor Networks (DL4SN)

Welcome to my final assessment repository. This folder contains all the documentation, source code, and assets for my coursework, demonstrating the process of taking machine learning out of the cloud and deploying it locally on an edge device.

The centerpiece of this submission is my final project: **EchoLume**.

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

