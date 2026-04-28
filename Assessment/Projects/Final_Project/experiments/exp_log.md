# Experiment Log

> Append-only. Each entry: date / configuration change / val acc / test acc / on-device / observation / figure paths.

---

## Entry template

```
### YYYY-MM-DD — <short title>

- **Configuration change**: <what differs from baseline>
- **Validation accuracy**: <%>
- **Test accuracy (INT8)**: <% @ threshold>
- **On-device**: inference <ms> / RAM <KB> / flash <KB> / DSP <ms>
- **Observation**: <one or two sentences>
- **Figures**: `report_figures/03_experiments/<exp_dir>/...`
```

---

## 2026-04-27 — Design decision: MFCC FFT length (autotune → manual)

- **Context**: EI Autotune suggested `FFT length = 512` for the MFCC block.
- **Issue**: with FFT 512 the DSP processing time on Cortex-M4F was estimated at **416 ms**, well above the 100 ms real-time budget for a keyword spotting loop.
- **Action**: manually reduced `FFT length` to `256`, keeping all other MFCC parameters (13 coef, frame 0.025 / stride 0.02 s, 32 filters, low_freq 80 Hz) unchanged.
- **Result**: DSP time dropped to **296 ms** (−29%). Feature explorer separability inspected visually after change — no obvious degradation.
- **Trade-off acknowledged**: 296 ms still exceeds the 100 ms target, but inference itself is only 4 ms; the dominant cost is MFCC computation, not the model. Further DSP cuts (e.g. fewer filters, shorter frame) deferred to a possible later experiment.
- **Figures**:
  - `report_figures/02_methods/mfcc_autotune_default.png` (autotune default, FFT 512, DSP 416 ms)
  - `report_figures/02_methods/mfcc_manual_tuned.png` (manual choice, FFT 256, DSP 296 ms)

---

## 2026-04-27 — Baseline (EI default 1D CNN, MFCC, INT8 + Float32)

- **Configuration**:
  - DSP: 13 MFCC coef, frame 0.025 / stride 0.02 s, FFT 256 (manually chosen, see entry above), 32 filters, low_freq 80 Hz
  - Model: EI default 1D CNN — Input 637 → Reshape (13 cols) → Conv1D 8 filters / kernel 3 → Dropout 0.25 → Conv1D 16 filters / kernel 3 → Dropout 0.25 → Flatten → Dense 6
  - Training: 200 epochs, lr 0.005, batch 32, val 20%, CPU; learned optimizer disabled; full augmentation (add noise / mask time / mask freq all Low, warp time on); profile int8 enabled
- **Validation accuracy**: 94.5% (INT8) / 95.1% (Float32) — loss 0.19 both
- **Test accuracy**: 81.95% (INT8) / 82.44% (Float32) — assumed threshold 0.6 (UNCERTAIN column visible)
- **On-device (INT8, autoreported by EI)**: inference ~4 ms / RAM ~12.5 KB / flash ~46.4 KB / DSP 296 ms
- **Per-class observation (INT8 test set)**:
  - `noise` 80% (→ unknown 14.3%, harmless)
  - `reading` 100%
  - `sleep` 90%
  - `turn_off` 76.7% (→ uncertain 13.3%, → turn_on 6.7%)
  - **`turn_on` 56.7%** (→ uncertain 26.7%, → turn_off 10%) — single worst class
  - `unknown` 86%
  - F1 ranks: reading 0.94 > sleep 0.92 > noise 0.89 > unknown 0.84 > turn_off 0.82 > **turn_on 0.69**
- **Quantization cost (free comparison)**: INT8 vs Float32 — val −0.6 pp, test −0.49 pp; turn_on confusion to turn_off jumps from 7.4% (Float32 val) to 11.1% (INT8 val) — quantization cost concentrated on the most confusable pair, not uniform.
- **Generalisation gap**: val 94.5% → test 81.95% = **−12.55 pp** (consistent with §7 limitation #4); much larger than the 0.49 pp quantization cost — generalisation, not quantization, is the bottleneck.
- **Figures**:
  - `report_figures/03_experiments/baseline/baseline_architecture.png`
  - `report_figures/03_experiments/baseline/baseline_hyperparams.png`
  - `report_figures/03_experiments/baseline/baseline_val_int8.png`
  - `report_figures/03_experiments/baseline/baseline_val_float32.png`
  - `report_figures/03_experiments/baseline/model_test_int8.png`
  - `report_figures/03_experiments/baseline/model_test_float32.png`

---

## 2026-04-28 — exp_wider (Conv 8/16 → 16/32)

- **Configuration change vs baseline**: Conv1D layer 1 filters 8 → **16**, Conv1D layer 2 filters 16 → **32**. All other MFCC / training / augmentation / training-hyperparam settings unchanged.
- **Hypothesis**: turn_on / turn_off confusion (turn_on F1 0.69 in baseline) may be capacity-bound — wider conv channels could capture finer fricative-tail differences.
- **Validation accuracy**: **96.3% (INT8, loss 0.49) / 95.7% (Float32, loss 0.21)** — note INT8 *higher* than Float32 on accuracy but with higher loss → quantization preserves argmax but lowers confidence on correctly classified samples.
- **Test accuracy**: **82.93% (INT8) / 82.93% (Float32)** @ threshold 0.6 — confusion matrices identical (argmax stable under quantization); only AUC differs (0.96 vs 0.98).
- **On-device (INT8 estimate, EI auto-reported)**: inference **7 ms** (vs baseline 4 ms, +75%) / Peak RAM **14.0 KB** (+12%) / Flash **49.4 KB** (+6%) / DSP 296 ms (unchanged). All well within MCU budgets (Cortex-M4F: 256 KB RAM, 1 MB Flash; real-time budget 100 ms). **Hardware capacity is not the bottleneck** — wider model fits comfortably; the problem with wider is purely behavioural (calibration / failure mode).
- **Per-class observation (INT8 test set, vs baseline)**:
  - `turn_on` 56.7% → **63.3%** ✅; F1 0.69 → **0.76** ✅
  - **but** `turn_on → turn_off` 10.0% → **33.3%** ❌ (×3.3) ; `turn_on → uncertain` 26.7% → 3.3%
  - `turn_off` 76.7% → 90% ✅; `turn_off → turn_on` 6.7% → 0% ✅
  - `noise` 80% → 65.7% (→ unknown 25.7%, harmless distractor confusion)
  - `sleep` 90% → 86.7%; `unknown` 86% → 90%; `reading` 100% → 100%
  - F1 ranks (worst → best): turn_on 0.76, turn_off 0.81, noise 0.79, unknown 0.83, sleep 0.91, reading 0.98
- **Quantization robustness gain (free finding)**: test-set quantization cost 0 pp (vs −0.49 pp in baseline). Wider channels provide redundancy that absorbs per-weight quantization noise; argmax stays stable under INT8.
- **Generalisation gap**: val 96.3% → test 82.93% = **−13.37 pp** (vs baseline −12.55 pp). Wider model *overfits harder*; it is not a generalisation fix.
- **Verdict (vs baseline)**: **deployment-worse despite higher headline accuracy**. The +1 pp aggregate accuracy and improved turn_on F1 hide a **3× rise in confidently-wrong turn_on→turn_off triggers** (10% → 33.3%). The wider model trades polite "uncertain → no response" failures for harmful "confident wrong action" failures. For a safety-relevant state machine, baseline is preferred. Diagnosis: turn_on/turn_off confusion is **not capacity-bound** — adding capacity worsens calibration without resolving the underlying acoustic similarity (consistent with §7 limitation #1: shared first ~800 ms of pronunciation). Likely a data problem: single-speaker, limited count.
- **Figures**:
  - `report_figures/03_experiments/exp_wider/wider_architecture.png` (Conv 16/32)
  - `report_figures/03_experiments/exp_wider/wider_hyperparams.png` (identical to baseline)
  - `report_figures/03_experiments/exp_wider/wider_val_int8.png`
  - `report_figures/03_experiments/exp_wider/wider_val_float32.png`
  - `report_figures/03_experiments/exp_wider/wider_test_int8.png`
  - `report_figures/03_experiments/exp_wider/wider_test_float32.png`

---

## 2026-04-28 — exp_dense (no Conv — sanity check)

- **Configuration change vs baseline**: removed both Conv1D + Dropout layers; replaced with Flatten → Dense 32 (ReLU) → Dense 6. All other MFCC / training / augmentation / training-hyperparam settings unchanged.
- **Hypothesis**: MFCC already extracts strong spectro-temporal features; a small dense head may approach CNN performance — testing whether convolution is actually pulling weight here.
- **Validation accuracy**: **75.0% (INT8, loss 0.86) / 75.0% (Float32, loss 0.69)** — same accuracy, INT8 loss noticeably higher (confidence margin shrunk by quantization).
- **Test accuracy**: **61.95% (INT8) / 62.44% (Float32)** @ threshold 0.6 — quantization cost only −0.49 pp (INT8 vs Float32 confusion matrices nearly identical; AUC 0.93 both).
- **On-device (INT8 estimate, EI auto-reported)**: inference **1 ms** (vs baseline 4 ms, −75%) / Peak RAM **1.8 KB** (vs 12.5 KB, −86%) / Flash **34.1 KB** (vs 46.4 KB, −26%) / DSP 296 ms (unchanged). Smallest of all three models — but cheapest does not mean best.
- **Per-class observation (INT8 test set, vs baseline)**:
  - `noise` 80% → **40%** ❌ (→ uncertain 45.7%; dense model essentially blind to background noise)
  - `reading` 100% → 93.3% (still strong; phonetically distinctive)
  - `sleep` 90% → **56.7%** ❌ (→ uncertain 26.7%, → unknown 10%)
  - `turn_off` 76.7% → 83.3% ✅ (slightly better, but see turn_on below)
  - **`turn_on` 56.7% → 43.3%** ❌ (→ turn_off **23.3%** — 2.3× worse than baseline 10%; → uncertain 30%); F1 0.69 → **0.55**
  - `unknown` 86% → 60% ❌
  - F1 ranks (worst → best): noise 0.51, turn_on 0.55, sleep 0.68, unknown 0.69, turn_off 0.76, reading 0.90
- **Strange "val turn_on" inversion**: on the val set turn_on is the model's *best* class (90.5% recall). On test it collapses to 43.3% (worst). This is the largest val→test per-class swing in any experiment so far — strong evidence that turn_on/turn_off separation in dense is memorisation, not learned representation. Conv 1D's local receptive field appears to capture the "on/off" tail-frame pattern in a way that survives distribution shift; flat dense does not.
- **Generalisation gap**: val 75.0% → test 61.95% = **−13.05 pp** (vs baseline −12.55 pp, wider −13.37 pp). Gap roughly the same in absolute pp, but the *floor* dropped 20 pp — same drift, much worse starting point.
- **Verdict (vs baseline)**: **CNN justification confirmed (yes)**. Dense model loses 20 pp test accuracy and breaks two safety-relevant classes (noise blindness, turn_on collapse) for a 4× RAM saving the MCU does not need. Conv layers do real work — they are not just decorative capacity, they extract the local time-frequency features that MFCC alone leaves implicit. This is a useful negative result: it falsifies the "MFCC already does the heavy lifting" hypothesis and locks Conv1D in as a load-bearing choice for the rest of the design.
- **Figures**:
  - `report_figures/03_experiments/exp_dense/dense_architecture.png` (Reshape → Flatten → Dense 32 → Output 6)
  - `report_figures/03_experiments/exp_dense/dense_hyperparams.png` (identical to baseline)
  - `report_figures/03_experiments/exp_dense/dense_val_int8.png`
  - `report_figures/03_experiments/exp_dense/dense_val_float32.png`
  - `report_figures/03_experiments/exp_dense/dense_test_int8.png`
  - `report_figures/03_experiments/exp_dense/dense_test_float32.png`
  - `report_figures/03_experiments/exp_dense/dense_ondevice.png`
