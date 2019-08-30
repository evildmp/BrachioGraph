# run with python3 turtle_draw.py

from turtle import *
import math


# describe the arm and its joints

inner_radius = 180    # the blue (inner) arm
outer_radius = 160    # the red (outer) arm
extent = 160          # the arc covered by each of the two joints
joint_angle = 90      # the centre of the outer arm relative to the blue arm
steps = 5             # number of degrees to step between drawing arcs
draw_arms_every = 10  # the number of degrees between drawing the arms


class T(Turtle):

    def draw_inner_arm(self, angle):

        self.up()
        self.home()
        self.width(2)

        # only draw the inner arm every draw_arms_every degrees
        if (angle/draw_arms_every).is_integer() or angle==extent:
            self.down()
            self.color("blue")
            self.left(angle)
            self.fd(inner_radius)
            self.dot(5, "black")

        else:
            self.left(angle)
            self.fd(inner_radius)

    def draw_outer_arm(self):

        self.rt(joint_angle)
        self.color("red")
        # go back to the start of the arm before drawing the arc
        self.fd(outer_radius)
        self.fd(-outer_radius)

    def draw_arc(self):

        # get the turtle into the correct position for drawing the arc
        self.up()
        self.rt(180)
        self.fd(outer_radius)
        self.rt(-90)

        # cover the undrawn part of the arc first
        self.circle(outer_radius, (360-extent)/2)

        # and then the part we want to draw
        self.color("gray")
        self.down()
        self.width(3)
        self.circle(outer_radius, extent)


def visualise():

    # set up the environment

    s = Screen()
    s.setup(width=800, height=800)

    mode("logo")

    t = T()
    t.speed(0)
    t.hideturtle()


    for angle in range (0, extent+1, steps):
        t.draw_inner_arm(angle)
        t.draw_outer_arm()
        t.draw_arc()

    s.exitonclick()


# mainloop()
