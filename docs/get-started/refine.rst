Refine
======

In the previous section, you :ref:`initialised a custom BrachioGraph <tutorial-custom-brachiograph>`.

Now we're going to save the definition in order to continue improving it.


Create a file to hold a custom defintion
------------------------------------------------

In the same directory as ``brachiograph.py`` create a new file called ``custom.py``.

In ``custom.py``, import the ``BrachioGraph`` class, and then create an instance with the pulse-width values you used
previously. For example::

  from brachiograph import BrachioGraph

  bg = BrachioGraph(
      servo_1_parked_pw=1870,
      servo_2_parked_pw=1450,
  )

Save the file. From now on, you will initialise BrachioGraph in the Python shell using this definition - do it now::

  from custom import bg


Counteract hysteresis
---------------------

The next step is to improve the behaviour of the machine. What we are going to do next is attempt to counteract
hysteresis.

To do this we need to find how much the arms tend to lag in each direction. First, lower the pen, because we need to
account for its drag::

  bg.pen.down()

On a scrap of paper, prepare a little table:

.. list-table:: Pulse width values for 90˚
   :header-rows: 1
   :stub-columns: 1

   * - Servo
     - ascending
     - descending
     - mean
     - adjustment
   * - Shoulder
     -
     -
     -
     -
   * - Elbow
     -
     -
     -
     -


Calculate hysteresis for the shoulder motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try::

  for shoulder in range(850, 1100): bg.set_pulse_widths(shoulder, 1000); sleep(0.02)
  #                          ^^^^ adjust this value in your experiments

This will rotate the inner arm to approximately the 0˚ - straight ahead - position. The ``shoulder`` value represents
the shoulder motor's pulse-width. We wait 0.02 seconds between each step, to slow down the progress.

Your job now is to repeat this multiple times, changing the ``1100`` above until you find a final value that stops the
arm as close to the right angle as possible.

Write down the value in the table, in the shoulder motor (ascending) cell.

Now we'll approach the same angle from the other direction::

   for shoulder in range(1300, 1070, -1): bg.set_pulse_widths(shoulder, 1500); sleep(0.02)
   #                           ^^^^ use the value you just wrote down as a starting value

Keep adjusting the target value, until once again you find a final value that stops the arm as close to the right angle
as possible.

Write this one down too, in the shoulder motor (descending) cell. You'll probably find that the values are about 30mS
apart. What this tells you is that friction, drag and other mechanical imperfections in the system mean that in each
direction the actual position is behind the target position, and that to get to the desire position, it will be
necessary to adjust the command to the servo by about 15mS.

Add the mean of the two values you recorded, and the adjustment value (i.e. half of the difference between them) to the
table.

Calculate hysteresis for the elbow motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we need to do the same with the elbow motor.

Start with::


  for elbow in range(1300, 1500): bg.set_pulse_widths(1055, elbow); sleep(0.02)
  #    use the mean value from the previous step here ^^^^

and adjust the ``1500`` until you find a value that stops the pen on a line at 90˚ from the inner arm. Then do the same
in the other direction::

  for elbow in range(1600, 1445, -1): bg.set_pulse_widths(1055, elbow); sleep(0.02)

and record the values in the table, which might look something like this:

.. list-table:: Pulse width values for 90˚
   :widths: 20 20 20 20 20
   :header-rows: 1
   :stub-columns: 1

   * - Servo
     - ascending
     - descending
     - mean
     - adjustment
   * - Shoulder
     - 1070
     - 1040
     - 1055
     - 15
   * - Elbow
     - 1475
     - 1445
     - 1460
     - 15




-------------

we'll use the ``set_pulse_widths()`` we used previously. First, use::

  bg.set_pulse_widths(1500, 1500)

to place both motors at approximately the centre of their travel.

Now, we'll draw the shoulder mot

Draw a test pattern
-------------------

::

    bg.test_pattern()







and a test file:

  bg.plot_file("test-patterns/accuracy.json")







The default up and down values for the pen are::

    pw_up = 1500
    pw_down = 1100

You need the pen to be just clear of the paper in the *up* position. The lifting movement can cause unwanted movement
of the pen, so you need to minimise that. You can try using different values around 1500 (plus or minus 200 or so)::

    bg.pen.rpi.set_servo_pulsewidth(18, <value>)





, adjusting the motors so that the pen will be at
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

    servo_1_parked_pw = 1500
    servo_2_parked_pw = 1500

Use ``bg.drive()`` to discover what pulse-width actually corresponds to 90˚ (ignore the shoulder motor for now).

Controls:

* 0: ``exit``
* a: ``decrease shoulder motor pulse-width 10µS`` (A: 1µS)
* s: ``increase shoulder motor pulse-width 10µS`` (S: 1µS)
* k: ``decrease elbow motor pulse-width 10µS`` (K: 1µS)
* l: ``increase elbow motor pulse-width 10µS`` (L: 1µS)

Use this value in the BrachioGraph definition, e.g. ``bg = BrachioGraph(servo_2_parked_pw=1430)``; you should now get
at least slightly better results (i.e. slightly straighter lines).

See :ref:`calibrate` for more sophisticated calibration.


Save your BrachioGraph definition
---------------------------------

The file ``bg.py`` is a good place to save your defined ``BrachioGraph`` instances  for future use. It
already contains examples for units built during the development process.
