from __future__ import annotations

from pathlib import Path
from typing import List

import fitz
import numpy as np

from image_to_path import Path2D, extract_paths_from_array


def extract_paths_from_pdf(
	pdf_path: str | Path,
	page_index: int = 0,
	dpi: int = 200,
	threshold: int = 180,
	invert: bool = True,
	min_area_px: float = 10.0,
	simplify_tolerance_px: float = 1.5,
) -> List[Path2D]:
	pdf = fitz.open(str(pdf_path))
	try:
		if page_index < 0 or page_index >= pdf.page_count:
			raise ValueError(
				f"Invalid page index {page_index}. PDF has {pdf.page_count} page(s)."
			)

		page = pdf[page_index]
		zoom = dpi / 72.0
		matrix = fitz.Matrix(zoom, zoom)
		pix = page.get_pixmap(matrix=matrix, alpha=False)

		image_data = np.frombuffer(pix.samples, dtype=np.uint8)
		image_data = image_data.reshape((pix.height, pix.width, pix.n))

		if pix.n == 1:
			gray = image_data
		else:
			# Weighted RGB grayscale conversion.
			gray = (
				0.299 * image_data[:, :, 0]
				+ 0.587 * image_data[:, :, 1]
				+ 0.114 * image_data[:, :, 2]
			).astype(np.uint8)

		return extract_paths_from_array(
			gray,
			threshold=threshold,
			invert=invert,
			min_area_px=min_area_px,
			simplify_tolerance_px=simplify_tolerance_px,
		)
	finally:
		pdf.close()
