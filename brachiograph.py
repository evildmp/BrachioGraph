# coding=utf-8

from time import sleep
import readchar
import math
import numpy
from plotter import Plotter


class BrachioGraph(Plotter):
    """A shoulder-and-elbow drawing robot class."""

    def __init__(
        self,
        virtual: bool = False,  # a virtual plotter runs in software only
        turtle: bool = False,  # create a turtle graphics plotter
        turtle_coarseness=None,  # a factor in degrees representing servo resolution
        #  ----------------- geometry of the plotter -----------------
        bounds: tuple = [-8, 4, 6, 13],  # the maximum rectangular drawing area
        inner_arm: float = 8,  # the lengths of the arms
        outer_arm: float = 8,
        #  ----------------- naive calculation values -----------------
        servo_1_parked_pw: int = 1500,  # pulse-widths when parked
        servo_2_parked_pw: int = 1500,
        servo_1_degree_ms: int = -10,  # milliseconds pulse-width per degree
        servo_2_degree_ms: int = 10,  # reversed for the mounting of the shoulder servo
        servo_1_parked_angle: int = -90,  # the arm angle in the parked position
        servo_2_parked_angle: int = 90,
        #  ----------------- hysteresis -----------------
        hysteresis_correction_1: int = 0,  # hardware error compensation
        hysteresis_correction_2: int = 0,
        #  ----------------- servo angles and pulse-widths in lists -----------------
        servo_1_angle_pws: tuple = [],  # pulse-widths for various angles
        servo_2_angle_pws: tuple = [],
        #  ----------------- servo angles and pulse-widths in lists (bi-directional) ------
        servo_1_angle_pws_bidi: tuple = [],  # bi-directional pulse-widths for various angles
        servo_2_angle_pws_bidi: tuple = [],
        #  ----------------- the pen -----------------
        pw_up: int = 1500,  # pulse-widths for pen up/down
        pw_down: int = 1100,
        #  ----------------- physical control -----------------
        wait: float = None,  # default wait time between operations
        angular_step: float = None,  # default step of the servos in degrees
        resolution: float = None,  # default resolution of the plotter in cm
    ):

        # set the geometry
        self.inner_arm = inner_arm
        self.outer_arm = outer_arm

        # Set the x and y position state, so it knows its current x/y position.
        self.x = -self.inner_arm
        self.y = self.outer_arm

        super().__init__(
            bounds=bounds,
            servo_1_parked_pw=servo_1_parked_pw,
            servo_2_parked_pw=servo_2_parked_pw,
            servo_1_degree_ms=servo_1_degree_ms,
            servo_2_degree_ms=servo_2_degree_ms,
            servo_1_parked_angle=servo_1_parked_angle,
            servo_2_parked_angle=servo_2_parked_angle,
            hysteresis_correction_1=hysteresis_correction_1,
            hysteresis_correction_2=hysteresis_correction_2,
            servo_1_angle_pws=servo_1_angle_pws,
            servo_2_angle_pws=servo_2_angle_pws,
            servo_1_angle_pws_bidi=servo_1_angle_pws_bidi,
            servo_2_angle_pws_bidi=servo_2_angle_pws_bidi,
            pw_up=pw_up,
            pw_down=pw_down,
            wait=wait,
            angular_step=angular_step,
            resolution=resolution,
            virtual=virtual,
            turtle=turtle,
            turtle_coarseness=turtle_coarseness,
        )

    def setup_turtle(self, coarseness):
        
        from turtle_plotter import BrachioGraphTurtle

        self.turtle = BrachioGraphTurtle(
            inner_arm=self.inner_arm,  # the length of the inner arm (blue)
            outer_arm=self.outer_arm,  # the length of the outer arm (red)
            shoulder_centre_angle=-90,  # the starting angle of the inner arm, relative to straight ahead
            shoulder_sweep=180,  # the arc covered by the shoulder motor
            elbow_centre_angle=90,  # the centre of the outer arm relative to the inner arm
            elbow_sweep=180,  # the arc covered by the elbow motor
            window_size=850,  # width and height of the turtle canvas
            speed=10,  # how fast to draw
            machine=self,
            coarseness=coarseness,
        )

        self.turtle.draw_grid()
        self.t = self.turtle

    def test_arcs(self):
        self.park()
        elbow_angle = 120
        self.move_angles(angle_2=elbow_angle)

        for angle_1 in range(-135, 15, 15):
            self.move_angles(angle_1=angle_1, draw=True)

            for angle_2 in range(elbow_angle, elbow_angle + 16):
                self.move_angles(angle_2=angle_2, draw=True)
            for angle_2 in range(elbow_angle + 16, elbow_angle - 16, -1):
                self.move_angles(angle_2=angle_2, draw=True)
            for angle_2 in range(elbow_angle - 16, elbow_angle + 1):
                self.move_angles(angle_2=angle_2, draw=True)

    # ----------------- trigonometric methods -----------------

    def xy_to_angles(self, x=0, y=0):
        """Return the servo angles required to reach any x/y position."""

        hypotenuse = math.sqrt(x**2 + y**2)

        if hypotenuse > self.inner_arm + self.outer_arm:
            raise Exception(
                f"Cannot reach {hypotenuse}; total arm length is {self.inner_arm + self.outer_arm}"
            )

        hypotenuse_angle = math.asin(x / hypotenuse)

        inner_angle = math.acos(
            (hypotenuse**2 + self.inner_arm**2 - self.outer_arm**2)
            / (2 * hypotenuse * self.inner_arm)
        )
        outer_angle = math.acos(
            (self.inner_arm**2 + self.outer_arm**2 - hypotenuse**2)
            / (2 * self.inner_arm * self.outer_arm)
        )

        shoulder_motor_angle = hypotenuse_angle - inner_angle
        elbow_motor_angle = math.pi - outer_angle

        return (math.degrees(shoulder_motor_angle), math.degrees(elbow_motor_angle))

    def angles_to_xy(self, shoulder_motor_angle, elbow_motor_angle):
        """Return the x/y co-ordinates represented by a pair of servo angles."""

        elbow_motor_angle = math.radians(elbow_motor_angle)
        shoulder_motor_angle = math.radians(shoulder_motor_angle)

        hypotenuse = math.sqrt(
            (
                self.inner_arm**2
                + self.outer_arm**2
                - 2
                * self.inner_arm
                * self.outer_arm
                * math.cos(math.pi - elbow_motor_angle)
            )
        )
        base_angle = math.acos(
            (hypotenuse**2 + self.inner_arm**2 - self.outer_arm**2)
            / (2 * hypotenuse * self.inner_arm)
        )
        inner_angle = base_angle + shoulder_motor_angle

        x = math.sin(inner_angle) * hypotenuse
        y = math.cos(inner_angle) * hypotenuse

        return (x, y)

    # ----------------- reporting methods -----------------

    def report(self):

        print(f"               -----------------|-----------------")
        print(f"               Servo 1          |  Servo 2        ")
        print(f"               -----------------|-----------------")

        h1, h2 = self.hysteresis_correction_1, self.hysteresis_correction_2
        print(f"hysteresis                 {h1:>2.1f}  |              {h2:>2.1f}")

        pw_1, pw_2 = self.get_pulse_widths()
        print(f"pulse-width               {pw_1:<4.0f}  |             {pw_2:<4.0f}")

        angle_1, angle_2 = self.angle_1, self.angle_2

        if angle_1 and angle_2:

            print(
                f"      angle               {angle_1:>4.0f}  |             {angle_2:>4.0f}"
            )

        print(f"               -----------------|-----------------")
        print(f"               min   max   mid  |  min   max   mid")
        print(f"               -----------------|-----------------")

        if (
            self.angles_used_1
            and self.angles_used_2
            and self.pulse_widths_used_1
            and self.pulse_widths_used_2
        ):

            min1 = min(self.pulse_widths_used_1)
            max1 = max(self.pulse_widths_used_1)
            mid1 = (min1 + max1) / 2
            min2 = min(self.pulse_widths_used_2)
            max2 = max(self.pulse_widths_used_2)
            mid2 = (min2 + max2) / 2

            print(
                f"pulse-widths  {min1:>4.0f}  {max1:>4.0f}  {mid1:>4.0f}  | {min2:>4.0f}  {max2:>4.0f}  {mid2:>4.0f}"
            )

            min1 = min(self.angles_used_1)
            max1 = max(self.angles_used_1)
            mid1 = (min1 + max1) / 2
            min2 = min(self.angles_used_2)
            max2 = max(self.angles_used_2)
            mid2 = (min2 + max2) / 2

            print(
                f"      angles  {min1:>4.0f}  {max1:>4.0f}  {mid1:>4.0f}  | {min2:>4.0f}  {max2:>4.0f}  {mid2:>4.0f}"
            )

        else:

            print(
                "No data recorded yet. Try calling the BrachioGraph.box() method first."
            )
