from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

import cv2
import numpy as np

Point = Tuple[float, float]
Path2D = List[Point]


def load_image_grayscale(image_path: str | Path) -> np.ndarray:
	image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
	if image is None:
		raise FileNotFoundError(f"Could not read image: {image_path}")
	return image


def binarize_image(gray: np.ndarray, threshold: int = 180, invert: bool = True) -> np.ndarray:
	mode = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
	_, binary = cv2.threshold(gray, threshold, 255, mode)
	return binary


def simplify_polyline(points: np.ndarray, tolerance_px: float = 1.5) -> np.ndarray:
	if len(points) < 3:
		return points
	return cv2.approxPolyDP(points, tolerance_px, False)


def contours_to_paths(
	contours: Sequence[np.ndarray],
	min_area_px: float = 10.0,
	simplify_tolerance_px: float = 1.5,
) -> List[Path2D]:
	paths: List[Path2D] = []
	for contour in contours:
		if cv2.contourArea(contour) < min_area_px:
			continue

		reduced = simplify_polyline(contour, simplify_tolerance_px)
		points = reduced.reshape(-1, 2)
		if len(points) < 2:
			continue

		path: Path2D = [(float(x), float(y)) for x, y in points]
		paths.append(path)
	return paths


def extract_paths_from_array(
	gray: np.ndarray,
	threshold: int = 180,
	invert: bool = True,
	min_area_px: float = 10.0,
	simplify_tolerance_px: float = 1.5,
) -> List[Path2D]:
	binary = binarize_image(gray, threshold=threshold, invert=invert)
	contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	return contours_to_paths(
		contours,
		min_area_px=min_area_px,
		simplify_tolerance_px=simplify_tolerance_px,
	)


def extract_paths_from_image(
	image_path: str | Path,
	threshold: int = 180,
	invert: bool = True,
	min_area_px: float = 10.0,
	simplify_tolerance_px: float = 1.5,
) -> List[Path2D]:
	gray = load_image_grayscale(image_path)
	return extract_paths_from_array(
		gray,
		threshold=threshold,
		invert=invert,
		min_area_px=min_area_px,
		simplify_tolerance_px=simplify_tolerance_px,
	)


def scale_paths(paths: Sequence[Path2D], mm_per_pixel: float = 0.2, flip_y: bool = True) -> List[Path2D]:
	if not paths:
		return []

	max_y = max(point[1] for path in paths for point in path)
	scaled: List[Path2D] = []
	for path in paths:
		out_path: Path2D = []
		for x, y in path:
			scaled_x = x * mm_per_pixel
			source_y = (max_y - y) if flip_y else y
			scaled_y = source_y * mm_per_pixel
			out_path.append((scaled_x, scaled_y))
		scaled.append(out_path)
	return scaled
