.. _drive:

Start up the BrachioGraph
=========================

Detach the inner arm
--------------------

Before doing anything else, detach the inner arm from the servos - otherwise you risk having the
machine flail around wildly when the servos are energised.

Create a ``BrachioGraph`` instance
----------------------------------

Power up the Raspberry Pi. Run (assuming that you :ref:`installed the required software in a virtual environment <set-up-venv>`)::

    sudo pigpiod
    source env/bin/activate
    cd BrachioGraph
    python

And then in the Python shell::

    from brachiograph import BrachioGraph

When you :ref:`assembled the BrachioGraph earlier <build-inner-arm>`, you measured, the arm lengths.

..  important::

    The arm lengths are not the lengths of the actual sticks or card, but the distances between the
    key points on them:

    * ``inner_arm``: between the centres of the two servo horns
    * ``outer_arm``: between the spindle of the motor and the pen

Initialise the BrachioGraph with the correct values, for example::

  bg = BrachioGraph(inner_arm=8.2, outer_arm=7.9)

If you managed to make them both exactly 8cm long, you're in luck and instead can simply do::

    bg = BrachioGraph()

because its defaults assume that the arms are both 8cm long.

The system will create a BrachioGraph instance and initialise itself, adjusting the motors so that the pen will be at
a nominal:

* x = ``-inner_arm`` (-8)
* y = ``outer_arm`` (8)

And this will correspond to:

* the upper arm at approximately -90 degrees, 1800µS pulse-width
* the lower arm at approximately 90 degrees to it, 1500µS pulse-width
* the lifting motor in the pen up position, 1700µS pulse width


.. _check-movement:

Initial checks
------------------

We must make sure that the arms move in the direction we expect. Run::

    bg.set_angles(angle_1=-90, angle_2=90)

This shouldn't do anything; the arms should already be at those angles.

Now try changing the values in five-degree increments, e.g.::

    bg.set_angles(angle_1=-85, angle_2=95)

then::

    bg.set_angles(angle_1=-80, angle_2=100)

Increasing the values should move the arms clockwise; decreasing them should move them anti-clockwise. To avoid violent
movement, don't move them more than five or ten degrees at a time.

If the movements are reversed (perhaps because you're using different motors, or have mounted a motor differently),
you can account for this in the BrachioGraph definition. The defaults are::

    servo_1_degree_ms = -10
    servo_2_degree_ms = 10

meaning that a 1 degree positive movement of motor 1 corresponds to a -10mS change in pulse-width, and a 1 degree
positive movement of motor 1 corresponds to a 10mS change in pulse-width. You can reverse either of these if necessary.


Finish building the plotter
---------------------------

Your plotter should look something like the example below. The arms may be a few degrees off the perpendicular, but
don't worry about that now.

.. image:: /images/starting-position.jpg
   :alt: 'Starting position'
   :class: 'main-visual'

Attach the horn to the lifting motor.

.. image:: /images/lifting-mechanism.jpg
   :alt: 'Pen-lifting mechanism'

The default up and down values for the pen are::

    pw_up = 1500
    pw_down = 1100

You need the pen to be just clear of the paper in the *up* position. The lifting movement can cause unwanted movement
of the pen, so you need to minimise that. You can try using different values around 1500 (plus or minus 200 or so)::

    bg.pen.rpi.set_servo_pulsewidth(18, <value>)

to find a good pair of up/down values. Then you can include them in your initialisation of the
BrachioGraph, by supplying ``pw_up`` and ``pw_down``


Take the BrachioGraph for a drive
---------------------------------

::

    bg.drive_xy()

Controls:

* 0: ``exit``
* a: ``decrease x position 1cm`` (A: ``.1cm``)
* s: ``increase x position 1cm`` (S: ``.1cm``)
* k: ``decrease y position 1cm`` (K: ``.1cm``)
* l: ``increase y position 1cm`` (L: ``.1cm``)

Use this to discover the bounds of the area the BrachioGraph can draw. Theoretically, the drawable area looks something
like this:

..  image:: /images/plotter-geometry/brachiograph-default-plotting-area.png
    :alt: 'Plotting area'
    :class: 'main-visual'

If you exceed the bounds of what is mathematically, physically or electronically possible, you'll get an error. In such
cases, it's often easiest to start again with ``bg = BrachioGraph()``.

The default BrachioGraph will draw within the limits of a box that has its bottom-left at -8, 4 and its upper-right at
6, 13 and that fits comfortably inside the area. It's initialised with::

    bounds = [-8, 4, 6, 13]

These are values that work well.

.. _start-plotting:

Test it
-------

Draw a box, using the ``bounds``::

    bg.box()

and a test pattern::

    bg.test_pattern()

If the lines are reasonably straight and the box is reasonably square, try plotting a file::

    bg.plot_file("test-patterns/accuracy.json")

However, almost certainly, the BrachioGraph will need some calibration to improve the output.


Basic calibration
-----------------

The simplest calibration is to ensure that at somewhere near the centre of its movement, the outer arm is at exactly
90˚ to the inner arm. The defaults assumed for the two motors (servo 1 is the shoulder, servo 2 is the elbow) are::

    servo_1_centre = 1500
    servo_2_centre = 1500

Use ``bg.drive()`` to discover what pulse-width actually corresponds to 90˚ (ignore the shoulder motor for now).

Controls:

* 0: ``exit``
* a: ``decrease shoulder motor pulse-width 10µS`` (A: 1µS)
* s: ``increase shoulder motor pulse-width 10µS`` (S: 1µS)
* k: ``decrease elbow motor pulse-width 10µS`` (K: 1µS)
* l: ``increase elbow motor pulse-width 10µS`` (L: 1µS)

Use this value in the BrachioGraph definition, e.g. ``bg = BrachioGraph(servo_2_centre=1430)``; you should now get
at least slightly better results (i.e. slightly straighter lines).

See :ref:`calibrate` for more sophisticated calibration.


Save your BrachioGraph definition
---------------------------------

The file ``bg.py`` is a good place to save your defined ``BrachioGraph`` instances  for future use. It
already contains examples for units built during the development process.
