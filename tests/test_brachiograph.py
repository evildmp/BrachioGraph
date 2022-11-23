import pytest
from pytest import approx
import numpy

from brachiograph import BrachioGraph
import linedraw


class TestBrachioGraph:

    bg = BrachioGraph(servo_1_parked_pw=1570, servo_2_parked_pw=1450, wait=0)

    def test_defaults_of_default_bg(self):
        assert (self.bg.angle_1, self.bg.angle_2) == (-90, 90)

    def test_parked_pws_correctly_assigned(self):
        assert (self.bg.servo_1_parked_pw, self.bg.servo_2_parked_pw) == (1570, 1450)


class TestBiDiBrachioGraph:

    bg = BrachioGraph(
        virtual=True,
        wait=0,
        servo_1_angle_pws_bidi={
            -135: {"cw": 2374, "acw": 2386},
            -120: {"cw": 2204, "acw": 2214},
            -105: {"cw": 2042, "acw": 2054},
            -90: {"cw": 1898, "acw": 1900},
            -75: {"cw": 1730, "acw": 1750},
            -60: {"cw": 1604, "acw": 1612},
            -45: {"cw": 1466, "acw": 1476},
            -30: {"cw": 1330, "acw": 1340},
            -15: {"cw": 1188, "acw": 1200},
            0: {"cw": 1048, "acw": 1060},
            15: {"cw": 904, "acw": 910},
            30: {"cw": 750, "acw": 766},
        },
        servo_2_angle_pws_bidi={
            15: {"cw": 783, "acw": 761},
            30: {"cw": 917, "acw": 901},
            45: {"cw": 1053, "acw": 1035},
            60: {"cw": 1183, "acw": 1167},
            75: {"cw": 1303, "acw": 1287},
            90: {"cw": 1427, "acw": 1417},
            105: {"cw": 1557, "acw": 1537},
            120: {"cw": 1697, "acw": 1681},
            135: {"cw": 1843, "acw": 1827},
            150: {"cw": 2003, "acw": 1987},
        },
        pw_up=1400,  # pulse-widths for pen up/down
        pw_down=1650,
    )

    def test_defaults_of_bg_with_bidi_pws(self):
        assert self.bg.get_pulse_widths() == (1899, 1412)
        assert (self.bg.angle_1, self.bg.angle_2) == (-90, 90)

    # ----------------- drawing methods -----------------

    def test_plot_from_file(self):
        self.bg.plot_file("test-patterns/accuracy.json")

    # ----------------- test pattern methods -----------------

    def test_test_pattern(self):
        self.bg.test_pattern()

    def test_vertical_lines(self):
        self.bg.vertical_lines()

    def test_horizontal_lines(self):
        self.bg.horizontal_lines()

    def test_box(self):
        self.bg.box()

    # ----------------- pen-moving methods -----------------

    def test_centre(self):
        self.bg.park()

    # ----------------- reporting methods -----------------

    def test_report(self):
        self.bg.report()


class TestErrors:
    def test_maths_errors(self):
        plotter = BrachioGraph(inner_arm=8.2, outer_arm=8.85, virtual=True, wait=0)
        with pytest.raises(Exception):
            plotter.xy_to_angles(-10.2, 13.85)
