# Bill of Materials (Baseline)

This BOM is for a 2-axis pen plotter using Arduino + CNC shield and an SG90 pen servo.

## Electronics

| Item | Qty | Notes |
|---|---:|---|
| Arduino Uno or Nano | 1 | Uno is easiest for CNC shield compatibility |
| CNC Shield (v3 style for Uno) | 1 | X/Y stepper sockets required |
| Stepper drivers (A4988/DRV8825/TMC2208) | 2 | One for X, one for Y |
| NEMA17 stepper motor | 2 | Select torque based on gantry weight |
| SG90 micro servo | 1 | Pen up/down |
| 12V DC power supply | 1 | 2A or above is typical for small machines |
| Endstop switch (mechanical/optical) | 2 | X-min and Y-min |
| USB cable for Arduino | 1 | Firmware + serial streaming |

## Motion Hardware

| Item | Qty | Notes |
|---|---:|---|
| GT2 timing belt | ~2-3 m | Depends on frame size |
| GT2 pulley (motor) | 2 | Match motor shaft (usually 5mm) |
| GT2 idler pulley | 2+ | Axis-dependent |
| Linear rails/rods + bearings | 2 axes | Choose one guidance system |
| Frame material (aluminum extrusion/printed parts/wood base) | 1 set | Based on your mechanical design |

## Mechanical + Consumables

| Item | Qty | Notes |
|---|---:|---|
| Pen holder assembly | 1 | Printed or machined |
| Fasteners (M3/M5 assorted) | 1 kit | For frame and motor mounts |
| Spacers, cable ties, wire sleeves | as needed | Cable management |
| A4/A3 paper clips/tape | as needed | Fixing paper to bed |

## Software

| Item | Use |
|---|---|
| Arduino IDE | Firmware upload and serial diagnostics |
| Python 3.10+ | Conversion + sender scripts |
| Inkscape (optional) | Manual vector prep |
| bCNC / UGS / CNCjs (optional) | Alternative G-code streaming |

## Optional Upgrades

- TMC drivers for quieter motion.
- Better servo linkage for consistent pen pressure.
- Raspberry Pi running CNCjs for untethered streaming.
