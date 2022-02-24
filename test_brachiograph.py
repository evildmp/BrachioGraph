import pytest

from brachiograph import BrachioGraph
import linedraw

bg = BrachioGraph(
    inner_arm=8,
    outer_arm=8,
    bounds=(-6, 4, 6, 12),
    virtual=True,
)

# ----------------- set-up tests -----------------

def test_initial_pulse_widths():
    assert bg.get_pulse_widths() == (1800, 1500)

# ----------------- drawing methods -----------------

def test_plot_from_file():
    bg.plot_file("test-patterns/accuracy.json")


# ----------------- test pattern methods -----------------

def test_test_pattern():
    bg.test_pattern()

def test_vertical_lines():
    bg.vertical_lines()

def test_horizontal_lines():
    bg.horizontal_lines()

def test_box():
    bg.box()


# ----------------- pen-moving methods -----------------

def test_centre():
    bg.park()


# ----------------- reporting methods -----------------

def test_report():
    bg.report()


def test_maths_errors():
    plotter = BrachioGraph(
        inner_arm=8.2,
        outer_arm=8.85,
        virtual=True
    )
    with pytest.raises(Exception):
        plotter.xy_to_angles(-10.2, 13.85)
