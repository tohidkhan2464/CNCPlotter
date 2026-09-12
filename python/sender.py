from __future__ import annotations

import argparse
import time
from pathlib import Path

import serial


import re

SETUP_COMMANDS = {"G20", "G21", "G90", "G91", "M2", "M30"}


class GCodeSender:
	def __init__(
		self,
		port: str,
		baudrate: int = 115200,
		timeout: float = 1.0,
		startup_delay: float = 2.0,
	) -> None:
		self.port = port
		self.baudrate = baudrate
		self.timeout = timeout
		self.startup_delay = startup_delay
		self.serial_conn: serial.Serial | None = None

	def __enter__(self) -> "GCodeSender":
		self.connect()
		return self

	def __exit__(self, exc_type, exc, tb) -> None:
		self.close()

	def connect(self) -> None:
		self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
		time.sleep(self.startup_delay)
		self.serial_conn.reset_input_buffer()
		self.serial_conn.reset_output_buffer()

	def close(self) -> None:
		if self.serial_conn and self.serial_conn.is_open:
			self.serial_conn.close()

	def _require_connection(self) -> serial.Serial:
		if self.serial_conn is None or not self.serial_conn.is_open:
			raise RuntimeError("Serial connection is not open")
		return self.serial_conn

	def send_line(
		self,
		line: str,
		wait_for_ok: bool = True,
		ignore_errors: bool = False,
	) -> str | None:
		conn = self._require_connection()
		payload = line.strip()
		if not payload:
			return None

		conn.write((payload + "\n").encode("utf-8"))
		conn.flush()

		if not wait_for_ok:
			return None

		while True:
			response = conn.readline().decode("utf-8", errors="ignore").strip()
			if not response:
				continue
			if response.lower() == "ok":
				return response
			if response.lower().startswith("error"):
				if ignore_errors:
					print(f"[WARNING] Controller reported error for '{payload}': {response} (ignored)")
					return response
				raise RuntimeError(f"Controller error for '{payload}': {response}")

	def stream_file(
		self,
		file_path: str,
		wait_for_ok: bool = True,
		ignore_errors: bool = False,
		filter_setup: bool = False,
	) -> int:
		line_count = 0
		with open(file_path, "r", encoding="utf-8") as handle:
			for raw in handle:
				clean = raw.split(";")[0]
				if "(" in clean and ")" in clean:
					clean = re.sub(r"\(.*?\)", "", clean)
				line = clean.strip()
				if not line:
					continue
				cmd_token = line.split()[0].upper()
				if filter_setup and cmd_token in SETUP_COMMANDS:
					continue
				self.send_line(line, wait_for_ok=wait_for_ok, ignore_errors=ignore_errors)
				line_count += 1
		return line_count


def stream_gcode_file(
	file_path: str,
	port: str,
	baudrate: int = 115200,
	wait_for_ok: bool = True,
	startup_delay: float = 2.0,
	ignore_errors: bool = False,
	filter_setup: bool = False,
) -> None:
	with GCodeSender(port=port, baudrate=baudrate, startup_delay=startup_delay) as sender:
		sent = sender.stream_file(
			file_path=file_path,
			wait_for_ok=wait_for_ok,
			ignore_errors=ignore_errors,
			filter_setup=filter_setup,
		)
		print(f"Sent {sent} command lines to {port} at {baudrate} baud")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Stream G-code file to a serial plotter")
	parser.add_argument("file", type=Path, help="Path to .gcode file")
	parser.add_argument("--port", required=True, help="Serial port, e.g. /dev/ttyUSB0")
	parser.add_argument("--baud", type=int, default=115200)
	parser.add_argument("--wait-ok", action=argparse.BooleanOptionalAction, default=True)
	parser.add_argument("--startup-delay", type=float, default=2.0)
	parser.add_argument(
		"--ignore-errors",
		action="store_true",
		help="Log warnings on controller error responses instead of aborting stream",
	)
	parser.add_argument(
		"--filter-setup",
		action="store_true",
		help="Skip non-motion setup codes (G20, G21, G90, G91, M2, M30) for legacy controllers",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	if not args.file.exists():
		raise FileNotFoundError(f"G-code file not found: {args.file}")
	stream_gcode_file(
		file_path=str(args.file.resolve()),
		port=args.port,
		baudrate=args.baud,
		wait_for_ok=args.wait_ok,
		startup_delay=args.startup_delay,
		ignore_errors=args.ignore_errors,
		filter_setup=args.filter_setup,
	)


if __name__ == "__main__":
	main()
