from pyb import *
from time import sleep
from math import *


def hypotenuse(side1, side2):
    return sqrt(side1 ** 2 + side2 ** 2)



class PantoGraph:

    def __init__(
        self,

        s1=Servo(1),
        s2=Servo(2),

        HEIGHT=18,               # distance of furthest vertical extension from motors
        L=10.15,            # the lengths of the arms

        # The angles are relative to each motor, so we need to know where each motor actually is.
        MOTOR_1_POS=5,     # position of motor 1 on the x axis
        MOTOR_2_POS=7.9,   # position of motor 2 on the x axis

        current_x=0,
        current_y=0,

        box_bounds=(0, 0, 10, 5),

        angle_multiplier=1,
        x_correction=0,
        y_correction=0

    ):

        self.s1 = s1
        self.s2 = s2
        self.HEIGHT = HEIGHT
        self.L = L
        self.MOTOR_1_POS = MOTOR_1_POS
        self.MOTOR_2_POS = MOTOR_2_POS
        self.current_x = current_x
        self.current_y = current_y
        self.box_bounds = box_bounds
        self.angle_multiplier = angle_multiplier
        self.x_correction = x_correction
        self.y_correction = y_correction


    def angles(self, x=0, y=0):

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

        return angle1 * self.angle_multiplier, angle2 * self.angle_multiplier


    def xy(self, x=0, y=0, time=500, wait=1, interpolate=1):

        if interpolate:

            x_length = x - self.current_x
            y_length = y - self.current_y

            length = sqrt(x_length ** 2 + y_length ** 2)

            no_of_steps = (interpolate * int(length)) + 1

            length_of_step_x = x_length/no_of_steps
            length_of_step_y = y_length/no_of_steps

            print("Moving from: {}, {} to {}, {} in {} steps".format(
                self.current_x, self.current_y, x, y, no_of_steps)
                )
            print(end="")

            for step in range(no_of_steps):
                print(".", end="")

                self.current_x = self.current_x + length_of_step_x
                self.current_y = self.current_y + length_of_step_y

                (angle1, angle2) = self.angles(self.current_x, self.current_y)

                self.s1.angle(angle1, int(time/no_of_steps))
                self.s2.angle(angle2, int(time/no_of_steps))

                sleep(4 * wait/no_of_steps)

            print()

        else:

            (angle1, angle2) = self.angles(x, y)

            self.s1.angle(angle1 + self.x_correction, time)
            self.s2.angle(angle2 + self.y_correction, time)

            sleep(wait)

        self.current_x, self.current_y = x, y


    def box(self, bounds=None, time=500, wait=1, interpolate=1, repeat=False):

        bounds = bounds or self.box_bounds

        self.xy(bounds[0], bounds[1], time=0, wait=.3, interpolate=0)

        while True:
            self.xy(bounds[0], bounds[1], time, wait, interpolate)
            self.xy(bounds[2], bounds[1], time, wait, interpolate)
            self.xy(bounds[2], bounds[3], time, wait, interpolate)
            self.xy(bounds[0], bounds[3], time, wait, interpolate)

    def test_pattern(self, bounds=None, time=500, wait=1, interpolate=0):

        bounds = bounds or self.box_bounds

        while True:
            for x in range(bounds[2]):

                self.xy(bounds[0] + x, bounds[1], time, wait, interpolate)
                self.xy(bounds[0] + x, bounds[3], time, wait, interpolate)
                self.xy(bounds[0] + x, bounds[1], time, wait, interpolate)

            for y in range(bounds[3]):

                self.xy(bounds[0], bounds[1] + y, time, wait, interpolate)
                self.xy(bounds[2], bounds[1] + y, time, wait, interpolate)
                self.xy(bounds[0], bounds[1] + y, time, wait, interpolate)

    def comparator(self, bounds=None, time=500, wait=1, interpolate=0):

        bounds = bounds or self.box_bounds

        while True:

            for y in range(0, bounds[3], 2):

                print(1)

                self.xy(bounds[0], bounds[1] + y, time, wait, interpolate)
                print(2)
                self.xy(bounds[2], bounds[1] + y, time, wait, interpolate)
                print(3)
                self.xy(bounds[0], bounds[1] + y, time, wait, interpolate)

            for y in range(1, bounds[3], 2):

                for x in range(bounds[2]):
                    print(4)

                    self.xy(x, bounds[1] + y, time, wait, interpolate)

                for x in range(bounds[2], 0, -1):

                    print(5)
                    self.xy(x, bounds[1] + y, time, wait, interpolate)


    def zero(self, time=500):
        self.s1.angle(0, time)
        self.s2.angle(0, time)



pg_small = PantoGraph(x_correction=5, y_correction=8)
pg_lg = PantoGraph(MOTOR_1_POS=3, MOTOR_2_POS=8, box_bounds=(0, 0, 10, 5), angle_multiplier=-1)



def arc():

    s1.angle(-55)
    s2.angle(-35)

    while True:

        for x in range(-35, 35):
            s1.angle(x-40)
            s2.angle(x+40)
            sleep(.01)

        for x in range(35, -35, -1):
            s1.angle(x-40)
            s2.angle(x+40)
            sleep(.01)


def sweep(start, end, time):

    s1.angle(start, 2000)
    s2.angle(-start, 2000)
    sleep(1)

    for angle in range(start, end, int((end-start)/abs(end-start))):

        s1.angle(angle, time)
        s2.angle(-angle, time)

        sleep(time/2000)

        for variation in range(0, 20):
            s2.angle(-angle + variation, time)
            s1.angle(angle + variation, time)
            sleep(time/2000)



def minmax():

    print(0, 0)

    s1.angle(0, 2000)
    s2.angle(0, 2000)

    sleep(2)

    print(-45, -45)

    s1.angle(-45, 2000)
    s2.angle(-45, 2000)

    sleep(2)

    print(45, -45)

    s1.angle(45, 2000)
    s2.angle(-45, 2000)

    sleep(2)

    print(45, 45)

    s1.angle(45, 2000)
    s2.angle(45, 2000)

    sleep(2)

    print(-45, 45)

    s1.angle(-45, 2000)
    s2.angle(45, 2000)

    sleep(2)













def cross_box(time=500):
    while True:
        xy(6.5, 3.5, time)  # centre
        sleep(1)
        xy(0, 3.5, time)    # left
        sleep(1)
        xy(6.5, 3.5, time)  # centre
        sleep(1)
        xy(6.5, 0, time)    # top
        sleep(1)
        xy(6.5, 3.5, time)  # centre
        sleep(1)
        xy(13, 3.5, time)   # right
        sleep(1)
        xy(6.5, 3.5, time)  # centre
        sleep(1)
        xy(6.5, 7, time)    # right
        sleep(1)
