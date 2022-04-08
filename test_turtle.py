import pytest

from turtle_draw import BrachioGraphTurtle

bgt = BrachioGraphTurtle(inner_arm=9, shoulder_centre_angle=-45, shoulder_sweep=120, outer_arm=7.5,  elbow_centre_angle=95, elbow_sweep=120)

def test_grid():
    bgt.draw_grid()


def test_outline():
    bgt.draw_outline()
