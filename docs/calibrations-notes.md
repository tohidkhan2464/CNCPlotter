# Calibration Notes

Use this procedure after first assembly and whenever mechanics or pen type changes.

## 1) Steps per mm

Target: axis movement in code matches physical movement.

1. Lift pen (`M5`).
2. Send `G0 X20 Y0` and measure actual X displacement.
3. Update `STEPS_PER_MM_X` using:

	new_steps_per_mm = old_steps_per_mm * (commanded_distance / measured_distance)

4. Repeat for Y with `G0 X0 Y20` and update `STEPS_PER_MM_Y`.

## 2) Pen Up / Pen Down angles

Tune in firmware:
- `PEN_UP_ANGLE`
- `PEN_DOWN_ANGLE`

Requirements:
- Pen up clears paper during travel.
- Pen down writes with consistent pressure, not scratching.

## 3) Homing

1. Ensure endstops are wired as active-low.
2. Run `G28`.
3. Verify motion goes toward min switches.
4. If moving wrong direction, fix wiring/logic before repeating.

## 4) Feed Rates

In Python G-code generation:
- `--travel-feed` for non-drawing moves.
- `--draw-feed` for drawing quality.

Start conservative:
- Travel: 2000-3000 mm/min
- Draw: 600-1200 mm/min

Increase gradually while checking for skipped steps and line wobble.

## 5) Verification Pattern

Plot a test file with:
- 20 x 20 mm square
- 50 mm horizontal and vertical lines
- small circle/curve

Record:
- dimension error
- corner squareness
- pen lift cleanliness

Store each run's G-code in `gcode/samples/` and notes in `tests/machine-tests/`.
