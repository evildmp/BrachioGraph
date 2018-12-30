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

        HEIGHT=18,          # distance of furthest vertical extension from motors
        L=10.15,            # the lengths of the arms

        # The angles are relative to each motor, so we need to know where each motor actually is.
        MOTOR_1_POS=4,      # position of motor 1 on the x axis
        MOTOR_2_POS=9,      # position of motor 2 on the x axis

        box_bounds=(0, 0, 13, 6),

        angle_multiplier=1,
        correction_1=0,
        correction_2=0,

        centre_1=1350, multiplier_1=425/45,
        centre_2=1315, multiplier_2=415/45
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
        self.HEIGHT = HEIGHT
        self.L = L
        self.MOTOR_1_POS, self.MOTOR_2_POS = MOTOR_1_POS, MOTOR_2_POS

        # the box bounds describe a rectangle that we can safely draw in
        self.box_bounds = box_bounds

        self.angle_multiplier = angle_multiplier

        self.correction_1 = correction_1
        self.correction_2 = correction_2

        self.centre_1, self.centre_2 = centre_1, centre_2
        self.multiplier_1, self.multiplier_2 = multiplier_1, multiplier_2

        self.current_x, self.current_y = self.box_bounds[2]/2, self.box_bounds[3]/2

        self.xy(self.current_x, self.current_y)


    def xy_to_angles(self, x=0, y=0):
        # Given a pair of x/y co-ordinates, returns the angle required of each arm.

        # calculate the x value relative to each motor
        x_relative_to_motor_1 = self.MOTOR_1_POS - x
        x_relative_to_motor_2 = self.MOTOR_2_POS - x

        # calculate the distance from each motor to the x/y point
        d1 = hypotenuse(x_relative_to_motor_1, self.HEIGHT - y)
        d2 = hypotenuse(x_relative_to_motor_2, self.HEIGHT - y)

        # calculate the angle between the 'd' edge and arm
        inner_angle_1 = acos((d1/self.L)/2)
        inner_angle_2 = acos((d2/self.L)/2)

        # calculate the angle between the d1 edge and the vertical
        outer_angle_1 = - atan(x_relative_to_motor_1/(self.HEIGHT-y))
        outer_angle_2 = - atan(x_relative_to_motor_2/(self.HEIGHT-y))

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

        elbow_1_x = sin(angle1) * self.L
        elbow_1_y = sqrt((self.L ** 2) - (elbow_1_x ** 2))

        elbow_2_x = sin(angle2) * self.L
        elbow_2_y = sqrt((self.L ** 2) - (elbow_2_x ** 2))

        elbow_horizontal_distance = (self.MOTOR_2_POS + elbow_2_x) - (self.MOTOR_1_POS + elbow_1_x)
        elbow_vertical_distance = elbow_2_y - elbow_1_y

        base_of_top_triangle = hypotenuse(elbow_horizontal_distance, elbow_vertical_distance)

        angle_of_base_of_top_triangle = asin((- elbow_vertical_distance) / base_of_top_triangle)

        corner_of_top_triangle = acos((base_of_top_triangle / 2) / self.L)

        y = sin(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.L
        x = cos(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.L

        return self.MOTOR_2_POS + elbow_2_x - x, self.HEIGHT - (elbow_2_y + y)


    def command_servo_angles(self, angle_1=0, angle_2=0):
        # moves the servo motor

        pulse_width_1, pulse_width_2 = self.servo_angles_to_pulse_widths(angle_1, angle_2)

        self.rpi.set_servo_pulsewidth(14, pulse_width_1)
        self.rpi.set_servo_pulsewidth(15, pulse_width_2)

        self.angle_1, self.angle_2 = angle_1, angle_2


    def servo_angles_to_pulse_widths(self, angle_1, angle_2):
        # Given a pair of angles, returns the appropriate pulse widths.

        pulse_width_1 = self.centre_1 - self.multiplier_1 * (angle_1 + self.correction_1)
        pulse_width_2 = self.centre_2 - self.multiplier_2 * (angle_2 + self.correction_2)

        return (pulse_width_1, pulse_width_2)


    def __str__(self):
        return self.current_x, self.current_y


    def zero(self):

        self.pen.up()

        x, y = self.angles_to_xy(0, 0)

        self.xy(x, y, wait=.1, interpolate=10)


    def centre(self):

        self.pen.up()
        self.xy(self.box_bounds[2]/2, self.box_bounds[3]/2)



    def report_actual_pulse_widths(self):

        actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
        actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return actual_pulse_width_1, actual_pulse_width_1


    def draw(self, x=0, y=0, wait=.1, interpolate=1):
        self.xy(x=x, y=y, wait=wait, interpolate=interpolate, draw=True)


    def xy(self, x=0, y=0, wait=1, interpolate=10, draw=False):
        # Moves the pen to the xy position; optionally draws

        if draw:
            self.pen.down()
        else:
            self.pen.up()

        (angle_1, angle_2) = self.xy_to_angles(x, y)
        (pulse_width_1, pulse_width_2) = self.servo_angles_to_pulse_widths(angle_1, angle_2)

        # if they are the same, we don't need to move anything
        if (pulse_width_1, pulse_width_2) == self.report_actual_pulse_widths():

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

        # print("Moving from: {:03.1f}, {:03.1f} to {:03.1f}, {:03.1f}".format(
        #     self.current_x, self.current_y, x, y
        #     ))
        # print("Length: {:3.2f}, Steps: {:3d}, Wait for each step: {:3.2f}, Interpolate {:3.2f}".format(
        #     length, no_of_steps, length * wait/no_of_steps, interpolate, end=""
        #     ))

        for step in tqdm(range(no_of_steps)):

            # print(".", end="")

            self.current_x = self.current_x + length_of_step_x
            self.current_y = self.current_y + length_of_step_y

            angle_1, angle_2 = self.xy_to_angles(self.current_x, self.current_y)

            self.command_servo_angles(angle_1, angle_2)

            if step + 1 < no_of_steps:
                sleep(length * wait/no_of_steps)

        # print("waiting for:", length * wait/10)
        sleep(length * wait/10)

        # print()



    def test_pattern(self, bounds=None, wait=1, interpolate=0, repeat=1):

        bounds = bounds or self.box_bounds

        for r in range(repeat):

            self.xy(bounds[0], bounds[1], wait, interpolate)

            for y in range(bounds[1], bounds[3] + 1):

                if y % 2 == 0:
                    self.draw(bounds[2], bounds[1] + y, wait, interpolate)
                    self.xy(bounds[2], bounds[1] + y + 1, wait, interpolate)
                else:
                    self.draw(bounds[0], bounds[1] + y, wait, interpolate)
                    self.xy(bounds[0], bounds[1] + y + 1, wait, interpolate)

        self.pen.up()


    def box(self, bounds=None, wait=1, interpolate=0, repeat=1):

        bounds = bounds or self.box_bounds

        self.xy(bounds[0], bounds[1], wait, interpolate)

        for r in range(repeat):
            self.draw(bounds[2], bounds[1], wait, interpolate)
            self.draw(bounds[2], bounds[3], wait, interpolate)
            self.draw(bounds[0], bounds[3], wait, interpolate)
            self.draw(bounds[0], bounds[1], wait, interpolate)

    def plot_lines(self, lines=[], wait=1, interpolate=1):
        divider = 102.4
        for line in tqdm(lines):
            x, y = line[0]
            self.xy(x/divider, y/divider)
            for segment in tqdm(line[1:]):
                x, y = segment
                self.draw(x/divider, y/divider, wait=wait, interpolate=interpolate)

        self.pen.up()


    def plot_file(self, filename="", wait=1, interpolate=1):

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines, wait=wait, interpolate=interpolate)

        self.pen.up()


class Pen:

    def __init__(self, pin=18, pw_up=1900, pw_down=1150, transition_time=0.25):

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


pg = PantoGraph(correction_1=45, correction_2=-45)
