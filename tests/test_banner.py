from gng import banner


def test_no_line_wider_than_terminal():
    for width in range(8, 121):
        for line in banner.render_screen(width, color=False).split("\n"):
            assert len(line) <= width, (width, line)


def test_ascii_mode_is_ascii():
    for width in (20, 40, 60, 80):
        assert banner.render_screen(width, color=False, ascii_only=True).isascii()


def test_no_ansi_when_color_off():
    assert "\x1b" not in banner.render_screen(80, color=False)


def test_full_banner_frame_is_not_ragged():
    lines = banner.render_banner(80, color=False, tagline="hii lol").split("\n")
    assert len({len(line) for line in lines}) == 1


def test_color_depth_detection(monkeypatch):
    monkeypatch.setenv("COLORTERM", "truecolor")
    assert banner.color_depth() == "truecolor"
    monkeypatch.setenv("COLORTERM", "")
    monkeypatch.setenv("TERM", "xterm-256color")
    assert banner.color_depth() == "256"
    monkeypatch.setenv("TERM", "xterm")
    assert banner.color_depth() == "16"
