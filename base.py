"""Contains a base class for a drawing robot."""

from time import sleep
import json
import math
import readchar
import tqdm
import pigpio
import numpy


try:
    pigpio.exceptions = False
    rpi = pigpio.pi()
    rpi.set_PWM_frequency(18, 50)
    pigpio.exceptions = True
    force_virtual = False

except AttributeError:
    print("pigpio daemon is not available; running in virtual mode")
    force_virtual = True


class BaseGraph:
    """A base class for the BrachioGraph and PantoGraph classes."""

    def __init__(
        self,
        virtual: bool = False,  # a virtual plotter runs in software only
        turtle: bool = False,  # create a turtle graphics plotter
        #  ----------------- geometry of the plotter -----------------
        bounds: tuple = [-8, 4, 6, 13],  # the maximum rectangular drawing area
        #  ----------------- naive calculation values -----------------
        servo_1_parked_pw: int = 1500,  # pulse-widths when parked
        servo_2_parked_pw: int = 1500,
        servo_1_degree_ms: int = -10,  # milliseconds pulse-width per degree
        servo_2_degree_ms: int = 10,
        servo_1_parked_angle: int = 0,  # the arm angle in the parked position
        servo_2_parked_angle: int = 0,
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

        self.virtual = virtual or force_virtual

        if turtle:
            self.setup_turtle()
            self.turtle.showturtle()
        else:
            self.turtle = False

        self.bounds = bounds

        # if pulse-widths to angles are supplied for each servo, we will feed them to
        # numpy.polyfit(), to produce a function for each one. Otherwise, we will use a simple
        # approximation based on a centre of travel of 1500µS and 10µS per degree

        self.servo_1_parked_pw = servo_1_parked_pw
        self.servo_1_degree_ms = servo_1_degree_ms
        self.servo_1_parked_angle = servo_1_parked_angle
        self.hysteresis_correction_1 = hysteresis_correction_1

        if servo_1_angle_pws_bidi:
            servo_1_angle_pws = []
            differences = []
            for angle, pws in servo_1_angle_pws_bidi.items():
                pw = (pws["acw"] + pws["cw"]) / 2
                servo_1_angle_pws.append([angle, pw])
                differences.append((pws["acw"] - pws["cw"]) / 2)
            self.hysteresis_correction_1 = numpy.mean(differences)

        if servo_1_angle_pws:
            servo_1_array = numpy.array(servo_1_angle_pws)
            self.angles_to_pw_1 = numpy.poly1d(
                numpy.polyfit(servo_1_array[:, 0], servo_1_array[:, 1], 3)
            )

        else:
            self.angles_to_pw_1 = self.naive_angles_to_pulse_widths_1

        self.servo_2_parked_pw = servo_2_parked_pw
        self.servo_2_degree_ms = servo_2_degree_ms
        self.servo_2_parked_angle = servo_2_parked_angle
        self.hysteresis_correction_2 = hysteresis_correction_2

        if servo_2_angle_pws_bidi:
            servo_2_angle_pws = []
            differences = []
            for angle, pws in servo_2_angle_pws_bidi.items():
                pw = (pws["acw"] + pws["cw"]) / 2
                servo_2_angle_pws.append([angle, pw])
                differences.append((pws["acw"] - pws["cw"]) / 2)
            self.hysteresis_correction_2 = numpy.mean(differences)

        if servo_2_angle_pws:
            servo_2_array = numpy.array(servo_2_angle_pws)
            self.angles_to_pw_2 = numpy.poly1d(
                numpy.polyfit(servo_2_array[:, 0], servo_2_array[:, 1], 3)
            )

        else:
            self.angles_to_pw_2 = self.naive_angles_to_pulse_widths_2

        # set some initial values required for moving methods

        self.previous_pw_1 = self.previous_pw_2 = 0
        self.active_hysteresis_correction_1 = self.active_hysteresis_correction_2 = 0
        self.reset_report()

        # create the pen object
        self.pen = Pen(
            bg=self, pw_up=pw_up, pw_down=pw_down, virtual=self.virtual
        )

        if self.virtual:

            print("Initialising virtual BrachioGraph")

            self.virtual_pw_1 = self.angles_to_pw_1(-90)
            self.virtual_pw_2 = self.angles_to_pw_2(90)

            # by default in virtual mode, we use a wait factor of 0 for speed
            self.wait = wait or 0

        else:

            # instantiate this Raspberry Pi as a pigpio.pi() instance
            self.rpi = pigpio.pi()

            # the pulse frequency should be no higher than 100Hz - higher values could (supposedly)
            # damage the servos
            self.rpi.set_PWM_frequency(14, 50)
            self.rpi.set_PWM_frequency(15, 50)

            # by default we use a wait factor of 0.1 for accuracy
            self.wait = wait or 0.1

        self.set_angles(self.servo_1_parked_angle, self.servo_2_parked_angle)

        self.status()

    def status(self):
        pass

    #  ----------------- angles-to-pulse-widths methods -----------------

    def naive_angles_to_pulse_widths_1(self, angle):
        return (angle - self.servo_1_parked_angle) * self.servo_1_degree_ms + self.servo_1_parked_pw

    def naive_angles_to_pulse_widths_2(self, angle):
        return (angle - self.servo_2_parked_angle) * self.servo_2_degree_ms + self.servo_2_parked_pw

    #  ----------------- hardware-related methods -----------------

    def set_pulse_widths(self, pw_1=None, pw_2=None):
        """Applies the supplied pulse-width values to the servos, or pretends to, if we're in
        virtual mode.
        """

        if self.virtual:

            if pw_1:
                if 500 < pw_1 < 2500:
                    self.virtual_pw_1 = pw_1
                else:
                    raise ValueError

            if pw_2:
                if 500 < pw_2 < 2500:
                    self.virtual_pw_2 = pw_2
                else:
                    raise ValueError

        else:

            if pw_1:
                self.rpi.set_servo_pulsewidth(14, pw_1)
            if pw_2:
                self.rpi.set_servo_pulsewidth(15, pw_2)

    def get_pulse_widths(self):
        """Returns the actual pulse-widths values; if in virtual mode, returns the nominal values -
        i.e. the values that they might be.
        """

        if self.virtual:

            actual_pulse_width_1 = self.virtual_pw_1
            actual_pulse_width_2 = self.virtual_pw_2

        else:

            actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
            actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return (actual_pulse_width_1, actual_pulse_width_2)

    def quiet(self, servos=[14, 15, 18]):
        """Stop sending pulses to the servos, so that they are no longer energised (and so that they
        stop buzzing).
        """

        if self.virtual:
            print("Going quiet")

        else:
            for servo in servos:
                self.rpi.set_servo_pulsewidth(servo, 0)

    # ----------------- pen-moving methods -----------------

    def xy(self, x=None, y=None, wait=0, interpolate=10, draw=False):
        """Moves the pen to the xy position; optionally draws while doing it."""

        wait = wait or self.wait

        if draw:
            self.pen.down()
        else:
            self.pen.up()

        x = x or self.x
        y = y or self.y

        (angle_1, angle_2) = self.xy_to_angles(x, y)

        # calculate how many steps we need for this move, and the x/y length of each
        (x_length, y_length) = (x - self.x, y - self.y)

        length = math.sqrt(x_length**2 + y_length**2)

        no_of_steps = int(length * interpolate) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False

        (length_of_step_x, length_of_step_y) = (x_length / no_of_steps, y_length / no_of_steps)

        for step in tqdm.tqdm(
            range(no_of_steps), desc="Interpolation", leave=False, disable=disable_tqdm
        ):

            self.x = self.x + length_of_step_x
            self.y = self.y + length_of_step_y

            angle_1, angle_2 = self.xy_to_angles(self.x, self.y)

            self.set_angles(angle_1, angle_2)

            if step + 1 < no_of_steps:
                sleep(length * wait / no_of_steps)

        sleep(length * wait / 10)

    def move_angles(self, angle_1=None, angle_2=None, wait=0, interpolate=10, draw=False):
        """Moves the servo motors to the specified angles step-by-step, calling set_angles() for
        each step.
        """

        wait = wait or self.wait

        if draw:
            self.pen.down()
        else:
            self.pen.up()

        diff_1 = diff_2 = 0

        if angle_1 is not None:
            diff_1 = angle_1 - self.angle_1
        if angle_2 is not None:
            diff_2 = angle_2 - self.angle_2

        length = math.sqrt(diff_1**2 + diff_2**2)

        no_of_steps = int(length * interpolate) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False

        (length_of_step_1, length_of_step_2) = (diff_1 / no_of_steps, diff_2 / no_of_steps)

        for step in tqdm.tqdm(
            range(no_of_steps), desc="Interpolation", leave=False, disable=disable_tqdm
        ):

            self.angle_1 = self.angle_1 + length_of_step_1
            self.angle_2 = self.angle_2 + length_of_step_2

            self.set_angles(self.angle_1, self.angle_2)

            if step + 1 < no_of_steps:
                sleep(length * wait / no_of_steps)

        sleep(length * wait / 10)

    def set_angles(self, angle_1=None, angle_2=None):
        """Moves the servo motors to the specified angles immediately. Relies upon getting accurate
        pulse-width values.

        Calls set_pulse_widths().

        Sets current_x, current_y.
        """

        pw_1 = pw_2 = None

        if angle_1 is not None:
            pw_1 = self.angles_to_pw_1(angle_1)

            if pw_1 > self.previous_pw_1:
                self.active_hysteresis_correction_1 = self.hysteresis_correction_1
            elif pw_1 < self.previous_pw_1:
                self.active_hysteresis_correction_1 = -self.hysteresis_correction_1

            self.previous_pw_1 = pw_1

            pw_1 = pw_1 + self.active_hysteresis_correction_1

            self.angle_1 = angle_1
            self.angles_used_1.add(int(angle_1))
            self.pulse_widths_used_1.add(int(pw_1))

        if angle_2 is not None:
            pw_2 = self.angles_to_pw_2(angle_2)

            if pw_2 > self.previous_pw_2:
                self.active_hysteresis_correction_2 = self.hysteresis_correction_2
            elif pw_2 < self.previous_pw_2:
                self.active_hysteresis_correction_2 = -self.hysteresis_correction_2

            self.previous_pw_2 = pw_2

            pw_2 = pw_2 + self.active_hysteresis_correction_2

            self.angle_2 = angle_2
            self.angles_used_2.add(int(angle_2))
            self.pulse_widths_used_2.add(int(pw_2))

        if self.turtle:

            x, y = self.angles_to_xy(self.angle_1, self.angle_2)

            self.turtle.setx(x * self.turtle.multiplier)
            self.turtle.sety(y * self.turtle.multiplier)

        self.set_pulse_widths(pw_1, pw_2)
        self.x, self.y = self.angles_to_xy(self.angle_1, self.angle_2)

    # ----------------- trigonometric methods -----------------

    def angles_to_xy(self, angle_1, angle_2):
        #  a dummy method; needs to be overridden
        return (0, 0)

    # ----------------- drawing methods -----------------

    def plot_file(self, filename="", wait=0, interpolate=10, bounds=None):
        """Passes the lines in the supplied JSON file to ``plot_lines()``"""

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "File plotting is only possible when BrachioGraph.bounds is set."

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines=lines, wait=wait, interpolate=interpolate, bounds=bounds, flip=True)

    def plot_lines(self, lines=[], wait=0, interpolate=10, rotate=False, flip=False, bounds=None):
        """Passes each segment of each line in lines to ``draw_line()``"""

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Line plotting is only possible when BrachioGraph.bounds is set."

        lines = self.rotate_and_scale_lines(lines=lines, bounds=bounds, flip=True)

        for line in tqdm.tqdm(lines, desc="Lines", leave=False):
            x, y = line[0]

            # only if we are not within 1mm of the start of the line, lift pen and go there
            if (round(self.x, 1), round(self.y, 1)) != (round(x, 1), round(y, 1)):
                self.xy(x, y, wait=wait, interpolate=interpolate)

            for point in tqdm.tqdm(line[1:], desc="Segments", leave=False):
                x, y = point
                self.xy(x, y, wait=wait, interpolate=interpolate, draw=True)

        self.park()

    def draw_line(self, start=(0, 0), end=(0, 0), wait=0, interpolate=10, both=False):
        """Draws a straight line between two points"""

        wait = wait or self.wait

        start_x, start_y = start
        end_x, end_y = end

        self.xy(x=start_x, y=start_y, wait=wait, interpolate=interpolate)

        self.xy(x=end_x, y=end_y, wait=wait, interpolate=interpolate, draw=True)

        if both:
            self.xy(x=start_x, y=start_y, wait=wait, interpolate=interpolate, draw=True)

    # ----------------- line-processing methods -----------------

    def rotate_and_scale_lines(self, lines=[], rotate=False, flip=False, bounds=None):

        (
            rotate,
            x_mid_point,
            y_mid_point,
            box_x_mid_point,
            box_y_mid_point,
            divider,
        ) = self.analyse_lines(lines=lines, rotate=rotate, bounds=bounds)

        for line in lines:

            for point in line:
                if rotate:
                    point[0], point[1] = point[1], point[0]

                x = point[0]
                x = x - x_mid_point  # shift x values so that they have zero as their mid-point
                x = x / divider  # scale x values to fit in our box width

                if flip ^ rotate:  # flip before moving back into drwaing pane
                    x = -x

                x = (
                    x + box_x_mid_point
                )  # shift x values so that they have the box x midpoint as their endpoint

                y = point[1]
                y = y - y_mid_point
                y = y / divider
                y = y + box_y_mid_point

                point[0], point[1] = x, y

        return lines

    def analyse_lines(self, lines=[], rotate=False, bounds=None):
        """lines is a tuple itself containing a number of tuples, each of which contains a number of
        2-tuples

        [
            [
                [3, 4],                               # |
                [2, 4],                               # |
                [1, 5],  #  a single point in a line  # |  a list of points defining a line
                [3, 5],                               # |
                [3, 7],                               # |
            ],
            [            #  all the lines
                [...],
                [...],
            ],
            [
                [...],
                [...],
            ],
        ]
        """

        # First, we create a pair of empty sets for all the x and y values in all of the lines of
        # the plot data.

        x_values_in_lines = set()
        y_values_in_lines = set()

        # Loop over each line and all the points in each line, to get sets of all the x and y
        # values:

        for line in lines:

            x_values_in_line, y_values_in_line = zip(*line)

            x_values_in_lines.update(x_values_in_line)
            y_values_in_lines.update(y_values_in_line)

        # Identify the minimum and maximum values.

        min_x, max_x = min(x_values_in_lines), max(x_values_in_lines)
        min_y, max_y = min(y_values_in_lines), max(y_values_in_lines)

        # Identify the range they span.

        x_range, y_range = max_x - min_x, max_y - min_y
        box_x_range, box_y_range = bounds[2] - bounds[0], bounds[3] - bounds[1]

        # And their mid-points.

        x_mid_point, y_mid_point = (max_x + min_x) / 2, (max_y + min_y) / 2
        box_x_mid_point, box_y_mid_point = (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2

        # Get a 'divider' value for each range - the value by which we must divide all x and y so
        # that they will # fit safely inside the drawing range of the plotter.

        # If both image and box are in portrait orientation, or both in landscape, we don't need to
        # rotate the plot.

        if (x_range >= y_range and box_x_range >= box_y_range) or (
            x_range <= y_range and box_x_range <= box_y_range
        ):

            divider = max((x_range / box_x_range), (y_range / box_y_range))
            rotate = False

        else:

            divider = max((x_range / box_y_range), (y_range / box_x_range))
            rotate = True
            x_mid_point, y_mid_point = y_mid_point, x_mid_point

        return rotate, x_mid_point, y_mid_point, box_x_mid_point, box_y_mid_point, divider

    # ----------------- test pattern methods -----------------

    def test_pattern(
        self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False
    ):

        self.vertical_lines(
            bounds=bounds,
            lines=lines,
            wait=wait,
            interpolate=interpolate,
            repeat=repeat,
            reverse=reverse,
            both=both,
        )
        self.horizontal_lines(
            bounds=bounds,
            lines=lines,
            wait=wait,
            interpolate=interpolate,
            repeat=repeat,
            reverse=reverse,
            both=both,
        )

    def vertical_lines(
        self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False
    ):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when BrachioGraph.bounds is set."

        if not reverse:
            top_y = self.bounds[1]
            bottom_y = self.bounds[3]
        else:
            bottom_y = self.bounds[1]
            top_y = self.bounds[3]

        for n in range(repeat):
            step = (self.bounds[2] - self.bounds[0]) / lines
            x = self.bounds[0]
            while x <= self.bounds[2]:
                self.draw_line((x, top_y), (x, bottom_y), interpolate=interpolate, both=both)
                x = x + step

        self.park()

    def horizontal_lines(
        self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False
    ):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when BrachioGraph.bounds is set."

        if not reverse:
            min_x = self.bounds[0]
            max_x = self.bounds[2]
        else:
            max_x = self.bounds[0]
            min_x = self.bounds[2]

        for n in range(repeat):
            step = (self.bounds[3] - self.bounds[1]) / lines
            y = self.bounds[1]
            while y <= self.bounds[3]:
                self.draw_line((min_x, y), (max_x, y), interpolate=interpolate, both=both)
                y = y + step

        self.park()

    def box(self, bounds=None, wait=0, interpolate=10, repeat=1, reverse=False):
        """Draw a box marked out by the ``bounds``."""

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Box drawing is only possible when BrachioGraph.bounds is set."

        self.xy(bounds[0], bounds[1], wait, interpolate)

        for r in tqdm.tqdm(tqdm.trange(repeat), desc="Iteration", leave=False):

            if not reverse:

                self.xy(bounds[2], bounds[1], wait, interpolate, draw=True)
                self.xy(bounds[2], bounds[3], wait, interpolate, draw=True)
                self.xy(bounds[0], bounds[3], wait, interpolate, draw=True)
                self.xy(bounds[0], bounds[1], wait, interpolate, draw=True)

            else:

                self.xy(bounds[0], bounds[3], wait, interpolate, draw=True)
                self.xy(bounds[2], bounds[3], wait, interpolate, draw=True)
                self.xy(bounds[2], bounds[1], wait, interpolate, draw=True)
                self.xy(bounds[0], bounds[1], wait, interpolate, draw=True)

        self.park()

    @property
    def bl(self):
        return (self.bounds[0], self.bounds[1])

    @property
    def tl(self):
        return (self.bounds[0], self.bounds[3])

    @property
    def tr(self):
        return (self.bounds[2], self.bounds[3])

    @property
    def br(self):
        return (self.bounds[2], self.bounds[1])

    def reset_report(self):

        self.angle_1 = self.angle_2 = None

        # Create sets for recording movement of the plotter.
        self.angles_used_1 = set()
        self.angles_used_2 = set()
        self.pulse_widths_used_1 = set()
        self.pulse_widths_used_2 = set()


class Pen:
    def __init__(self, bg, pw_up=1700, pw_down=1300, pin=18, transition_time=0.25, virtual=False):

        self.bg = bg
        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time
        self.virtual = virtual
        if self.virtual:

            print("Initialising virtual Pen")

        else:

            self.rpi = pigpio.pi()
            self.rpi.set_PWM_frequency(self.pin, 50)

        self.up()
        sleep(0.3)
        self.down()
        sleep(0.3)
        self.up()
        sleep(0.3)

    def down(self):

        if self.virtual:
            self.virtual_pw = self.pw_down

        else:
            self.rpi.set_servo_pulsewidth(self.pin, self.pw_down)
            sleep(self.transition_time)

        if self.bg.turtle:
            self.bg.turtle.down()
            self.bg.turtle.color("blue")
            self.bg.turtle.width(1)

        self.position = "down"

    def up(self):

        if self.virtual:
            self.virtual_pw = self.pw_up

        else:
            self.rpi.set_servo_pulsewidth(self.pin, self.pw_up)
            sleep(self.transition_time)

        if self.bg.turtle:
            self.bg.turtle.up()

        self.position = "up"

    # for convenience, a quick way to set pen motor pulse-widths
    def pw(self, pulse_width):

        if self.virtual:
            self.virtual_pw = pulse_width

        else:
            self.rpi.set_servo_pulsewidth(self.pin, pulse_width)

    def calibrate(self):

        print(f"Calibrating the pen-lifting servo.")
        print(f"See https://brachiograph.art/how-to/calibrate.html")

        pw_1, pw_2 = self.bg.get_pulse_widths()
        pw_3 = self.pw_up

        while True:
            self.bg.set_pulse_widths(pw_1, pw_2)
            self.pw(pw_3)

            key = readchar.readchar()

            if key == "0":
                break
            elif key == "a":
                pw_1 = pw_1 - 10
                continue
            elif key == "s":
                pw_1 = pw_1 + 10
                continue
            elif key == "k":
                pw_2 = pw_2 - 10
                continue
            elif key == "l":
                pw_2 = pw_2 + 10
                continue

            elif key == "t":
                if pw_3 == self.pw_up:
                    pw_3 = self.pw_down
                else:
                    pw_3 = self.pw_up
                continue

            elif key == "z":
                pw_3 = pw_3 - 10
                print(pw_3)
                continue
            elif key == "x":
                pw_3 = pw_3 + 10
                print(pw_3)
                continue

            elif key == "u":
                self.pw_up = pw_3
            elif key == "d":
                self.pw_down = pw_3
            else:
                continue

            mid = (self.pw_up + self.pw_down) / 2
            print(
                f"Pen-up pulse-width: {self.pw_up}µS, pen-down pulse-width: {self.pw_down}µS, mid-point: {mid}"
            )

        print()
        print("Use these values in your BrachioGraph definition:")
        print()
        print(f"pen_up={self.pw_up}, pen_down={self.pw_down}")
