# Hardware Setup

## Bill of Materials

| Item | Spec | Qty | Notes |
|---|---|---|---|
| Arduino Nano 33 BLE Sense | nRF52840, Cortex-M4F 64 MHz, 256 KB RAM, 1 MB Flash; onboard MP34DT05 PDM microphone | 1 | All inference and DSP run on this board. |
| WS2812B addressable LED strip | 5 V, GRB 800 kHz protocol; 10 LEDs (segment cut from a longer strip) | 1 | Driven from the Nano's 3.3 V rail (see *Power* below). |
| USB cable (Micro-USB) | Standard USB 2.0 | 1 | Powers the Nano from the host PC; the LED strip draws from the Nano's regulated rail. |
| 3D-printed enclosure | PLA, 4-part assembly (Base, Base Cover, Diffuser, Lid) | 1 set | STL/3MF in `3D_Printer/`. |

## Pin map

| Function | MCU pin | Connected to | Notes |
|---|---|---|---|
| WS2812B data in | D2 | Strip DIN | `LED_PIN = 2` in `arduino/echolume/echolume.ino`. |
| WS2812B power | 3.3 V | Strip VCC | Driven directly from the Nano's 3.3 V rail; see *Power* note. |
| WS2812B ground | GND | Strip GND | Common ground with MCU. |
| Microphone | onboard MP34DT05 | — | PDM, 16 kHz mono; no external wiring required. |

## Power

- The Nano 33 BLE Sense is powered over USB from a host PC.
- The 10-LED WS2812B segment is powered from the **Nano's 3.3 V rail**, not from a separate 5 V supply. WS2812B is nominally rated at 5 V but is driven reliably here at 3.3 V because (a) the strip is short (10 pixels), (b) brightness is software-capped via `strip.setBrightness(150)` (≈ 59 % of maximum) which lowers peak current per LED, and (c) operating from the same 3.3 V rail as the MCU keeps the data line within VIH at the first pixel without a level shifter.
- This is a deliberate simplicity choice for a desk demo. For a longer strip or for full-brightness white, a separate 5 V supply with a logic-level shifter on DIN would be required.

## Wiring

The full wiring is three jumpers from Nano → strip:

```
Nano 33 BLE Sense        WS2812B (10 LED)
---------------------    ----------------
D2  ────────────────────► DIN
3V3 ────────────────────► VCC
GND ────────────────────► GND
```

Photographs of the assembled hardware: `report_figures/05_hardware/` (4 images, captions TBD — to be matched against the actual views).

## 3D enclosure

Files (in `3D_Printer/`):

| File | Purpose |
|---|---|
| `Base.stl` / `Base.3mf` | Main housing for the Nano + strip |
| `Base Cover.stl` | Underside cover |
| `Diffuser.stl` | Translucent diffuser over the LED strip |
| `Lid 3.stl` | Top lid |
| `528071-3ft-led-tower-lamp-...pdf` | Source design reference (LED tower lamp) |

**Print parameters used (PLA):** 0.2 mm layer height, 15 % gyroid infill, default speed (≈ 50 mm/s), 3 perimeters, supports off for the diffuser to keep it translucent. Total print time ≈ several hours across the four parts.

The Diffuser is the only translucency-critical part; the rest are opaque structural. The 4-part split allows reprinting the Diffuser separately if its translucency degrades over time.
