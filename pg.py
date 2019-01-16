from time import sleep
from math import *
import sys
import pigpio
import json
from tqdm import tqdm


def hypotenuse(side1, side2):
    return sqrt(side1 ** 2 + side2 ** 2)


class PantoGraph:

    def __init__(
        self,

        driver=4,            # the lengths of the arms
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
        self.rpi.set_PWM_frequency(14, 100)
        self.rpi.set_PWM_frequency(15, 100)

        # create the pen object, and make sure the pen is up
        self.pen = Pen()
        self.pen.up()

        # set the pantograph geometry
        self.DRIVER = DRIVER
        self.FOLLOWER = FOLLOWER
        self.MOTOR_1_POS, self.MOTOR_2_POS = MOTOR_1_POS, MOTOR_2_POS

        # the box bounds describe a rectangle that we can safely draw in
        self.box_bounds = box_bounds

        self.angle_multiplier = angle_multiplier

        self.correction_1 = correction_1
        self.correction_2 = correction_2

        self.centre_1, self.centre_2 = centre_1, centre_2
        self.multiplier_1, self.multiplier_2 = multiplier_1, multiplier_2


        # the arm cannot work well close to the motors
        self.adder = self.DRIVER * 1.3

        # Initialise the pantograph with the motors straight ahead
        self.set_angles(0, 0)
        self.current_x, self.current_y = self.angles_to_xy(0, 0)


    # ----------------- reporting methods -----------------

    def status(self):

        x, y = self.current_x, self.current_y

        print("Driver/follower arm length: {:03.1f}".format(self.DRIVER, self.FOLLOWER))
        print("Furthest reach: {:03.1f}".format(self.furthest_reach()))
        print("Motor 1 & 2 positions:        {:03.1f}, {:03.1f}".format(self.MOTOR_1_POS, self.MOTOR_2_POS))
        print("Motor angle corrections:      {:03.1f}, {:03.1f}".format(self.correction_1, self.correction_2))
        print("Pulse-width angle multipliers {:03.1f}, {:03.1f}".format(self.multiplier_1, self.multiplier_2))
        print()
        print("Pen x/y:      {: 3.1f}, {: 3.1f}".format(x, y))
        print("Servo angles: {: 3.1f}, {: 3.1f}".format(*self.xy_to_angles(x,y)))
        print("Pulse widths: {:03},    {:03}".format(*self.get_pulse_widths()))


    def drawing_area(self):

        motor_distance = self.MOTOR_2_POS - self.MOTOR_1_POS

        for angle_1 in range(0, -90, -10):
            for angle_2 in range(0, angle_1 -10, -10):

                a1 = radians(angle_1)
                a2 = radians(angle_2)

                elbow_1_x = sin(a1) * self.L                            # s=o/h, s*h=o
                elbow_1_y = sqrt((self.L ** 2) - (elbow_1_x ** 2))      # h2=l2+x2, l=sqrt h2-x2

                elbow_2_x = sin(a2) * self.L
                elbow_2_y = sqrt((self.L ** 2) - (elbow_2_x ** 2))

                elbow_dx = motor_distance + elbow_2_x - elbow_1_x
                elbow_dy = elbow_2_y - elbow_1_y

                base_of_top_triangle = hypotenuse(elbow_dx, elbow_dy)

                angle_of_base_of_top_triangle = asin((elbow_dy) / base_of_top_triangle)

                corner_of_top_triangle = acos((base_of_top_triangle / 2) / self.L) #c=a/h,

                x_to_elbow = cos(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.L #  c=a/h, c*h=a
                y_to_elbow = sin(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.L # s=o/h, o=s*h
                x = elbow_1_x + x_to_elbow + self.MOTOR_1_POS
                y = elbow_1_y + y_to_elbow -self.L

                # x = round(x, 1)
                # y = round(y, 1)


                print(
                    "angles: {:3.0f}, {:3.0f};".format(angle_1, angle_2),
                    "elbow1: {:4.1f}, {:4.1f};".format(elbow_1_x, elbow_1_y),
                    "elbow2: {:4.1f}, {:4.1f};".format(elbow_2_x, elbow_2_y),
                    "base length: {:3.0f};".format(base_of_top_triangle),
                    "base/corner: {:3.0f}, {:3.0f};".format(degrees(angle_of_base_of_top_triangle), degrees(base_of_top_triangle)),
                    "elbow dx/dy: {:4.1f}, {:4.1f};".format(elbow_dx, elbow_dy),
                    "elbow to x/y: {:4.1f}, {:4.1f};".format(x_to_elbow, y_to_elbow),
                    "x/y: {:4.1f}, {:4.1f}".format(x, y)
                )
            print()


    # ----------------- drawing methods -----------------

    def plot_file(self, filename="", wait=1, interpolate=1, rotate=False, divider=102.4):

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines, wait=wait, interpolate=interpolate, rotate=rotate, divider=divider)

        self.pen.up()


    def plot_lines(self, lines=[], wait=1, interpolate=1, rotate=False, divider=102.4):

        for line in tqdm(lines):
            x, y = line[0]
            self.xy(x/divider, y/divider, rotate=rotate)
            for segment in tqdm(line[1:]):
                x, y = segment
                self.draw(x/divider, y/divider, wait=wait, interpolate=interpolate, rotate=rotate)

        self.pen.up()


    def draw(self, x=0, y=0, wait=.5, interpolate=1, rotate=False):
        self.xy(x=x, y=y, wait=wait, interpolate=interpolate, draw=True, rotate=rotate)


    def test_pattern(self, bounds=None, wait=1, interpolate=0, rotate=False, repeat=1):

        bounds = bounds or self.box_bounds

        for r in range(repeat):

            self.xy(bounds[0], bounds[1], wait, interpolate)

            for y in range(bounds[1], bounds[3] + 1):

                if y % 2 == 0:
                    self.draw(bounds[2], bounds[1] + y, wait, interpolate, rotate=rotate)
                    self.xy(bounds[2], bounds[1] + y + 1, wait, interpolate, rotate=rotate)
                else:
                    self.draw(bounds[0], bounds[1] + y, wait, interpolate, rotate=rotate)
                    self.xy(bounds[0], bounds[1] + y + 1, wait, interpolate, rotate=rotate)

        self.pen.up()


    def box(self, bounds=None, wait=1, interpolate=0, rotate=False, repeat=1, reverse=False):

        bounds = bounds or self.box_bounds

        self.xy(bounds[0], bounds[1], wait, interpolate)

        for r in range(repeat):

            if not reverse:

                self.draw(bounds[2], bounds[1], wait, interpolate, rotate=rotate)
                self.draw(bounds[2], bounds[3], wait, interpolate, rotate=rotate)
                self.draw(bounds[0], bounds[3], wait, interpolate, rotate=rotate)
                self.draw(bounds[0], bounds[1], wait, interpolate, rotate=rotate)

            else:

                self.draw(bounds[0], bounds[3], wait, interpolate, rotate=rotate)
                self.draw(bounds[2], bounds[3], wait, interpolate, rotate=rotate)
                self.draw(bounds[2], bounds[1], wait, interpolate, rotate=rotate)
                self.draw(bounds[0], bounds[1], wait, interpolate, rotate=rotate)


    # ----------------- pen-moving methods -----------------


    def centre(self):

        self.pen.up()
        self.xy(self.box_bounds[2]/2, self.box_bounds[3]/2)


    def xy(self, x=0, y=0, wait=.5, interpolate=10, draw=False, rotate=False):
        # Moves the pen to the xy position; optionally draws

        if rotate:
            (x, y) = (y,x)

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

        (length_of_step_x, length_of_step_y) = (x_length/no_of_steps, y_length/no_of_steps)

        for step in tqdm(range(no_of_steps)):

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


    def get_pulse_widths(self):

        actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
        actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return actual_pulse_width_1, actual_pulse_width_2


    # ----------------- trigonometric methods -----------------

    def furthest_reach(self):
        return self.L + sqrt(self.L ** 2 - (self.MOTOR_2_POS-self.MOTOR_1_POS)/2)


    def xy_to_angles(self, x=0, y=0):
        # Given a pair of x/y co-ordinates, returns the angle required of each arm.

        # we add L to y, so that y=0 is a safe distance from the motors

        y = y + self.adder

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

        return x, y - self.adder



class Pen:

    def __init__(self, pin=18, pw_up=2100, pw_down=1250, transition_time=0.25):

        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time

        self.rpi = pigpio.pi()
        self.rpi.set_PWM_frequency(self.pin, 100)

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

pg = PantoGraph(driver=4, follower=9.8, motor_1_pos=-2.5, motor_2_pos=2.5, centre_1 = 1850, multiplier_1 = 9.556, centre_2= 950, multiplier_2 = 9.111, box_bounds=(-4, 0, 4, 5))
