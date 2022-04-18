import math
from turtle import Turtle, Screen


class BaseTurtle(Turtle):
    def __init__(
        self,
        window_size: int = 800,  # width and height of the turtle canvas
        reach: float = 16,
        speed: int = 0,  # how fast to draw
        machine=None,  # the PantoGraph object to which the turtle belongs
        coarseness: int = 0,  # a factor, in degrees, to represent the resolution of the servos
    ):

        super().__init__()

        self.window_size = window_size
        self.reach = reach
        self.machine = machine
        self.coarseness = coarseness

        if self.machine:
            self.angle_1 = self.machine.angle_1
            self.angle_2 = self.machine.angle_2

        # some basic dimensions of the drawing area

        grid_size = (
            self.window_size / 1.05
        )  # the grid is a little smaller than the window

        self.multiplier = grid_size / 2 / self.reach
        self.draw_reach = (
            self.reach * self.multiplier * 1.05
        )  # maximum possible drawing reach

        # set up the screen for the turtle

        self.screen = Screen()
        self.screen.mode("logo")

        self.speed(0)
        self.screen.tracer(speed, 0)
        self.screen.setup(width=window_size, height=window_size)

    # ----------------- grid drawing methods -----------------

    def draw_grid(self):
        self.draw_grid_lines(draw_every=1, color="#bbb", width=1, include_numbers=False)
        self.draw_grid_lines(draw_every=5, color="black", width=1, include_numbers=True)

    def draw_grid_lines(
        self, draw_every=1, color="gray", width=1, include_numbers=False
    ):
        self.color(color)
        self.width(width)

        for i in range(int(-self.reach), int(self.reach + 1)):
            if not (i % draw_every):

                draw_i = i * self.multiplier
                self.up()
                self.goto(draw_i, -self.draw_reach)
                self.down()
                self.goto(draw_i, self.draw_reach)
                self.up()
                self.goto(-self.draw_reach, draw_i)
                self.down()
                self.goto(self.draw_reach, draw_i)

                if include_numbers:

                    self.up()
                    self.goto(i * self.multiplier, -1 * self.multiplier)
                    self.write(" " + str(i), move=False, font=("Helvetica", 16, "bold"))
                    self.goto(-self.reach * self.multiplier, i * self.multiplier)
                    self.write(i, move=False, font=("Helvetica", 16, "bold"))

    def set_angles(self, angle_1, angle_2):

        if self.coarseness:

            coarsened_angle_1 = self.coarsen_angle(angle_1)
            coarsened_angle_2 = self.coarsen_angle(angle_2)

            diff_1 = coarsened_angle_1 - self.angle_1
            diff_2 = coarsened_angle_2 - self.angle_2
            length = math.sqrt(diff_1**2 + diff_2**2)
            no_of_steps = int(length * 10)

            if no_of_steps:

                (length_of_step_1, length_of_step_2) = (
                    diff_1 / no_of_steps,
                    diff_2 / no_of_steps,
                )

                for step in range(no_of_steps):
                    self.angle_1 = self.angle_1 + length_of_step_1
                    self.angle_2 = self.angle_2 + length_of_step_2

                    x, y = self.machine.angles_to_xy(self.angle_1, self.angle_2)
                    self.setpos(x * self.multiplier, y * self.multiplier)
        else:

            x, y = self.machine.angles_to_xy(angle_1, angle_2)
            self.setpos(x * self.multiplier, y * self.multiplier)

    def coarsen_angle(self, angle):
        return round(angle / self.coarseness) * self.coarseness


class BrachioGraphTurtle(BaseTurtle):
    """A turtle-graphics implementation of a BrachioGraph. Instantiate your ``BrachioGraph`` with
    ``turtle=True`` to create a turtle version of it, that copies everything the BrachioGraph does.
    """

    def __init__(
        self,
        inner_arm: float = 8,
        outer_arm: float = 8,
        window_size: int = 800,  # width and height of the turtle canvas
        speed: int = 0,  # how fast to draw
        shoulder_centre_angle=0,  # the starting angle of the inner arm, relative to straight ahead
        elbow_centre_angle=90,  # the centre of the outer arm relative to the inner arm
        shoulder_sweep=180,  # the arc covered by the shoulder motor
        elbow_sweep=180,  # the arc covered by the elbow motor
        machine=None,  # the BrachioGraph object to which the turtle belongs
        coarseness: int = 0,  # a factor, in degrees, to represent the resolution of the servos
    ):

        self.inner_arm = inner_arm
        self.outer_arm = outer_arm
        self.shoulder_centre_angle = shoulder_centre_angle
        self.shoulder_sweep = shoulder_sweep
        self.elbow_centre_angle = elbow_centre_angle
        self.elbow_sweep = elbow_sweep

        super().__init__(
            reach=self.inner_arm + self.outer_arm,
            window_size=window_size,
            speed=speed,
            machine=machine,
            coarseness=coarseness,
        )

        self.screen.title(
            f"inner length {self.inner_arm}cm • centre {self.shoulder_centre_angle}˚ • sweep {self.shoulder_sweep}˚  •  outer length {self.outer_arm}cm • centre {self.elbow_centre_angle}˚ • sweep {self.elbow_sweep}˚"
        )

    def simple_title(self, title=""):
        title = title or "BrachioGraph, multiple values"
        self.screen.title(title)

    # ----------------- arc drawing methods -----------------

    def draw_pen_arc(self, width=1, color="black"):

        # get the turtle into the correct position for drawing the arc
        self.up()
        self.rt(180)
        self.fd(self.outer_arm * self.multiplier)
        self.rt(-90)

        # cover the undrawn part of the arc first
        self.circle(self.outer_arm * self.multiplier, (360 - self.elbow_sweep) / 2)

        # and then the part we want to draw
        self.color(color)
        self.down()
        self.width(width)
        self.circle(self.outer_arm * self.multiplier, self.elbow_sweep)

    def draw_arms_arc(self, elbow_centre_angle, width, color="black", reverse=False):

        # how far do we reach from the origin with this elbow angle?
        reach = math.sqrt(
            self.inner_arm**2
            + self.outer_arm**2
            - 2
            * self.inner_arm
            * self.outer_arm
            * math.cos(
                math.radians(
                    # inner angle of the two arms
                    180
                    - elbow_centre_angle
                )
            )
        )
        # angle between the inner arm and the line of maximum reach when the inner arm is fully right
        # avoid a division by zero error
        if reach == 0:
            a = 0
        elif (self.inner_arm**2 + reach**2 - self.outer_arm**2) / (
            2 * self.inner_arm * reach
        ) > 1:
            a = 0
        else:
            a = math.acos(
                (self.inner_arm**2 + reach**2 - self.outer_arm**2)
                / (2 * self.inner_arm * reach)
            )
        # the angle of the the line of maximum relative to 0
        heading = self.shoulder_centre_angle + self.shoulder_sweep / 2 + math.degrees(a)

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
        self.rt(self.shoulder_centre_angle - self.shoulder_sweep / 2)
        self.fd(self.inner_arm * self.multiplier)
        self.rt(self.elbow_centre_angle)
        self.draw_pen_arc(width, color=color or "red")

        # sweep inner arm with outer arm fully right
        outer_arm_angle = self.elbow_centre_angle + self.elbow_sweep / 2
        self.draw_arms_arc(
            outer_arm_angle, width, color=color or "purple4", reverse=True
        )

        # sweep outer arm with inner arm fully right
        self.up()
        self.home()
        self.rt(self.shoulder_centre_angle + self.shoulder_sweep / 2)
        self.fd(self.inner_arm * self.multiplier)
        self.rt(self.elbow_centre_angle)
        self.draw_pen_arc(width, color=color or "orange")

        self.screen.update()

    def draw_arcs(self, every=2, color="orange"):

        for angle in range(
            int(self.shoulder_centre_angle + self.shoulder_sweep / 2),
            int(self.shoulder_centre_angle - self.shoulder_sweep / 2 - 1),
            -every,
        ):

            self.up()
            self.home()

            self.rt(angle)
            self.fd(self.inner_arm * self.multiplier)

            self.rt(self.elbow_centre_angle)

            self.draw_pen_arc(color=color)

    def draw_arms(self, every=60):

        for angle in range(
            int(self.shoulder_centre_angle + self.shoulder_sweep / 2),
            int(self.shoulder_centre_angle - self.shoulder_sweep / 2 - 1),
            -every,
        ):
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


class PantoGraphTurtle(BaseTurtle):
    """A turtle-graphics implementation of a PantoGraph. Instantiate your ``PantoGraph`` with
    ``turtle=True`` to create a turtle version of it, that copies everything the PantoGraph does.
    """

    def __init__(
        self,
        driver: int = 8,
        follower: int = 8,
        motor_1_pos: float = -1.5,
        motor_2_pos: float = 1.5,
        window_size: int = 800,  # width and height of the turtle canvas
        speed: int = 0,  # how fast to draw
        motor_1_centre_angle: float = 0,  # starting angle of first arm, relative to straight ahead
        motor_2_centre_angle: float = 0,  # starting angle of 2nd arm, relative to straight ahead
        motor_1_sweep: int = 180,  # the arc covered by the first motor
        motor_2_sweep: int = 180,  # the arc covered by the second motor
        machine=None,  # the PantoGraph object to which the turtle belongs
        coarseness: int = 0,  # a factor, in degrees, to represent the resolution of the servos
    ):

        # set the pantograph geometry
        self.driver = driver
        self.follower = follower
        self.motor_1_pos = motor_1_pos
        self.motor_2_pos = motor_2_pos
        self.motor_1_centre_angle = motor_1_centre_angle
        self.motor_2_centre_angle = motor_2_centre_angle
        self.motor_1_sweep = motor_1_sweep
        self.motor_2_sweep = motor_2_sweep

        super().__init__(
            reach=self.driver + self.follower,
            window_size=window_size,
            speed=speed,
            machine=machine,
            coarseness=coarseness,
        )

        self.screen.title(
            f"driver length {self.driver}cm • centre {self.motor_1_centre_angle}˚ • sweep {self.motor_1_sweep}˚  •  follower length {self.follower}cm • centre {self.motor_2_centre_angle}˚ • sweep {self.motor_2_sweep}˚"
        )
