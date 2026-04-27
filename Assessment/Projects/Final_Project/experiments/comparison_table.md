# Comparison Table

> Append new experiments as new columns. **Do not remove the baseline column.**

| Metric | baseline |
|---|---|
| DSP | MFCC (13 coef, frame 0.025/0.02s, FFT 512) |
| Architecture | EI default 1D CNN (Conv8 → Conv16 → Dense6) |
| Quantization | INT8 |
| Augmentation | EI full set |
| Validation acc | 93.3% |
| Test acc (INT8) @ 0.6 | 80% |
| Test acc (INT8) @ 0.5 | 83% |
| Inference (ms) | 4 |
| DSP (ms) | 258 |
| Peak RAM (KB) | 12.5 |
| Flash (KB) | 46.4 |
| Notes | turn_on/turn_off confusion at low threshold |
