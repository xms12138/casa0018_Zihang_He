# Comparison Table

> Append new experiments as new columns. **Do not remove the baseline column.**
> All rows reflect the model under INT8 quantization unless noted. `_` = pending.

| Metric | baseline | exp_wider | exp_dense |
|---|---|---|---|
| Architecture | Conv 8 → Conv 16 → Flatten → Dense 6 | Conv **16** → Conv **32** → Flatten → Dense 6 | (no Conv) Flatten → Dense 32 → Dense 6 |
| Conv kernel | 3 | 3 | — |
| Dropout | 0.25 | 0.25 | — |
| DSP | MFCC (13 coef, frame 0.025/0.02s, FFT 256) | same | same |
| Augmentation | EI Low + warp time | same | same |
| Training | 200 ep / lr 0.005 / batch 32 / val 20% / CPU | same | same |
| **Val acc — Float32** | 95.1% | 95.7% | 75.0% |
| **Val acc — INT8** | 94.5% | **96.3%** | 75.0% |
| **Test acc — Float32** @ 0.6 | 82.44% | 82.93% | 62.44% |
| **Test acc — INT8** @ 0.6 | 81.95% | **82.93%** | **61.95%** ❌ |
| **Quantization Δ (test)** | −0.49 pp | **0 pp** ✅ | −0.49 pp |
| **Val→Test gap (INT8)** | −12.55 pp | **−13.37 pp** ⚠️ | −13.05 pp |
| Worst-class F1 (INT8 test) | turn_on 0.69 | turn_on 0.76 | **noise 0.51** / turn_on 0.55 |
| turn_on accuracy (INT8 test) | 56.7% | 63.3% | **43.3%** ❌ |
| **turn_on → turn_off (INT8 test)** | 10.0% | **33.3%** ❌ | 23.3% ❌ |
| turn_on → uncertain (INT8 test) | 26.7% | 3.3% | 30.0% |
| turn_off accuracy (INT8 test) | 76.7% | 90.0% | 83.3% |
| noise accuracy (INT8 test) | 80.0% | 65.7% | **40.0%** ❌ |
| Inference (ms, INT8 est.) | ~4 | **7** (+75%) | **1** (−75%) |
| Peak RAM (KB, INT8 est.) | ~12.5 | **14.0** (+12%) | **1.8** (−86%) |
| Flash (KB, INT8 est.) | ~46.4 | **49.4** (+6%) | **34.1** (−26%) |
| DSP (ms, fixed) | 296 | 296 | 296 |
| **Verdict** | reference; safest failure mode | +1 pp aggregate, but turn_on→turn_off **×3.3** worse — deployment-worse despite higher F1 | −20 pp test acc; noise blindness + turn_on collapse — confirms Conv layers are load-bearing |
