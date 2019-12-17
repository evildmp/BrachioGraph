import pytest

from brachiograph import BrachioGraph

virtual_bg = BrachioGraph(
    inner_arm=8,
    outer_arm=8,
    bounds=(-6, 4, 6, 12),
    virtual_mode=True
)


# ----------------- drawing methods -----------------

def test_plot_from_file():
    virtual_bg.plot_file("test-patterns/test-pattern.json")

def test_plot_from_file_with_prestart():
    virtual_bg.plot_file("test-patterns/test-pattern.json", pre_start=True)


# ----------------- test pattern methods -----------------

def test_test_pattern():
    virtual_bg.test_pattern()

def test_vertical_lines():
    virtual_bg.vertical_lines()

def test_horizontal_lines():
    virtual_bg.horizontal_lines()

def test_box():
    virtual_bg.box()


# ----------------- pen-moving methods -----------------

def test_centre():
    virtual_bg.centre()


# ----------------- reporting methods -----------------

def test_report():
    virtual_bg.report()


def test_maths_errors():
    plotter = BrachioGraph(
      inner_arm=8.2,
      outer_arm=8.85,
    )
    plotter.xy_to_angles(-10.2, 13.85)
