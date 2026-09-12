from path_to_gcode import GCodeConfig, generate_gcode, optimize_paths


def test_generate_gcode_has_expected_markers() -> None:
    paths = [[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]]
    gcode = generate_gcode(paths, GCodeConfig())

    assert gcode[0].startswith("; Generated")
    assert "G21" in gcode
    assert "G90" in gcode
    assert "M3 S30" in gcode
    assert "M5" in gcode
    assert gcode[-2] == "M2"


def test_optimize_paths_reorders_by_nearest_start() -> None:
    paths = [
        [(50.0, 0.0), (60.0, 0.0)],
        [(5.0, 0.0), (10.0, 0.0)],
    ]
    optimized = optimize_paths(paths, start=(0.0, 0.0))
    assert optimized[0][0] == (5.0, 0.0)
