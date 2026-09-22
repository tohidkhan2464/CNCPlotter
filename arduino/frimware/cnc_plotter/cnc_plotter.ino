#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Servo.h>

// CNC shield style pins (adjust to your board/wiring).
const uint8_t X_STEP_PIN = 2;
const uint8_t Y_STEP_PIN = 3;
const uint8_t X_DIR_PIN = 5;
const uint8_t Y_DIR_PIN = 6;
const uint8_t ENABLE_PIN = 8;

const uint8_t X_MIN_PIN = 9;
const uint8_t Y_MIN_PIN = 10;

const uint8_t PEN_SERVO_PIN = 12;

const float STEPS_PER_MM_X = 80.0;
const float STEPS_PER_MM_Y = 80.0;

const float MAX_SPEED_STEPS = 1800.0;
const float ACCEL_STEPS = 900.0;

const int PEN_UP_ANGLE = 90;
const int PEN_DOWN_ANGLE = 30;

const long HOME_TRAVEL_STEPS = 12000;

AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
MultiStepper steppers;
Servo penServo;

float currentXmm = 0.0;
float currentYmm = 0.0;
bool absoluteMode = true;

String commandBuffer;


float stepsToMmX(long steps) {
	return ((float)steps) / STEPS_PER_MM_X;
}


float stepsToMmY(long steps) {
	return ((float)steps) / STEPS_PER_MM_Y;
}


long mmToStepsX(float mm) {
	return lround(mm * STEPS_PER_MM_X);
}


long mmToStepsY(float mm) {
	return lround(mm * STEPS_PER_MM_Y);
}


void penUp() {
	penServo.write(PEN_UP_ANGLE);
	delay(150);
}


void penDown(int angle = PEN_DOWN_ANGLE) {
	penServo.write(angle);
	delay(150);
}


bool readAxisValue(const String &cmd, char axis, float &outVal) {
	int idx = cmd.indexOf(axis);
	if (idx < 0) {
		return false;
	}

	int start = idx + 1;
	int end = start;
	while (end < cmd.length()) {
		char c = cmd.charAt(end);
		if ((c >= '0' && c <= '9') || c == '-' || c == '+' || c == '.') {
			end++;
			continue;
		}
		break;
	}

	outVal = cmd.substring(start, end).toFloat();
	return true;
}


void moveTo(float targetXmm, float targetYmm) {
	long targets[2];
	targets[0] = mmToStepsX(targetXmm);
	targets[1] = mmToStepsY(targetYmm);

	steppers.moveTo(targets);
	steppers.runSpeedToPosition();

	currentXmm = targetXmm;
	currentYmm = targetYmm;
}


void reportPosition() {
	Serial.print("X:");
	Serial.print(currentXmm, 3);
	Serial.print(" Y:");
	Serial.println(currentYmm, 3);
}


void homeAxes() {
	// Home X toward the negative direction until endstop or soft travel limit.
	stepperX.setMaxSpeed(MAX_SPEED_STEPS / 2.0);
	stepperX.moveTo(-HOME_TRAVEL_STEPS);
	while (stepperX.distanceToGo() != 0 && digitalRead(X_MIN_PIN) == HIGH) {
		stepperX.run();
	}
	stepperX.stop();
	stepperX.runToPosition();
	stepperX.setCurrentPosition(0);

	// Home Y toward the negative direction until endstop or soft travel limit.
	stepperY.setMaxSpeed(MAX_SPEED_STEPS / 2.0);
	stepperY.moveTo(-HOME_TRAVEL_STEPS);
	while (stepperY.distanceToGo() != 0 && digitalRead(Y_MIN_PIN) == HIGH) {
		stepperY.run();
	}
	stepperY.stop();
	stepperY.runToPosition();
	stepperY.setCurrentPosition(0);

	stepperX.setMaxSpeed(MAX_SPEED_STEPS);
	stepperY.setMaxSpeed(MAX_SPEED_STEPS);

	currentXmm = 0.0;
	currentYmm = 0.0;
}


void processCommand(String cmd) {
	// Strip inline comments starting with ';'
	int commentIdx = cmd.indexOf(';');
	if (commentIdx >= 0) {
		cmd = cmd.substring(0, commentIdx);
	}

	// Strip inline comments wrapped in '(...)'
	int parenIdx = cmd.indexOf('(');
	if (parenIdx >= 0) {
		int parenEnd = cmd.indexOf(')', parenIdx);
		if (parenEnd >= 0) {
			cmd = cmd.substring(0, parenIdx) + cmd.substring(parenEnd + 1);
		} else {
			cmd = cmd.substring(0, parenIdx);
		}
	}

	cmd.trim();
	cmd.toUpperCase();
	if (cmd.length() == 0) {
		Serial.println("ok");
		return;
	}

	// Linear / Rapid moves
	if (cmd.startsWith("G0") || cmd.startsWith("G1")) {
		float targetX = currentXmm;
		float targetY = currentYmm;
		float xVal = 0.0;
		float yVal = 0.0;

		if (readAxisValue(cmd, 'X', xVal)) {
			targetX = absoluteMode ? xVal : (currentXmm + xVal);
		}
		if (readAxisValue(cmd, 'Y', yVal)) {
			targetY = absoluteMode ? yVal : (currentYmm + yVal);
		}

		moveTo(targetX, targetY);
		Serial.println("ok");
		return;
	}

	// Units: Millimeters (G21) / Inches (G20)
	if (cmd.startsWith("G21")) {
		Serial.println("ok");
		return;
	}
	if (cmd.startsWith("G20")) {
		Serial.println("error: inches mode (G20) not supported, use millimeters (G21)");
		return;
	}

	// Distance mode: Absolute (G90) / Incremental (G91)
	if (cmd.startsWith("G90")) {
		absoluteMode = true;
		Serial.println("ok");
		return;
	}
	if (cmd.startsWith("G91")) {
		absoluteMode = false;
		Serial.println("ok");
		return;
	}

	// Set Position (G92)
	if (cmd.startsWith("G92")) {
		readAxisValue(cmd, 'X', currentXmm);
		readAxisValue(cmd, 'Y', currentYmm);
		stepperX.setCurrentPosition(mmToStepsX(currentXmm));
		stepperY.setCurrentPosition(mmToStepsY(currentYmm));
		Serial.println("ok");
		return;
	}

	// Dwell (G4)
	if (cmd.startsWith("G4")) {
		float pVal = 0.0;
		if (readAxisValue(cmd, 'P', pVal)) {
			delay((unsigned long)pVal);
		} else if (readAxisValue(cmd, 'S', pVal)) {
			delay((unsigned long)(pVal * 1000.0));
		}
		Serial.println("ok");
		return;
	}

	// Homing (G28)
	if (cmd.startsWith("G28")) {
		homeAxes();
		Serial.println("ok");
		return;
	}

	// Program End (M2, M30)
	if (cmd.startsWith("M2") || cmd.startsWith("M30")) {
		penUp();
		Serial.println("ok");
		return;
	}

	// Custom servo angle (M300 S<angle>) - check before M3 to avoid prefix shadowing
	if (cmd.startsWith("M300")) {
		float sVal = 0.0;
		if (readAxisValue(cmd, 'S', sVal)) {
			penServo.write((int)sVal);
			delay(150);
			Serial.println("ok");
			return;
		}
	}

	// Pen down (M3, optionally with S<angle>)
	if (cmd.startsWith("M3")) {
		float sVal = 0.0;
		if (readAxisValue(cmd, 'S', sVal)) {
			penDown((int)sVal);
		} else {
			penDown();
		}
		Serial.println("ok");
		return;
	}

	// Pen up (M5)
	if (cmd.startsWith("M5")) {
		penUp();
		Serial.println("ok");
		return;
	}

	// Report current position (M114)
	if (cmd.startsWith("M114")) {
		reportPosition();
		Serial.println("ok");
		return;
	}

	Serial.print("error: unsupported command: ");
	Serial.println(cmd);
}


void readSerialCommands() {
	while (Serial.available() > 0) {
		char c = (char)Serial.read();
		if (c == '\n' || c == '\r') {
			if (commandBuffer.length() > 0) {
				processCommand(commandBuffer);
				commandBuffer = "";
			}
			continue;
		}
		commandBuffer += c;
	}
}


void setup() {
	Serial.begin(115200);

	pinMode(ENABLE_PIN, OUTPUT);
	digitalWrite(ENABLE_PIN, LOW);

	pinMode(X_MIN_PIN, INPUT_PULLUP);
	pinMode(Y_MIN_PIN, INPUT_PULLUP);

	penServo.attach(PEN_SERVO_PIN);
	penUp();

	stepperX.setMaxSpeed(MAX_SPEED_STEPS);
	stepperX.setAcceleration(ACCEL_STEPS);
	stepperY.setMaxSpeed(MAX_SPEED_STEPS);
	stepperY.setAcceleration(ACCEL_STEPS);

	steppers.addStepper(stepperX);
	steppers.addStepper(stepperY);

	Serial.println("CNC plotter ready");
	Serial.println("ok");
}


void loop() {
	readSerialCommands();
}
