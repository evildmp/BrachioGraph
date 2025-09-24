Geometric calculation
=====================

BrachioGraph is an *arm-writer* - it moves the pen by adjusting the angles of its arms. All its
movements are rotational - it can only move in curves. This has some consequences that make it
challenging to draw with.

Whether it needs to move one arm or both to move the pen from one point to another,
what it draws will not be a straight line. The shortest distance between two points might be
a straight line, but the simplest movement between them is certainly not. Simply moving the
motors to the correct position for the end-point will draw a curved line rather than a straight
one.

Instead, it's necessary to break down any straight line into a series of much shorter lines along
its length - enough to make the line as straight as possible. The movement of servo motors is
rather coarse, which is why all the lines a BrachioGraph produces are wiggly.


.. _mathematics:

The mathematics
---------------

A physical plotter instance is modelled with a ``BrachioGraph`` instance. Given x/y co-ordinates, a plotter
must be able to derive the appropriate motor angles.


Translating co-ordinates to angles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, the arms are both 9cm long and the pen is at ``x=4, y=10``.

.. image:: /images/geometry.png
   :alt: 'BrachioGraph geometry'
   :class: 'main-visual'

The ``xy_to_angles()`` method receives x and y co-ordinates as arguments. The first thing it does is find a line
from the origin (the shoulder motor) to the pen, and its angle from the y-axis::

    hypotenuse = math.sqrt(x ** 2 + y ** 2)
    hypotenuse_angle = math.asin(x/hypotenuse)

Given ``x=4, y=10``, ``hypotenuse`` is 10.77, and its angle from the y-axis (``hypotenuse_angle``) is 21.8 degrees
(0.38 radians).

The hypotenuse line, the inner arm and the outer arm form a second triangle. All their lengths are known, so we can
find the angle between the line of the hypotenuse of the first triangle and the inner arm:

::

    inner_angle = math.acos(
        (hypotenuse ** 2 + self.inner_arm ** 2 - self.outer_arm ** 2) / (2 * hypotenuse * self.inner_arm)
    )

which is 53.25 degrees. The ``hypotenuse_angle`` minus the ``inner_angle`` gives us the angle of the shoulder motor
(from the y-axis)::

    shoulder_motor_angle = hypotenuse_angle - inner_angle

in other words, -31.45 degrees. So now we know what angle to set the shoulder motor to.

And similarly, we can find the angle at the elbow, between the inner and outer arms::

    outer_angle = math.acos(
        (self.inner_arm ** 2 + self.outer_arm ** 2 - hypotenuse ** 2) / (2 * self.inner_arm * self.outer_arm)
    )

The angle of the outer arm relative to the inner arm is 180 degrees (or π radians) minus the ``outer_angle``::

    elbow_motor_angle = math.pi - outer_angle

Finally we convert the angle values to degrees and return them::

    return (math.degrees(shoulder_motor_angle), math.degrees(elbow_motor_angle))


Translating angles to co-ordinates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Obtaining angles from co-ordinates is essentially the reverse process, in ``angles_to_xy()``. This method isn't
actually used in the ``BrachioGraph``, but can be useful when experimenting.
