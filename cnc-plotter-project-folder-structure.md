# CNC Handwriting Plotter — Project Folder Structure

A clean folder structure makes the project easier to manage and present.

## Recommended structure

```text
cnc-handwriting-plotter/
├── arduino/
│   ├── firmware/
│   │   └── cnc_plotter.ino
│   └── libraries/
├── python/
│   ├── main.py
│   ├── image_to_path.py
│   ├── pdf_to_path.py
│   ├── path_to_gcode.py
│   ├── sender.py
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
│   ├── calibration-notes.md
│   └── project-report.md
├── tests/
│   ├── simulation/
│   └── machine-tests/
└── README.md
```

---

## What each folder means

### `arduino/`
Contains the firmware code for the controller board.

### `python/`
Contains all file-processing and G-code generation scripts.

### `drawings/`
Stores source files and converted artwork.

### `gcode/`
Stores generated G-code files and sample outputs.

### `docs/`
Contains your report material, wiring notes, and calibration details.

### `tests/`
Contains simulation files and real machine test logs.

---

## Best practice

For a final-year project, keep the Python and Arduino code separate. That makes it easier to explain:
- what runs on the Arduino
- what runs on the computer
- what is input
- what is output

---

## Suggested order of work

1. Build the Arduino firmware folder.
2. Build the Python conversion scripts.
3. Add sample drawings.
4. Generate G-code outputs.
5. Add documentation.
6. Add testing and calibration notes.
