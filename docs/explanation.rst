Explanation
===========

The hardware
------------

The Raspberry Pi
~~~~~~~~~~~~~~~~

A Raspberry Pi Zero is perfectly adequate to control and power the servos. The Pi can be connected to a host by USB,
using the OTG mode (RNDIS), and powered that way, along with all three servos - but this arrangement is not wholly
reliable and you may find that the machine occasionally reboots, because of lack of power. A separate power supply for
the Pi is much more reliable.


The servo motors
~~~~~~~~~~~~~~~~

`SG90 motors <http://www.towerpro.com.tw/product/sg90-analog/>`_ are ideal. They are extremely cheap (though beware of
even cheaper counterfeits) and perfectly adequate.

More powerful and more accurate motors will give you better results.

SG90 motors are **analog**, and use a small circuit to convert the pulse-widths into motor angles. **Digital** servo
motors also exist; they tend to be faster and more powerful. However, *small digital motors do not work well*. They are
twitchy and try to correct for errors much faster than analog motors. This means that in a mechanism such as this, they
quickly start oscillating wildly, as each movement overshoots and corrects (this is made worse by having two motors
affecting each other).


The cardboard
~~~~~~~~~~~~~

The card for the arms (and the base) needs to be stiff in both directions. Picture-mounting board is ideal. A
picture-framing shop will almost certainly give you free off-cuts.

The mathematics
---------------

The BrachioGraph object contains two trignometric methods, to translate x/y co-ordinates of the pen into angles of the
motors and vice-versa. Using the example illustrated below, the arms are both 9cm long and the pen is at ``x=4, y=10``.

Translating co-ordinates to angles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /images/geometry.png
   :alt: 'BrachioGraph geometry'
   :class: 'main-visual'

The ``xy_to_angles()`` method receives x and y co-ordinates as arguments. First we find a line from the origin (the
shoulder motor) to the pen, and its angle from the y-axis::

    hypotenuse = math.sqrt(x ** 2 + y ** 2)
    hypotenuse_angle = math.asin(x/hypotenuse)

Given ``x=4, y=10``, ``hypotenuse`` is 10.77, and its angle from the y-axis (``hypotenuse_angle``) is 21.8 degrees
(0.38 radians).

The hypotenuse line, the inner arm and the outer arm form a second triangle. All their lengths are known, so we can
find the angle between the line of the hypotenuse of the first triangle and the inner arm:

::

    inner_angle = math.acos(
        (hypotenuse ** 2 + self.INNER_ARM ** 2 - self.OUTER_ARM ** 2) / (2 * hypotenuse * self.INNER_ARM)
    )

which is 53.25 degrees. The ``hypotenuse_angle`` minus the ``inner_angle`` gives us the angle of the shoulder motor
(from the y-axis)::

    shoulder_motor_angle = hypotenuse_angle - inner_angle

in other words, -31.45 degrees. So now we know what angle to set the shoulder motor to.

And similarly, we can find the angle at the elbow, between the inner and outer arms::

    outer_angle = math.acos(
        (self.INNER_ARM ** 2 + self.OUTER_ARM ** 2 - hypotenuse ** 2) / (2 * self.INNER_ARM * self.OUTER_ARM)
    )

The angle of the outer arm relative to the inner arm is 180 degrees (or π radians) minus the ``outer_angle``::

    elbow_motor_angle = math.pi - outer_angle

Finally we convert the angle values to degrees and return them::

    return (math.degrees(shoulder_motor_angle), math.degrees(elbow_motor_angle))


Translating angles to co-ordinates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Obtaining angles from co-odinates is essentially the reverse process, in ``angles_to_xy()``. This method isn't
actually used in the ``BrachioGraph``, but can be useful when experimenting.
