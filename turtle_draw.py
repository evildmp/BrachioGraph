# run with python3 turtle_draw.py

from turtle import *
import math


# describe the arm and its joints

inner_radius = 4    # the blue (inner) arm
outer_radius = 4    # the red (outer) arm
inner_extent = 120          # the arc covered by each of the two joints
outer_extent = 120
joint_angle = 90      # the centre of the outer arm relative to the blue arm
steps = 5             # number of degrees to step between drawing arcs
draw_arms_every = 10  # the number of degrees between drawing the arms


class T(Turtle):

    def draw_inner_arm(self, angle):

        self.up()
        self.home()
        self.width(2)

        # only draw the inner arm every draw_arms_every degrees
        if (angle/draw_arms_every).is_integer() or angle==inner_extent:
            self.down()
            self.color("blue")
            self.left(angle)
            self.fd(inner_radius * self.multiplier)
            self.dot(5, "black")

        else:
            self.left(angle)
            self.fd(inner_radius * self.multiplier)

    def draw_outer_arm(self):

        self.rt(joint_angle)
        self.color("red")
        # go back to the start of the arm before drawing the arc
        self.fd(outer_radius * self.multiplier)
        self.fd(-outer_radius * self.multiplier)

    def draw_arc(self):

        # get the turtle into the correct position for drawing the arc
        self.up()
        self.rt(180)
        self.fd(outer_radius * self.multiplier)
        self.rt(-90)

        # cover the undrawn part of the arc first
        self.circle(outer_radius * self.multiplier, (360-outer_extent)/2)

        # and then the part we want to draw
        self.color("gray")
        self.down()
        self.width(3)
        self.circle(outer_radius * self.multiplier, outer_extent)


def visualise():

    # set up the environment

    s = Screen()
    s.setup(width=800, height=800)

    mode("logo")

    t = T()

    t.multiplier = 400/(inner_radius + outer_radius)


    t.speed(0)
    t.hideturtle()


    for angle in range (0, inner_extent+1, steps):
        t.draw_inner_arm(angle)
        t.draw_outer_arm()
        t.draw_arc()

    s.exitonclick()


class PGT(T):

    def __init__(
        self,

        driver=4,                  # the lengths of the arms
        follower=10,            # the lengths of the arms

        # The angles are relative to each motor, so we need to know where each motor actually is.
        motor_1_pos = -1, # position of motor 1 on the x axis
        motor_2_pos = 1,  # position of motor 2 on the x axis

        box_bounds=(-3, -3, 3, 3),

        angle_multiplier=1, # set to -1 if necessary to reverse directions
        correction_1=0,
        correction_2=0,

        centre_1=1350, multiplier_1=425/45,
        centre_2=1350, multiplier_2=415/45
        ):

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

        super().__init__()


    def angles_to_xy(self, angle1, angle2):
        # Given the angle of each arm, returns the x/y co-ordinates

        angle1 = math.radians(angle1 * self.angle_multiplier)
        angle2 = math.radians(angle2 * self.angle_multiplier)

        # calculate the x position of the elbows
        elbow_1_x = math.sin(angle1) * self.DRIVER
        elbow_2_x = math.sin(angle2) * self.DRIVER

        print("elbows x:", elbow_1_x, elbow_2_x)

        # calculate the y position of the elbows
        elbow_1_y = math.cos(angle1) * self.DRIVER
        elbow_2_y = math.cos(angle2) * self.DRIVER

        print("elbows y:", elbow_1_y, elbow_2_y)

        motor_distance = self.MOTOR_2_POS - self.MOTOR_1_POS

        # calculate x and y distances between the elbows
        elbow_dx = motor_distance + elbow_2_x - elbow_1_x
        elbow_dy = elbow_2_y - elbow_1_y

        print("elbow distances:", elbow_dx, elbow_dy)

        # calculate the length of the base of the top triangle
        base_of_top_triangle = math.sqrt(elbow_dx ** 2 + elbow_dy ** 2)

        print("base_of_top_triangle:", base_of_top_triangle)

        # calculate the angle at which the top triangle is tilted
        angle_of_base_of_top_triangle = math.asin((elbow_dy) / base_of_top_triangle)

        print("angle_of_base_of_top_triangle", math.degrees(angle_of_base_of_top_triangle))

        # calculate the left inner angle of the top triangle
        corner_of_top_triangle = math.acos((base_of_top_triangle / 2) / self.FOLLOWER)

        print("corner_of_top_triangle", math.degrees(corner_of_top_triangle))

        # calculate the x and y distances to the left elbow
        x_to_elbow = math.cos(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.FOLLOWER
        y_to_elbow = math.sin(corner_of_top_triangle + angle_of_base_of_top_triangle) * self.FOLLOWER

        print("x_to_elbow, y_to_elbow", x_to_elbow, y_to_elbow)

        x = elbow_1_x + x_to_elbow + self.MOTOR_1_POS
        y = elbow_1_y + y_to_elbow

        # return x, y - self.adder

        return x, y


def visualisepg():

    # set up the environment

    s = Screen()
    s.setup(width=800, height=800)


    mode("logo")

    t = PGT()
    t.speed(0)
    t.up()

    multiplier = 400/(t.DRIVER + t.FOLLOWER)

    t.goto(t.MOTOR_1_POS*multiplier, 0)
    t.dot(10, "red")
    t.goto(t.MOTOR_2_POS*multiplier, 0)
    t.dot(10, "blue")



    for angle1 in range (-180, 20, steps):
        for angle2 in range (0, 200, steps):
            x, y = t.angles_to_xy(angle1, angle2)

            t.goto(t.MOTOR_1_POS*multiplier, 0)
            t.setheading(angle1)
            t.down()
            t.color("red")
            t.forward(t.DRIVER*multiplier)

            t.color("green")
            t.goto(x*multiplier, y*multiplier)
            t.up()

            t.goto(t.MOTOR_2_POS*multiplier, 0)
            t.setheading(angle2)
            t.down()
            t.color("blue")
            t.forward(t.DRIVER*multiplier)

            t.color("yellow")
            t.goto(x*multiplier, y*multiplier)
            t.dot(4 , "blue")
            t.up()

    s.exitonclick()

visualise()
mainloop()
