### [Projects/Final_Project](./Projects/Final_Project)

This folder acts as the technical hub for the EchoLume project. It contains all the code and assets required to replicate the physical build and the machine learning pipeline:

* **`arduino/`**: The deployment firmware in C++ for the Arduino Nano 33 BLE Sense, integrating the Edge Impulse model, the PDM microphone, and the finite state machine (FSM) for the WS2812B LEDs.
* **`edge_impulse/`**: Exported models and configuration files from the Edge Impulse platform.
* **`experiments/`**: Documentation and data analyzing the different model architectures tested (e.g., Conv 8/16 vs. Conv 16/32 vs. Dense).
* **`3D_Printer/`**: CAD files and assets used for the physical enclosure of the smart lamp.
* **`scripts/`**: Python utility scripts used during the data processing and analysis phases.
* **`report_figures/`**: All visual assets, graphs, and hardware photos used in the main report.
