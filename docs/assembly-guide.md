# CNC Plotter Assembly Guide

This guide explains how to assemble the plotter, mount the motors and pen hardware, and wire everything to the Arduino and CNC shield used by the firmware in [arduino/frimware/cnc_plotter.ino](../arduino/frimware/cnc_plotter.ino).

## 1) Required Parts List

### Main electronics

| Item | Qty | Notes |
|---|---:|---|
| Arduino Uno | 1 | Recommended for CNC shield v3 compatibility |
| CNC Shield v3 style board | 1 | Holds the stepper drivers and breaks out axis pins |
| Stepper driver module | 2 | A4988, DRV8825, or compatible |
| NEMA17 stepper motor | 2 | One for X, one for Y |
| SG90 micro servo | 1 | Pen up/down control |
| Mechanical endstop switch | 2 | X-min and Y-min |
| 12V DC power supply | 1 | Size for your motor current needs |
| USB cable | 1 | Firmware upload and serial G-code streaming |

### Motion and structure

| Item | Qty | Notes |
|---|---:|---|
| Frame material | 1 set | Acrylic, aluminum extrusion, wood, or printed frame |
| Linear guides or rods | 2 axes | Choose one guidance style |
| Belt and pulleys or lead screw parts | 2 axes | Match your mechanical design |
| Pen holder | 1 | Must hold the pen vertical and stable |
| Fasteners and spacers | 1 kit | M3/M5 screws, nuts, standoffs, zip ties |

### Consumables

| Item | Notes |
|---|---|
| Hookup wire | Use stranded wire for motors and power |
| Servo extension wire | Helpful if the servo is mounted away from the controller |
| Screw terminals or dupont leads | Depending on shield and endstop style |
| Cable sleeves or zip ties | For strain relief and cable routing |

## 2) Mechanical Assembly Order

### Step 1: Build the base frame

Assemble the frame so the X axis is horizontal and the Y axis moves the carriage or bed in the orthogonal direction. Make sure the structure is square before tightening all fasteners.

### Step 2: Mount the X and Y motion parts

Install the rails, rods, belts, or leadscrews for both axes. The X motor should drive the X carriage, and the Y motor should drive the Y carriage or bed. Keep both axes aligned so the motion is smooth by hand before powering the motors.

### Step 3: Mount the stepper motors

Attach the NEMA17 motors securely to the frame. Align each pulley or coupler so the belt or screw runs straight and does not rub.

### Step 4: Install the pen carriage

Fit the pen holder on the moving carriage. The pen should touch the paper only when lowered and should lift cleanly without dragging when raised.

### Step 5: Mount the endstops

Install one endstop for X-min and one for Y-min. Place them where the carriage can reach them safely during homing without crashing into the frame.

### Step 6: Mount the electronics

Mount the Arduino Uno and CNC shield in a dry, protected area. Leave space for cable routing, driver access, and the USB connector.

## 3) Wiring Guide

The current firmware pin map is:

| Function | Arduino pin |
|---|---:|
| X step | D2 |
| Y step | D3 |
| X direction | D5 |
| Y direction | D6 |
| Driver enable | D8 |
| X-min endstop | D9 |
| Y-min endstop | D10 |
| Pen servo signal | D11 |

### Stepper driver and motor wiring

1. Insert the X stepper driver into the X driver socket on the CNC shield.
2. Insert the Y stepper driver into the Y driver socket on the CNC shield.
3. Connect the X motor cable to the X motor output on the shield.
4. Connect the Y motor cable to the Y motor output on the shield.
5. Set the driver current limit before running the motors.
6. Confirm the driver orientation before powering the board.

If your motor direction is reversed, swap the motor connector or invert the direction in firmware.

### Endstop wiring

Use the firmware's `INPUT_PULLUP` wiring style:

| Endstop | Arduino pin | Wire to switch |
|---|---:|---|
| X-min | D9 | Signal and GND |
| Y-min | D10 | Signal and GND |

Wire each switch between the signal pin and GND. The triggered state should read LOW.

### Servo wiring

| Servo wire | Connect to |
|---|---|
| Signal | D11 |
| 5V | Stable 5V supply |
| GND | Common ground with Arduino and power supply |

The servo signal is controlled by the Arduino, but the servo power should come from a stable 5V source that can supply the startup current. Share ground between the servo supply and Arduino.

### Power wiring

| Power connection | Connect to |
|---|---|
| 12V supply positive | CNC shield motor power input +12V |
| 12V supply negative | CNC shield GND |
| USB | Arduino USB port for upload and serial streaming |

Do not hot-swap stepper motors while powered. Check the shield power jumper arrangement before applying both USB and external power.

## 4) Recommended Wire-by-Wire Connections

| From | To |
|---|---|
| X motor cable | X motor output on CNC shield |
| Y motor cable | Y motor output on CNC shield |
| X-min switch signal | Arduino D9 |
| X-min switch ground | Arduino GND |
| Y-min switch signal | Arduino D10 |
| Y-min switch ground | Arduino GND |
| Servo signal | Arduino D11 |
| Servo VCC | 5V supply |
| Servo GND | Common GND |
| 12V PSU positive | CNC shield motor supply +12V |
| 12V PSU negative | CNC shield GND |

## 5) Driver Setup Before First Power-On

1. Verify each stepper driver is oriented correctly in the shield socket.
2. Set the driver current limit low before the first motion test.
3. Make sure the motor connectors are fully seated.
4. Double-check that no bare wires can short against the frame.
5. Ensure the pen is lifted before the first test move.

## 6) First Power-On and Test Sequence

1. Power the Arduino by USB only.
2. Upload the firmware.
3. Open the serial monitor at 115200 baud.
4. Send `M5` and confirm the pen lifts.
5. Send `M3` and confirm the pen lowers.
6. Send `G0 X5 Y5` and confirm a short move.
7. Send `M114` and confirm the reported position.
8. Test `G28` after confirming the endstops are wired correctly.

## 7) Troubleshooting Notes

| Symptom | Likely cause | Check |
|---|---|---|
| Motor does not move | Driver missing, wrong orientation, no power | Reseat the driver and check 12V supply |
| Motor turns the wrong way | Direction reversed | Flip the motor connector or change direction logic |
| Endstop never triggers | Wrong pin or wrong switch wiring | Confirm signal to D9/D10 and GND wiring |
| Servo jitters or resets board | Weak 5V supply | Use a stronger servo supply and common ground |
| Firmware reports unsupported command | Command not in supported set | Use `G0`, `G1`, `G28`, `M3`, `M5`, `M300`, or `M114` |

## 8) Notes for This Project

The Python pipeline creates G-code, then [python/sender.py](../python/sender.py) streams those lines over serial. The Arduino sketch does not interpret image data directly; it only executes the motion and pen commands it receives.
