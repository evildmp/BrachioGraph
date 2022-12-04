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
            -135: {"asc": 2374, "des": 2386},
            -120: {"asc": 2204, "des": 2214},
            -105: {"asc": 2042, "des": 2054},
            -90: {"asc": 1898, "des": 1900},
            -75: {"asc": 1730, "des": 1750},
            -60: {"asc": 1604, "des": 1612},
            -45: {"asc": 1466, "des": 1476},
            -30: {"asc": 1330, "des": 1340},
            -15: {"asc": 1188, "des": 1200},
            0: {"asc": 1048, "des": 1060},
            15: {"asc": 904, "des": 910},
            30: {"asc": 750, "des": 766},
        },
        servo_2_angle_pws_bidi={
            15: {"asc": 783, "des": 761},
            30: {"asc": 917, "des": 901},
            45: {"asc": 1053, "des": 1035},
            60: {"asc": 1183, "des": 1167},
            75: {"asc": 1303, "des": 1287},
            90: {"asc": 1427, "des": 1417},
            105: {"asc": 1557, "des": 1537},
            120: {"asc": 1697, "des": 1681},
            135: {"asc": 1843, "des": 1827},
            150: {"asc": 2003, "des": 1987},
        },
        pw_up=1400,  # pulse-widths for pen up/down
        pw_down=1650,
    )

    def test_defaults_of_bg_with_bidi_pws(self):
        assert self.bg.get_pulse_widths() == (1894, 1421)
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
