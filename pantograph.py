from collections import namedtuple
from time import sleep
from math import *
import sys

import json
from tqdm import tqdm, trange
import readchar

import pigpio


def hypotenuse(side1, side2):
    return sqrt(side1 ** 2 + side2 ** 2)


class PantoGraph:

    def __init__(
        self,

        driver=4,                  # the lengths of the arms
        follower=10.15,            # the lengths of the arms

        # The angles are relative to each motor, so we need to know where each motor actually is.
        motor_1_pos = -1.5, # position of motor 1 on the x axis
        motor_2_pos = 1.5,  # position of motor 2 on the x axis

        box_bounds=(-3, -3, 3, 3),

        angle_multiplier=1, # set to -1 if necessary to reverse directions
        correction_1=0,
        correction_2=0,

        centre_1=1350, multiplier_1=425/45,
        centre_2=1350, multiplier_2=415/45
    ):

        # instantiate this Raspberry Pi as a pigpio.pi() instance
        self.rpi = pigpio.pi()

        # the pulse frequency should be 100Hz - higher values could damage the servos
        self.rpi.set_PWM_frequency(14, 50)
        self.rpi.set_PWM_frequency(15, 50)

        # create the pen object, and make sure the pen is up
        self.pen = Pen(pg=self)
        self.pen.up()

        # set the pantograph geometry
        self.DRIVER = driver
        self.FOLLOWER = follower
        self.MOTOR_1_POS, self.MOTOR_2_POS = motor_1_pos, motor_2_pos

        # the box bounds describe a rectangle that we can safely draw in
        self.box_bounds = box_bounds

        self.angle_multiplier = angle_multiplier

        self.correction_1 = correction_1
        self.correction_2 = correction_2

        self.centre_1, self.centre_2 = centre_1, centre_2
        self.multiplier_1, self.multiplier_2 = multiplier_1, multiplier_2

        # Initialise the pantograph with the motors straight ahead
        self.rpi.set_servo_pulsewidth(14, 1350)
        self.rpi.set_servo_pulsewidth(15, 1350)

        self.set_angles(0, 0)
        self.current_x, self.current_y = self.angles_to_xy(0, 0)

        self.quiet()


    def set_up(self):

        self.motors = (
            {
                "motor": 1,
                "pin": 14,
                "calibrations": (
                    {"angle": 0, "description": "straight ahead"},
                    {"angle": -90, "description": "straight out to the left"},
                )
            },
            {
                "motor": 2,
                "pin": 15,
                "calibrations": (
                    {"angle": 0, "description": "straight ahead"},
                    {"angle": 90, "description": "straight out to the right"},
                )
            }
        )

        print("Important! Before doing anything else, loosen the servo screws, so there won't be any accidents with the arms. \n")

        input("Press Return when you are ready to start calibrating. \n")

        print("""---------------------------------------------------------
Controls:

    < and >: decrease/increase pulse width by 100µS.
    { and }: decrease/increase pulse width by  10µS.
    [ and ]: decrease/increase pulse width by   1µS.
    0      : confirm that the arm is at the correct angle
--------------------------------------------------------- \n""")

        for motor in self.motors:

            pin = motor["pin"]

            pw = 1350
            self.rpi.set_servo_pulsewidth(pin, pw)

            print("Adjusting servo on pin {}\n".format(pin))

            print("    Pulse width: 1350µS (more or less in the centre of its travel).\n")

            print("    Attach the driver arm so that it points outward at between 30˚ and 45˚.\n")

            # first, find the pulse width for an angle of zero
            angle = motor["calibrations"][0]["angle"]
            description = motor["calibrations"][0]["description"]

            # interactively discover the pulse width
            motor["zero"] = self.calibrate(pin, angle, description)

            # next, find the pulse width for an angle of ninety degrees left or right
            angle = motor["calibrations"][1]["angle"]
            description = motor["calibrations"][1]["description"]

            # interactively discover the pulse width
            motor["ninety"] = self.calibrate(pin, angle, description)


            # the multiplier is the difference in pulse width required for 1˚ of motion
            motor["multiplier"] = (motor["ninety"] - motor["zero"]) / angle

        self.centre_1 = self.motors[0]["zero"]
        self.multiplier_1 = self.motors[0]["multiplier"]
        self.centre_2 = self.motors[1]["zero"]
        self.multiplier_2 = self.motors[1]["multiplier"]

        print("Pulse widths\n")
        print("Motor     0˚ ±90˚ ∆/degree")
        for motor in self.motors:

            print("  {}    {:4} {:4}  {:.4f}".format(
                motor["motor"],
                motor["zero"],
                motor["ninety"],
                motor["multiplier"]
            ))


    def calibrate(self, pin, angle, description):

        adjustments = {"<": -100, ">": +100, "{": -10, "}": +10, "[": -1, "]": +1, "0": "done"}

        pw = 1350
        self.rpi.set_servo_pulsewidth(pin, pw)

        print("        Now use the controls to move the arm to {}˚ (i.e. {}).\n".format(angle, description))

        while True:
            key = readchar.readchar()

            adjustment = adjustments.get(key, None)

            if adjustment:
                if adjustment=="done":
                    print("\n")
                    return pw
                else:
                    pw = pw + adjustment
                    print("        pulse width: {} ".format(pw), end="\r")
                    self.rpi.set_servo_pulsewidth(pin, pw)


    # ----------------- reporting methods -----------------

    def status(self):

        x, y = self.current_x, self.current_y

        print("Driver/follower arm length: {:03.1f}/{:03.1f}".format(self.DRIVER, self.FOLLOWER))
        print("Furthest reach: {:03.1f}".format(self.furthest_reach))
        print("Motor 1 & 2 positions:        {:03.1f}, {:03.1f}".format(self.MOTOR_1_POS, self.MOTOR_2_POS))
        print("Motor angle corrections:      {:03.1f}, {:03.1f}".format(self.correction_1, self.correction_2))
        print("0˚ pulse widths:              {:03}, {:03}".format(self.centre_1, self.centre_2))
        print("Pulse-width angle multipliers {:03.1f}, {:03.1f}".format(self.multiplier_1, self.multiplier_2))
        print()
        print("Pen x/y:      {: 3.1f}, {: 3.1f}".format(x, y))
        print("Servo angles: {: 3.1f}, {: 3.1f}".format(*self.xy_to_angles(x,y)))
        print("Pulse widths: {:03},    {:03}".format(*self.get_pulse_widths()))


    def drawing_area(self):

        # This is an experimental method in progress. It's intended to help find the largest usable drawing
        # areas, by sweeping the motors through a wide range.

        motor_distance = self.MOTOR_2_POS - self.MOTOR_1_POS

        for angle_1 in range(0, -107, -10):
            for angle_2 in range(0, angle_1 -10, -10):

                x, y = self.angles_to_xy(angle_1, angle_2)

                # x = round(x, 1)
                # y = round(y, 1)


                print(
                    "angles: {:3.0f}, {:3.0f};".format(angle_1, angle_2),
                    # "elbow1: {:4.1f}, {:4.1f};".format(elbow_1_x, elbow_1_y),
                    # "elbow2: {:4.1f}, {:4.1f};".format(elbow_2_x, elbow_2_y),
                    # "base length: {:3.0f};".format(base_of_top_triangle),
                    # "base/corner: {:3.0f}, {:3.0f};".format(degrees(angle_of_base_of_top_triangle), degrees(base_of_top_triangle)),
                    # "elbow dx/dy: {:4.1f}, {:4.1f};".format(elbow_dx, elbow_dy),
                    # "elbow to x/y: {:4.1f}, {:4.1f};".format(x_to_elbow, y_to_elbow),
                    "x/y: {:4.1f}, {:4.1f}".format(x, y)
                )
            print()

    def sweep(self):
        pass



    # ----------------- drawing methods -----------------


    def plot_file(self, filename="", wait=.1, interpolate=10, rotate=False, bounds=None):

        bounds = bounds or self.box_bounds

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines=lines, wait=wait, interpolate=interpolate, rotate=rotate, bounds=bounds)


    def plot_lines(self, lines=[], wait=.1, interpolate=10, rotate=False, bounds=None):

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

        x_range = max_x - min_x
        y_range = max_y - min_y

        x_mid_point = (max_x + min_x) / 2
        y_mid_point = (max_y + min_y) / 2

        box_x_range = bounds[2] - bounds[0]
        box_y_range = bounds[3] - bounds[1]

        box_x_mid_point = (bounds[0] + bounds[2]) / 2
        box_y_mid_point = (bounds[1] + bounds[3]) / 2


        # Get a 'divider' value for each range - the value by which we must divide all x and y so that they will
        # fit safely inside the drawing range of the plotter.

        #
        # If both image and box are in portrait orientation, or both in landscape, we don't need to rotate the plot.

        if (x_range >= y_range and box_x_range >= box_y_range) or (x_range <= y_range and box_x_range <= box_y_range):

            divider = max((x_range / box_x_range), (y_range / box_y_range))
            rotate = False

        else:

            divider = max((x_range / box_y_range), (y_range / box_x_range))
            rotate = True
            x_mid_point, y_mid_point = y_mid_point, x_mid_point

        # Now, divide each value, and take into account the offset from zero of each range

        for line in lines:

            for point in line:
                if rotate:
                    point[0], point[1] = point[1], point[0]

                x = point[0]
                x = x - x_mid_point         # shift x values so that they have zero as their mid-point
                x = x / divider             # scale x values to fit in our box width
                x = x + box_x_mid_point     # shift x values so that they have the box x midpoint as their endpoint
                point[0] = x

                y = point[1]
                y = y - y_mid_point
                # if rotate:
                #     y = -y
                y = y / divider
                y = y + box_y_mid_point

                point[1] = y

        for line in tqdm(lines, desc="Lines", leave=False):
            x, y = line[0]
            self.xy(x, y)
            for point in tqdm(line[1:], desc="Segments", leave=False):
                x, y = point
                self.draw(x, y, wait=wait, interpolate=interpolate)

        self.pen.up()

        self.quiet()



    def draw(self, x=0, y=0, wait=.5, interpolate=10):
        self.xy(x=x, y=y, wait=wait, interpolate=interpolate, draw=True)


    def test_pattern(self, bounds=None, wait=1, interpolate=10, repeat=1):

        bounds = bounds or self.box_bounds

        for r in tqdm(trange(repeat, desc='Iteration'), leave=False):

            self.xy(bounds[0], bounds[1], wait, interpolate)

            for y in range(bounds[1], bounds[3] + 1):

                if y % 2 == 0:
                    self.draw(bounds[2], bounds[1] + y, wait, interpolate)
                    self.xy(bounds[2], bounds[1] + y + 1, wait, interpolate)
                else:
                    self.draw(bounds[0], bounds[1] + y, wait, interpolate)
                    self.xy(bounds[0], bounds[1] + y + 1, wait, interpolate)

        self.pen.up()

        self.quiet()


    def box(self, bounds=None, wait=.15, interpolate=10, repeat=1, reverse=False):

        bounds = bounds or self.box_bounds

        self.xy(bounds[0], bounds[1], wait, interpolate)

        for r in tqdm(trange(repeat), desc='Iteration', leave=False):

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

        self.pen.up()

        self.quiet()

    # ----------------- pen-moving methods -----------------


    def centre(self):

        self.pen.up()
        self.xy(self.box_bounds[2]/2, self.box_bounds[3]/2)

        self.quiet()


    def xy(self, x=0, y=0, wait=.1, interpolate=10, draw=False):
        # Moves the pen to the xy position; optionally draws

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

        length = hypotenuse(x_length, y_length)

        no_of_steps = int(length * interpolate) or 1

        if no_of_steps < 100:
            disable_tqdm = True
        else:
            disable_tqdm = False


        (length_of_step_x, length_of_step_y) = (x_length/no_of_steps, y_length/no_of_steps)

        for step in tqdm(range(no_of_steps), desc='Interpolation', leave=False, disable=disable_tqdm):

            self.current_x = self.current_x + length_of_step_x
            self.current_y = self.current_y + length_of_step_y

            angle_1, angle_2 = self.xy_to_angles(self.current_x, self.current_y)

            self.set_angles(angle_1, angle_2)

            if step + 1 < no_of_steps:
                sleep(length * wait/no_of_steps)

        sleep(length * wait/10)


    # ----------------- arm-moving methods -----------------

    def zero(self):

        self.pen.up()

        self.set_angles(0, 0)

        self.current_x, self.current_y = self.angles_to_xy(0, 0)


    def set_angles(self, angle_1=0, angle_2=0):
        # moves the servo motor

        pw_1, pw_2 = self.angles_to_pulse_widths(angle_1, angle_2)

        self.set_pulse_widths(pw_1, pw_2)


        # We record the angles, so we that we know where the arms are for future reference.
        self.angle_1, self.angle_2 = angle_1, angle_2


    #  ----------------- hardware-related methods -----------------

    def angles_to_pulse_widths(self, angle_1, angle_2):
        # Given a pair of angles, returns the appropriate pulse widths.

        pulse_width_1 = self.centre_1 + self.multiplier_1 * (angle_1 + self.correction_1)
        pulse_width_2 = self.centre_2 + self.multiplier_2 * (angle_2 + self.correction_2)

        return (pulse_width_1, pulse_width_2)


    def set_pulse_widths(self, pw_1, pw_2):

        self.rpi.set_servo_pulsewidth(14, pw_1)
        self.rpi.set_servo_pulsewidth(15, pw_2)

        sleep(.01)


    def get_pulse_widths(self):

        actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
        actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return actual_pulse_width_1, actual_pulse_width_2


    # ----------------- trigonometric methods -----------------

    @property
    def furthest_reach(self):
        return self.DRIVER + sqrt(self.FOLLOWER ** 2 - (self.MOTOR_2_POS-self.MOTOR_1_POS)/2)


    def xy_to_angles(self, x=0, y=None):

        if y is None:
            y = self.furthest_reach

        # Given a pair of x/y co-ordinates, returns the angle required of each arm.

        # we add L to y, so that y=0 is a safe distance from the motors

        # y = y + self.adder

        # calculate the x value relative to each motor
        x_relative_to_motor_1 = self.MOTOR_1_POS - x
        x_relative_to_motor_2 = self.MOTOR_2_POS - x

        # calculate the distance from each motor to the x/y point
        d1 = hypotenuse(x_relative_to_motor_1, y)
        d2 = hypotenuse(x_relative_to_motor_2, y)

        # # calculate the angle between the d line and arm
        # inner_angle_1 = acos((d1/self.L)/2)
        # inner_angle_2 = acos((d2/self.L)/2)

        # calculate the angle between the d line and driver arm
        inner_angle_1 = acos((self.DRIVER **2 + d1 ** 2 - self.FOLLOWER ** 2) / (2 * self.DRIVER * d1))
        inner_angle_2 = acos((self.DRIVER **2 + d2 ** 2 - self.FOLLOWER ** 2) / (2 * self.DRIVER * d2))

        # calculate the angle between the d line and the vertical
        outer_angle_1 = - atan(x_relative_to_motor_1/y)
        outer_angle_2 = - atan(x_relative_to_motor_2/y)

        # calculate the sum of the angles in degrees
        angle1 = degrees(outer_angle_1 - inner_angle_1)
        angle2 = degrees(inner_angle_2 + outer_angle_2)

        return (
            angle1 * self.angle_multiplier,
            angle2 * self.angle_multiplier
            )


    def angles_to_xy(self, angle1, angle2):
        # Given the angle of each arm, returns the x/y co-ordinates

        angle1 = radians(angle1 * self.angle_multiplier)
        angle2 = radians(angle2 * self.angle_multiplier)

        # calculate the x position of the elbows
        elbow_1_x = sin(angle1) * self.DRIVER
        elbow_2_x = sin(angle2) * self.DRIVER

        # calculate the y position of the elbows
        elbow_1_y = sqrt((self.DRIVER ** 2) - (elbow_1_x ** 2))
        elbow_2_y = sqrt((self.DRIVER ** 2) - (elbow_2_x ** 2))

        motor_distance = self.MOTOR_2_POS - self.MOTOR_1_POS

        # calculate x and y distances between the elbows
        elbow_dx = motor_distance + elbow_2_x - elbow_1_x
        elbow_dy = elbow_2_y - elbow_1_y

        # calculate the length of the base of the top triangle
        base_of_top_triangle = hypotenuse(elbow_dx, elbow_dy)

        # calculate the angle at which the top triangle is tilted
        angle_of_base_of_top_triangle = asin((- elbow_dy) / base_of_top_triangle)

        # calculate the left inner angle of the top triangle
        corner_of_top_triangle = acos((base_of_top_triangle / 2) / self.FOLLOWER)

        # calculate the x and y distances to the left elbow
        x_to_elbow = cos(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.FOLLOWER
        y_to_elbow = sin(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.FOLLOWER

        x = elbow_1_x + x_to_elbow + self.MOTOR_1_POS
        y = elbow_1_y + y_to_elbow

        # return x, y - self.adder

        return x, y


    def quiet(self, servos=[14, 15, 18]):

        for servo in servos:
            self.rpi.set_servo_pulsewidth(servo, 0)


class Pen:

    def __init__(self, pg, pin=18, pw_up=1650, pw_down=2100, transition_time=0.25):

        self.pg = pg
        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time

        self.rpi = pigpio.pi()
        self.rpi.set_PWM_frequency(self.pin, 50)

        self.up()


    def down(self):
        self.rpi.set_servo_pulsewidth(self.pin, self.pw_down)
        sleep(self.transition_time)


    def up(self):
        self.rpi.set_servo_pulsewidth(self.pin, self.pw_up)
        sleep(self.transition_time)


# pg = PantoGraph(correction_1=45, correction_2=-45)

# small servo version
#
# pg = PantoGraph(MOTOR_1_POS=4, MOTOR_2_POS=7, centre_1 = 1050, multiplier_1 =970/90, centre_2= 2100, multiplier_2=950/90, box_bounds=(0,0,10,7), HEIGHT=19)

# pg = PantoGraph(MOTOR_1_POS=-1.5, MOTOR_2_POS=1.5, L=12, centre_1 = 1900, multiplier_1 = 10.333, centre_2= 900, multiplier_2 = 10.445, box_bounds=(-3, -3, 3, 3))

# pg = PantoGraph(MOTOR_1_POS=-2.5, MOTOR_2_POS=2.5, L=9.8, centre_1 = 1620, multiplier_1 = 9.556, centre_2= 1090, multiplier_2 = 9.111, box_bounds=(-4, 0, 4, 5))

# # large servos and box
#
# pg = PantoGraph(driver=4, follower=9.8, motor_1_pos=-1.7, motor_2_pos=1.7, centre_1 = 1864, multiplier_1 = 9.2779, centre_2= 964, multiplier_2 = 9.4222, box_bounds=(-4, 0, 4, 5))

# pg = PantoGraph(driver=6.8, follower=10.7, motor_1_pos=-1.7, motor_2_pos=1.7, centre_1 = 1639, multiplier_1 = 9.211, centre_2= 1060, multiplier_2 = 9.4444, box_bounds=(-6, 7, 6, 15.5))


# # small servos and box
#
# pg = PantoGraph(driver=4, follower=9.8, motor_1_pos=-1.5, motor_2_pos=1.5, centre_1 = 2040, multiplier_1 = 10.6222, centre_2= 950, multiplier_2 = 10.2778, box_bounds=(-4, 0, 4, 5))

# pg = PantoGraph(driver=4.65, follower=9.8, motor_1_pos=-1.5, motor_2_pos=1.5, centre_1 = 2225, multiplier_1 = 9.5, centre_2=900, multiplier_2 = 10.2221, box_bounds=(-4.5, 7, 4.5, 13))

# set 1
# pg = PantoGraph(driver=6.8, follower=10.7, motor_1_pos=-1.5, motor_2_pos=1.5, centre_1 = 1730, multiplier_1 = 9.5556, centre_2= 1110, multiplier_2 = 10, box_bounds=(-5, 8, 5, 15))

# set 2
# pg = PantoGraph(driver=6.85, follower=11.85, motor_1_pos=-1.5, motor_2_pos=1.5, centre_1 = 1670, multiplier_1 = 9.6667, centre_2= 1100, multiplier_2 = 9.6667, box_bounds=(-7, 8, 7, 18))

# set 3
# pg = PantoGraph(driver=8.5, follower=12.65, motor_1_pos=-1.5, motor_2_pos=1.5, centre_1 = 1760, multiplier_1 = 9.6667, centre_2= 922, multiplier_2 = 9.6667, box_bounds=(-7, 8, 7, 18))

# set 4
# pg = PantoGraph(driver=6.9, follower=10.7, motor_1_pos=-1.5, motor_2_pos=1.5, centre_1 = 2042, multiplier_1 = 10.2667, centre_2= 813, multiplier_2 = 9.4556, box_bounds=(-6.5, 7, 6.5, 15))

# set 4
# pg = PantoGraph(driver=6.85, follower=10.7, motor_1_pos=-1.55, motor_2_pos=1.55, centre_1 = 1721, multiplier_1 = 9.6778, centre_2= 850, multiplier_2 = 9.8889, box_bounds=(-6.5, 7, 6.5, 15))

# set 5
pg = PantoGraph(driver=6.85, follower=10.7, motor_1_pos=-1.55, motor_2_pos=1.55, centre_1 = 1721, multiplier_1 = 9.6778, centre_2= 983, multiplier_2 = 9.8889, box_bounds=(-6, 8, 6, 15.5))
