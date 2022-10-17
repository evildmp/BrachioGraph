"""Contains a base class for a drawing robot."""

from time import sleep
import pigpio
import numpy
from plotter import Plotter


class Plotter(Plotter):

    def __init__(
        self,
        #  ----------------- geometry of the plotter -----------------
        bounds: tuple = [-10, 5, 10, 15],  # the maximum rectangular drawing area
        #  ----------------- naive calculation values -----------------
        servo_1_parked_pw: int = 1500,  # pulse-widths when parked
        servo_2_parked_pw: int = 1500,
        servo_1_degree_ms: float = -10,  # milliseconds pulse-width per degree
        servo_2_degree_ms: float = 10,
        servo_1_parked_angle: float = 0,  # the arm angle in the parked position
        servo_2_parked_angle: float = 0,
        #  ----------------- hysteresis -----------------
        hysteresis_correction_1: float = 0,  # hardware error compensation
        hysteresis_correction_2: float = 0,
        #  ----------------- servo angles and pulse-widths in lists -----------------
        servo_1_angle_pws: tuple = (),  # pulse-widths for various angles
        servo_2_angle_pws: tuple = (),
        #  ----------------- servo angles and pulse-widths in lists (bi-directional) ------
        servo_1_angle_pws_bidi: tuple = (
        ),  # bi-directional pulse-widths for various angles
        servo_2_angle_pws_bidi: tuple = (),
        #  ----------------- the pen -----------------
        pen_pin: int = 18,
        pen_transition_time: float = 0.25,
        pw_up: int = 1500,  # pulse-widths for pen up/down
        pw_down: int = 1100,
        #  ----------------- physical control -----------------
        wait: float = None,  # default wait time between operations
        resolution: float = None,  # default resolution of the plotter in cm
        **kwargs
    ):

        self.angle_shoulder = servo_1_parked_angle
        self.angle_elbow = servo_2_parked_angle

        self.bounds = bounds

        # if pulse-widths to angles are supplied for each servo, we will feed them to
        # numpy.polyfit(), to produce a function for each one. Otherwise, we will use a simple
        # approximation based on a centre of travel of 1500µS and 10µS per degree

        self.pen_pin = pen_pin
        self.pen_transition_time = pen_transition_time
        self.pw_up = pw_up
        self.pw_doen = pw_down
        self.servo_1_parked_pw = servo_1_parked_pw
        self.servo_1_degree_ms = servo_1_degree_ms
        self.servo_1_parked_angle = servo_1_parked_angle
        self.hysteresis_correction_1 = hysteresis_correction_1

        if servo_1_angle_pws_bidi:
            servo_1_angle_pws = []
            differences = []
            for angle, pws in servo_1_angle_pws_bidi.items():
                pw = (pws["acw"] + pws["cw"]) / 2
                servo_1_angle_pws.append([angle, pw])
                differences.append((pws["acw"] - pws["cw"]) / 2)
            self.hysteresis_correction_1 = numpy.mean(differences)

        if servo_1_angle_pws:
            servo_1_array = numpy.array(servo_1_angle_pws)
            self.angles_to_pw_1 = numpy.poly1d(
                numpy.polyfit(servo_1_array[:, 0], servo_1_array[:, 1], 3))

        else:
            self.angles_to_pw_1 = self.naive_angles_to_pulse_widths_1

        self.servo_2_parked_pw = servo_2_parked_pw
        self.servo_2_degree_ms = servo_2_degree_ms
        self.servo_2_parked_angle = servo_2_parked_angle
        self.hysteresis_correction_2 = hysteresis_correction_2

        if servo_2_angle_pws_bidi:
            servo_2_angle_pws = []
            differences = []
            for angle, pws in servo_2_angle_pws_bidi.items():
                pw = (pws["acw"] + pws["cw"]) / 2
                servo_2_angle_pws.append([angle, pw])
                differences.append((pws["acw"] - pws["cw"]) / 2)
            self.hysteresis_correction_2 = numpy.mean(differences)

        if servo_2_angle_pws:
            servo_2_array = numpy.array(servo_2_angle_pws)
            self.angles_to_pw_2 = numpy.poly1d(
                numpy.polyfit(servo_2_array[:, 0], servo_2_array[:, 1], 3))

        else:
            self.angles_to_pw_2 = self.naive_angles_to_pulse_widths_2

        # set some initial values required for moving methods
        self.previous_pw_1 = self.previous_pw_2 = 0
        self.active_hysteresis_correction_1 = self.active_hysteresis_correction_2 = 0

        try:
            pigpio.exceptions = False
            # instantiate this Raspberry Pi as a pigpio.pi() instance
            self.rpi = pigpio.pi()
            # the pulse frequency should be no higher than 100Hz - higher values could
            # (supposedly) # damage the servos
            self.rpi.set_PWM_frequency(14, 50)
            self.rpi.set_PWM_frequency(15, 50)
            self.rpi.set_PWM_frequency(self.pen_pin, 50)
            pigpio.exceptions = True
            # by default we use a wait factor of 0.1 for accuracy
            self.wait = wait if wait is not None else 0.1

        except AttributeError:
            print("FATAL: pigpio daemon is not available.")
            exit(1)


        self.resolution = resolution or 1

        super().__init__(
            bounds=bounds,
            hysteresis_correction_1=hysteresis_correction_1,
            hysteresis_correction_2=hysteresis_correction_2,
            wait=wait,
            **kwargs
            # resolution=resolution,
            # turtle=turtle,
            # turtle_coarseness=turtle_coarseness,
        )

        self.move_angles(angle_shoulder=self.servo_1_parked_angle, angle_elbow=self.servo_2_parked_angle)

        self.status()

    #  ----------------- angles-to-pulse-widths methods -----------------

    def naive_angles_to_pulse_widths_1(self, angle):
        """A rule-of-thumb calculation of pulse-width for the desired servo angle"""
        return (angle - self.servo_1_parked_angle
                ) * self.servo_1_degree_ms + self.servo_1_parked_pw

    def naive_angles_to_pulse_widths_2(self, angle):
        """A rule-of-thumb calculation of pulse-width for the desired servo angle"""
        return (angle - self.servo_2_parked_angle
                ) * self.servo_2_degree_ms + self.servo_2_parked_pw

    # ----------------- physical control methods -----------------

    def set_angle_servo_shoulder(self, angle):
        # TODO: verify that angle is within boundaries? is_angle_in_range()
        pw_1 = None
        pw_1 = self.angles_to_pw_1(angle)

        if pw_1 > self.previous_pw_1:
            self.active_hysteresis_correction_1 = self.hysteresis_correction_1
        elif pw_1 < self.previous_pw_1:
            self.active_hysteresis_correction_1 = -self.hysteresis_correction_1

        self.previous_pw_1 = pw_1

        pw_1 = pw_1 + self.active_hysteresis_correction_1

        self.pulse_widths_used_1.add(int(pw_1))

        self.set_pulse_widths(pw_1=pw_1)

    def set_angle_servo_elbow(self, angle):
        # TODO: verify that angle is within boundaries? is_angle_in_range()
        pw_2 = None
        pw_2 = self.angles_to_pw_2(angle)

        if pw_2 > self.previous_pw_2:
            self.active_hysteresis_correction_2 = self.hysteresis_correction_2
        elif pw_2 < self.previous_pw_2:
            self.active_hysteresis_correction_2 = -self.hysteresis_correction_2

        self.previous_pw_2 = pw_2

        pw_2 = pw_2 + self.active_hysteresis_correction_2

        self.pulse_widths_used_2.add(int(pw_2))

        self.set_pulse_widths(pw_2=pw_2)

    def set_pulse_widths(self, pw_1=None, pw_2=None):
        """Applies the supplied pulse-width values to the servos."""

        if pw_1:
            self.rpi.set_servo_pulsewidth(14, pw_1)
        if pw_2:
            self.rpi.set_servo_pulsewidth(15, pw_2)

    def get_pulse_widths(self):
        """Returns the actual pulse-widths values"""

        actual_pulse_width_1 = self.rpi.get_servo_pulsewidth(14)
        actual_pulse_width_2 = self.rpi.get_servo_pulsewidth(15)

        return (actual_pulse_width_1, actual_pulse_width_2)

    def quiet(self, servos=[14, 15, 18]):
        """Stop sending pulses to the servos, so that they are no longer energised (and so that they
        stop buzzing).
        """
        for servo in servos:
            self.rpi.set_servo_pulsewidth(servo, 0)

    def reset_report(self):

        self.angle_shoulder = self.angle_elbow = None

        # Create sets for recording movement of the plotter.
        self.angle_history_shoulder = set()
        self.angle_history_elbow = set()
        self.pulse_widths_used_1 = set()
        self.pulse_widths_used_2 = set()

    # overriding pen control methods.
    def pen_up(self):
        self.rpi.set_servo_pulsewidth(self.pen_pin, self.pw_up)
        sleep(self.pen_transition_time)

        self.pen_position = "up"

    def pen_down(self):
        self.rpi.set_servo_pulsewidth(self.pen_pin, self.pw_down)
        sleep(self.pen_transition_time)

        self.pen_position = "down"
