Improve the output
==================

In the previous section, you :ref:`initialised a custom BrachioGraph <tutorial-custom-brachiograph>`.

Now we're going to save the definition in order to continue improving it.


Create a file to hold a custom definition
------------------------------------------------

In the same directory as ``brachiograph.py`` create a new file called ``custom.py``.

In ``custom.py``, import the ``BrachioGraph`` class, and then create an instance with the pulse-width values you used
previously. For example::

    from brachiograph import BrachioGraph

    bg = BrachioGraph(
        servo_1_parked_pw=1570,
        servo_2_parked_pw=1450,
    )

Save the file. From now on, you will initialise BrachioGraph in the Python shell using this definition - do it now::

    from custom import bg


.. _hysteresiscompensation:

Counteract hysteresis
---------------------

The next step is to improve the behaviour of the machine. The motors are not powerful, the arms and the plastic gears
and components tend to flex under stress, and there's slack in the system too. As a result, when you command the arms
to a certain position, they will be a degree or so short of the target. And when you attempt to reach the same angle
from the other direction, the same thing will happen, except that the error's now on the other side of the correct
angle.

This behaviour is called :ref:`hysteresis <about-hysteresis>`, and we can attempt to counteract it. We'll do this by
accounting for it, and commanding the motors to *overshoot* their targets by an equivalent distance. Add hysteresis
correction to the BrachioGraph definition in ``custom.py``:

..  code-block::
    :emphasize-lines: 6-7

    from brachiograph import BrachioGraph

    bg = BrachioGraph(
        servo_1_parked_pw=1570,
        servo_2_parked_pw=1450,
        hysteresis_correction_1=10,
        hysteresis_correction_2=10,
        )

Exit the Python shell, start it again, and import your custom defined BrachioGraph once more::

    from custom import bg

Try the test pattern again, in both directions, by using the ``both`` option::


    bg.test_pattern(both=True)

Now you should get better results. Try hysteresis correction values between 7 and 20, to see what works best. Remember
to exit the Python shell and import the definition into a new one each time you change it.

.. _pulse-width-degrees:

Adjust the angle calculations
---------------------------------

The default definition assumes that a 10 µs difference in pulse-width will result in a 1 degree difference in the
motor's position. In practice, you'll likely find that it's not quite 10 µs. This will introduce distortion into the
drawings. Assuming that when you do ``bg.park()``, the inner arm is exactly at -90˚, try this::

    bg.set_angles(angle_1=0)

Is the inner arm now exactly at 0˚? If not, try different values for ``angle_1`` until it's as close as possible.
Find out the actual pulse-width value, and subtract it from the -90˚ pulse-width value. That's the difference required
to move 90º. If you divide it by 90, you'll get a value corresponding to 1 degree of movement.

Do a similar check with the outer arm. Add the values you discovered to the definition in ``custom.py``, for example:

..  code-block::
    :emphasize-lines: 8-9

    from brachiograph import BrachioGraph

    bg = BrachioGraph(
        servo_1_parked_pw=1570,
        servo_2_parked_pw=1450,
        hysteresis_correction_1=10,
        hysteresis_correction_2=10,
        servo_1_degree_ms=-9.8,
        servo_2_degree_ms=10.1,
        )

**Notice that the value for servo 1 is negative.** (They're different because one of the servos is mounted upside-down.
If you get the sign wrong, the arm will move in the opposite direction.)

------------

Between them, the hysteresis and angle calculation adjustments should improve the output substantially. At this point,
:ref:`you can try converting some of your own images to lines and JSON values <use-linedraw>` using the ``linedraw``
module.

For even better results, you should go on to the next section, for more sophisticated plotter calibration.
