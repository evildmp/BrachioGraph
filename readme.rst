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


Calibrate the PantoGraph more accurately
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First of all, bear in mind that you're doing this with hobby servos, not precision devices, not to
mention a mechanism made of card and ballpoint pens. There is enough slack and play in this system
to swamp any delicate adjustments you make completely.

Still - we should do the best we can. So:

Remove the arms from the servos. Start up a PantoGraph::

    from pg import *
    pg = PantoGraph()

Start with motor 1.

Assuming it's on pin 14, run::

    pg.set_pw(pin=14, pw=1350)

1350 µS is the nominal pulse width corresponding to the nominal central or neutral position of
most servo motors.

Now attach attach a long horn to the servo, so that you can more easily judge its angles. If 0
degrees is straight ahead, pointing out over the paper, attach the horn at whatever seems closest
to -30 degrees, i.e. pointing outwards. (We want it pointing outwards in the centre of its range of
movement, as most of the time in practice the arm will need to point outwards.q)

Now, change the pulse width, until the horn points straight ahead at 0 degrees. This is your
*centre value*; make a note of it.

Do the same for -90 degrees (straight out).

Now you know what value corresponds to 0 degrees for that arm, what value corresponds to 90
degrees, and if you divide the difference between them by 90 you'll know what change in pulse width
corresponds to a 1 degree change:

    (*centre value* - *straight out value*) / 90

This is the *multiplier* value for that arm.

Now repeat the process for the second arm.

It helps a lot to judge the angles if you actually attach an arm to the horn, once you're confident
that you're not going to be making them smash into each other.

Suppose your values were as follows:

* Servo 1 0 degrees: 1060
* Servo 1 -90 degrees: 2020
* Servo 2 0 degrees: 1775
* Servo 1 90 degrees: 860

Then you would instantiate your PantoGraph obect thus::

    pg=PantoGraph(
        centre_1=1060,
        multiplier_1=(2020-1060)/90,
        centre_2=1775,
        multiplier_2=(1775-860)/90
    )

And now you'll find that when you issue a command such as::

    pg.command_servo_angles(-45, 45)

both arms will point out at a perfect 45 degrees.

What? They don't?! Welcome to the world of hobby servos...
pg.

Reference
---------

PantoGraph classes and methods


Background
----------

The mathematics.