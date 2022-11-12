from plotter import Plotter
from pytest import approx


class TestBasicPlotter:

    plotter = Plotter()

    def test_status_report(self):
        self.plotter.status()

    def test_defaults_of_default_plotter(self):
        assert (
            self.plotter.angles_to_pw_1 == self.plotter.naive_angles_to_pulse_widths_1
        )
        assert (
            self.plotter.angles_to_pw_2 == self.plotter.naive_angles_to_pulse_widths_2
        )
        assert self.plotter.get_pulse_widths() == (1500, 1500)

    def test_can_land_at_0_degrees(self):
        self.plotter.set_angles(0, 0)
        assert (self.plotter.angle_1, self.plotter.angle_2) == (0, 0)

    def test_xy(self):
        self.plotter.xy(0, 6)


class TestBiDiPlotter:

    plotter = Plotter(
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
        assert (
            self.plotter.angles_to_pw_1 != self.plotter.naive_angles_to_pulse_widths_1
        )

        assert self.plotter.angles_to_pw_1(-90) == approx(1894, abs=1e-0)
        assert self.plotter.angles_to_pw_2(90) == approx(1422, abs=1e-0)

        assert self.plotter.hysteresis_correction_1 == approx(5.416666)
        assert self.plotter.hysteresis_correction_2 == approx(-8.3)

        assert self.plotter.get_pulse_widths() == (
            approx(1054 + self.plotter.hysteresis_correction_1, abs=1e-0),
            approx(617 + self.plotter.hysteresis_correction_2, abs=1e-0),
        )
        assert (self.plotter.angle_1, self.plotter.angle_2) == (0, 0)
