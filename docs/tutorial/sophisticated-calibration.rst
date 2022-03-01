.. _tutorial-sophisticated-calibration:

Apply more sophisticated calibration
====================================

Although you applied hysteresis correction and angle calculation adjustments in the previous section, they are still
based on a naïve assumption that probably isn't true: that the motors exhibit *linear* behaviour. In fact, over some
parts of their travel they will move further per millisecond difference in pulse-width than over others.

The only way to discover the actual behaviour is empirically.


Remount the inner arm
---------------------

Remove the inner arm, and initialise a default BrachioGraph instance::

    from brachiograph import BrachioGraph
    bg = BrachioGraph()

Now reattach the inner arm, but instead of placing it at -90˚ as before, place it at -60˚ degrees - see
:ref:`rotating-drawing-area` for a fuller explanation why, but in short, it puts the arm in a position where it can
operate closer to the centre of the motor's movement, where it's more accurate and consistent.

The outer arm should still be at 90˚ to the inner arm.


Use screws, if you like
-----------------------

You can run the arms without screwing them into place; friction is quite enough. But for better results, make a hole in
the arms so that you can screw them onto their motors more firmly. This reduces flex.


.. _polyfit:

Conduct a sweep
---------------

What we are going to do now is find out the actual pulse-widths that correspond to a number of angles. We'll do it in
both directions, to get an average for each angle and take account of hysteresis, and then we will use numpy to find a
formula that gives us :ref:`a curve that corresponds to these points <explanation-non-linearity>`, and the ones in
between them.

This is where the :download:`template grid </supporting-files/template-grid.pdf>` comes in handy.


Create a table
~~~~~~~~~~~~~~

Prepare another table on some paper:

..  list-table::
    :widths: 45 5 5 5 5 5 5 5 5 5 5 5

    * - **shoulder angle**
      - -135˚
      - **-120˚**
      - -105˚
      - **-90˚**
      - -75˚
      - **-60˚**
      - -45˚
      - **-30˚**
      - -15˚
      - **0˚**
      - 15˚
    * - clockwise
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
    * - anti-clockwise
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
    * - **elbow angle**
      - 15˚
      - **30˚**
      - 45˚
      - **60˚**
      - 75˚
      - **90˚**
      - 105˚
      - **120˚**
      - 135˚
      - **150˚**
      - 165˚
    * - clockwise
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
    * - anti-clockwise
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -
      -


Lower the pen
~~~~~~~~~~~~~

Lower the pen, because we need to account for its drag::

  bg.pen.down()


Drive the plotter
~~~~~~~~~~~~~~~~~

Now, use the ``drive()`` method to control the pulse-widths interactively from the keyboard::

    bg.drive()

The controls are:

..  list-table::
    :stub-columns: 1

    * -
      - Exit
      - -10 µs
      - -1 µs
      - \+ 10 µs
      - \+ 1 µs
    * -
      - ``0``
      -
      -
      -
      -
    * - Shoulder
      -
      - ``a``
      - ``A``
      - ``s``
      - ``S``
    * - Elbow
      -
      - ``k``
      - ``K``
      - ``l``
      - ``L``

First, move the *outer* arm to about 150˚. This is to keep it out of the way of the edge of the grid while working on
the inner arm.

Now from somewhere left of -135˚, start moving the *inner* arm clockwise. Record the pulse-width for the angles listed
in the table. If you overshoot an angle, go back and approach it again, always from the same side.

Then, do the same for the same angles, but working anti-clockwise.

You don't need to do all the angles listed in the table - just do the ones shown in bold; if you're a perfectionist,
you can do more of them.

..  note::

    It's quite hard to judge these angle accurately, because of the distance between the arm and the printed
    protractor. A good way is to sight along the printed angle, from just above the board level.

Then add your own vales to a Python dictionary, which might look something like this::

    servo_1_angle_pws_bidi = {
        -135: {'cw': 2305, 'acw': 2284},
        -120: {'cw': 2131, 'acw': 2114},
        -90:  {'cw': 1841, 'acw': 1821},
        -60:  {'cw': 1576, 'acw': 1569},
        -30:  {'cw': 1315, 'acw': 1309},
        0:    {'cw': 1061, 'acw': 1039},
        30:   {'cw':  765, 'acw':  754},
    },

(``cw`` = clockwise, ``acw`` = anti-clockwise; ``bidi`` in the dictionary name just stands for "bidirectional".)

And then place the inner arm at exactly 0˚ so that the outer arm is in the right place over the template (the elbow
motor spindle should be at exactly 0, 8), and do the same for ``servo_2_angle_pws_bidi``. It's much easier to judge
angles accurately with the outer arm, because you can see where the pen actually touches the drawing surface.

Your dictionary of values might be something like::

    servo_2_angle_pws_bidi = {
        30:  {'cw':  899, 'acw': 873},
        60:  {'cw': 1169, 'acw': 1153},
        75:  {'cw': 1289, 'acw': 1273},
        90:  {'cw': 1411, 'acw': 1403},
        105: {'cw': 1541, 'acw': 1529},
        120: {'cw': 1675, 'acw': 1663},
        150: {'cw': 1975, 'acw': 1963},
    }

Finally, add the two dictionaries to the BrachioGraph definition:

..  code-block::
    :emphasize-lines: 10-15

    from brachiograph import BrachioGraph

    bg = BrachioGraph(
        # servo_1_parked_pw=1570,
        # servo_2_parked_pw=1450,
        # hysteresis_correction_1=10,
        # hysteresis_correction_2=10,
        # servo_1_degree_ms=-9.8,
        # servo_2_degree_ms=10.1,
        servo_1_angle_pws_bidi = {
            # add all the values here
        },
        servo_2_angle_pws_bidi = {
            # add all the values here
        },
        )

Note that the previous parameters are no longer required and can be removed or commented out - or even left alone;
they'll simply be ignored now.

This definition should do a pretty good job of ironing out some of the slack and imprecision inherent in the system,
and even make up somewhat for the low quality of the motors. It can't work miracles though. The output will always be
lo-fi and shaky. But that's how it's meant to be.
