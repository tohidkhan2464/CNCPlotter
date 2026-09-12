# Serial Smoke Test

## Goal
Verify that firmware accepts commands and responds with `ok`.

## Procedure
1. Connect Arduino via USB.
2. Start serial monitor or run:
   - `python python/sender.py gcode/samples/smoke-square.gcode --port /dev/ttyUSB0 --baud 115200`
3. Manually test commands:
   - `M5`
   - `M3`
   - `G0 X5 Y5`
   - `M114`
4. Confirm no `error:` responses.

## Pass Criteria
- All commands receive `ok`.
- Axis moves in expected direction.
- Pen actuates visibly up/down.
