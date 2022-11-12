# coding=utf-8

from time import sleep
from collections import namedtuple
import readchar
from math import *
import numpy
import json
import pigpio
from plotter import Plotter, Pen


def hypotenuse(side1, side2):
    return sqrt(side1**2 + side2**2)


class PantoGraph(Plotter):
    """A drawing robot with a pantograph design."""

    def __init__(
        self,
        #  ----------------- geometry of the plotter -----------------
        driver=8,  # the lengths of the arms
        follower=8,  # the lengths of the arms
        # The angles are relative to each motor, so we need to know where each motor actually is.
        motor_1_pos=-1.5,  # position of motor 1 on the x axis
        motor_2_pos=1.5,  # position of motor 2 on the x axis
        bounds=(-3, 3, 3, 6),  # the maximum rectangular drawing area
        angle_multiplier=1,  # set to -1 if necessary to reverse directions
        correction_1=0,
        correction_2=0,
        centre_1=1500,
        multiplier_1=425 / 45,
        centre_2=1500,
        multiplier_2=415 / 45,
        #  ----------------- naive calculation values -----------------
        servo_1_parked_pw=1500,  # pulse-widths when parked
        servo_2_parked_pw=1500,
        servo_1_degree_ms=-10,  # milliseconds pulse-width per degree
        servo_2_degree_ms=10,  # reversed for the mounting of the shoulder servo
        servo_1_parked_angle=-45,  # the arm angle in the parked position
        servo_2_parked_angle=45,
        #  ----------------- hysteresis -----------------
        hysteresis_correction_1=0,  # hardware error compensation
        hysteresis_correction_2=0,
        #  ----------------- servo angles and pulse-widths in lists -----------------
        servo_1_angle_pws=[],  # pulse-widths for various angles
        servo_2_angle_pws=[],
        #  ----------------- servo angles and pulse-widths in lists (bi-directional) ------
        servo_1_angle_pws_bidi=[],  # bi-directional pulse-widths for various angles
        servo_2_angle_pws_bidi=[],
        #  ----------------- the pen -----------------
        pw_up=1500,  # pulse-widths for pen up/down
        pw_down=1100,
        #  ----------------- misc -----------------
        wait: float = None,  # default wait time between operations
        resolution: float = None,  # default resolution of the plotter in cm
        virtual=False,  # run in virtual mode
        turtle=False,
    ):

        # set the pantograph geometry
        self.driver = driver
        self.follower = follower
        self.motor_1_pos, self.motor_2_pos = motor_1_pos, motor_2_pos

        self.angle_multiplier = angle_multiplier

        self.correction_1 = correction_1
        self.correction_2 = correction_2

        self.centre_1, self.centre_2 = centre_1, centre_2
        self.multiplier_1, self.multiplier_2 = multiplier_1, multiplier_2

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
            resolution=resolution,
            virtual=virtual,
            turtle=turtle,
        )

        self.set_angles(0, 0)
        self.x, self.y = self.angles_to_xy(0, 0)
        self.quiet()

    # ----------------- trigonometric methods -----------------

    @property
    def furthest_reach(self):
        return self.driver + sqrt(
            self.follower**2 - (self.motor_2_pos - self.motor_1_pos) / 2
        )

    def xy_to_angles(self, x=0, y=None):
        """Takes a pair of x/y co-ordinates, and returns the angle required of each arm."""

        if y is None:
            y = self.furthest_reach

        # calculate the x value relative to each motor
        x_relative_to_motor_1 = self.motor_1_pos - x
        x_relative_to_motor_2 = self.motor_2_pos - x

        # calculate the distance from each motor to the x/y point
        d1 = hypotenuse(x_relative_to_motor_1, y)
        d2 = hypotenuse(x_relative_to_motor_2, y)

        # calculate the angle between the d line and driver arm
        inner_angle_1 = acos(
            (self.driver**2 + d1**2 - self.follower**2) / (2 * self.driver * d1)
        )
        inner_angle_2 = acos(
            (self.driver**2 + d2**2 - self.follower**2) / (2 * self.driver * d2)
        )

        # calculate the angle between the d line and the vertical
        outer_angle_1 = -asin(x_relative_to_motor_1 / d1)
        outer_angle_2 = -asin(x_relative_to_motor_2 / d1)

        # calculate the sum of the angles in degrees
        angle1 = degrees(outer_angle_1 - inner_angle_1)
        angle2 = degrees(inner_angle_2 + outer_angle_2)

        return (angle1 * self.angle_multiplier, angle2 * self.angle_multiplier)

    def angles_to_xy(self, angle1, angle2):
        """Given the angle of each arm, return the x/y co-ordinates."""

        angle1 = radians(angle1)
        angle2 = radians(angle2)

        # calculate the x position of the elbows
        elbow_1_x = sin(angle1) * self.driver
        elbow_2_x = sin(angle2) * self.driver

        # calculate the y position of the elbows
        elbow_1_y = cos(angle1) * self.driver
        elbow_2_y = cos(angle2) * self.driver

        motor_distance = self.motor_2_pos - self.motor_1_pos

        # calculate x and y distances between the elbows
        elbow_dx = motor_distance + elbow_2_x - elbow_1_x
        elbow_dy = elbow_2_y - elbow_1_y

        # calculate the length of the base of the top triangle
        base_of_top_triangle = hypotenuse(elbow_dx, elbow_dy)

        # calculate the angle at which the top triangle is tilted
        if elbow_dx:
            angle_of_base_of_top_triangle = atan(elbow_dy / elbow_dx)
        elif elbow_dy:
            angle_of_base_of_top_triangle = asin(
                elbow_dy / hypotenuse(elbow_dx, elbow_dy)
            )
        else:
            angle_of_base_of_top_triangle = 0

        # calculate inner angles of the top triangle relative to its base
        corner_of_top_triangle = acos((base_of_top_triangle / 2) / self.follower)

        # calculate the x and y distances to the left elbow
        x_to_elbow = (
            cos(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.follower
        )
        y_to_elbow = (
            sin(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.follower
        )

        x = elbow_1_x + x_to_elbow + self.motor_1_pos
        y = elbow_1_y + y_to_elbow

        return x, y

    def setup_turtle(self):

        from turtle_plotter import PantoGraphTurtle
        
        self.turtle = PantoGraphTurtle(
            driver=self.driver,
            follower=self.follower,
            motor_1_pos=self.motor_1_pos,
            motor_2_pos=self.motor_2_pos,
            window_size=800,
            speed=5,
            machine=self,
            coarseness=self.turtle_coarseness,
        )

        self.turtle.draw_grid()
