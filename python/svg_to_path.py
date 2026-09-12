from __future__ import annotations

from pathlib import Path
from typing import List

from svgpathtools import svg2paths

Point = tuple[float, float]
Path2D = List[Point]


def _sample_segment(segment, mm_per_unit: float, min_samples: int = 8) -> Path2D:
    segment_length = float(max(segment.length(error=1e-4), 1.0))
    samples = max(min_samples, int(segment_length / 4.0))
    points: Path2D = []
    for i in range(samples + 1):
        t = i / samples
        z = segment.point(t)
        points.append((z.real * mm_per_unit, z.imag * mm_per_unit))
    return points


def extract_paths_from_svg(svg_path: str | Path, mm_per_unit: float = 1.0) -> List[Path2D]:
    paths, _ = svg2paths(str(svg_path))
    extracted: List[Path2D] = []

    for curve_path in paths:
        polyline: Path2D = []
        for segment in curve_path:
            sampled = _sample_segment(segment, mm_per_unit)
            if polyline and sampled:
                sampled = sampled[1:]
            polyline.extend(sampled)

        if len(polyline) >= 2:
            extracted.append(polyline)

    return extracted