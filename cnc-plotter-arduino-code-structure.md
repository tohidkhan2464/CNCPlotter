# CNC Handwriting Plotter — Arduino Code Structure

This is the structure you can follow for the Arduino side of a pen plotter.

## 1) Main job of Arduino code

The Arduino program should:
- Receive commands from the computer.
- Move the X and Y axes.
- Control pen up/down.
- Home the machine.
- Execute G-code or simplified motion commands.

---

## 2) Common options

### Option A: GRBL firmware
Use GRBL if you want the Arduino to behave like a CNC controller.

**Good for:**
- G-code streaming.
- Simple setup.
- Standard CNC workflows.

**You do not write much custom motion code** in this case.

### Option B: Custom Arduino sketch
Use a custom sketch if you want to build the control logic yourself.

**Good for:**
- Final-year project explanation.
- Full control over pen-lift logic.
- Learning motor control.

---

## 3) Recommended Arduino sketch sections

### A. Library includes
Typical libraries:
- `Stepper.h` or `AccelStepper.h` for stepper control.
- `Servo.h` for pen lift.
- `SoftwareSerial.h` only if needed.

### B. Pin definitions
Define pins for:
- X step
- X direction
- Y step
- Y direction
- Enable
- Endstops
- Servo pin

### C. Machine constants
Store values such as:
- Steps per mm
- Max speed
- Acceleration
- Pen up angle
- Pen down angle
- Plot size

### D. Setup function
In `setup()`:
- Initialize serial communication.
- Set pin modes.
- Home the machine if needed.
- Move pen to safe position.

### E. Command parser
In `loop()`:
- Read incoming serial data line by line.
- Identify commands like:
  - `G0` rapid move
  - `G1` drawing move
  - `G28` home
  - pen up / pen down commands
- Convert commands into motor movement.

### F. Motion functions
Create helper functions such as:
- `moveTo(x, y)`
- `penUp()`
- `penDown()`
- `homeAxes()`
- `drawLine()`

---

## 4) Suggested logic flow

1. Computer sends a command.
2. Arduino reads the command.
3. Arduino parses the command.
4. If it is a movement command, calculate steps.
5. Move X/Y motors.
6. If it is a pen command, move the servo.
7. Send `ok` or status back to the PC.

---

## 5) Simple pseudo-structure

```cpp
#include <Servo.h>
#include <AccelStepper.h>

void setup() {
  Serial.begin(115200);
  pinMode(...);
  penUp();
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    parseCommand(cmd);
  }
}

void parseCommand(String cmd) {
  if (cmd starts with G0 or G1) move motors;
  if (cmd is pen up) lift pen;
  if (cmd is pen down) lower pen;
  if (cmd is G28) home axes;
}
```

---

## 6) If using GRBL

If you choose GRBL:
- Flash GRBL to the Arduino.
- Use G-code sender software.
- Only customize GRBL if you need special pen-lift support.

This is easier than writing a full motion controller yourself.

---

## 7) If using custom code

If you write your own firmware, start with:
- X/Y movement only.
- Then add pen up/down.
- Then add homing.
- Then add command parsing.
- Then add speed and acceleration.

That sequence is safest and easiest to debug.
