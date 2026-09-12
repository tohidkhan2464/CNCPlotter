# CNC Handwriting Plotter — Software Installation List

This list assumes a DIY pen plotter built with an Arduino-based controller and a PC/laptop for preparing drawings and sending G-code.

## 1) Core software

### A. Arduino IDE
**Purpose:** Upload firmware or custom control code to the Arduino board.

**Install:**
- Download Arduino IDE from the official Arduino website.
- Install it on Windows, Linux, or macOS.

**Use for:**
- Uploading custom Arduino sketches.
- Uploading GRBL-based firmware if needed.
- Serial monitor testing.

### B. USB driver for Arduino board
**Purpose:** Make the computer recognize the Arduino board over USB.

**Install:**
- Install the driver if your board needs one.
- Many official boards work automatically; some clone boards use CH340 or similar USB chips.

**Use for:**
- Serial communication.
- Firmware upload.

### C. Inkscape
**Purpose:** Create or edit vector drawings and convert artwork into SVG.

**Install:**
- Download and install Inkscape.

**Use for:**
- Designing drawings.
- Converting imported images into vector outlines.
- Preparing SVG files for G-code conversion.

### D. Python 3
**Purpose:** Run scripts for image/PDF processing and G-code generation.

**Install:**
- Install Python 3.
- Ensure `python` or `python3` works from the terminal.

**Use for:**
- Custom preprocessing scripts.
- PDF/image conversion.
- SVG-to-G-code automation.

### E. G-code sender
**Purpose:** Send G-code from PC to the Arduino-controlled machine.

**Options:**
- Universal Gcode Sender (UGS)
- Repetier Host
- Pronterface

**Use for:**
- Connecting to Arduino over USB.
- Streaming G-code.
- Manual machine testing.

---

## 2) Recommended Python libraries

Install these with pip only if you choose the Python pipeline.

### A. vpype
**Purpose:** Clean and optimize vector paths.

```bash
pip install vpype
```

### B. vpype-gcode or vpype-gscrib
**Purpose:** Convert vector drawings into G-code.

```bash
pip install vpype-gcode
```

or

```bash
pipx inject vpype vpype-gscrib
```

### C. Pillow
**Purpose:** Work with images.

```bash
pip install pillow
```

### D. OpenCV
**Purpose:** Image thresholding, edge detection, contour tracing.

```bash
pip install opencv-python
```

### E. pdf2image or PyMuPDF
**Purpose:** Read PDF pages and convert them to images or extract content.

```bash
pip install pdf2image pymupdf
```

### F. pyserial
**Purpose:** Send commands to Arduino through serial.

```bash
pip install pyserial
```

---

## 3) Optional but useful software

### A. CAMotics
**Purpose:** Simulate G-code before running the machine.

**Use for:**
- Safety checking.
- Visualizing tool paths.

### B. OctoPrint
**Purpose:** Optional web-based control and monitoring.

**Use for:**
- Remote G-code sending.
- Headless control.

### C. Blender / Illustrator / Affinity Designer
**Purpose:** Advanced vector creation.

**Use for:**
- Designing precise artwork.
- Preparing complex line drawings.

---

## 4) Suggested installation order

1. Install Arduino IDE.
2. Install the Arduino USB driver if required.
3. Install Inkscape.
4. Install Python 3.
5. Install Python libraries.
6. Install a G-code sender.
7. Install CAMotics for simulation.

---

## 5) Best beginner setup

If you want the simplest path, use:
- Arduino IDE
- Inkscape
- Universal Gcode Sender
- Python 3
- pyserial
- Pillow

If you want the more advanced automation path, add:
- OpenCV
- vpype
- vpype-gcode or vpype-gscrib
- PDF libraries

---

## 6) Notes

- Use Arduino IDE if your controller is an Arduino Uno or Mega.
- Use Python on the computer for image/PDF conversion and G-code creation.
- Use a G-code sender to test the machine before connecting everything to real paper.
- Always simulate the G-code first if possible.
