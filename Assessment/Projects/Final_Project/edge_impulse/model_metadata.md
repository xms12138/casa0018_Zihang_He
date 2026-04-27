# Model Metadata

- **Edge Impulse project URL**: _TBD_
- **Project ID**: _TBD_
- **Exported library**: `exported_library/ei-xms.12138-project-1-arduino-1.0.1-impulse-#1.zip`
- **Last sync**: _TBD_

## Impulse summary

| Block | Setting | Value |
|---|---|---|
| DSP | type | MFCC |
| DSP | coefficients | 13 |
| DSP | frame length / stride | 0.025s / 0.02s |
| DSP | FFT length | 512 |
| DSP | filter number | 32 |
| DSP | low frequency | 80 Hz |
| Model | architecture | EI default 1D CNN (Conv8 → Conv16 → Flatten → Dense6) |
| Model | input | 637 features (reshaped 13 cols) |
| Quantization | mode | INT8 |

## Performance snapshot

| Metric | Value |
|---|---|
| Validation accuracy | 93.3% |
| INT8 test accuracy @ threshold 0.6 | 80% |
| INT8 test accuracy @ threshold 0.5 | 83% |
| On-device inference | 4 ms |
| On-device DSP | 258 ms |
| Peak RAM | 12.5 KB |
| Flash | 46.4 KB |
