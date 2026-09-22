# CNC Plotter — Complete User & Operator Guidebook

This guidebook provides an end-to-end operational manual for running the CNC Handwriting / Pen Plotter. It covers how to convert artwork (PNG, JPG, PDF, SVG) into machine-ready G-code, how to stream G-code to the Arduino Uno, critical electrical and operating precautions, and troubleshooting steps.

---

## Table of Contents

1. [System Architecture & Overview](#1-system-architecture--overview)
2. [Critical Precautions & Operating Rules](#2-critical-precautions--operating-rules)
   - [Does Arduino Uno Need to Stay Connected to the Laptop?](#does-arduino-uno-need-to-stay-connected-to-the-laptop)
   - [Power Supply Sequencing (Protecting Stepper Drivers)](#power-supply-sequencing-protecting-stepper-drivers)
   - [Serial Port Exclusivity & Linux Permissions](#serial-port-exclusivity--linux-permissions)
   - [Mechanical Limits & Emergency Stop](#mechanical-limits--emergency-stop)
3. [Step-by-Step Workflow](#3-step-by-step-workflow)
   - [Step 1: One-Time Arduino Firmware Setup](#step-1-one-time-arduino-firmware-setup)
   - [Step 2: Python Environment Setup](#step-2-python-environment-setup)
   - [Step 3: Preparing Artwork & Converting PNG to G-code](#step-3-preparing-artwork--converting-png-to-g-code)
   - [Step 4: Machine Setup & Work Zeroing](#step-4-machine-setup--work-zeroing)
   - [Step 5: Streaming G-code to the Plotter](#step-5-streaming-g-code-to-the-plotter)
4. [Advanced Tuning & Command Flags](#4-advanced-tuning--command-flags)
5. [Troubleshooting & FAQs](#5-troubleshooting--faqs)
6. [Quick Reference Cheat Sheet](#6-quick-reference-cheat-sheet)

---

## 1. System Architecture & Overview

The CNC Plotter system works via a coordinated pipeline split between your computer and the Arduino controller:

```text
+-------------------------------------------------------------+
|                      LAPTOP / COMPUTER                      |
|                                                             |
|  [Input Image: PNG/JPG/SVG/PDF]                             |
|              │                                              |
|              ▼                                              |
|  [python/main.py] ─── Contour extraction & vectorization    |
|              │                                              |
|              ▼                                              |
|  [gcode/generated/*.gcode] ─── G0, G1, M3 (down), M5 (up)   |
|              │                                              |
|              ▼                                              |
|  [python/sender.py] ── Streams line-by-line over USB Serial |
+──────────────────────────────┬──────────────────────────────+
                               │ USB Cable (115200 baud)
                               │ Streams line -> waits for "ok"
                               ▼
+─────────────────────────────────────────────────────────────+
|                     CNC PLOTTER HARDWARE                    |
|                                                             |
|  Arduino Uno (Logic: 5V from USB)                           |
|       │                                                     |
|       ▼                                                     |
|  CNC Shield V3 + A4988 Drivers (Power: External 12V DC)     |
|       ├── Stepper Motor X (D2 Step, D5 Dir)                 |
|       ├── Stepper Motor Y (D3 Step, D6 Dir)                 |
|       └── SG90 Micro Servo (D11 / SpinEnable - Pen Lift)    |
+-------------------------------------------------------------+
```

---

## 2. Critical Precautions & Operating Rules

### Does Arduino Uno Need to Stay Connected to the Laptop?

> [!IMPORTANT]
> **YES! The Arduino Uno MUST remain connected via the USB cable to your laptop for the entire duration of the plotting process.**

#### Why?
1. **Limited Arduino Memory**: An Arduino Uno (ATmega328P) has only **2 KB of SRAM** and **32 KB of Flash memory**. It cannot store a complete G-code file, which typically contains hundreds or thousands of lines (e.g. 5,000+ lines for detailed line art).
2. **Real-Time Streaming**: The Python script (`sender.py`) acts as the "brain streamer." It sends **one line of G-code** over the USB serial connection, waits for the Arduino to execute the move and respond with `ok`, and only then sends the next line.
3. **Laptop Sleep Settings**:
   - Make sure your laptop's **Sleep / Suspend / Hibernate mode is disabled** while plotting.
   - If the laptop suspends, goes to sleep, or closes its lid, the USB connection drops, the serial link is severed, and your plot will freeze midway, ruining the drawing.

---

### Power Supply Sequencing (Protecting Stepper Drivers)

The CNC Plotter requires **two separate power sources**:
1. **5V USB Power**: Powers the Arduino Uno logic board and serial communications.
2. **12V DC External Power (2A to 5A)**: Connected to the screw terminal on the CNC Shield V3 to provide power to the NEMA 17 stepper motors.

> [!CAUTION]
> **NEVER hot-plug or unplug stepper motor cables while the 12V power supply is turned on!**
> Disconnecting a stepper motor while current is flowing induces massive inductive back-EMF voltage spikes that will **instantly destroy the A4988 / DRV8825 stepper driver chips**.

#### Correct Power-Up Sequence:
1. Ensure the 12V DC power adapter is **switched OFF / unplugged**.
2. Check that all 4-pin stepper motor connectors and the servo connector are firmly seated.
3. Plug the **USB cable** from the Arduino Uno into the laptop. (The Arduino LEDs will light up).
4. Turn **ON** the external 12V DC power supply to energize the stepper motors.

#### Correct Power-Down Sequence:
1. Turn **OFF** the external 12V DC power supply first.
2. Unplug the **USB cable** from the laptop.

---

### Serial Port Exclusivity & Linux Permissions

#### 1. Exclusive Port Access
Only **one application** can access the Arduino serial port at any given time.
- If the **Arduino IDE Serial Monitor** or **Serial Plotter** is open, the Python script will fail with:
  ```text
  serial.serialutil.SerialException: [Errno 16] Device or resource busy: '/dev/ttyACM0'
  ```
- **Rule**: Always close the Arduino IDE Serial Monitor before running `sender.py` or `main.py --send`.

#### 2. Linux Device Names
- Genuine Arduino Uno boards (ATmega16U2 chip) typically show up as:
  ```text
  /dev/ttyACM0   (or /dev/ttyACM1)
  ```
- Clone Arduino Uno / Nano boards (CH340 / CP2102 chips) typically show up as:
  ```text
  /dev/ttyUSB0   (or /dev/ttyUSB1)
  ```
- On Windows, they appear as `COM3`, `COM4`, etc.

To check the connected port on Linux, run:
```bash
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```
or inspect kernel messages:
```bash
dmesg | grep -E "ttyACM|ttyUSB" | tail -n 5
```

#### 3. Linux Dialout Group Permissions
If you encounter `Permission denied: '/dev/ttyACM0'`, add your user to the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
```
*(Log out and log back in for changes to take effect, or run `sudo chmod 666 /dev/ttyACM0` as a temporary fix for the current session).*

---

### Mechanical Limits & Emergency Stop

1. **Secure the Paper**: Always tape down all 4 corners of your paper using masking tape or paper clips. If the paper shifts during drawing, the plot will be misaligned.
2. **Check Cable Clearance**: Ensure motor and servo cables can move freely across the full travel range without catching or snagging on frame rails.
3. **Emergency Stop Methods**:
   If the pen crashes or an axis hits a mechanical stop:
   - **Option 1**: Turn off the 12V DC motor power switch or pull the DC power barrel jack.
   - **Option 2**: Press the **RESET** button on the CNC Shield / Arduino Uno.
   - **Option 3**: Press `Ctrl + C` in the terminal running the Python script to halt command streaming.

---

## 3. Step-by-Step Workflow

### Step 1: One-Time Arduino Firmware Setup

Before running the Python scripts, upload the firmware to the Arduino:

1. Open the Arduino IDE.
2. Open [`arduino/frimware/cnc_plotter/cnc_plotter.ino`](file:///home/tohid/CNCPlotter/arduino/frimware/cnc_plotter/cnc_plotter.ino).
3. Ensure required libraries are installed via **Library Manager** (`Ctrl + Shift + I`):
   - `AccelStepper` by Mike McCauley
   - `Servo` (built-in)
4. Under **Tools**:
   - **Board**: Select *Arduino Uno*
   - **Port**: Select your Arduino port (e.g. `/dev/ttyACM0` or `COM3`)
5. Click **Upload** (`Ctrl + U`).
6. After upload succeeds, close the Arduino IDE or close its Serial Monitor.

---

### Step 2: Python Environment Setup

Open a terminal in the project root directory (`/home/tohid/CNCPlotter`):

```bash
cd /home/tohid/CNCPlotter

# Activate the virtual environment
source .venv/bin/activate

# (Optional) Verify dependencies are installed
pip install -r python/requirements.txt
```

---

### Step 3: Preparing Artwork & Converting PNG to G-code

#### 1. Prepare your input file
- Place your PNG image in the `drawings/input/` folder (e.g. `drawings/input/my_drawing.png`).
- **Best Image Practices**:
  - High contrast (pure black lines on clean white background).
  - Clear outlines (line art, sketches, handwriting, or logos work best).
  - Avoid heavy gradients, shadows, or noisy photo backgrounds.

#### 2. Convert PNG to G-code
Run `main.py` pointing to your image:

```bash
python python/main.py drawings/input/example.png
```

You will see output summarizing the conversion:
```text
Paths: 42
G-code lines: 646
Saved: /home/tohid/CNCPlotter/gcode/generated/example.gcode
```

The generated file will be saved under `gcode/generated/<filename>.gcode`.

#### 3. Tuning the Drawing Size (`--mm-per-pixel`)
By default, `--mm-per-pixel` is `0.2`.
- If an image is 500 pixels wide: `500 * 0.2 mm = 100 mm` (10 cm wide plot).
- To make the plot smaller: use `--mm-per-pixel 0.1` (50 mm wide).
- To make the plot larger: use `--mm-per-pixel 0.3` (150 mm wide).

Example:
```bash
python python/main.py drawings/input/example.png --mm-per-pixel 0.15 --threshold 190
```

---

### Step 4: Machine Setup & Work Zeroing

1. **Tape Paper to Bed**: Fasten your sheet (A4/A5) flat to the plotting bed.
2. **Move to Origin (0,0)**:
   - With 12V power off (or steppers disabled), gently move the X and Y carriage by hand to the bottom-left corner of the paper where you want the plot to begin.
   - This physical position will be treated as `(0, 0)` in your G-code coordinates.
3. **Check Pen Height**:
   - Insert your pen (fineliner, gel pen, or ballpoint) into the servo holder.
   - When the servo is at **Pen Up (`M5`, 90°)**: The pen tip should hover **3–5 mm above the paper**.
   - When the servo is at **Pen Down (`M3`, 30°)**: The pen tip should rest gently on the paper with slight spring or gravity pressure without digging into the sheet.
4. **Power On**: Turn on the 12V external power supply.

---

### Step 5: Streaming G-code to the Plotter

You can stream using either of two methods:

#### Method A: Standalone Sender (Recommended)
This method separates generation from transmission, allowing you to inspect the G-code or run multiple test runs:

```bash
python python/sender.py gcode/generated/example.gcode --port /dev/ttyACM0 --baud 115200
```

*(Replace `/dev/ttyACM0` with `/dev/ttyUSB0` or `COMx` depending on your board).*

#### Method B: All-in-One Convert & Stream
You can generate G-code and immediately stream it in a single command using the `--send` flag:

```bash
python python/main.py drawings/input/example.png --send --port /dev/ttyACM0 --baud 115200
```

#### What happens during transmission:
1. Python connects to `/dev/ttyACM0` and waits 2 seconds for Arduino initialization.
2. Python sends commands line by line (`G21`, `G90`, `M5`, `G0 X...`, `M3`, `G1 X...`).
3. For each command, the Arduino executes the motion and returns `ok`.
4. When all lines finish, the script prints:
   ```text
   Sent 646 command lines to /dev/ttyACM0 at 115200 baud
   ```
5. The pen raises (`M5`), and plotting is complete.

---

## 4. Advanced Tuning & Command Flags

### Options for `python/main.py` (G-code Generator)

| Option | Default | Purpose |
|---|---|---|
| `--threshold` | `180` | Grayscale threshold (0–255) to separate drawing strokes from paper background. Lower values detect only dark lines; higher values pick up lighter pencil marks. |
| `--mm-per-pixel` | `0.2` | Scaling factor in millimeters per image pixel. Controls overall plot dimensions. |
| `--simplify` | `1.5` | Douglas-Peucker path simplification tolerance (in pixels). Higher values reduce file size and smooth curves; lower values preserve intricate detail. |
| `--min-area` | `10.0` | Filters out small dust spots or noisy speckles below this area (in pixels). |
| `--draw-feed` | `1200` | Pen-down drawing speed in mm/min (adjust lower for pens that skip at high speeds). |
| `--travel-feed` | `3000` | Pen-up rapid transit speed in mm/min. |
| `--pen-up-cmd` | `"M5"` | Firmware command to lift pen (defaults to servo 90°). |
| `--pen-down-cmd`| `"M3 S30"` | Firmware command to lower pen (defaults to servo 30°). |
| `--no-optimize` | `False` | Disables nearest-neighbor path reordering (recommended to keep optimization enabled). |

### Options for `python/sender.py` (G-code Streamer)

| Option | Default | Purpose |
|---|---|---|
| `--port` | *(required)* | Serial device (e.g. `/dev/ttyACM0`, `/dev/ttyUSB0`, `COM3`). |
| `--baud` | `115200` | Serial baud rate (must match `Serial.begin(115200)` in firmware). |
| `--filter-setup` | `False` | Skips non-motion setup codes (`G20`, `G21`, `G90`, `G91`, `M2`, `M30`). Useful if connecting to legacy or minimal firmware. |
| `--ignore-errors`| `False` | Logs a warning on controller error responses instead of aborting the stream. |
| `--startup-delay`| `2.0` | Seconds to pause after opening serial port to allow Arduino auto-reset to settle. |

### Working with Other Formats (PDF & SVG)

- **Vector SVG Files**:
  ```bash
  python python/main.py drawings/input/sample.svg --mm-per-pixel 0.2
  ```
- **PDF Documents** (extracts vector paths or rasterizes pages):
  ```bash
  python python/main.py drawings/input/document.pdf --page 0 --dpi 200 --mm-per-pixel 0.2
  ```

---

## 5. Troubleshooting & FAQs

| Symptom / Error | Cause | Solution |
|---|---|---|
| `SerialException: [Errno 16] Device or resource busy` | Arduino IDE Serial Monitor or another terminal is open and occupying the port. | Close the Serial Monitor in Arduino IDE and close any other serial terminal (`screen`, `minicom`). |
| `Permission denied: '/dev/ttyACM0'` | Current Linux user is not in the `dialout` group. | Run `sudo usermod -a -G dialout $USER`, then log out and log back in. Or temporarily: `sudo chmod 666 /dev/ttyACM0`. |
| `RuntimeError: Controller error for 'G21': error: unsupported command` | Arduino is running an older firmware build that lacks setup command handling. | **Fix 1**: Re-upload the latest [`arduino/frimware/cnc_plotter/cnc_plotter.ino`](file:///home/tohid/CNCPlotter/arduino/frimware/cnc_plotter/cnc_plotter.ino).<br>**Fix 2**: Add `--filter-setup` to the sender command to bypass setup codes. |
| Stepper motors hum or vibrate without turning | 1. 12V motor power is off.<br>2. Stepper coil wire pair mismatched.<br>3. Driver current potentiometer (`Vref`) set too low. | 1. Verify 12V power supply is on and outputting 12V.<br>2. Check coil pairs with a multimeter.<br>3. Tune driver Vref to ~0.6V–0.8V. |
| Pen scratches paper or ink doesn't flow | Pen down angle too low or too high; or pen tip dried out. | Test pen height. Adjust `--pen-down-cmd "M3 S35"` (or desired angle) to calibrate touch pressure. |
| Plot is mirrored (backwards) or inverted | Motor direction pin logic inverted or motor plug reversed. | Invert motor direction in firmware (`stepperX.setPinsInverted(...)`) or rotate the 4-pin motor connector 180° (with 12V power OFF!). |
| Drawing dimensions are inaccurate (e.g. 50 mm measures 25 mm) | `STEPS_PER_MM` mismatch in firmware or microstepping jumper missing under driver. | Install all 3 jumpers under each driver on the CNC shield for 1/16 microstepping, and tune `STEPS_PER_MM_X` / `STEPS_PER_MM_Y` in `cnc_plotter.ino`. |
| Plot stops midway and freezes | Laptop entered sleep/suspend mode, or loose USB cable. | Set laptop screen and sleep timers to "Never Sleep while on AC Power". Secure USB cable. |

---

## 6. Quick Reference Cheat Sheet

Save this quick reference for your day-to-day plotting sessions:

```bash
# 1. Open project directory & activate virtual environment
source .venv/bin/activate

# 2. Check connected Arduino serial port
ls /dev/ttyACM* /dev/ttyUSB*

# 3. Convert input image to G-code
python python/main.py drawings/input/example.png --mm-per-pixel 0.2

# 4. Turn on 12V motor power & zero pen to bottom-left corner

# 5. Stream G-code to machine
python python/sender.py gcode/generated/example.gcode --port /dev/ttyACM0 --baud 115200

# Emergency Stop: Turn off 12V power switch, press Arduino RESET, or press Ctrl+C
```
