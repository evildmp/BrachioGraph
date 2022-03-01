.. _drive:

Start up the BrachioGraph
=========================

..  warning::

    Before doing anything else, **detach the inner arm from the servos** - otherwise you risk having the machine flail
    around wildly when the servos are energised.


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


Attach and test the inner arm
-----------------------------

Now reattach the inner arm, so that the machine now looks more or less like this.

.. image:: /images/inner-arm-attached.jpg
   :alt:

It should be as close to -90˚ (as marked on the grid) as possible, but don't worry if it's not, we'll adjust that later.

Run a quick test::

  bg.set_angles(0, 90)

The first value is the angle of the inner arm, the second the angle of the outer arm. The inner arm should swing
clockwise to about 0˚. Send it back to its starting point with::

  bg.park()


Attach and test the outer arm
-----------------------------

Now reattach the outer arm. It should be in a position as close as possible to 90˚ relative to the inner arm:

.. image:: /images/outer-arm-attached.jpg
   :alt:

Test it::

  bg.set_angles(-90, 120)

The arm should swing clockwise from its 90˚ position by about 30˚. Park the arms again with ``bg.park()``.


Adjust the pen lifting mechanism
--------------------------------

Try lowering and lifting the pen motor::

  bg.pen.down()
  bg.pen.up()

Adjust the horn on the motor and the position of the pen in the clothes peg so that in the *down*
position the pen firmly touches the paper, and in the *up* position it clears it by a millimetre or two.


Do a status check
-----------------

Run::

  bg.status()

The BrachioGraph will report its status::

  ------------------------------------------
                        | Servo 1 | Servo 2
                        | Shoulder| Elbow
  ----------------------|---------|---------
            pulse-width |    1500 |    1500
                  angle |     -90 |      90
  hysteresis correction |     0.0 |     0.0
  ------------------------------------------

  ------------------------------------------
  pen: up
  ------------------------------------------
  bottom left: (-8, 4) top right: (6, 13)
  ------------------------------------------
