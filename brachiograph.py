# coding=utf-8

from time import sleep
import readchar
import math
import numpy
import json

try:
    import pigpio
    force_virtual_mode = False
except ModuleNotFoundError:
    print("pigpio not installed, running in test mode")
    force_virtual_mode = True

import tqdm


class BrachioGraph:

    def __init__(
        self,
        inner_arm=8,                # the lengths of the arms
        outer_arm=8,
        servo_1_centre=1500,        # shoulder motor centre pulse-width
        servo_2_centre=1500,        # elbow motor centre pulse-width
        servo_1_angle_pws=[],       # pulse-widths for various angles
        servo_2_angle_pws=[],
        servo_1_degree_ms=-10,      # milliseconds pulse-width per degree
        servo_2_degree_ms=10,       # reversed for the mounting of the elbow servo
        arm_1_centre=-60,
        arm_2_centre=90,
        hysteresis_correction_1=0,  # hardware error compensation
        hysteresis_correction_2=0,
        bounds=[-8, 4, 6, 13],      # the maximum rectangular drawing area
        wait=None,
        virtual_mode = False,
        pw_up=1500,                 # pulse-widths for pen up/down
        pw_down=1100,
    ):

        # set the pantograph geometry
        self.INNER_ARM = inner_arm
        self.OUTER_ARM = outer_arm

        self.virtual_mode = virtual_mode or force_virtual_mode

        # the box bounds describe a rectangle that we can safely draw in
        self.bounds = bounds

        # if pulse-widths to angles are supplied for each servo, we will feed them to
        # numpy.polyfit(), to produce a function for each one. Otherwise, we will use a simple
        # approximation based on a centre of travel of 1500µS and 10µS per degree

        self.servo_1_centre = servo_1_centre
        self.servo_1_degree_ms = servo_1_degree_ms
        self.arm_1_centre = arm_1_centre
        self.hysteresis_correction_1 = hysteresis_correction_1

        self.servo_2_centre = servo_2_centre
        self.servo_2_degree_ms = servo_2_degree_ms
        self.arm_2_centre = arm_2_centre
        self.hysteresis_correction_2 = hysteresis_correction_2

        if servo_1_angle_pws:
            servo_1_array = numpy.array(servo_1_angle_pws)
            self.angles_to_pw_1 = numpy.poly1d(
                numpy.polyfit(
                    servo_1_array[:,0],
                    servo_1_array[:,1],
                    3
                )
            )

        else:
            self.angles_to_pw_1 = self.naive_angles_to_pulse_widths_1

        if servo_2_angle_pws:
            servo_2_array = numpy.array(servo_2_angle_pws)
            self.angles_to_pw_2 = numpy.poly1d(
                numpy.polyfit(
                    servo_2_array[:,0],
                    servo_2_array[:,1],
                    3
                )
            )

        else:
            self.angles_to_pw_2 = self.naive_angles_to_pulse_widths_2


        # create the pen object, and make sure the pen is up
        self.pen = Pen(bg=self, pw_up=pw_up, pw_down=pw_down, virtual_mode=self.virtual_mode)

        if self.virtual_mode:

            print("Initialising virtual BrachioGraph")

            self.virtual_pw_1 = self.angles_to_pw_1(-90)
            self.virtual_pw_2 = self.angles_to_pw_2(90)

            # by default in virtual mode, we use a wait factor of 0 for speed
            self.wait = wait or 0

            print("    Pen is up")
            print("    Pulse-width 1", self.virtual_pw_1)
            print("    Pulse-width 2", self.virtual_pw_2)

        else:

            # instantiate this Raspberry Pi as a pigpio.pi() instance
            self.rpi = pigpio.pi()

            # the pulse frequency should be no higher than 100Hz - higher values could (supposedly) damage the servos
            self.rpi.set_PWM_frequency(14, 50)
            self.rpi.set_PWM_frequency(15, 50)

            # Initialise the pantograph with the motors in the centre of their travel
            self.rpi.set_servo_pulsewidth(14, self.angles_to_pw_1(-90))
            sleep(0.3)
            self.rpi.set_servo_pulsewidth(15, self.angles_to_pw_2(90))
            sleep(0.3)

            # by default we use a wait factor of 0.1 for accuracy
            self.wait = wait or .1

        # Now the plotter is in a safe physical state.

        # Set the x and y position state, so it knows its current x/y position.
        self.current_x = -self.INNER_ARM
        self.current_y = self.OUTER_ARM

        self.reset_report()

        self.previous_pw_1 = self.previous_pw_2 = 0
        self.active_hysteresis_correction_1 = self.active_hysteresis_correction_2 = 0

    # methods in this class:
    # drawing
    # line-processing
    # test patterns
    # pen-moving methods
    # angles-to-pulse-widths
    # hardware-related
    # trigonometric methods
    # calibration
    # manual driving methods
    # reporting methods

    # ----------------- drawing methods -----------------


    def plot_file(self, filename="", wait=0, interpolate=10, bounds=None):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "File plotting is only possible when BrachioGraph.bounds is set."

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines=lines, wait=wait, interpolate=interpolate, bounds=bounds, flip=True)


    def plot_lines(self, lines=[], wait=0, interpolate=10, rotate=False, flip=False, bounds=None):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Line plotting is only possible when BrachioGraph.bounds is set."

        lines = self.rotate_and_scale_lines(lines=lines, bounds=bounds, flip=True)

        for line in tqdm.tqdm(lines, desc="Lines", leave=False):
            x, y = line[0]

            # only if we are not within 1mm of the start of the line, lift pen and go there
            if (round(self.current_x, 1), round(self.current_y, 1)) != (round(x, 1), round(y, 1)):
                self.xy(x, y, wait=wait, interpolate=interpolate)

            for point in tqdm.tqdm(line[1:], desc="Segments", leave=False):
                x, y = point
                self.draw(x, y, wait=wait, interpolate=interpolate)

        self.park()


    def draw_line(self, start=(0, 0), end=(0, 0), wait=0, interpolate=10, both=False):

        wait = wait or self.wait

        start_x, start_y = start
        end_x, end_y = end

        self.pen.up()
        self.xy(x=start_x, y=start_y, wait=wait, interpolate=interpolate)

        self.pen.down()
        self.draw(x=end_x, y=end_y, wait=wait, interpolate=interpolate)

        if both:
            self.draw(x=start_x, y=start_y, wait=wait, interpolate=interpolate)

        self.pen.up()


    def draw(self, x=0, y=0, wait=0, interpolate=10):

        wait = wait or self.wait

        self.xy(x=x, y=y, wait=wait, interpolate=interpolate, draw=True)

    # ----------------- line-processing methods -----------------

    def rotate_and_scale_lines(self, lines=[], rotate=False, flip=False, bounds=None):

        rotate, x_mid_point, y_mid_point, box_x_mid_point, box_y_mid_point, divider = self.analyse_lines(
            lines=lines, rotate=rotate, bounds=bounds
        )

        for line in lines:

            for point in line:
                if rotate:
                    point[0], point[1] = point[1], point[0]

                x = point[0]
                x = x - x_mid_point         # shift x values so that they have zero as their mid-point
                x = x / divider             # scale x values to fit in our box width
                x = x + box_x_mid_point     # shift x values so that they have the box x midpoint as their endpoint

                if flip ^ rotate:
                    x = -x

                y = point[1]
                y = y - y_mid_point
                y = y / divider
                y = y + box_y_mid_point

                point[0], point[1] = x, y

        return lines


    def analyse_lines(self, lines=[], rotate=False, bounds=None):

        # lines is a tuple itself containing a number of tuples, each of which contains a number of 2-tuples
        #
        # [                                                                                     # |
        #     [                                                                                 # |
        #         [3, 4],                               # |                                     # |
        #         [2, 4],                               # |                                     # |
        #         [1, 5],  #  a single point in a line  # |  a list of points defining a line   # |
        #         [3, 5],                               # |                                     # |
        #         [3, 7],                               # |                                     # |
        #     ],                                                                                # |
        #     [                                                                                 # |  all the lines
        #         [...],                                                                        # |
        #         [...],                                                                        # |
        #     ],                                                                                # |
        #     [                                                                                 # |
        #         [...],                                                                        # |
        #         [...],                                                                        # |
        #     ],                                                                                # |
        # ]                                                                                     # |

        # First, we create a pair of empty sets for all the x and y values in all of the lines of the plot data.

        x_values_in_lines = set()
        y_values_in_lines = set()

        # Loop over each line and all the points in each line, to get sets of all the x and y values:

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

        # Get a 'divider' value for each range - the value by which we must divide all x and y so that they will
        # fit safely inside the drawing range of the plotter.

        # If both image and box are in portrait orientation, or both in landscape, we don't need to rotate the plot.

        if (x_range >= y_range and box_x_range >= box_y_range) or (x_range <= y_range and box_x_range <= box_y_range):

            divider = max((x_range / box_x_range), (y_range / box_y_range))
            rotate = False

        else:

            divider = max((x_range / box_y_range), (y_range / box_x_range))
            rotate = True
            x_mid_point, y_mid_point = y_mid_point, x_mid_point

        return rotate, x_mid_point, y_mid_point, box_x_mid_point, box_y_mid_point, divider


    # ----------------- test pattern methods -----------------

    def test_pattern(self, bounds=None, wait=0, interpolate=10, repeat=1):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when BrachioGraph.bounds is set."

        for r in tqdm.tqdm(tqdm.trange(repeat, desc='Iteration'), leave=False):

            for y in range(bounds[1], bounds[3], 2):

                self.xy(bounds[0],   y,     wait, interpolate)
                self.draw(bounds[2], y,     wait, interpolate)
                self.xy(bounds[2],   y + 1, wait, interpolate)
                self.draw(bounds[0], y + 1, wait, interpolate)

        self.park()


    def vertical_lines(self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when BrachioGraph.bounds is set."

        if not reverse:
            top_y =    self.bounds[1]
            bottom_y = self.bounds[3]
        else:
            bottom_y = self.bounds[1]
            top_y =    self.bounds[3]

        step = (self.bounds[2] - self.bounds[0]) /  lines
        x = self.bounds[0]
        while x <= self.bounds[2]:
            self.draw_line((x, top_y), (x, bottom_y), interpolate=interpolate, both=both)
            x = x + step

        self.park()


    def horizontal_lines(self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False):

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

        step = (self.bounds[3] - self.bounds[1]) / lines
        y = self.bounds[1]
        while y <= self.bounds[3]:
            self.draw_line((min_x, y), (max_x, y), interpolate=interpolate, both=both)
            y = y + step

        self.park()


    def grid_lines(self, bounds=None, lines=4, wait=0, interpolate=10, repeat=1, reverse=False, both=False):

        self.vertical_lines(
            bounds=bounds, lines=lines, wait=wait, interpolate=interpolate, repeat=repeat, reverse=reverse, both=both
            )
        self.horizontal_lines(
            bounds=bounds, lines=lines, wait=wait, interpolate=interpolate, repeat=repeat, reverse=reverse, both=both
            )


    def box(self, bounds=None, wait=0, interpolate=10, repeat=1, reverse=False):

        wait = wait or self.wait
        bounds = bounds or self.bounds

        if not bounds:
            return "Box drawing is only possible when BrachioGraph.bounds is set."

        self.xy(bounds[0], bounds[1], wait, interpolate)

        for r in tqdm.tqdm(tqdm.trange(repeat), desc='Iteration', leave=False):

            if not reverse:

                self.draw(bounds[2], bounds[1], wait, interpolate)
                self.draw(bounds[2], bounds[3], wait, interpolate)
                self.draw(bounds[0], bounds[3], wait, interpolate)
                self.draw(bounds[0], bounds[1], wait, interpolate)

            else:

                self.draw(bounds[0], bounds[3], wait, interpolate)
                self.draw(bounds[2], bounds[3], wait, interpolate)
                self.draw(bounds[2], bounds[1], wait, interpolate)
                self.draw(bounds[0], bounds[1], wait, interpolate)

        self.park()


    # ----------------- pen-moving methods -----------------

    def xy(self, x=0, y=0, wait=0, interpolate=10, draw=False):
        # Moves the pen to the xy position; optionally draws

        wait = wait or self.wait

        if draw:
            self.pen.down()
        else:
            self.pen.up()

        (angle_1, angle_2) = self.xy_to_angles(x, y)
        (pulse_width_1, pulse_width_2) = self.angles_to_pulse_widths(angle_1, angle_2)

        # if they are the same, we don't need to move anything
        if (pulse_width_1, pulse_width_2) == self.get_pulse_widths():

            # ensure the pantograph knows its x/y positions
            self.current_x = x
            self.current_y = y

            return

        # we assume the pantograph knows its x/y positions - if not, there could be
        # a sudden movement later

        # calculate how many steps we need for this move, and the x/y length of each
        (x_length, y_length) = (x - self.current_x, y - self.current_y)

        length = math.sqrt(x_length ** 2 + y_length **2)

        no_of_steps = int(length * interpolate) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False

        (length_of_step_x, length_of_step_y) = (x_length/no_of_steps, y_length/no_of_steps)

        for step in tqdm.tqdm(range(no_of_steps), desc='Interpolation', leave=False, disable=disable_tqdm):

            self.current_x = self.current_x + length_of_step_x
            self.current_y = self.current_y + length_of_step_y

            angle_1, angle_2 = self.xy_to_angles(self.current_x, self.current_y)

            self.set_angles(angle_1, angle_2)

            if step + 1 < no_of_steps:
                sleep(length * wait/no_of_steps)

        sleep(length * wait/10)


    def set_angles(self, angle_1=0, angle_2=0):
        # moves the servo motor

        pw_1, pw_2 = self.angles_to_pulse_widths(angle_1, angle_2)

        if pw_1 > self.previous_pw_1:
            self.active_hysteresis_correction_1 = self.hysteresis_correction_1
        elif pw_1 < self.previous_pw_1:
            self.active_hysteresis_correction_1 = - self.hysteresis_correction_1

        if pw_2 > self.previous_pw_2:
            self.active_hysteresis_correction_2 = self.hysteresis_correction_2
        elif pw_2 < self.previous_pw_2:
            self.active_hysteresis_correction_2 = - self.hysteresis_correction_2

        self.previous_pw_1 = pw_1
        self.previous_pw_2 = pw_2

        self.set_pulse_widths(pw_1 + self.active_hysteresis_correction_1, pw_2 + self.active_hysteresis_correction_2)

        # We record the angles, so we that we know where the arms are for future reference.
        self.angle_1, self.angle_2 = angle_1, angle_2

        self.angles_used_1.add(int(angle_1))
        self.angles_used_2.add(int(angle_2))
        self.pulse_widths_used_1.add(int(pw_1))
        self.pulse_widths_used_2.add(int(pw_2))


    #  ----------------- angles-to-pulse-widths methods -----------------

    def naive_angles_to_pulse_widths_1(self, angle):
        return (angle - self.arm_1_centre) * self.servo_1_degree_ms + self.servo_1_centre

    def naive_angles_to_pulse_widths_2(self, angle):
        return (angle - self.arm_2_centre) * self.servo_2_degree_ms + self.servo_2_centre


    def angles_to_pulse_widths(self, angle_1, angle_2):
        # Given a pair of angles, returns the appropriate pulse widths.

        # at present we assume only one method of calculating, using the angles_to_pw_1 and angles_to_pw_2
        # functions created using numpy

        pulse_width_1, pulse_width_2 = self.angles_to_pw_1(angle_1), self.angles_to_pw_2(angle_2)

        return (pulse_width_1, pulse_width_2)


    #  ----------------- hardware-related methods -----------------

    def set_pulse_widths(self, pw_1, pw_2):

        if self.virtual_mode:

            if (500 < pw_1 < 2500) and (500 < pw_2 < 2500):

                self.virtual_pw_1 = self.angles_to_pw_1(pw_1)
                self.virtual_pw_2 = self.angles_to_pw_2(pw_2)

            else:
               raise ValueError

        else:

            self.rpi.set_servo_pulsewidth(14, pw_1)
            self.rpi.set_servo_pulsewidth(15, pw_2)


    def get_pulse_widths(self):

        if self.virtual_mode:

            actual_pulse_width_1 = self.virtual_pw_1
            actual_pulse_width_2 = self.virtual_pw_2

        else:

            actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
            actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return (actual_pulse_width_1, actual_pulse_width_2)


    def park(self):

        # parks the plotter

        if self.virtual_mode:
            print("Parking")

        self.pen.up()
        self.xy(-self.INNER_ARM, self.OUTER_ARM)
        sleep(1)
        # self.quiet()


    def quiet(self, servos=[14, 15, 18]):

        # stop sending pulses to the servos

        if self.virtual_mode:
            print("Going quiet")

        else:

            for servo in servos:
                self.rpi.set_servo_pulsewidth(servo, 0)


    # ----------------- trigonometric methods -----------------

    # Every x/y position of the plotter corresponds to a pair of angles of the arms. These methods
    # calculate:
    #
    # the angles required to reach any x/y position
    # the x/y position represented by any pair of angles

    def xy_to_angles(self, x=0, y=0):

        # convert x/y co-ordinates into motor angles

        hypotenuse = math.sqrt(x**2+y**2)

        if hypotenuse > self.INNER_ARM + self.OUTER_ARM:
            raise Exception(f"Cannot reach {hypotenuse}; total arm length is {self.INNER_ARM + self.OUTER_ARM}")

        hypotenuse_angle = math.asin(x/hypotenuse)

        inner_angle = math.acos(
            (hypotenuse**2+self.INNER_ARM**2-self.OUTER_ARM**2)/(2*hypotenuse*self.INNER_ARM)
        )
        outer_angle = math.acos(
            (self.INNER_ARM**2+self.OUTER_ARM**2-hypotenuse**2)/(2*self.INNER_ARM*self.OUTER_ARM)
        )

        shoulder_motor_angle = hypotenuse_angle - inner_angle
        elbow_motor_angle = math.pi - outer_angle

        return (math.degrees(shoulder_motor_angle), math.degrees(elbow_motor_angle))


    def angles_to_xy(self, shoulder_motor_angle, elbow_motor_angle):

        # convert motor angles into x/y co-ordinates

        elbow_motor_angle = math.radians(elbow_motor_angle)
        shoulder_motor_angle = math.radians(shoulder_motor_angle)

        hypotenuse = math.sqrt(
            (self.INNER_ARM ** 2 + self.OUTER_ARM ** 2 - 2 * self.INNER_ARM * self.OUTER_ARM * math.cos(
                math.pi - elbow_motor_angle)
            )
        )
        base_angle = math.acos(
            (hypotenuse ** 2 + self.INNER_ARM ** 2 - self.OUTER_ARM ** 2) / (2 * hypotenuse * self.INNER_ARM)
        )
        inner_angle = base_angle + shoulder_motor_angle

        x = math.sin(inner_angle) * hypotenuse
        y = math.cos(inner_angle) * hypotenuse

        return(x, y)


    # ----------------- calibration -----------------

    def calibrate(self, servo=1):

        pin = {1: 14, 2: 15}[servo]

        servo_centre = {1: self.servo_1_centre, 2: self.servo_2_centre}.get(servo)
        servo_angle_pws = []
        texts = {
            "arm-name": {1: "inner", 2: "outer"},
            "nominal-centre": {1: 0, 2: 90},
            "mount-arm": {
                1: "(straight ahead)",
                2: "(i.e. to the right) to the inner arm)"
            },
        "safe-guess": {1: -60, 2: 90}
        }

        pw = servo_centre

        print(f"Calibrating servo {servo}, for the {texts['arm-name'][servo]} arm.")
        print(f"See https://brachiograph.art/how-to/calibrate.html")
        print()
        self.rpi.set_servo_pulsewidth(pin, pw)
        print(f"The servo is now at {pw}µS, in the centre of its range of movement.")
        print("Attach the protractor to the base, with its centre at the axis of the servo.")

        print(f"Mount the arm at a position as close as possible to {texts['nominal-centre'][servo]}˚ {texts['mount-arm'][servo]}.")

        print("Now drive the arm to a known angle, as marked on the protractor.")
        print("When the arm reaches the angle, press 1 and record the angle. Do this for as many angles as possible.")
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
            elif key=="a":
                pw = pw - 10
            elif key=="s":
                pw = pw + 10
            elif key=="A":
                pw = pw - 1
            elif key=="S":
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

        pw = int(numpy.poly1d(
            numpy.polyfit(
                servo_array[:,0],
                servo_array[:,1],
                3
            )
        )(0))

        self.rpi.set_servo_pulsewidth(pin, pw)
        print()
        print(f"The servo is now at {int(pw)}µS, which should correspond to {texts['nominal-centre'][servo]}˚.")
        print("If necessary, remount the arm at the centre of its optimal sweep for your drawing area.")
        print()
        print(f"Alternatively as a rule of thumb, if the arms are of equal length, use the position closest to {texts['safe-guess'][servo]}˚.")

        print("Carefully count how many spline positions you had to move the arm by to get it there.")
        print("Multiply that by the number of degrees for each spline to get the angle by which you moved it.")
        offset = float(input("Enter the angle by which you moved the arm (anti-clockwise is negative): "))

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
            elif key=="a":
                pw_1 = pw_1 - 10
            elif key=="s":
                pw_1 = pw_1 + 10
            elif key=="A":
                pw_1 = pw_1 - 1
            elif key=="S":
                pw_1 = pw_1 + 1
            elif key=="k":
                pw_2 = pw_2 - 10
            elif key=="l":
                pw_2 = pw_2 + 10
            elif key=="K":
                pw_2 = pw_2 - 1
            elif key=="L":
                pw_2 = pw_2 + 1

            print(pw_1, pw_2)

            self.set_pulse_widths(pw_1, pw_2)


    def drive_xy(self):

        # move the pen up/down and left/right using the keyboard

        while True:
            key = readchar.readchar()

            if key == "0":
                return
            elif key=="a":
                self.current_x = self.current_x - 1
            elif key=="s":
                self.current_x = self.current_x + 1
            elif key=="A":
                self.current_x = self.current_x - .1
            elif key=="S":
                self.current_x = self.current_x + .1
            elif key=="k":
                self.current_y = self.current_y - 1
            elif key=="l":
                self.current_y = self.current_y + 1
            elif key=="K":
                self.current_y = self.current_y - .1
            elif key=="L":
                self.current_y = self.current_y + .1

            print(self.current_x, self.current_y)

            self.xy(self.current_x, self.current_y)


    # ----------------- reporting methods -----------------

    def report(self):

        print(f"               -----------------|-----------------")
        print(f"               Servo 1          |  Servo 2        ")
        print(f"               -----------------|-----------------")

        pw_1, pw_2 = self.get_pulse_widths()
        print(f"pulse-width               {pw_1:<4.0f}  |             {pw_2:<4.0f}")

        angle_1, angle_2 = self.angle_1, self.angle_2

        if angle_1 and angle_2:

            print(f"      angle               {angle_1:>4.0f}  |             {angle_2:>4.0f}")

        print(f"               -----------------|-----------------")
        print(f"               min   max   mid  |  min   max   mid")
        print(f"               -----------------|-----------------")

        if self.angles_used_1 and self.angles_used_2 and self.pulse_widths_used_1 and self.pulse_widths_used_2:

            min1 = min(self.pulse_widths_used_1)
            max1 = max(self.pulse_widths_used_1)
            mid1 = (min1 + max1) / 2
            min2 = min(self.pulse_widths_used_2)
            max2 = max(self.pulse_widths_used_2)
            mid2 = (min2 + max2) / 2

            print(f"pulse-widths  {min1:>4.0f}  {max1:>4.0f}  {mid1:>4.0f}  | {min2:>4.0f}  {max2:>4.0f}  {mid2:>4.0f}")

            min1 = min(self.angles_used_1)
            max1 = max(self.angles_used_1)
            mid1 = (min1 + max1) / 2
            min2 = min(self.angles_used_2)
            max2 = max(self.angles_used_2)
            mid2 = (min2 + max2) / 2

            print(f"      angles  {min1:>4.0f}  {max1:>4.0f}  {mid1:>4.0f}  | {min2:>4.0f}  {max2:>4.0f}  {mid2:>4.0f}")

        else:

            print("No data recorded yet. Try calling the BrachioGraph.box() method first.")


    def reset_report(self):

        self.angle_1 = self.angle_2 = None

        # Create sets for recording movement of the plotter.
        self.angles_used_1 = set()
        self.angles_used_2 = set()
        self.pulse_widths_used_1 = set()
        self.pulse_widths_used_2 = set()


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


class Pen:

    def __init__(self, bg, pw_up=1700, pw_down=1300, pin=18, transition_time=0.25, virtual_mode=False):

        self.bg = bg
        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time
        self.virtual_mode = virtual_mode
        if self.virtual_mode:

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

        if self.virtual_mode:
            self.virtual_pw = self.pw_down

        else:
            self.rpi.set_servo_pulsewidth(self.pin, self.pw_down)
            sleep(self.transition_time)


    def up(self):

        if self.virtual_mode:
            self.virtual_pw = self.pw_up

        else:
            self.rpi.set_servo_pulsewidth(self.pin, self.pw_up)
            sleep(self.transition_time)


    # for convenience, a quick way to set pen motor pulse-widths
    def pw(self, pulse_width):

        if self.virtual_mode:
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
            elif key=="a":
                pw_1 = pw_1 - 10
                continue
            elif key=="s":
                pw_1 = pw_1 + 10
                continue
            elif key=="k":
                pw_2 = pw_2 - 10
                continue
            elif key=="l":
                pw_2 = pw_2 + 10
                continue

            elif key=="t":
                if pw_3 == self.pw_up:
                    pw_3 = self.pw_down
                else:
                    pw_3 = self.pw_up
                continue

            elif key=="z":
                pw_3 = pw_3 - 10
                print(pw_3)
                continue
            elif key=="x":
                pw_3 = pw_3 + 10
                print(pw_3)
                continue

            elif key=="u":
                self.pw_up = pw_3
            elif key=="d":
                self.pw_down = pw_3
            else:
                continue

            mid = (self.pw_up + self.pw_down) / 2
            print(f"Pen-up pulse-width: {self.pw_up}µS, pen-down pulse-width: {self.pw_down}µS, mid-point: {mid}")

        print()
        print("Use these values in your BrachioGraph definition:")
        print()
        print(f"pen_up={self.pw_up}, pen_down={self.pw_down}")
