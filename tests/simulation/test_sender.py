import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from sender import GCodeSender, SETUP_COMMANDS


def test_sender_filters_setup_and_comments():
    sample_content = (
        "; Header comment\n"
        "G21 ; set to mm\n"
        "G90\n"
        "M5 (lift pen)\n"
        "G0 X10 Y10 F3000 ; travel\n"
        "M3 S30\n"
        "G1 X20 Y20 F1200\n"
        "M2\n"
        "; Footer comment\n"
    )

    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".gcode") as f:
        f.write(sample_content)
        temp_path = f.name

    try:
        sender = GCodeSender(port="/dev/null")
        sender.send_line = MagicMock(return_value="ok")

        # Test with filter_setup=True
        count = sender.stream_file(temp_path, filter_setup=True)
        # G21, G90, M2 should be skipped; comments should be stripped; remaining: M5, G0 X10 Y10 F3000, M3 S30, G1 X20 Y20 F1200
        assert count == 4
        sent_calls = [call[0][0] for call in sender.send_line.call_args_list]
        assert sent_calls == ["M5", "G0 X10 Y10 F3000", "M3 S30", "G1 X20 Y20 F1200"]

        # Test with filter_setup=False
        sender.send_line.reset_mock()
        count_all = sender.stream_file(temp_path, filter_setup=False)
        assert count_all == 7
        sent_all = [call[0][0] for call in sender.send_line.call_args_list]
        assert sent_all == [
            "G21",
            "G90",
            "M5",
            "G0 X10 Y10 F3000",
            "M3 S30",
            "G1 X20 Y20 F1200",
            "M2",
        ]
    finally:
        Path(temp_path).unlink(missing_ok=True)
