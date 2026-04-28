# Self-drawn diagrams (mermaid sources)

These three diagrams render natively on GitHub and can be embedded into the
report by either pasting the mermaid source, or by exporting each block to PNG
via the Mermaid Live Editor (https://mermaid.live) into this same directory.

---

## 1. System overview

```mermaid
flowchart LR
    A[Onboard PDM mic<br/>MP34DT05<br/>16 kHz mono] --> B[MFCC DSP<br/>13 coef · FFT 256<br/>~296 ms / window]
    B --> C[1D CNN INT8<br/>Conv 8 → Conv 16 → Dense 6<br/>~4 ms / inference]
    C --> D{best_value<br/>≥ 0.60 ?}
    D -- no --> A
    D -- yes --> E[Finite State Machine<br/>OFF · GENERAL · READING · SLEEP<br/>1 s state lock]
    E --> F[WS2812B strip<br/>10 LEDs · D2 · 3.3 V<br/>brightness 150/255]
```

---

## 2. State machine

```mermaid
stateDiagram-v2
    direction LR
    [*] --> OFF
    OFF --> GENERAL: turn_on
    GENERAL --> READING: reading
    GENERAL --> SLEEP: sleep
    READING --> SLEEP: sleep
    SLEEP --> READING: reading
    GENERAL --> OFF: turn_off
    READING --> OFF: turn_off
    SLEEP --> OFF: turn_off

    note right of OFF
        Colour: all off
    end note
    note right of GENERAL
        Colour: ice blue (0,255,200)
    end note
    note right of READING
        Colour: pure white (255,255,255)
    end note
    note right of SLEEP
        Colour: warm orange-red (255,50,0)
    end note
```

`noise` and `unknown` predictions are silently ignored (no transition).
Predictions with `best_value < 0.60` are treated as `uncertain` and ignored.
A 1 s state lock after each accepted transition prevents a single utterance
being re-classified across multiple frames.

---

## 3. Model architecture (baseline)

```mermaid
flowchart TB
    A["Input<br/>637 features<br/>flat vector from MFCC"] --> B["Reshape<br/>13 columns<br/>(time × cepstral)"]
    B --> C["Conv1D<br/>8 filters · kernel 3 · ReLU"]
    C --> D["Dropout 0.25"]
    D --> E["Conv1D<br/>16 filters · kernel 3 · ReLU"]
    E --> F["Dropout 0.25"]
    F --> G["Flatten"]
    G --> H["Dense 6 · softmax<br/>{turn_on, turn_off, reading, sleep, noise, unknown}"]
```

INT8 quantization applied post-training. On-device estimate (Cortex-M4F):
~4 ms inference, ~12.5 KB peak RAM, ~46.4 KB flash.
