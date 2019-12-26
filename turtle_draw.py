# run with python3 turtle_draw.py

from turtle import *
import math


class BrachioGraphTurtle(Turtle):

    def __init__(self,
        inner_arm=8,          # the length of the inner arm (blue)
        shoulder_centre_angle=0,  # the starting angle of the inner arm, relative to straight ahead
        shoulder_sweep=180,     # the arc covered by the shoulder motor

        outer_arm=8,          # the length of the outer arm (red)
        elbow_centre_angle=90,  # the centre of the outer arm relative to the inner arm
        elbow_sweep=180,        # the arc covered by the elbow motor

        window_size=800,        # width and height of the turtle canvas
        speed=0                 # how fast to draw
        ):

        self.inner_arm = inner_arm
        self.outer_arm = outer_arm
        self.shoulder_centre_angle = shoulder_centre_angle
        self.shoulder_sweep = shoulder_sweep
        self.elbow_centre_angle = elbow_centre_angle
        self.elbow_sweep = elbow_sweep
        self.window_size = window_size

        # some basic dimensions of the drawing area

        grid_size = self.window_size / 1.05  # the grid is a little smaller than the window

        # scale the plotter dimensions to fill the screen
        self.multiplier = grid_size / 2 / (self.inner_arm + self.outer_arm)

        self.reach = self.inner_arm + self.outer_arm  # the maximum possible distance the arms could reach
        self.draw_reach = self.reach * self.multiplier * 1.05  # maximum possible drawing reacg

        # set up the screen for the turtle

        self.screen = Screen()
        self.screen.mode("logo")
        self.screen.title(f"inner length {self.inner_arm}cm • centre {self.shoulder_centre_angle}˚ • sweep {self.shoulder_sweep}˚  •  outer length {self.outer_arm}cm • centre {self.elbow_centre_angle}˚ • sweep {self.elbow_sweep}˚")
        self.screen.setup(width=window_size, height=window_size)

        super().__init__()

        self.speed(0)
        self.hideturtle()
        self.screen.tracer(speed, 0)


    def simple_title(self, title=""):
        title = title or "BrachioGraph, multiple values"
        self.screen.title(title)


    # ----------------- grid drawing methods -----------------

    def draw_grid(self):
        self.draw_grid_lines(draw_every=1, color="gray", width=1, include_numbers=False)
        self.draw_grid_lines(draw_every=5, color="black", width=2, include_numbers=True)

    def draw_grid_lines(self, draw_every=1, color="gray", width=1, include_numbers=False):

        self.color(color)
        self.width(width)

        for i in range(int(-self.reach), int(self.reach +1)):
            if not (i % draw_every):

                draw_i = i * self.multiplier
                self.up()
                self.goto(draw_i, - self.draw_reach)
                self.down()
                self.goto(draw_i, self.draw_reach)
                self.up()
                self.goto(- self.draw_reach, draw_i)
                self.down()
                self.goto(self.draw_reach, draw_i)

                if include_numbers:

                    self.up()
                    self.goto(i * self.multiplier, - 1 * self.multiplier)
                    self.write(" " + str(i), move=False, font=("Helvetica", 16, "bold"))
                    self.goto(- self.reach * self.multiplier, i * self.multiplier)
                    self.write(i, move=False, font=("Helvetica", 16, "bold"))



    # ----------------- arc drawing methods -----------------

    def draw_pen_arc(self, width=1, color="black"):

        # get the turtle into the correct position for drawing the arc
        self.up()
        self.rt(180)
        self.fd(self.outer_arm * self.multiplier)
        self.rt(-90)

        # cover the undrawn part of the arc first
        self.circle(self.outer_arm * self.multiplier, (360 - self.elbow_sweep)/2)

        # and then the part we want to draw
        self.color(color)
        self.down()
        self.width(width)
        self.circle(self.outer_arm * self.multiplier, self.elbow_sweep)

    def draw_arms_arc(self, elbow_centre_angle, width, color="black", reverse=False):

        # how far do we reach from the origin with this elbow angle?
        reach = math.sqrt(
            self.inner_arm ** 2 + self.outer_arm ** 2 - 2 * self.inner_arm * self.outer_arm * math.cos(math.radians(
                # inner angle of the two arms
                180 - elbow_centre_angle)
            )
        )
        # angle between the inner arm and the line of maximum reach when the inner arm is fully right
        # avoid a division by zero error
        if reach == 0:
            a = 0
        elif (self.inner_arm ** 2 + reach ** 2 - self.outer_arm ** 2) / (2 * self.inner_arm * reach) > 1:
            a = 0
        else:
            a = math.acos((self.inner_arm ** 2 + reach ** 2 - self.outer_arm ** 2) / (2 * self.inner_arm * reach))
        # the angle of the the line of maximum relative to 0
        heading = self.shoulder_centre_angle + self.shoulder_sweep/2 + math.degrees(a)

        if reverse:
            sweep = self.shoulder_sweep * -1
            heading = heading - self.shoulder_sweep
        else:
            sweep = self.shoulder_sweep

        self.draw_arc_around_origin(heading, reach, sweep, width, color)


    def draw_arc_around_origin(self, heading, reach, sweep, width, color):

        self.up()
        self.home()
        self.rt(heading)
        self.fd(reach * self.multiplier)
        self.setheading(heading - 90)
        self.down()
        self.width(width)
        self.color(color)
        self.circle(reach * self.multiplier, sweep)


    # ----------------- outline drawing -----------------

    def draw_outline(self, width=4, color=None, lightness=1):

        # sweep inner arm with outer arm fully left
        outer_arm_angle = self.elbow_centre_angle - self.elbow_sweep / 2
        self.draw_arms_arc(outer_arm_angle, width, color=color or "blue")

        # sweep outer arm with inner arm fully left
        self.up()
        self.home()
        self.rt(self.shoulder_centre_angle - self.shoulder_sweep/2)
        self.fd(self.inner_arm * self.multiplier)
        self.rt(self.elbow_centre_angle)
        self.draw_pen_arc(width, color=color or "red")

        # sweep inner arm with outer arm fully right
        outer_arm_angle = self.elbow_centre_angle + self.elbow_sweep / 2
        self.draw_arms_arc(outer_arm_angle, width, color=color or "purple4", reverse=True)

        # sweeo outer arm with inner arm fully right
        self.up()
        self.home()
        self.rt(self.shoulder_centre_angle + self.shoulder_sweep/2)
        self.fd(self.inner_arm * self.multiplier)
        self.rt(self.elbow_centre_angle)
        self.draw_pen_arc(width, color=color or "orange")

        self.screen.update()


    def draw_arcs(self, every=2, color="orange"):

        for angle in range (int(self.shoulder_centre_angle + self.shoulder_sweep/2), int(self.shoulder_centre_angle - self.shoulder_sweep/2 - 1), - every):

            self.up()
            self.home()

            self.rt(angle)
            self.fd(self.inner_arm * self.multiplier)

            self.rt(self.elbow_centre_angle)

            self.draw_pen_arc(color=color)


    def draw_arms(self, every=60):

        for angle in range (int(self.shoulder_centre_angle + self.shoulder_sweep/2), int(self.shoulder_centre_angle - self.shoulder_sweep/2 -1), -every):
            self.up()
            self.home()
            self.width(6)

            self.down()

            self.color("blue")
            self.rt(angle)
            self.fd(self.inner_arm * self.multiplier)

            self.rt(self.elbow_centre_angle)
            self.color("red")
            self.fd(self.outer_arm * self.multiplier)

        self.screen.update()
