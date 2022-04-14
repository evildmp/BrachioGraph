# coding=utf-8

from time import sleep
import readchar
import math
import numpy
from turtle_draw import BrachioGraphTurtle
from base import BaseGraph


class BrachioGraph(BaseGraph):
    def __init__(
        self,
        virtual: bool = False,  # a virtual plotter runs in software only
        turtle: bool = False,  # create a turtle graphics plotter
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
            servo_2_parked_pw=servo_1_parked_pw,
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
            virtual=virtual,
            turtle=turtle,
        )

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

    def park(self):
        """Park the plotter with the inner arm at -90˚ and the outer arm at 90˚ to it.

        This corresponds to an x/y position:

        * x: ``-inner_arm``
        * y: ``outer_arm``
        """

        if self.virtual:
            print("Parking")

        self.pen.up()

        self.xy(-self.inner_arm, self.outer_arm)
        sleep(1)

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
                - 2 * self.inner_arm * self.outer_arm * math.cos(math.pi - elbow_motor_angle)
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

    # ----------------- calibration -----------------

    def auto_calibrate(self):
        self.park()

        for elbow in range(90, 136):
            self.set_angles(None, elbow)
            sleep(0.01)

        for shoulder in range(-90, -140, -1):
            self.set_angles(shoulder, None)
            sleep(0.01)

    def calibrate(self, servo=1):

        pin = {1: 14, 2: 15}[servo]

        servo_centre = {1: self.servo_1_parked_pw, 2: self.servo_2_parked_pw}.get(servo)
        servo_angle_pws = []
        texts = {
            "arm-name": {1: "inner", 2: "outer"},
            "nominal-centre": {1: 0, 2: 90},
            "mount-arm": {1: "(straight ahead)", 2: "(i.e. to the right) to the inner arm)"},
            "safe-guess": {1: -60, 2: 90},
        }

        pw = servo_centre

        print(f"Calibrating servo {servo}, for the {texts['arm-name'][servo]} arm.")
        print(f"See https://brachiograph.art/how-to/calibrate.html")
        print()
        self.rpi.set_servo_pulsewidth(pin, pw)
        print(f"The servo is now at {pw}µS, in the centre of its range of movement.")
        print("Attach the protractor to the base, with its centre at the axis of the servo.")

        print(
            f"Mount the arm at a position as close as possible to {texts['nominal-centre'][servo]}˚ {texts['mount-arm'][servo]}."
        )

        print("Now drive the arm to a known angle, as marked on the protractor.")
        print(
            "When the arm reaches the angle, press 1 and record the angle. Do this for as many angles as possible."
        )
        print()
        print("When you have done all the angles, press 2.")
        print("Press 0 to exit at any time.")

        while True:
            key = readchar.readchar()

            if key == "0":
                return
            elif key == "1":
                angle = float(input("Enter the angle: "))
                servo_angle_pws.append([angle, pw])
            elif key == "2":
                break
            elif key == "a":
                pw = pw - 10
            elif key == "s":
                pw = pw + 10
            elif key == "A":
                pw = pw - 1
            elif key == "S":
                pw = pw + 1
            else:
                continue

            print(pw)

            self.rpi.set_servo_pulsewidth(pin, pw)

        print(f"------------------------")
        print(f"Recorded angles servo {servo}")
        print(f"------------------------")
        print(f"  angle  |  pulse-width ")
        print(f"---------+--------------")

        servo_angle_pws.sort()
        for [angle, pw] in servo_angle_pws:
            print(f" {angle:>6.1f}  |  {pw:>4.0f}")

        servo_array = numpy.array(servo_angle_pws)

        pw = int(numpy.poly1d(numpy.polyfit(servo_array[:, 0], servo_array[:, 1], 3))(0))

        self.rpi.set_servo_pulsewidth(pin, pw)
        print()
        print(
            f"The servo is now at {int(pw)}µS, which should correspond to {texts['nominal-centre'][servo]}˚."
        )
        print(
            "If necessary, remount the arm at the centre of its optimal sweep for your drawing area."
        )
        print()
        print(
            f"Alternatively as a rule of thumb, if the arms are of equal length, use the position closest to {texts['safe-guess'][servo]}˚."
        )

        print(
            "Carefully count how many spline positions you had to move the arm by to get it there."
        )
        print(
            "Multiply that by the number of degrees for each spline to get the angle by which you moved it."
        )
        offset = float(
            input("Enter the angle by which you moved the arm (anti-clockwise is negative): ")
        )

        print(f"---------------------------")
        print(f"Calculated angles {texts['arm-name'][servo]} arm")
        print(f"---------------------------")
        print(f"   angle  |  pulse-width   ")
        print(f"----------+----------------")

        servo_angle_including_offset_pws = []

        for [angle, pw] in servo_angle_pws:
            angle_including_offset = round(angle + offset, 1)
            servo_angle_including_offset_pws.append([angle_including_offset, pw])
            print(f"  {angle:>6.1f}  |  {pw:>4.0f}")

        print()
        print("Use this list of angles and pulse-widths in your BrachioGraph definition:")
        print()
        print(f"servo_{servo}_angle_pws={servo_angle_including_offset_pws}")

    # ----------------- manual driving methods -----------------

    def drive(self):

        # adjust the pulse-widths using the keyboard

        pw_1, pw_2 = self.get_pulse_widths()

        self.set_pulse_widths(pw_1, pw_2)

        while True:
            key = readchar.readchar()

            if key == "0":
                return
            elif key == "a":
                pw_1 = pw_1 - 10
            elif key == "s":
                pw_1 = pw_1 + 10
            elif key == "A":
                pw_1 = pw_1 - 2
            elif key == "S":
                pw_1 = pw_1 + 2
            elif key == "k":
                pw_2 = pw_2 - 10
            elif key == "l":
                pw_2 = pw_2 + 10
            elif key == "K":
                pw_2 = pw_2 - 2
            elif key == "L":
                pw_2 = pw_2 + 2

            print(pw_1, pw_2)

            self.set_pulse_widths(pw_1, pw_2)

    def drive_xy(self):

        # move the pen up/down and left/right using the keyboard

        while True:
            key = readchar.readchar()

            if key == "0":
                return
            elif key == "a":
                self.x = self.x - 1
            elif key == "s":
                self.x = self.x + 1
            elif key == "A":
                self.x = self.x - 0.1
            elif key == "S":
                self.x = self.x + 0.1
            elif key == "k":
                self.y = self.y - 1
            elif key == "l":
                self.y = self.y + 1
            elif key == "K":
                self.y = self.y - 0.1
            elif key == "L":
                self.y = self.y + 0.1

            print(self.x, self.y)

            self.xy(self.x, self.y)

    # ----------------- reporting methods -----------------

    def status(self):
        print("------------------------------------------")
        print("                      | Servo 1 | Servo 2 ")
        print("                      | Shoulder| Elbow   ")
        print("----------------------|---------|---------")

        pw_1, pw_2 = self.get_pulse_widths()
        print(f"{'pulse-width |':>23}", f"{pw_1:>7.0f}", "|", f"{pw_2:>7.0f}")

        angle_1, angle_2 = self.angle_1, self.angle_2
        print(f"{'angle |':>23}", f"{angle_1:>7.0f}", "|", f"{angle_2:>7.0f}")

        h1, h2 = self.hysteresis_correction_1, self.hysteresis_correction_2
        print(f"{'hysteresis correction |':>23}", f"{h1:>7.1f}", "|", f"{h2:>7.1f}")
        print("------------------------------------------")
        print(f"{'x/y location |':>23}", f"{self.x:>7.1f}", "|", f"{self.y:>7.1f}")
        print()
        print("------------------------------------------")
        print("pen:", self.pen.position)

        bl = self.bounds[0], self.bounds[1]
        tr = self.bounds[2], self.bounds[3]
        print("------------------------------------------")
        print("bottom left:", bl, "top right:", tr)
        print("------------------------------------------")

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

            print(f"      angle               {angle_1:>4.0f}  |             {angle_2:>4.0f}")

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

            print("No data recorded yet. Try calling the BrachioGraph.box() method first.")

    def setup_turtle(self):
        self.turtle = BrachioGraphTurtle(
            inner_arm=self.inner_arm,  # the length of the inner arm (blue)
            outer_arm=self.outer_arm,  # the length of the outer arm (red)
            shoulder_centre_angle=-90,  # the starting angle of the inner arm, relative to straight ahead
            shoulder_sweep=180,  # the arc covered by the shoulder motor
            elbow_centre_angle=90,  # the centre of the outer arm relative to the inner arm
            elbow_sweep=180,  # the arc covered by the elbow motor
            window_size=800,  # width and height of the turtle canvas
            speed=0,  # how fast to draw
        )

        self.turtle.draw_grid()
