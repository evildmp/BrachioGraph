PantoGraph - a pentagonal Python-powered plotter
================================================

PantoGraph is a simplePython application to drive a home-built plotter.

.. image:: /images/plotter.jpg
   :alt: 'The PantoGraph plotter'

Note: **this documentation is in progress and incomplete**.

Get started
-----------

Build the plotter
~~~~~~~~~~~~~~~~~

Make sure the length between the holes in each of the four arms is identical. The easiest way to
do this is to drill them all at once, and insert the ballpoint pen tube through the first set of
holes in all the arms, before drilling the second set, again all at once.

It's recommended to make the length between holes no more than 10cm, unless you have more powerful
servos at your disposal.

Double arms to hold the pen will help keep it straight.

Cut sections of tube to use as hinges.

Fasten the arms **loosely** to the servos - don't tighten them yet.

Make sure your pantograph moves freely.


Wire up up the servos
~~~~~~~~~~~~~~~~~~~~~

Wire the plotter up to a Raspberry Pi or MicroPython board with sufficient GPIO pins.

The plotter defaults to using the following GPIO pins for the arms:

* 14: left arm
* 15: right arm
* 18: pen up/down


Install requirements
~~~~~~~~~~~~~~~~~~~~

Raspberry Pi version
^^^^^^^^^^^^^^^^^^^^

Use pip to install:

* ``pigpio``
* ``tqdm``

Download the PantoGraph application, for example with ``git@github.com:evildmp/PantoGraph.git`` or
``https://github.com/evildmp/PantoGraph.git``.


Test it
~~~~~~~

Launch a Python 3 shell from the ``PantoGraph`` directory.

Create a ``PantoGraph`` instance::

    from pg import *
    pg = PantoGraph()

The servos and arms will move immediately (this is why it's important to have fastened the arms
loosely). Now issue a command::

    pg.command_servo_angles(0, 0)

This sets both arms to 0 degrees, i.e. straight ahead out over the paper. Adjust the arms and
tighten them. Continue, each time checking that the behaviour of the machine seems correct::

    pg.command_servo_angles(-15, 0)  # set arm 1 to -15 degrees, arm 2 to 0 degrees
    pg.command_servo_angles(0, 0)
    pg.command_servo_angles(0, 15)   # set arm 1 to 0 degrees, arm 2 to 15 degrees
    pg.command_servo_angles(-15, 15)

As you gain confidence, try larger angles::

    pg.command_servo_angles(-30, 30)
    pg.command_servo_angles(-45, -45)
    pg.command_servo_angles(-60, -30)
    pg.command_servo_angles(-60, 15)
    pg.command_servo_angles(-60, 0)
    pg.command_servo_angles(-60, -15)
    pg.command_servo_angles(-60, -30)

... and so on.

..  important::

    Generally, you should avoid angles greater than 90 degrees between the two arms.

Now try a test pattern::

    pg.test_pattern(repeat=5)

Or commanding the arm to move to particular x/y positions::

    pg.xy(x, y)

And drawing a line to a new point::

    pg.draw(x, y)


How to ...
----------

Render a photograph for plotting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use `my fork of the linedraw application <https://github.com/evildmp/linedraw>`_::

    import linedraw

    lines=linedraw.sketch("image.jpg")

    with open("image.json", "w") as myfile:
        json.dump(lines, myfile)


    pg.plot_file("image.json")

Note that linedraw defaults to a maximum image dimension of 1024; the ``PantoGraph.plot_lines()``
method assumes this and divides dimensions by 102.4 to fit a 10cm box.

Reference
---------

PantoGraph classes and methods


Background
----------

The mathematics.