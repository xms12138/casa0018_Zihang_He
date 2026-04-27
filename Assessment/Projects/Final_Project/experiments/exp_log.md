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

## 2026-04-25 — Baseline (EI default 1D CNN, MFCC, INT8)

- **Configuration**: 13 MFCC coef, frame 0.025/0.02s, FFT 512, 32 filters, low_freq 80 Hz; EI default 1D CNN (Conv8 → Conv16 → Flatten → Dense6); full augmentation; learned optimizer disabled; CPU training.
- **Validation accuracy**: 93.3%
- **Test accuracy (INT8)**: 80% @ threshold 0.6 / 83% @ threshold 0.5
- **On-device**: inference 4 ms / RAM 12.5 KB / flash 46.4 KB / DSP 258 ms
- **Observation**: turn_on / turn_off confused below threshold 0.5 (~25% misclassification); val-test gap 13% suggests distribution shift.
- **Figures**: `report_figures/03_experiments/baseline/`
