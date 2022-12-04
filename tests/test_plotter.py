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
        assert (self.plotter.angles_to_pw_1 == self.plotter.sophisticated_angles_to_pulse_widths_1)
        assert (self.plotter.angles_to_pw_2 == self.plotter.sophisticated_angles_to_pulse_widths_2)

        assert self.plotter.angles_to_pw_1(-90) == approx(1894, abs=1e-0)
        assert self.plotter.angles_to_pw_1(-90, direction="asc") == approx(1900, abs=1e-0)
        assert self.plotter.angles_to_pw_1(-90, direction="des") == approx(1889, abs=1e-0)
        assert self.plotter.angles_to_pw_2(90) == approx(1422, abs=1e-0)
        assert self.plotter.angles_to_pw_2(90, direction="asc") == approx(1428, abs=1e-0)
        assert self.plotter.angles_to_pw_2(90, direction="des") == approx(1414, abs=1e-0)

        assert self.plotter.get_pulse_widths() == (approx(1054, abs=1e-0), approx(617, abs=1e-0))
        assert (self.plotter.angle_1, self.plotter.angle_2) == (0, 0)
