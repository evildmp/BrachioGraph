"""Contains a base class for a drawing robot.
 virtual version."""

from time import sleep
from plotter import Plotter

class Plotter(Plotter):
    def virtualise(self):
        # TODO: write this
        print("Initialising virtual BrachioGraph")
        self.virtual = True
        # self.virtual_pw_1 = self.angles_to_pw_1(-90)
        # self.virtual_pw_2 = self.angles_to_pw_2(90)
        # by default in virtual mode, we use a wait factor of 0 for speed


    def park(self):
        print("Parking.")
    # ----------------- physical control methods -----------------

    def set_pulse_widths(self, pw_1=None, pw_2=None):
        """Applies the supplied pulse-width values to the servos."""

        if self.virtual:

            if pw_1:
                if 500 < pw_1 < 2500:
                    self.virtual_pw_1 = pw_1
                else:
                    raise ValueError

            if pw_2:
                if 500 < pw_2 < 2500:
                    self.virtual_pw_2 = pw_2
                else:
                    raise ValueError

    def get_pulse_widths(self):
        """Returns the actual pulse-widths values; if in virtual mode, returns the nominal values -
        i.e. the values that they might be.
        """

        if self.virtual:

            actual_pulse_width_1 = self.virtual_pw_1
            actual_pulse_width_2 = self.virtual_pw_2

    def quiet(self, servos=[14, 15, 18]):
        """Stop sending pulses to the servos, so that they are no longer energised (and so that they
        stop buzzing).
        """

        print("Going quiet")

class Pen:
    def __init__(
        self, bg, pw_up=1700, pw_down=1300, pin=18, transition_time=0.25
    ):

        self.bg = bg
        self.pin = pin
        self.pw_up = pw_up
        self.pw_down = pw_down
        self.transition_time = transition_time

        print("Initialising virtual Pen")

        self.up()
        sleep(0.3)
        self.down()
        sleep(0.3)
        self.up()
        sleep(0.3)

    def down(self):

        self.virtual_pw = self.pw_down

        if self.bg.turtle:
            self.bg.turtle.down()
            self.bg.turtle.color("blue")
            self.bg.turtle.width(1)

        self.position = "down"

    def up(self):

        self.virtual_pw = self.pw_up

        if self.bg.turtle:
            self.bg.turtle.up()

        self.position = "up"

    # for convenience, a quick way to set pen motor pulse-widths
    def pw(self, pulse_width):

        self.virtual_pw = pulse_width
