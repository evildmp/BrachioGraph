import pytest
from pytest import approx

from pantograph import PantoGraph

pg = PantoGraph(
    virtual=True, wait=0,
)

# ----------------- set-up tests -----------------


def test_initial_pulse_widths():
    # assert pg.get_pulse_widths() == (1500, 1500)
    assert (pg.angle_1, pg.angle_2) == (0, 0)


class TestTrigonometry:

    pg = PantoGraph(
        virtual=True,
        motor_1_pos=0,
        motor_2_pos=0,
    )

    def test_xy_to_angles(self):
        assert self.pg.xy_to_angles(0, 16) == approx((0, 0))
        assert self.pg.xy_to_angles(16, 0) == approx((90, 90))
        assert self.pg.xy_to_angles(-16, 0) == approx((-90, -90))
        assert self.pg.xy_to_angles(-8, 8) == approx((-90, 0))
        assert self.pg.xy_to_angles(8, 8) == approx((0, 90))
        assert self.pg.xy_to_angles(-8, 0) == approx((-150, -30))
        assert self.pg.xy_to_angles(0, 8) == approx((-60, 60))
        assert self.pg.xy_to_angles(8, 0) == approx((30, 150))

    def test_angles_to_xy(self):
        assert self.pg.angles_to_xy(-90, 0) == approx((-8, 8))
        assert self.pg.angles_to_xy(0, 90) == approx((8, 8))
        assert self.pg.angles_to_xy(-90, 90) == approx((0, 0))
        assert self.pg.angles_to_xy(-60, 60) == approx((0, 8))
        assert self.pg.angles_to_xy(-150, -30) == approx((-8, 0))

        # In these three cases, the xy position could actually be
        # anywhere on a circle around the elbows, so we just
        # assume that the arms are at 0˚
        assert self.pg.angles_to_xy(0, 0) == approx((0, 16))
        assert self.pg.angles_to_xy(90, 90) == approx((8, 8))
        assert self.pg.angles_to_xy(-90, -90) == approx((-8, 8))

    def test_angles_to_xy_and_back_again(self):
        angles = (-30, 30)
        xy = self.pg.angles_to_xy(angles[0], angles[1])
        assert self.pg.xy_to_angles(xy[0], xy[1]) == approx(angles)

        angles = (-40, 20)
        xy = self.pg.angles_to_xy(angles[0], angles[1])
        assert self.pg.xy_to_angles(xy[0], xy[1]) == approx(angles)

        angles = (0, 20)
        xy = self.pg.angles_to_xy(angles[0], angles[1])
        assert self.pg.xy_to_angles(xy[0], xy[1]) == approx(angles)

        angles = (0, 90)
        xy = self.pg.angles_to_xy(angles[0], angles[1])
        assert self.pg.xy_to_angles(xy[0], xy[1]) == approx(angles)

        angles = (5, 95)
        xy = self.pg.angles_to_xy(angles[0], angles[1])
        assert self.pg.xy_to_angles(xy[0], xy[1]) == approx(angles)

        for a1 in range(-120, 1):
            xy = self.pg.angles_to_xy(a1, 0)
            assert self.pg.xy_to_angles(xy[0], xy[1]) == approx((a1, 0))

    def test_xy_to_angles_and_back_again(self):
        xy = (5, 2)
        angles = self.pg.xy_to_angles(xy[0], xy[1])
        assert self.pg.angles_to_xy(angles[0], angles[1]) == approx(xy)

    def test_move_motors(self):
        self.pg.move_angles(-95, 30)
        self.angle_1 = -95
        self.angle_2 = 30


# # ----------------- drawing methods -----------------
#
# def test_plot_from_file():
#     bg.plot_file("test-patterns/accuracy.json")
#
#
# # ----------------- test pattern methods -----------------
#
# def test_test_pattern():
#     bg.test_pattern()
#
# def test_vertical_lines():
#     bg.vertical_lines()
#
# def test_horizontal_lines():
#     bg.horizontal_lines()
#
# def test_box():
#     pg.box()
#
#
# # ----------------- pen-moving methods -----------------
#
# def test_centre():
#     bg.park()
#
# def test_can_land_at_0_degrees():
#     bg.set_angles(0, 0)
#     assert (bg.angle_1, bg.angle_2) == (0, 0)
#
# # ----------------- reporting methods -----------------
#
# def test_report():
#     bg.report()
#
#
# def test_maths_errors():
#     plotter = BrachioGraph(
#         inner_arm=8.2,
#         outer_arm=8.85,
#         virtual=True
#     )
#     with pytest.raises(Exception):
#         plotter.xy_to_angles(-10.2, 13.85)
