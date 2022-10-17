"""PCA9685 based drawing robot class."""

from time import sleep
import busio
from board import SCL, SDA
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from plotter import Plotter

class Plotter(Plotter):
    def __init__(
        self,
        resolution: float = 1,     # default resolution of the plotter in cm

        #  ----------------- geometry of the plotter
        bounds:    tuple = [-10, 5, 10, 15],       # the maximum rectangular drawing area
        inner_arm: float = 8,                      # the lengths of the arms
        outer_arm: float = 8,

        #  ----------------- servo calibration
        angle_offset_servo_shoulder: float = 30,   # offset (in BG's reference model)
                                                   # for the shoulder servo's zero degrees.
                                                   # the arm has been attached after the servo has
                                                   # been initialized to this offset.
                                                   # see https://www.brachiograph.art/_downloads/94e7b4ab642ebc644e516e616c26aaa3/template-grid.pdf
        angle_parked_servo_shoulder: float = -90,  # the arm angle in the parked position
        angle_parked_servo_elbow:    float = 90,
        angle_pen_up:   float = 0,
        angle_pen_down: float = 30,

        #  ----------------- hysteresis # TODO: implement
        hysteresis_correction_1: float = 0,  # hardware error compensation
        hysteresis_correction_2: float = 0,

        #  ----------------- movement speed
        wait:       float = 0.05,  # default wait time between operations
        **kwargs
    ):

        self.initialise_pca9685()

        super().__init__(
            bounds=bounds,
            angle_parked_servo_shoulder=angle_parked_servo_shoulder,
            angle_parked_servo_elbow=angle_parked_servo_elbow,
            angle_offset_servo_shoulder=angle_offset_servo_shoulder,
            hysteresis_correction_1=hysteresis_correction_1,
            hysteresis_correction_2=hysteresis_correction_2,
            angle_pen_up=angle_pen_up,
            angle_pen_down=angle_pen_down,
            wait=wait,
            resolution=resolution,
            inner_arm=inner_arm,
            outer_arm=outer_arm,
            **kwargs
        )

        self.park()
        self.status()

    def initialise_pca9685(self):
        self.i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = 50
        self.servo_shoulder = servo.Servo(self.pca.channels[0])
        self.servo_elbow    = servo.Servo(self.pca.channels[1])
        self.servo_pen      = servo.Servo(self.pca.channels[2])

    def angle_absolute_shoulder(self, angle_motor_shoulder):
        """Convert shoulder servo angles
        from BrachioGraph's reference system (Y axis=0, +/-90)
        to Adafruit's (0-180)
        and take into account configured servo offset."""
        angle_shoulder = self.angle_offset_servo_shoulder - angle_motor_shoulder
        return angle_shoulder

    def set_angle_servo_shoulder(self, angle):
        angle_servo_shoulder_abs = self.angle_absolute_shoulder(angle)
        if self.is_angle_in_range(angle_servo_shoulder_abs):
            self.servo_shoulder.angle = angle_servo_shoulder_abs

    def set_angle_servo_elbow(self, angle):
        if self.is_angle_in_range(angle):
            self.servo_shoulder.angle = angle

    def set_angle_servo_pen(self, angle):
        if self.is_angle_in_range(angle):
            self.servo_pen.angle = angle
