.. _drive:

Start up the BrachioGraph
=========================

Detach the inner arm
--------------------

Before doing anything else, **detach the inner arm from the servos** - otherwise you risk having the
machine flail around wildly when the servos are energised.

Create a ``BrachioGraph`` instance
----------------------------------

Power up the Raspberry Pi. Run::

    sudo pigpiod
    source env/bin/activate
    cd BrachioGraph
    python

And then in the Python shell, import the ``BrachioGraph`` class from the ``brachiograph`` module::

    from brachiograph import BrachioGraph

Create a BrachioGraph instance from the class::

  bg = BrachioGraph()

This initialises a BrachioGraph instance ``bg`` that you can interact with.

You'll hear the motors buzz as it sets them to their default, parked, position.


Reattach the inner arm
-----------------------

Now reattach the inner arm, so that the machine now looks more or less like this.

.. image:: /images/starting-position.jpg
   :alt:

The arms should be as close to perpendicular as possible, but don't worry if they are not perfectly
at 90˚ to the drawing area or to each other - we will adjust that later.


Add the pen-lifting horn
------------------------

Attach the horn to the lifting motor.

.. image:: /images/lifting-mechanism.jpg
   :alt:


Do a status check
-----------------

Run::

  bg.status()

The BrachioGraph will report its status::

  ------------------------------------------
                        | Servo 1 | Servo 2
                        | Shoulder| Elbow
  ----------------------|---------|---------
            pulse-width |    1800 |    1500
                  angle |     -90 |      90
  hysteresis correction |     0.0 |     0.0
  ------------------------------------------

  ------------------------------------------
  pen: up
  ------------------------------------------
  bottom left: (-8, 4) top right: (6, 13)
  ------------------------------------------


.. _tutorial-move-arms:

Move the arms
-------------

The ``BrachioGraph.set_pulse_widths()`` method is a manual way of setting the pulse-widths that
determine the position of a servo. Try this::

  bg.set_pulse_widths(1800, 1500)

Nothing should happen, because those are already the pulse-widths it's applying. But try
incrementing the first servo pulse-width by 100 (milliseconds) - make sure you get the numbers
right, because a wrong value can send the arms flying::

  bg.set_pulse_widths(1900, 1500)

This should move the inner arm a few degrees anti-clockwise. Try some different values for the two
servos, changing them by no more than 100 at a time, until the arms seem to be perpendicular to
each other and the drawing area.

Make a note of those two values; we'll use them in the next step.


.. _tutorial-custom-brachiograph:

Initialise a custom BrachioGraph
--------------------------------

Let's say the two values you noted in the previous step were 1870 for the shoulder motor and 1450 for the elbow motor.
In that case, re-initialise the BrachioGraph with the values (but use whatever values you discovered)::

  bg=BrachioGraph(servo_1_parked_pw=1870, servo_2_parked_pw=1450)


Adjust the pen lifting motor
----------------------------

The pen motor should be in the *up* position. Try lowering and lifting it::

  bg.pen.down()
  bg.pen.up()

Adjust the horn on the motor and the position of the pen in the clothes peg so that in the *down*
position the pen touches the paper, and in the *up* position it doesn't.


Start drawing
-------------

Now you should be able to draw a box::

  bg.box(bounds=[-2, 7, 2, 11])

This means: draw a rectangle defined by the co-ordinates -2, 7 at one corner and 2, 11 at the opposite corner (the shoulder motor is always at 0,0):

.. image:: /images/box.png
   :alt:

The BrachioGraph will draw your square. It will be a wobbly, imperfect square, but it should be a
recognisable square, about 4cm wide and tall.

Try increasing the dimensions oof the box progressively, for example::

  bg.box(bounds=[-3, 6, 3, 12])

The next job is to improve the accuracy and precision of the plotter.
