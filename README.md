# CNC Handwriting Plotter

End-to-end student-friendly CNC pen plotter project using:
- Arduino firmware for XY + pen control.
- Python pipeline to convert image/PDF/SVG files to G-code.
- Serial sender to stream G-code to the controller.

This repository follows the structure and workflow in:
- **[GUIDE.md](GUIDE.md) — Complete Step-by-Step Operator Guidebook & Precautions**
- [cnc-plotter-arduino-code-structure.md](cnc-plotter-arduino-code-structure.md)
- [cnc-plotter-python-file-to-gcode-pipeline.md](cnc-plotter-python-file-to-gcode-pipeline.md)
- [cnc-plotter-project-folder-structure.md](cnc-plotter-project-folder-structure.md)
- [docs/assembly-guide.md](docs/assembly-guide.md)
- [docs/wiring-diagram.md](docs/wiring-diagram.md)
- [docs/bom.md](docs/bom.md)

It is also aligned with practices seen in your provided references:
- Inkscape/vector-to-G-code mindset.
- G-code streaming over serial with `ok` acknowledgements.
- Pen up/down mapped to `M5`/`M3` style commands.

## Folder Structure

```text
CNCPlotter/
├── arduino/
│   └── frimware/
│       └── cnc_plotter.ino
├── python/
│   ├── image_to_path.py
│   ├── pdf_to_path.py
│   ├── svg_to_path.py
│   ├── path_to_gcode.py
│   ├── sender.py
│   ├── main.py
│   └── requirements.txt
├── drawings/
│   ├── input/
│   └── output/
├── gcode/
│   ├── generated/
│   └── samples/
├── docs/
│   ├── wiring-diagram.md
│   ├── bom.md
│   └── calibrations-notes.md
└── tests/
	 ├── simulation/
	 └── machine-tests/
```

## 1) Hardware/Firmware Path

1. Open [arduino/frimware/cnc_plotter.ino](arduino/frimware/cnc_plotter.ino) in Arduino IDE.
2. Install libraries:
	- `AccelStepper`
	- `Servo`
3. Adjust pin mappings and machine constants in the sketch.
4. Upload to Arduino Uno/Nano + CNC shield.
5. Test over serial monitor at `115200` baud:
	- `M5` (pen up)
	- `M3` (pen down)
	- `G0 X10 Y10`
	- `G28` (home)

## 2) Python Pipeline Path

### Install

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Generate G-code

```bash
python main.py ../drawings/input/example.png
```

Output goes to `gcode/generated/<input>.gcode`.

### Supported input formats
- Images: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`
- PDF: `.pdf`
- Vector: `.svg`

### Useful options

```bash
python main.py ../drawings/input/example.pdf --page 0 --dpi 200 --threshold 180 --mm-per-pixel 0.2
python main.py ../drawings/input/example.svg --draw-feed 1200 --travel-feed 3000
python main.py ../drawings/input/example.png --no-optimize
```

## 3) Stream G-code to Arduino

```bash
python sender.py ../gcode/generated/example.gcode --port /dev/ttyUSB0 --baud 115200
```

Or from pipeline directly:

```bash
python main.py ../drawings/input/example.png --send --port /dev/ttyUSB0 --baud 115200
```

## 4) G-code Conventions Used

- `G21` millimeters
- `G90` absolute positioning
- `G0` travel moves
- `G1` drawing moves
- `M3` pen down
- `M5` pen up
- `M2` end program

These are intentionally close to GRBL-style flows while keeping firmware simple and explainable.

## 5) Calibration Checklist

1. Tune `STEPS_PER_MM_X` and `STEPS_PER_MM_Y` in firmware.
2. Tune `PEN_UP_ANGLE` and `PEN_DOWN_ANGLE` for your servo mount.
3. Confirm homing switch logic (`INPUT_PULLUP` expects active-low endstops).
4. Draw a 20 mm square and measure actual result.
5. Adjust scaling and repeat until error is acceptable.

## 6) Safety Notes

- Keep motor current limits conservative for A4988/DRV8825 drivers.
- Always test generated G-code with pen lifted first.
- Home axes slowly when testing endstop direction.
- Never force axis travel against hard stops.

## 7) Academic/Project Report Notes

This repository is split to clearly show:
- Computer-side preprocessing and G-code generation (`python/`).
- Controller-side motion execution (`arduino/`).
- Documentation and calibration evidence (`docs/`, `tests/`).

That separation helps for final-year demo and viva explanations.
