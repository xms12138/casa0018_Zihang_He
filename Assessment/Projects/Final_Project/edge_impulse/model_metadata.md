# Model Metadata

- **Edge Impulse project URL (public)**: https://studio.edgeimpulse.com/public/973891/latest
- **Project ID**: 973891
- **Project name (EI Studio)**: `xms.12138-project-1`
- **Exported library**: `exported_library/ei-xms.12138-project-1-arduino-1.0.1-impulse-#1.zip`
- **Last sync**: 2026-04-28

## Impulse summary

| Block | Setting | Value |
|---|---|---|
| DSP | type | MFCC |
| DSP | coefficients | 13 |
| DSP | frame length / stride | 0.025 s / 0.02 s |
| DSP | FFT length | 256 (manual; autotune default 512 — see exp_log) |
| DSP | filter number | 32 |
| DSP | low frequency | 80 Hz |
| DSP | output features | 637 (reshape 13 cols) |
| Model | architecture | EI default 1D CNN (Conv 8 → Conv 16 → Flatten → Dense 6) |
| Model | dropout | 0.25 (×2) |
| Training | epochs / lr / batch | 200 / 0.005 / 32 |
| Training | augmentation | Add noise Low + Mask time Low + Mask freq Low + Warp time on |
| Training | learned optimizer | disabled |
| Quantization | mode | INT8 (also Float32 evaluated for comparison) |

## Performance snapshot — baseline (INT8 unless noted)

| Metric | Value |
|---|---|
| Validation accuracy (INT8) | 94.5% |
| Validation accuracy (Float32) | 95.1% |
| Test accuracy @ threshold 0.6 (INT8) | 81.95% |
| Test accuracy @ threshold 0.6 (Float32) | 82.44% |
| Quantization Δ (test) | −0.49 pp |
| Validation → Test gap | −12.55 pp |
| Worst-class F1 (INT8 test) | turn_on 0.69 |
| On-device inference (INT8 est.) | ~4 ms |
| On-device DSP | 296 ms |
| Peak RAM (INT8 est.) | ~12.5 KB |
| Flash (INT8 est.) | ~46.4 KB |

## Live testing (deployed Nano 33 BLE Sense, threshold 0.6)

| Metric | Value |
|---|---|
| Total trials | 100 |
| Correct state transitions | 88 |
| Aggregate live accuracy | 88.0% |

See `experiments/exp_log.md` entry 2026-04-28 for protocol, per-speaker split, and per-keyword breakdown.
