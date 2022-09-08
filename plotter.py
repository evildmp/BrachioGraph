"""Contains a base class for a drawing robot."""

from time import sleep
import json
import math
import tqdm
import numpy
import re
import readchar

class Plotter:
    def __init__(
        self,
        turtle:  bool = False,     # create a turtle graphics plotter
        turtle_coarseness = None,  # a factor in degrees representing servo resolution

        resolution: float = 1,     # default resolution of the plotter in cm

        #  ----------------- geometry of the plotter
        bounds:    tuple = [-10, 5, 10, 15],       # the maximum rectangular drawing area
        inner_arm: float = 8,                      # the lengths of the arms
        outer_arm: float = 8,

        #  ----------------- servo calibration
        angle_offset_servo_shoulder: float = 30,   # offset (in BG's reference model)
                                                   # for the shoulder servo's zero degrees.
                                                   # the arm has been attached after the servo has
                                                   # been initialized to this offset.
                                                   # see https://www.brachiograph.art/_downloads/94e7b4ab642ebc644e516e616c26aaa3/template-grid.pdf
        angle_parked_servo_shoulder: float = -90,  # the arm angle in the parked position
        angle_parked_servo_elbow:    float = 90,
        angle_pen_up:   float = 0,
        angle_pen_down: float = 30,

        #  ----------------- hysteresis # TODO: implement
        hysteresis_correction_1: float = 0,  # hardware error compensation
        hysteresis_correction_2: float = 0,

        #  ----------------- movement speed
        wait:       float = 0.05,  # default wait time between operations
        **kwargs
    ):
        self.reset_report()
        self.angle_shoulder = angle_parked_servo_shoulder
        self.angle_elbow = angle_parked_servo_elbow
        self.angle_offset_servo_shoulder = angle_offset_servo_shoulder
        self.angle_pen_up = angle_pen_up
        self.angle_pen_down = angle_pen_down
        self.wait = wait
        self.resolution = resolution
        self.bounds = bounds
        self.angle_parked_servo_shoulder = angle_parked_servo_shoulder
        self.hysteresis_correction_1 = hysteresis_correction_1
        self.angle_parked_servo_elbow = angle_parked_servo_elbow
        self.hysteresis_correction_2 = hysteresis_correction_2
        self.active_hysteresis_correction_1 = self.active_hysteresis_correction_2 = 0

        # set the geometry
        self.inner_arm = inner_arm
        self.outer_arm = outer_arm

        # Set the x and y position state, so it knows its current x/y position.
        self.x = -self.inner_arm
        self.y = self.outer_arm

        if turtle == True:
            self.setup_turtle(turtle_coarseness)
            self.turtle.showturtle()
        else:
            self.turtle = False


    def setup_turtle(self, coarseness):
        """Initialises a Python turtle based on this plotter."""
        from turtle_plotter import BaseTurtle
        from turtle_plotter import BrachioGraphTurtle
        self.turtle = BaseTurtle(
            window_size=850,  # width and height of the turtle canvas
            speed=10,  # how fast to draw
            machine=self,
            coarseness=coarseness,
        )

        self.turtle.draw_grid()
        self.t = self.turtle

    #  ----------------- plotting methods -----------------
    def plot_file(self, filename="", wait=None, resolution=None, bounds=None):
        """Plots and image encoded as JSON lines in ``filename``. Passes the lines in the supplied
        JSON file to ``plot_lines()``.
        """

        bounds = bounds or self.bounds

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(
            lines=lines, wait=wait, resolution=resolution, bounds=bounds, flip=True
        )

    def plot_lines(
        self,
        lines=[],
        wait=None,
        resolution=None,
        rotate=False,
        flip=False,
        bounds=None,
    ):
        """Passes each segment of each line in lines to ``draw_line()``"""

        bounds = bounds or self.bounds

        lines = self.rotate_and_scale_lines(lines=lines, bounds=bounds, flip=True)

        for line in tqdm.tqdm(lines, desc="Lines", leave=False):
            x, y = line[0]

            # only if we are not within 1mm of the start of the line, lift pen and go there
            if (round(self.x, 1), round(self.y, 1)) != (round(x, 1), round(y, 1)):
                self.xy(x, y, wait=wait, resolution=resolution)

            for point in line[1:]:
                x, y = point
                self.xy(x, y, wait=wait, resolution=resolution, draw=True)

        self.park()

    #  ----------------- x/y drawing methods -----------------
    def box(self, bounds=None, wait=None, resolution=None, repeat=1, reverse=False, park=False):
        """Draw a box marked out by the ``bounds``."""

        bounds = bounds or self.bounds

        if not bounds:
            return "Box drawing is only possible when the bounds attribute is set."

        self.xy(bounds[0], bounds[1], wait, resolution)

        for r in tqdm.tqdm(tqdm.trange(repeat), desc="Iteration", leave=False):

            if not reverse:
                self.xy(bounds[2], bounds[1], wait, resolution, draw=True)
                self.xy(bounds[2], bounds[3], wait, resolution, draw=True)
                self.xy(bounds[0], bounds[3], wait, resolution, draw=True)
                self.xy(bounds[0], bounds[1], wait, resolution, draw=True)

            else:
                self.xy(bounds[0], bounds[3], wait, resolution, draw=True)
                self.xy(bounds[2], bounds[3], wait, resolution, draw=True)
                self.xy(bounds[2], bounds[1], wait, resolution, draw=True)
                self.xy(bounds[0], bounds[1], wait, resolution, draw=True)

        if park:
            self.park()

    def test_pattern(
        self,
        bounds=None,
        lines=4,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        self.vertical_lines(
            bounds=bounds,
            lines=lines,
            wait=wait,
            resolution=resolution,
            repeat=repeat,
            reverse=reverse,
            both=both,
        )
        self.horizontal_lines(
            bounds=bounds,
            lines=lines,
            wait=wait,
            resolution=resolution,
            repeat=repeat,
            reverse=reverse,
            both=both,
        )

    def vertical_lines(
        self,
        bounds=None,
        lines=4,
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
                self.draw_line(
                    (x, top_y), (x, bottom_y), resolution=resolution, both=both
                )
                x = x + step

        self.park()

    def horizontal_lines(
        self,
        bounds=None,
        lines=4,
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
                self.draw_line((min_x, y), (max_x, y), resolution=resolution, both=both)
                y = y + step

        self.park()

    def draw_line(
        self, start=(0, 0), end=(0, 0), wait=None, resolution=None, both=False
    ):
        """Draws a line between two points"""

        start_x, start_y = start
        end_x, end_y = end

        self.xy(x=start_x, y=start_y, wait=wait, resolution=resolution)

        self.xy(x=end_x, y=end_y, wait=wait, resolution=resolution, draw=True)

        if both:
            self.xy(x=start_x, y=start_y, wait=wait, resolution=resolution, draw=True)

    def xy(self, x=None, y=None, wait=None, resolution=None, draw=False):
        """Moves the pen to the xy position; optionally draws while doing it. ``None`` for x or y
        means that the pen will not be moved in that dimension.
        """

        wait = wait or self.wait
        resolution = resolution or self.resolution

        x = x if x is not None else self.x
        y = y if y is not None else self.y

        (angle_shoulder, angle_elbow) = self.xy_to_angles(x, y)

        self.move_angles(angle_shoulder=angle_shoulder, angle_elbow=angle_elbow, draw=draw, wait=wait, resolution=resolution)

    #  ----------------- servo angle drawing methods -----------------
    def move_angles(
        self, angle_shoulder=None, angle_elbow=None, wait=None, resolution=None, draw=False
    ):
        """Moves the servo motors to the specified angles step-by-step, calling ``set_angles()`` for
        each step. ``resolution`` refers to *degrees* of movement. ``None`` for one of the angles
        means that that servo will not move.
        """

        wait = wait or self.wait
        resolution = resolution or self.resolution

        if draw:
            self.pen_down()
        else:
            self.pen_up()

        diff_1 = diff_2 = 0

        if angle_shoulder is not None:
            diff_1 = angle_shoulder - self.angle_shoulder
        if angle_elbow is not None:
            diff_2 = angle_elbow - self.angle_elbow

        length = math.sqrt(diff_1**2 + diff_2**2)

        no_of_steps = int(length / resolution) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False

        (length_of_step_1, length_of_step_2) = (
            diff_1 / no_of_steps,
            diff_2 / no_of_steps,
        )

        for step in tqdm.tqdm(
            range(no_of_steps), desc="Interpolation", leave=False, disable=disable_tqdm
        ):

            self.angle_shoulder = self.angle_shoulder + length_of_step_1
            self.angle_elbow = self.angle_elbow + length_of_step_2

            self.set_angles(self.angle_shoulder, self.angle_elbow)

            if step + 1 < no_of_steps:
                sleep(length * wait / no_of_steps)

        sleep(length * wait / 10)

    def set_angles(self, angle_shoulder=None, angle_elbow=None):
        """Moves the servo motors to the specified angles immediately.

        Sets ``x``, ``y``.
        """

        if self.turtle:
            self.turtle.set_angles(self.angle_shoulder, self.angle_elbow)

        if angle_shoulder is not None:
            self.angle_shoulder = angle_shoulder
            self.angle_history_shoulder.add(int(angle_shoulder))
            self.set_angle_servo_shoulder(angle_shoulder)
        if angle_elbow is not None:
            self.angle_elbow = angle_elbow
            self.angle_history_elbow.add(int(angle_elbow))
            self.set_angle_servo_elbow(angle_elbow)

        self.x, self.y = self.angles_to_xy(self.angle_shoulder, self.angle_elbow)

        if self.turtle:
            self.turtle.set_angles(self.angle_shoulder, self.angle_elbow)

    def set_angle_servo_shoulder(self, angle):
        """Dummy method that moves the servo. To be implemented in mode-related classes."""
        pass
    def set_angle_servo_elbow(self, angle):
        """Dummy method that moves the servo. To be implemented in mode-related classes."""
        pass
    def set_angle_servo_pen(self, angle):
        """Dummy method that moves the servo. To be implemented in mode-related classes."""
        pass

    def is_angle_in_range(self,angle, servo_angle_min=0, servo_angle_max=180):
        """Verify that angle is within valid range."""
        if angle >= servo_angle_min and angle <= servo_angle_max:
            return True
        else:
            print("ERROR: Angle value out of range ("+str(angle)+")")
            return False

    def park(self):
        """Park the pen."""
        self.pen_up()
        self.move_angles(self.angle_parked_servo_shoulder, self.angle_parked_servo_elbow)

    # ----------------- pen-moving methods -----------------
    def pen_down(self):
        self.set_angle_servo_pen(self.angle_pen_down)
        self.pen_position = "down"

        if self.turtle:
            self.turtle.down()
            self.turtle.color("blue")
            self.turtle.width(1)

        sleep(self.wait)

    def pen_up(self):
        self.set_angle_servo_pen(self.angle_pen_up)
        self.pen_position = "up"

        if self.turtle:
            self.turtle.up()

        sleep(self.wait)

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
        ) = self.analyse_lines(lines=lines, rotate=rotate, bounds=bounds)

        for line in lines:

            for point in line:
                if rotate:
                    point[0], point[1] = point[1], point[0]

                x = point[0]
                x = (
                    x - x_mid_point
                )  # shift x values so that they have zero as their mid-point
                x = x / divider  # scale x values to fit in our box width

                if flip ^ rotate:  # flip before moving back into drawing pane
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
        box_x_mid_point, box_y_mid_point = (bounds[0] + bounds[2]) / 2, (
            bounds[1] + bounds[3]
        ) / 2

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

        return (
            rotate,
            x_mid_point,
            y_mid_point,
            box_x_mid_point,
            box_y_mid_point,
            divider,
        )

    def drive(self):
        """Control servo angles and x/y position using the keyboard."""

        print("Entering manual drive mode. Press 'q' to exit, '?' for help.")
        while True:
            key = readchar.readchar()

            if key == "q":
                print("Exiting manual drive mode.")
                return
            elif key == "9":
                self.status()
            elif key == "?":
                print("Manual drive commands:")
                print(f" {'wasd/WASD':<23}", "move x/y")
                print(f" {'z/x':<23}", "shoulder servo angle -/+ 0.2")
                print(f" {'c/v':<23}", "elbow servo angle    -/+ 0.2")
                print(f" {'Z/X':<23}", "shoulder servo angle -/+ 1")
                print(f" {'C/V':<23}", "elbow servo angle    -/+ 1")
                print(f" {'1/2':<23}", "pen up/down")
                print(f" {'9':<23}", "print status")
                print(f" {'q':<23}", "exit manual drive mode")
                print(f" {'?':<23}", "print this message")

            elif key == "1":
                self.pen_up()
            elif key == "2":
                self.pen_down()

            # x/y controls are WASD
            elif key == "w":
                self.y += 0.1
            elif key == "W":
                self.y += 1
            elif key == "a":
                self.x -= 0.1
            elif key == "A":
                self.x -= 1
            elif key == "s":
                self.y -= 0.1
            elif key == "S":
                self.y -= 1
            elif key == "d":
                self.x += 0.1
            elif key == "D":
                self.x += 1

            # servo angle controls are ZXCV
            elif key == "Z":
                self.angle_shoulder -= 1
            elif key == "X":
                self.angle_shoulder += 1
            elif key == "z":
                self.angle_shoulder -= 0.2
            elif key == "x":
                self.angle_shoulder += 0.2
            elif key == "C":
                self.angle_elbow -= 1
            elif key == "V":
                self.angle_elbow += 1
            elif key == "c":
                self.angle_elbow -= 0.2
            elif key == "v":
                self.angle_elbow += 0.2

            if re.search('[wasdWASD]', key):
                self.xy(self.x, self.y)
                print(f"{'x/y location |':>23}", f"{self.x:>14.1f}", "|", f"{self.y:>11.1f}")
            elif re.search('[zxcvZXCV]', key):
                self.set_angles(self.angle_shoulder, self.angle_elbow)
                print(f"{'angle |':>23}", f"{self.angle_shoulder:>14.0f}", "|", f"{self.angle_elbow:>11.0f}")
            elif re.search('[12]', key):
                print(f"{'pen |':>23}", f"{self.pen_position:<25}")

    # ----------------- reporting methods -----------------

    def status(self):
        """Provides a report of the plotter status. Subclasses should override this to
        report on their own status."""

        print("-----------------------------------------------------")
        print("                      | Shoulder Servo | Elbow Servo ")
        print("----------------------|----------------|-------------")

        angle_shoulder, angle_elbow = self.angle_shoulder, self.angle_elbow
        print(f"{'angle |':>23}", f"{angle_shoulder:>14.0f}", "|", f"{angle_elbow:>11.0f}")

        h1, h2 = self.hysteresis_correction_1, self.hysteresis_correction_2
        print(f"{'hysteresis correction |':>23}", f"{h1:>14.1f}", "|", f"{h2:>11.1f}")
        print("-----------------------------------------------------")
        print(f"{'x/y location |':>23}", f"{self.x:>14.1f}", "|", f"{self.y:>11.1f}")
        print()
        print("-----------------------------------------------------")
        print(f"{'pen |':>23}", f"{self.pen_position:<25}")

        print("-----------------------------------------------------")
        print(
            "left:",
            self.left,
            "right:",
            self.right,
            "top:",
            self.top,
            "bottom:",
            self.bottom,
        )
        print("-----------------------------------------------------")

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
        self.angle_shoulder = self.angle_elbow = None

        # Create sets for recording movement of the plotter.
        self.angle_history_shoulder = set()
        self.angle_history_elbow = set()

    def test_arcs(self):
        self.park()
        elbow_angle = 120
        self.move_angles(angle_elbow=elbow_angle)

        for angle_shoulder in range(-135, 15, 15):
            self.move_angles(angle_shoulder=angle_shoulder, draw=True)

            for angle_elbow in range(elbow_angle, elbow_angle + 16):
                self.move_angles(angle_elbow=angle_elbow, draw=True)
            for angle_elbow in range(elbow_angle + 16, elbow_angle - 16, -1):
                self.move_angles(angle_elbow=angle_elbow, draw=True)
            for angle_elbow in range(elbow_angle - 16, elbow_angle + 1):
                self.move_angles(angle_elbow=angle_elbow, draw=True)

    # ----------------- reporting methods -----------------

    def report(self):

        print(f"               -----------------|-----------------")
        print(f"                 Shoulder Servo |   Elbow Servo   ")
        print(f"               -----------------|-----------------")

        h1, h2 = self.hysteresis_correction_1, self.hysteresis_correction_2
        print(f"hysteresis                 {h1:>2.1f}  |              {h2:>2.1f}")

        pw_1, pw_2 = self.get_pulse_widths()
        print(f"pulse-width               {pw_1:<4.0f}  |             {pw_2:<4.0f}")

        angle_shoulder, angle_elbow = self.angle_shoulder, self.angle_elbow

        if angle_shoulder and angle_elbow:

            print(
                f"      angle               {angle_shoulder:>4.0f}  |             {angle_elbow:>4.0f}"
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
    # ----------------- trigonometric methods -----------------

    def xy_to_angles(self, x=0, y=0):
        """
        Return the servo angles required to reach any x/y position.
        angle_motor_shoulder is +/-90, related to the Y axis.
        angle_motor_elbow is 0-180, related to the inner arm, with 0 resulting in the outer arm fully extended.
        """

        hypotenuse = math.sqrt(x**2 + y**2)

        if hypotenuse > self.inner_arm + self.outer_arm:
            raise Exception(
                f"Cannot reach {hypotenuse}; total arm length is {self.inner_arm + self.outer_arm}"
            )

        hypotenuse_angle = math.asin(x / hypotenuse)
        hyp_angle = math.atan(x / y)

        inner_angle = math.acos(
            (hypotenuse**2 + self.inner_arm**2 - self.outer_arm**2) /
            (2 * hypotenuse * self.inner_arm))
        outer_angle = math.acos(
            (self.inner_arm**2 + self.outer_arm**2 - hypotenuse**2) /
            (2 * self.inner_arm * self.outer_arm))

        # print("Inner angle is "+str(inner_angle)+" outer angle is "+str(outer_angle))
        angle_motor_shoulder = hypotenuse_angle - inner_angle
        angle_motor_elbow = math.pi - outer_angle

        return (math.degrees(angle_motor_shoulder),
                math.degrees(angle_motor_elbow))

    def angles_to_xy(self, angle_shoulder, angle_elbow):
        """Return the x/y co-ordinates represented by a pair of servo angles."""

        angle_elbow = math.radians(angle_elbow)
        angle_shoulder = math.radians(angle_shoulder)

        hypotenuse = math.sqrt(
            (self.inner_arm**2 + self.outer_arm**2 - 2 * self.inner_arm *
             self.outer_arm * math.cos(math.pi - angle_elbow)))
        base_angle = math.acos(
            (hypotenuse**2 + self.inner_arm**2 - self.outer_arm**2) /
            (2 * hypotenuse * self.inner_arm))
        inner_angle = base_angle + angle_shoulder

        x = math.sin(inner_angle) * hypotenuse
        y = math.cos(inner_angle) * hypotenuse

        return (x, y)
