# Wiring Diagram Notes

This file describes the firmware pin map used in [arduino/frimware/cnc_plotter.ino](../arduino/frimware/cnc_plotter.ino).

## Firmware Pin Map

| Function | Pin |
|---|---:|
| X step | D2 |
| Y step | D3 |
| X dir | D5 |
| Y dir | D6 |
| Driver enable | D8 |
| X min endstop | D9 |
| Y min endstop | D10 |
| Pen servo signal | D11 |

## Wiring Blocks

1. Stepper drivers and motors
- Install X and Y stepper drivers on CNC shield.
- Confirm driver orientation (EN pin alignment).
- Connect X motor to X driver output, Y motor to Y driver output.

2. Endstops
- Use `INPUT_PULLUP` style wiring:
  - Switch between signal pin and GND.
  - X endstop to D9, Y endstop to D10.
- Triggered state should read `LOW`.

3. Pen servo
- Signal wire to D11.
- Power from stable 5V source.
- Common ground between servo supply and Arduino ground is required.

4. Power
- 12V to CNC shield motor power input.
- USB can be used for logic/programming.
- Verify your shield power-jumper arrangement before powering both USB and external supply.

## Bring-Up Checklist

1. Power off before plugging drivers.
2. Set current limit on each stepper driver.
3. Power on and upload firmware.
4. Test commands in serial monitor (115200 baud):
	- `M5` pen up
	- `M3` pen down
	- `G0 X5 Y5` short move
	- Manually trigger endstops then run `G28`
5. If axis direction is reversed:
	- flip dir logic in wiring/firmware or invert motor connector.

## Caution

- Do not hot-swap stepper motors while powered.
- Incorrect driver orientation can permanently damage the driver.
