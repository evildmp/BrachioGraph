"""Contains a base class for a drawing robot."""

from time import sleep, monotonic
import json
import pprint
import math
import readchar
import tqdm
import pigpio
import numpy


class Plotter:
    def __init__(
        self,
        virtual: bool = False,  # a virtual plotter runs in software only
        turtle: bool = False,  # create a turtle graphics plotter
        turtle_coarseness=None,  # a factor in degrees representing servo resolution
        #  ----------------- geometry of the plotter -----------------
        bounds: tuple = [-10, 5, 10, 15],  # the maximum rectangular drawing area
        #  ----------------- naive calculation values -----------------
        servo_1_parked_pw: int = 1500,  # pulse-widths when parked
        servo_2_parked_pw: int = 1500,
        servo_1_degree_ms: float = -10,  # milliseconds pulse-width per degree
        servo_2_degree_ms: float = 10,
        servo_1_parked_angle: float = 0,  # the arm angle in the parked position
        servo_2_parked_angle: float = 0,
        #  ----------------- hysteresis -----------------
        hysteresis_correction_1: float = 0,  # hardware error compensation
        hysteresis_correction_2: float = 0,
        #  ----------------- servo angles and pulse-widths in lists -----------------
        servo_1_angle_pws: tuple = (),  # pulse-widths for various angles
        servo_2_angle_pws: tuple = (),
        #  ----------------- servo angles and pulse-widths in lists (bi-directional) ------
        servo_1_angle_pws_bidi: tuple = (),  # bi-directional pulse-widths for various angles
        servo_2_angle_pws_bidi: tuple = (),
        #  ----------------- the pen -----------------
        pw_up: int = None,  # pulse-widths for pen up/down
        pw_down: int = None,
        #  ----------------- physical control -----------------
        angular_step: float = None,  # default step of the servos in degrees
        wait: float = None,  # default wait time between operations
        resolution: float = None,  # default resolution of the plotter in cm
    ):

        self.last_moved = monotonic()
        self.virtual = virtual
        self.angle_1 = servo_1_parked_angle
        self.angle_2 = servo_2_parked_angle

        if turtle:
            try:
                from turtle import Turtle, Screen

                self.setup_turtle(turtle_coarseness)
                self.turtle.showturtle()

            except ModuleNotFoundError:
                self.turtle = False
                print("Turtle mode unavailable")
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
            # use the bi-directional values to obtain mean values, and a hysteresis correction value
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
            # use the bi-directional values to obtain mean values, and a hysteresis correction value
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

        if self.virtual:
            self.wait = wait or 0
            self.virtualise()

        else:
            try:
                pigpio.exceptions = False
                # instantiate this Raspberry Pi as a pigpio.pi() instance
                self.rpi = pigpio.pi()
                # the pulse frequency should be no higher than 100Hz - higher values could
                # (supposedly) # damage the servos
                self.rpi.set_PWM_frequency(14, 50)
                self.rpi.set_PWM_frequency(15, 50)
                pigpio.exceptions = True
                self.virtual = False
                # by default we use a wait factor of 0.01 seconds for better control
                self.wait = wait if wait is not None else 0.01

            except AttributeError:
                print("pigpio daemon is not available; running in virtual mode")
                self.virtualise()
                self.wait = wait if wait is not None else 0

        # create the pen object
        pw_up = pw_up or 1400
        pw_down = pw_down or 1600

        self.pen = Pen(bg=self, pw_up=pw_up, pw_down=pw_down, virtual=self.virtual)

        self.angular_step = angular_step or 0.1
        self.resolution = resolution or 0.1

        self.set_angles(self.servo_1_parked_angle, self.servo_2_parked_angle)
        sleep(1)

        self.status()

    def virtualise(self):

        print("Initialising virtual BrachioGraph")

        self.virtual_pw_1 = self.angles_to_pw_1(-90)
        self.virtual_pw_2 = self.angles_to_pw_2(90)
        self.virtual = True

    def setup_turtle(self, coarseness):
        """Initialises a Python turtle based on this plotter."""

        from turtle_plotter import BaseTurtle

        self.turtle = BaseTurtle(
            window_size=850,  # width and height of the turtle canvas
            speed=10,  # how fast to draw
            machine=self,
            coarseness=coarseness,
        )

        self.turtle.draw_grid()
        self.t = self.turtle

    #  ----------------- plotting methods -----------------

    def plot_file(self, filename="", bounds=None, angular_step=None, wait=None, resolution=None):
        """Plots and image encoded as JSON lines in ``filename``. Passes the lines in the supplied
        JSON file to ``plot_lines()``.
        """

        bounds = bounds or self.bounds

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines, bounds, angular_step, wait, resolution, flip=True)

    def plot_lines(
        self,
        lines=[],
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        flip=False,
        rotate=False,
    ):
        """Passes each segment of each line in lines to ``draw_line()``"""

        bounds = bounds or self.bounds

        lines = self.rotate_and_scale_lines(lines=lines, bounds=bounds, flip=True)

        for line in tqdm.tqdm(lines, desc="Lines", leave=False):
            x, y = line[0]

            # only if we are not within 1mm of the start of the line, lift pen and go there
            if (round(self.x, 1), round(self.y, 1)) != (round(x, 1), round(y, 1)):
                self.xy(x, y, angular_step, wait, resolution)

            for point in line[1:]:
                x, y = point
                self.xy(x, y, angular_step, wait, resolution, draw=True)

        self.park()

    #  ----------------- pattern-drawing methods -----------------

    def box(
        self, bounds=None, angular_step=None, wait=None, resolution=None, repeat=1, reverse=False
    ):
        """Draw a box marked out by the ``bounds``."""

        bounds = bounds or self.bounds

        if not bounds:
            return "Box drawing is only possible when the bounds attribute is set."

        self.xy(bounds[0], bounds[1], angular_step, wait, resolution)

        for r in tqdm.tqdm(tqdm.trange(repeat), desc="Iteration", leave=False):

            if not reverse:

                self.xy(bounds[2], bounds[1], angular_step, wait, resolution, draw=True)
                self.xy(bounds[2], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[0], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[0], bounds[1], angular_step, wait, resolution, draw=True)

            else:

                self.xy(bounds[0], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[2], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[2], bounds[1], angular_step, wait, resolution, draw=True)
                self.xy(bounds[0], bounds[1], angular_step, wait, resolution, draw=True)

        self.park()

    def test_pattern(
        self,
        lines=4,
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        self.vertical_lines(lines, bounds, angular_step, wait, resolution, repeat, reverse, both)
        self.horizontal_lines(lines, bounds, angular_step, wait, resolution, repeat, reverse, both)

    def vertical_lines(
        self,
        lines=4,
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when the bounds attribute is set."

        if not reverse:
            top_y = self.top
            bottom_y = self.bottom
        else:
            bottom_y = self.top
            top_y = self.bottom

        for n in range(repeat):
            step = (self.right - self.left) / lines
            x = self.left
            while x <= self.right:
                self.draw_line((x, top_y), (x, bottom_y), angular_step, wait, resolution, both)
                x = x + step

        self.park()

    def horizontal_lines(
        self,
        lines=4,
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when the bounds attribute is set."

        if not reverse:
            min_x = self.left
            max_x = self.right
        else:
            max_x = self.left
            min_x = self.right

        for n in range(repeat):
            step = (self.bottom - self.top) / lines
            y = self.top
            while y >= self.bottom:
                self.draw_line((min_x, y), (max_x, y), angular_step, wait, resolution, both)
                y = y + step

        self.park()

    #  ----------------- x/y drawing methods -----------------

    def draw_line(
        self, start=(0, 0), end=(0, 0), angular_step=None, wait=None, resolution=None, both=False
    ):
        """Draws a line between two points"""

        start_x, start_y = start
        end_x, end_y = end

        self.xy(start_x, start_y, angular_step, wait, resolution)

        self.xy(end_x, end_y, angular_step, wait, resolution, draw=True)

        if both:
            self.xy(start_x, start_y, angular_step, wait, resolution, draw=True)

    def xy(self, x=None, y=None, angular_step=None, wait=None, resolution=None, draw=False):
        """Moves the pen to the xy position; optionally draws while doing it. ``None`` for x or y
        means that the pen will not be moved in that dimension.
        """

        wait = wait if wait is not None else self.wait
        resolution = resolution or self.resolution

        x = x if x is not None else self.x
        y = y if y is not None else self.y
        (angle_1, angle_2) = self.xy_to_angles(x, y)

        if draw:

            # calculate how many steps we need for this move, and the x/y length of each
            (x_length, y_length) = (x - self.x, y - self.y)

            length = math.sqrt(x_length**2 + y_length**2)

            no_of_steps = round(length / resolution) or 1

            if no_of_steps < 100:
                disable_tqdm = True
            else:
                disable_tqdm = False

            (length_of_step_x, length_of_step_y) = (x_length / no_of_steps, y_length / no_of_steps)

            for step in range(no_of_steps):

                self.x = self.x + length_of_step_x
                self.y = self.y + length_of_step_y

                angle_1, angle_2 = self.xy_to_angles(self.x, self.y)
                self.move_angles(angle_1, angle_2, angular_step, wait, draw)

        else:
            self.move_angles(angle_1, angle_2, angular_step, wait, draw)

    #  ----------------- servo angle drawing methods -----------------

    def move_angles(self, angle_1=None, angle_2=None, angular_step=None, wait=None, draw=False):
        """Moves the servo motors to the specified angles step-by-step, calling ``set_angles()`` for
        each step. ``None`` for one of the angles means that that servo will not move.
        """

        wait = wait if wait is not None else self.wait
        angular_step = angular_step or self.angular_step

        if draw:
            self.pen.down()
        else:
            self.pen.up()

        diff_1 = diff_2 = 0

        if angle_1 is not None:
            diff_1 = angle_1 - self.angle_1
        if angle_2 is not None:
            diff_2 = angle_2 - self.angle_2

        no_of_steps = int(max(map(abs, (diff_1 / angular_step, diff_2 / angular_step)))) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False

        (length_of_step_1, length_of_step_2) = (diff_1 / no_of_steps, diff_2 / no_of_steps)

        for step in tqdm.tqdm(
            range(no_of_steps), desc="Progress", leave=False, disable=disable_tqdm
        ):

            self.angle_1 = self.angle_1 + length_of_step_1
            self.angle_2 = self.angle_2 + length_of_step_2

            time_since_last_moved = monotonic() - self.last_moved
            if time_since_last_moved < wait:
                sleep(wait - time_since_last_moved)

            self.set_angles(self.angle_1, self.angle_2)

            self.last_moved = monotonic()

    # ----------------- pen-moving methods -----------------

    def set_angles(self, angle_1=None, angle_2=None):
        """Moves the servo motors to the specified angles immediately. Relies upon getting accurate
        pulse-width values. ``None`` for one of the angles means that that servo will not move.

        Calls ``set_pulse_widths()``.

        Sets ``current_x``, ``current_y``.
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

        self.x, self.y = self.angles_to_xy(self.angle_1, self.angle_2)

        if self.turtle:
            self.turtle.set_angles(self.angle_1, self.angle_2)

        self.set_pulse_widths(pw_1, pw_2)

    def park(self):
        """Park the plotter."""

        if self.virtual:
            print("Parking")

        self.pen.up()

        self.move_angles(self.servo_1_parked_angle, self.servo_2_parked_angle)

    #  ----------------- angles-to-pulse-widths methods -----------------

    def naive_angles_to_pulse_widths_1(self, angle):
        """A rule-of-thumb calculation of pulse-width for the desired servo angle"""
        return (angle - self.servo_1_parked_angle) * self.servo_1_degree_ms + self.servo_1_parked_pw

    def naive_angles_to_pulse_widths_2(self, angle):
        """A rule-of-thumb calculation of pulse-width for the desired servo angle"""
        return (angle - self.servo_2_parked_angle) * self.servo_2_degree_ms + self.servo_2_parked_pw

    # ----------------- line-processing methods -----------------

    def rotate_and_scale_lines(self, lines=[], rotate=False, flip=False, bounds=None):
        """Rotates and scales the lines so that they best fit the available drawing ``bounds``."""
        (
            rotate,
            x_mid_point,
            y_mid_point,
            box_x_mid_point,
            box_y_mid_point,
            divider,
        ) = self.analyse_lines(lines, rotate, bounds)

        for line in lines:

            for point in line:
                if rotate:
                    point[0], point[1] = point[1], point[0]

                x = point[0]
                x = x - x_mid_point  # shift x values so that they have zero as their mid-point
                x = x / divider  # scale x values to fit in our box width

                if flip ^ rotate:  # flip before moving back into drawing pane
                    x = -x

                # shift x values so that they have the box x midpoint as their endpoint
                x = x + box_x_mid_point

                y = point[1]
                y = y - y_mid_point
                y = y / divider
                y = y + box_y_mid_point

                point[0], point[1] = x, y

        return lines

    def analyse_lines(self, lines=[], rotate=False, bounds=None):
        """
        Analyses the co-ordinates in ``lines``, and returns:

        * ``rotate``: ``True`` if the image needs to be rotated by 90˚ in order to fit better
        * ``x_mid_point``, ``y_mid_point``: mid-points of the image
        * ``box_x_mid_point``, ``box_y_mid_point``: mid-points of the ``bounds``
        * ``divider``: the value by which we must divide all x and y so that they will fit safely
          inside the bounds.

        ``lines`` is a tuple itself containing a number of tuples, each of which contains a number
        of 2-tuples::

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

        bounds = bounds or self.bounds

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
        # that they will fit safely inside the bounds.

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

        return (rotate, x_mid_point, y_mid_point, box_x_mid_point, box_y_mid_point, divider)

    # ----------------- physical control methods -----------------

    def set_pulse_widths(self, pw_1=None, pw_2=None):
        """Applies the supplied pulse-width values to the servos, or pretends to, if we're in
        virtual mode.
        """

        if self.virtual:

            if pw_1:
                if 500 < pw_1 < 2500:
                    self.virtual_pw_1 = int(pw_1)
                else:
                    raise ValueError

            if pw_2:
                if 500 < pw_2 < 2500:
                    self.virtual_pw_2 = int(pw_2)
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

    # ----------------- manual driving methods -----------------

    def capture_pws(self):
        """
        Helps capture angle/pulse-width data for the servos, as a dictionary to be used
        in a Plotter definition.
        """

        print(
            """
Drive each servo over a wide range of movement (do not exceed a pulse-width
range ~600 to ~2400). To capture the pulse-width value for a particular angle,
press "c", then enter the angle. For each angle, do this in both directions,
clockwise and anti-clockwise. Press "0" to exit.
        """
        )

        pw_1, pw_2 = self.get_pulse_widths()
        pen_pw = self.pen.get_pw()

        last_action = values = None
        pws1_dict = {}
        pws2_dict = {}
        pen_pw_dict = {}

        print("0 to exit, c to capture a value, v to show captured values")
        print("Shoulder a: -10  A: -1   s: +10  S: +1")
        print("Elbow    k: -10  K: -1   l: +10  L: +1")
        print("Pen      z: -10          x: +10")

        controls = {
            "a": [-10, 0, 0, "acw"],
            "A": [-1, 0, 0, "acw"],
            "s": [+10, 0, 0, "cw"],
            "S": [+1, 0, 0, "cw"],
            "k": [0, -10, 0, "acw"],
            "K": [0, -1, 0, "acw"],
            "l": [0, +10, 0, "cw"],
            "L": [0, +1, 0, "cw"],
            "z": [0, 0, -10],
            "x": [0, 0, +10],
        }

        while True:
            # move the arms if commanded
            key = readchar.readchar()
            values = controls.get(key)

            if values:

                if values[0] or values[1] or values[2]:
                    previous_pw_1, previous_pw_2, previous_pen_pw = pw_1, pw_2, pen_pw
                    pw_1 += values[0]
                    pw_2 += values[1]
                    pen_pw += values[2]

                    print(f"shoulder: {pw_1}, elbow: {pw_2}, pen: {pen_pw}")

                    self.set_pulse_widths(pw_1, pw_2)
                    self.pen.pw(pen_pw)

                    last_action = values

            elif key == "0" or key == "v":
                # exit and print results
                print("servo_1_angle_pws_bidi =")
                pprint.pp(pws1_dict, sort_dicts=True, indent=4)
                print("servo_2_angle_pws_bidi =")
                pprint.pp(pws2_dict, sort_dicts=True, indent=4)
                print("Pen pulse-widths =")
                pprint.pp(pen_pw_dict)

                if key == "0":
                    return

            elif key == "c":
                # capture a value
                if not last_action:
                    print("Drive the servos to a new position first")

                # add the values - if any - to the dictionaries
                elif last_action[0]:
                    angle = int(input("Enter the angle of the inner arm: "))
                    pws1_dict.setdefault(angle, {})[last_action[3]] = pw_1

                    print(pws1_dict)

                elif last_action[1]:
                    angle = int(input("Enter the angle of the outer arm: "))
                    pws2_dict.setdefault(angle, {})[last_action[3]] = pw_2

                    print(pws2_dict)

                elif last_action[2]:
                    state = input("Enter the state of the pen ([u]p, [d]own):")
                    pen_pw_dict[state] = pen_pw

                    print(pen_pw)

    def drive_xy(self):
        """Control the x/y position using the keyboard."""

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
        """Provides a report of the plotter status. Subclasses should override this to
        report on their own status."""

        print("------------------------------------------")
        print("                      | Servo 1 | Servo 2 ")
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

        print("------------------------------------------")
        print(f"left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom}")
        print("------------------------------------------")
        print(f"wait: {self.wait} seconds")
        print("------------------------------------------")
        print(f"resolution: {self.resolution} cm")
        print("------------------------------------------")
        print(f"angular step: {self.angular_step}˚")
        print("------------------------------------------")

    @property
    def left(self):
        return self.bounds[0]

    @property
    def bottom(self):
        return self.bounds[1]

    @property
    def right(self):
        return self.bounds[2]

    @property
    def top(self):
        return self.bounds[3]

    def reset_report(self):

        self.angle_1 = self.angle_2 = None

        # Create sets for recording movement of the plotter.
        self.angles_used_1 = set()
        self.angles_used_2 = set()
        self.pulse_widths_used_1 = set()
        self.pulse_widths_used_2 = set()

    # ----------------- trigonometric methods -----------------

    def xy_to_angles(self, x=0, y=0):
        """Return the servo angles required to reach any x/y position. This is a dummy method in
        the base class; it needs to be overridden in a sub-class implementation."""
        return (0, 0)

    def angles_to_xy(self, angle_1, angle_2):
        """Return the servo angles required to reach any x/y position. This is a dummy method in
        the base class; it needs to be overridden in a sub-class implementation."""
        return (0, 0)


class Pen:
    def __init__(self, bg, pw_up=1700, pw_down=1300, pin=18, transition_time=0.25, virtual=False):

        self.bg = bg
        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time
        self.position = "down"
        self.virtual = virtual
        if self.virtual:

            print("Initialising virtual Pen")

        else:

            self.rpi = pigpio.pi()
            self.rpi.set_PWM_frequency(self.pin, 50)

        self.up()

    def down(self):

        if self.position == "up":

            if self.virtual:
                self.virtual_pw = self.pw_down

            else:
                self.ease_pen(self.pw_up, self.pw_down)
                # self.rpi.set_servo_pulsewidth(self.pin, self.pw_down)

            if self.bg.turtle:
                self.bg.turtle.down()
                self.bg.turtle.color("blue")
                self.bg.turtle.width(1)

            self.position = "down"

    def up(self):

        if self.position == "down":

            if self.virtual:
                self.virtual_pw = self.pw_up

            else:
                self.ease_pen(self.pw_down, self.pw_up)
                # self.rpi.set_servo_pulsewidth(self.pin, self.pw_up)

            if self.bg.turtle:
                self.bg.turtle.up()

            self.position = "up"

    def ease_pen(self, start, end):
        """
        Moves the pen gently instead of all at once. Slower but reduces marking on the paper.
        """
        diff = end - start
        angle = start
        length_of_step = diff / abs(diff)

        for i in range(abs(diff)):
            angle += length_of_step
            self.rpi.set_servo_pulsewidth(self.pin, angle)
            sleep(0.001)

    # for convenience, a quick way to set pen motor pulse-widths
    def pw(self, pulse_width):

        if self.virtual:
            self.virtual_pw = pulse_width

        else:
            self.rpi.set_servo_pulsewidth(self.pin, pulse_width)

    # for convenience, a quick way to get pen motor pulse-widths
    def get_pw(self):

        if self.virtual:
            return self.virtual_pw

        else:
            return self.rpi.get_servo_pulsewidth(self.pin)
