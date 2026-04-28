# EchoLume: An Offline Voice-Controlled Adaptive Smart Lamp on the Edge

**Zihang He** &nbsp;·&nbsp; [GitHub](https://github.com/xms12138/casa0018_Zihang_He/tree/main/Assessment) &nbsp;·&nbsp; [Edge Impulse public project](https://studio.edgeimpulse.com/public/973891/latest)

## Introduction

Smart lamps that respond to voice are now everywhere, but the dominant pattern — Alexa, Google Home and similar — sends audio off-device for cloud inference, trading user privacy and a working internet connection for accuracy. EchoLume asks whether that trade is necessary for a four-command desk lamp.

EchoLume is an offline, privacy-preserving smart lamp running an INT8-quantised keyword-spotting model entirely on an Arduino Nano 33 BLE Sense (Cortex-M4F, 64 MHz). Audio never leaves the board: the on-board PDM microphone captures speech, an MFCC front-end and a 1D CNN classify it, and a finite state machine drives a WS2812B addressable LED strip. Four control words — `turn_on`, `turn_off`, `reading`, `sleep` — switch the lamp between ambient, reading and rest scenes; two distractor classes (`noise`, `unknown`) absorb non-target sounds.

The implementation builds on Warden's _Speech Commands_ dataset (Warden, 2018) and the _Hello Edge_ line of micro-controller keyword spotting (Zhang et al., 2017), with Edge Impulse as the training-and-export harness. The contribution this report documents is not a novel architecture but a structured exploration of the design space — what stays in budget, what improves the failure mode, and what does not.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/05_hardware/front.jpg" width="330">
</p>

_Figure 1. EchoLume on a desk._

## Research Question

Can a sub-50 KB INT8 keyword-spotting model deployed on a Cortex-M4F microcontroller deliver reliable, fully offline voice control of an addressable RGB lamp under realistic desk-use conditions?

## Application Overview

The signal path is a five-stage pipeline (Figure 2). The on-board MP34DT05 PDM microphone samples at 16 kHz mono. An MFCC block produces a 637-feature vector per 1 s sliding window — 13 cepstral coefficients across roughly 49 frames — which is reshaped to a 13-column matrix and fed to a 1D CNN exported as INT8 from Edge Impulse. The classifier outputs a softmax over six classes; predictions whose top-1 probability falls below 0.60 are treated as `uncertain` and ignored.

Above the classifier sits a finite state machine (Figure 3) that converts the keyword stream into a lamp scene. Four lamp states (OFF, GENERAL, READING, SLEEP) are linked by legal transitions: `turn_on` is honoured only from OFF, `turn_off` from any non-OFF state, and `reading` and `sleep` toggle scenes within the on-states. A 1 s state-lock prevents a single utterance being re-classified across consecutive frames. The LED strip (10 WS2812B pixels driven from the Nano's 3.3 V rail on D2) renders the active state as ice-blue, white or warm orange-red.

This separation matters: the FSM lets the system fail gracefully. If the classifier returns a low-confidence prediction, the FSM drops it; if it returns an illegal one (e.g. `sleep` while OFF), the FSM ignores it. Failures collapse into "no action" rather than "wrong action".

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/system_overview.png" width="720">
</p>

_Figure 2. EchoLume signal-path overview._

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/state_machine.png" width="460">
</p>

_Figure 3. Lamp state machine (threshold 0.60, 1 s state lock). `noise`, `unknown` and sub-threshold predictions are ignored._

## Data

The dataset comprises 1,025 one-second utterances across six classes (Figure 4). The four action classes (`turn_on`, `turn_off`, `reading`, `sleep`) are 150 self-recorded samples each, captured on the same Nano 33 BLE Sense microphone the system later runs inference on, removing one source of acoustic distribution shift between training and deployment.

Two distractor classes back the action vocabulary against a noisy environment. `noise` (175 samples) is drawn from the MS-SNSD noisy-speech dataset (Reddy et al., 2019) via Edge Impulse's public datasets. `unknown` (250 samples) is a balanced subset of Google Speech Commands V2 (Warden, 2018) with the four target words filtered out. The 80/20 train/test split is applied uniformly; Edge Impulse subdivides 20 % of training for validation during model fitting.

The action classes are balanced and the distractor classes deliberately oversampled, on the heuristic that a keyword spotter's ability to _not_ fire matters as much as its ability to fire. The single largest known limitation is that all 600 action samples come from one primary speaker — a generalisation risk addressed in _Results_.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/01_data/class_distribution.png" width="620">
</p>

_Figure 4. Dataset class distribution (n = 1,025)._

## Model

The baseline model is the Edge Impulse default 1D CNN (Figure 5): two stacked Conv1D blocks (8 and 16 filters, kernel 3, ReLU, each followed by 25 % dropout), a Flatten, and a six-way softmax. Reshaping the 637-feature input to 13 columns gives the convolutions the time × cepstral structure they need to learn local spectro-temporal patterns; the modest filter count keeps INT8 weights well under the Nano's 1 MB flash and 256 KB RAM.

The DSP block was the first non-trivial design decision. Edge Impulse's autotune recommended an FFT length of 512, which produced a per-window DSP cost of 416 ms on the Cortex-M4F — over four times the 100 ms real-time budget for a keyword loop. Manually reducing the FFT length to 256 cut DSP to 296 ms (−29 %) with no visible loss of separability in the feature explorer. Inference itself remains 4 ms; DSP is the dominant cost, and the choice is a deliberate trade between window-rate latency and frequency resolution.

Training used 200 epochs, learning rate 0.005, batch 32, with the Edge Impulse augmentation stack at "Low" intensity (additive noise, time and frequency masking, time warp). Quantisation is post-training INT8.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/02_methods/model_architecture.png" width="380">
</p>

_Figure 5. Baseline 1D CNN architecture._

## Experiments

Three architectures were compared on the same DSP, augmentation and training schedule. The goal was not to chase headline accuracy, but to test which architectural choices are load-bearing for this data and which are decorative.

**Baseline (Conv 8/16).** Validation 94.5 % INT8 (95.1 % Float32); test 81.95 % INT8 at threshold 0.6 (82.44 % Float32). The val→test gap of −12.55 pp is far larger than the −0.49 pp INT8 quantisation cost — generalisation, not quantisation, is the bottleneck. Per-class F1 ranks `reading` 0.94, `sleep` 0.92, `noise` 0.89, `unknown` 0.84, `turn_off` 0.82, `turn_on` 0.69. The `turn_on`/`turn_off` pair is the structural weak spot: the two utterances share their first ~800 ms; only the trailing fricative differs. On-device profile: 4 ms inference, 12.5 KB RAM, 46.4 KB flash.

**exp_wider (Conv 16/32).** Doubling the convolutional channels was hypothesised to capture finer fricative-tail differences. Headline metrics improved (val 96.3 % INT8, test 82.93 %, `turn_on` F1 → 0.76), but the per-class breakdown reveals a worse failure mode: `turn_on → turn_off` confusion rose from 10 % to 33 % (×3.3). The wider model trades polite "uncertain → no response" failures for confident "wrong-action" failures — a regression for a state-machine application. Capacity is not the bottleneck; calibration is.

**exp_dense (no Conv).** Replacing both Conv1D blocks with a single Dense 32 head tested whether MFCC features alone make the convolutions redundant. They do not: test accuracy collapses to 61.95 % (−20 pp), `noise` to 40 %, `turn_on` to 43 %. The dense head memorises validation patterns (its `turn_on` validation recall is 90 %) but does not generalise. Convolutions do real work even at this scale, and the experiment locks Conv1D in as load-bearing for the rest of the design.

| Metric                | baseline | exp_wider           | exp_dense                     |
| --------------------- | -------- | ------------------- | ----------------------------- |
| Val acc (INT8)        | 94.5 %   | **96.3 %**          | 75.0 %                        |
| Test acc @ 0.6 (INT8) | 81.95 %  | **82.93 %**         | 61.95 %                       |
| `turn_on` F1          | 0.69     | 0.76                | 0.55                          |
| `turn_on → turn_off`  | 10 %     | **33 %**            | 23 %                          |
| Inference (ms)        | 4        | 7                   | 1                             |
| Peak RAM (KB)         | 12.5     | 14.0                | 1.8                           |
| Flash (KB)            | 46.4     | 49.4                | 34.1                          |
| Verdict               | shipped  | unsafe failure mode | confirms Conv is load-bearing |

_Table 1. Cross-experiment summary (INT8 unless noted)._

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/03_experiments/baseline/model_test_int8.png" width="660">
</p>

_Figure 6. Baseline INT8 test-set confusion matrix (threshold 0.6)._

## Results and Observations

The shipped firmware uses the baseline INT8 model. A live-testing session of 100 trials (4 keywords × 25 trials, threshold 0.6, 1 s state lock) was conducted as a real-world check. Eighty trials were performed by the author and twenty by an additional speaker (m, 23, no prior exposure); mouth-to-mic distance varied 0.05–0.5 m, with half the trials run with light background music playing. A trial counted as correct only if the LED strip transitioned to the intended state.

The aggregate result was **88/100 = 88.0 %** correct transitions — author 71/80, helper 17/20. The per-keyword breakdown shown in Figure 7 (24/25 `reading`, 24/25 `sleep`, 22/25 `turn_off`, 18/25 `turn_on`) is approximate: per-trial outcomes were not logged at the time, so the integer split across keywords is reconstructed from in-session observations and is consistent with the baseline EI test-set ranking. Aggregates and qualitative ranking are exact.

Two findings stood out. First, live recall exceeded EI test-set recall on every keyword (Figure 8). The likely explanations are speaker overlap with training data, and the more lenient FSM-level criterion: the state-lock collapses many uncertain frames into a benign no-action rather than an explicit miss. Second, the dominant failure mode was no-response on `turn_on`, never wrong-state on `turn_on` — exactly the pattern predicted by the baseline confusion matrix. A separate failure mode appeared during the helper session: 1–2 false triggers caused by a bystander speaking nearby. These were not counted in the 12 listed failures because they were not logged at the time, but they are worth flagging as a real-world weakness.

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/04_testing/live_test_per_keyword.png" width="660">
</p>

_Figure 7. Live-testing results per keyword (n = 25 each)._

<p align="center">
  <img src="https://raw.githubusercontent.com/xms12138/casa0018_Zihang_He/main/Assessment/Projects/Final_Project/report_figures/04_testing/live_test_vs_ei.png" width="660">
</p>

_Figure 8. Live test versus Edge Impulse test-set recall, per keyword._

**Limitations.** Three structural weaknesses are visible in the data above. (1) `turn_on` and `turn_off` share their leading 800 ms, leaving the model dependent on the trailing fricative — the worst class in every experiment. (2) The −12.55 pp val→test gap reflects a real distribution shift, almost certainly tied to (3) the dataset being recorded by a single primary speaker. Two further issues warrant brief mention: the 296 ms DSP cost still exceeds the 100 ms real-time budget but does not break functionality, since inference itself is only 4 ms; and the confidence threshold trades coverage for safety — 0.5 raises recall but lifts wrong-state errors, while 0.6 is the conservative pick. The bystander false-trigger mode points to a missing capability: without a wake-word gate or voice-activity threshold, sub-threshold utterances from the environment can still nudge state.

**What would I do next.** A multi-speaker re-recording of the action classes would directly attack the val→test gap. A wake-word stage (e.g. "EchoLume, …") would suppress bystander triggers. A small depthwise-separable variant of the Conv1D backbone is a candidate that keeps the Cortex-M4F budget within reach while improving calibration on the `turn_on`/`turn_off` boundary.

## Bibliography

1. Reddy, C. K. A., Beyrami, E., Pool, J., Cutler, R., Srinivasan, S., & Gehrke, J. (2019). _A Scalable Noisy Speech Dataset and Online Subjective Test Framework._ Interspeech 2019. https://arxiv.org/abs/1909.08050
2. Warden, P. (2018). _Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition._ arXiv:1804.03209. https://arxiv.org/abs/1804.03209
3. Zhang, Y., Suda, N., Lai, L., & Chandra, V. (2017). _Hello Edge: Keyword Spotting on Microcontrollers._ arXiv:1711.07128. https://arxiv.org/abs/1711.07128

---

## Declaration of Authorship

I, Zihang He, confirm that the work presented in this assessment is my own. Where information has been derived from other sources, I confirm that this has been indicated in the work.

_Zihang He_

2026-04-28

Word count: 1648 (body text only — title, captions, tables, bibliography and declaration excluded).
