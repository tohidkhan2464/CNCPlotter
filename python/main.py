from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from image_to_path import Path2D, extract_paths_from_image, scale_paths
from path_to_gcode import GCodeConfig, generate_gcode, optimize_paths, save_gcode
from pdf_to_path import extract_paths_from_pdf
from sender import stream_gcode_file
from svg_to_path import extract_paths_from_svg


def _default_output_path(input_path: Path) -> Path:
	repo_root = Path(__file__).resolve().parents[1]
	generated = repo_root / "gcode" / "generated"
	generated.mkdir(parents=True, exist_ok=True)
	return generated / f"{input_path.stem}.gcode"


def _load_paths(args: argparse.Namespace) -> List[Path2D]:
	suffix = args.input.suffix.lower()
	if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}:
		raw_paths = extract_paths_from_image(
			args.input,
			threshold=args.threshold,
			invert=args.invert,
			min_area_px=args.min_area,
			simplify_tolerance_px=args.simplify,
		)
		return scale_paths(raw_paths, mm_per_pixel=args.mm_per_pixel, flip_y=True)

	if suffix == ".pdf":
		raw_paths = extract_paths_from_pdf(
			args.input,
			page_index=args.page,
			dpi=args.dpi,
			threshold=args.threshold,
			invert=args.invert,
			min_area_px=args.min_area,
			simplify_tolerance_px=args.simplify,
		)
		return scale_paths(raw_paths, mm_per_pixel=args.mm_per_pixel, flip_y=True)

	if suffix == ".svg":
		return extract_paths_from_svg(args.input, mm_per_unit=args.mm_per_pixel)

	raise ValueError(f"Unsupported input format: {suffix}")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Convert image/PDF/SVG artwork into plotter-ready G-code."
	)
	parser.add_argument("input", type=Path, help="Input file (.png/.jpg/.pdf/.svg)")
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		default=None,
		help="Output G-code file path (default: gcode/generated/<input>.gcode)",
	)

	parser.add_argument("--threshold", type=int, default=180)
	parser.add_argument("--invert", action=argparse.BooleanOptionalAction, default=True)
	parser.add_argument("--simplify", type=float, default=1.5, help="Polyline simplify tolerance (px)")
	parser.add_argument("--min-area", type=float, default=10.0, help="Minimum contour area in px")
	parser.add_argument("--mm-per-pixel", type=float, default=0.2)

	parser.add_argument("--page", type=int, default=0, help="PDF page index")
	parser.add_argument("--dpi", type=int, default=200, help="PDF rasterization DPI")

	parser.add_argument("--draw-feed", type=int, default=1200)
	parser.add_argument("--travel-feed", type=int, default=3000)
	parser.add_argument("--pen-up-cmd", default="M5")
	parser.add_argument("--pen-down-cmd", default="M3 S30")
	parser.add_argument("--no-optimize", action="store_true")

	parser.add_argument("--send", action="store_true", help="Stream generated G-code to serial")
	parser.add_argument("--port", default="/dev/ttyUSB0")
	parser.add_argument("--baud", type=int, default=115200)
	parser.add_argument("--wait-ok", action=argparse.BooleanOptionalAction, default=True)
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
	args.input = args.input.resolve()

	if not args.input.exists():
		raise FileNotFoundError(f"Input file not found: {args.input}")

	paths = _load_paths(args)
	if not args.no_optimize:
		paths = optimize_paths(paths)

	config = GCodeConfig(
		draw_feed_mm_min=args.draw_feed,
		travel_feed_mm_min=args.travel_feed,
		pen_up_cmd=args.pen_up_cmd,
		pen_down_cmd=args.pen_down_cmd,
	)
	gcode_lines = generate_gcode(paths, config=config)

	output_path = args.output.resolve() if args.output else _default_output_path(args.input)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	save_gcode(gcode_lines, str(output_path))

	print(f"Paths: {len(paths)}")
	print(f"G-code lines: {len(gcode_lines)}")
	print(f"Saved: {output_path}")

	if args.send:
		stream_gcode_file(
			file_path=str(output_path),
			port=args.port,
			baudrate=args.baud,
			wait_for_ok=args.wait_ok,
			ignore_errors=args.ignore_errors,
			filter_setup=args.filter_setup,
		)


if __name__ == "__main__":
	main()
