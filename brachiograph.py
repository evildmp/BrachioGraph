# coding=utf-8
class BrachioGraph():
    """A shoulder-and-elbow drawing robot class."""

    def __init__(
        self,
        mode = "pigpio",           # machine mode: [pigpio|PCA9685|virtual]
        turtle:  bool = False,     # create a turtle graphics plotter
        turtle_coarseness = None,  # a factor in degrees representing servo resolution

        resolution: float = 1,     # default resolution of the plotter in cm
        #  ----------------- geometry of the plotter
        bounds:    tuple = [-8, 4, 6, 13],  # the maximum rectangular drawing area
        inner_arm: float = 8,               # the lengths of the arms
        outer_arm: float = 8,

        #  ----------------- servo calibration
        angle_offset_servo_shoulder: float = 30,   # offset (in BG's reference model)
                                                   # for the servo's zero degrees.
        angle_parked_servo_shoulder: float = -90,  # the arm angle in the parked position
        angle_parked_servo_elbow:    float = 90,
        angle_pen_up:                float = 0,
        angle_pen_down:              float = 30,

        #  ----------------- hysteresis # TODO: implement for PCA9685
        hysteresis_correction_1: int = 0,  # hardware error compensation
        hysteresis_correction_2: int = 0,

        #  ----------------- movement speed
        wait:       float = 0.05,  # default wait time between operations
        **kwargs
    ):
        if   mode == "PCA9685":
            from plotter_pca9685 import Plotter
        elif mode == "pigpio":
            from plotter_pigpio  import Plotter
        elif mode == "virtual":
            from plotter_virtual import Plotter
        else:
            print("FATAL: mode {mode} not recognized.")
            exit(1)

        self.plotter = Plotter(
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
            turtle=turtle,
            turtle_coarseness=turtle_coarseness,
            inner_arm=inner_arm,
            outer_arm=outer_arm,
            **kwargs
        )

if __name__=="__main__":
    bg = BrachioGraph(mode="virtual",turtle=True)
