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

Now reattach the inner arm, but instead of placing it at -90˚ as before, place it at about -60˚ degrees - see
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

This is where the :download:`template grid </supporting-files/template-grid.pdf>` comes in handy. If you haven't already
done so, affix the template to the plotter base, so that the shoulder motor's spindle is at 0, 0 (see :ref:`assembly` for
reference).

To help you collect the pulse-width values you need, use the ``capture_pws()`` method::

    bg.capture_pws()

Use the controls indicated to move the arms:

..  list-table::
    :stub-columns: 1

    * -
      - -10 µs
      - -1 µs
      - \+ 10 µs
      - \+ 1 µs
    * -
      -
      -
      -
      -
    * - Shoulder
      - ``a``
      - ``A``
      - ``s``
      - ``S``
    * - Elbow
      - ``k``
      - ``K``
      - ``l``
      - ``L``
    * - Pen
      - ``z``
      -
      - ``x``
      -

..  list-table::
    :stub-columns: 1

    * - Capture pulse-width value
      - ``c``
    * - Show captured values
      - ``v``
    * - Exit
      - ``0``


First, move the *outer* arm to about 150˚. This is to keep it out of the way of the edge of the grid while working on
the inner arm.

Now from somewhere left of -135˚, start moving the *inner* arm clockwise. Record the pulse-width for the main
angles shown on the template - press ``c`` when exactly over it, and enter the angle.

Each angle needs to be captured in both directions, clockwise and anti-clockwise. Press ``v`` to see the data you
are collecting.

..  note::

    It's quite hard to judge these angle accurately, because of the distance between the arm and the printed
    protractor. A good way is to sight along the printed angle, from just above the board level.

Once you have collected all the angles in both directions for the shoulder motor, do the same for the elbow motor.

Move the inner arm to exactly 0˚ so that the outer arm is in the right place over the template (the elbow
motor spindle should be at exactly 0, 8), then move the outer arm over the range of angles. It's much easier to judge
angles accurately with the outer arm, because you can see where the pen actually touches the drawing surface.

Check for any missing values (use ``v``), and when done, ``0``. The output might be something like::

    servo_1_angle_pws_bidi =
    {30: {'cw': 769, 'acw': 759},
     15: {'cw': 919, 'acw': 919},
     0: {'cw': 1059, 'acw': 1069},
     -15: {'cw': 1209, 'acw': 1219},
     -30: {'cw': 1349, 'acw': 1339},
     -45: {'cw': 1459, 'acw': 1459},
     -60: {'cw': 1579, 'acw': 1589},
     -75: {'cw': 1719, 'acw': 1709},
     -105: {'cw': 1999, 'acw': 1979},
     -120: {'cw': 2119, 'acw': 2129},
     -135: {'cw': 2289, 'acw': 2289},
     -90: {'acw': 1859, 'cw': 1859}}
    servo_2_angle_pws_bidi =
    {15: {'cw': 656, 'acw': 639},
     30: {'cw': 788, 'acw': 778},
     45: {'cw': 928, 'acw': 908},
     60: {'cw': 1058, 'acw': 1048},
     75: {'cw': 1218, 'acw': 1208},
     90: {'cw': 1368, 'acw': 1358},
     105: {'cw': 1518, 'acw': 1508},
     120: {'cw': 1668, 'acw': 1668},
     135: {'cw': 1818, 'acw': 1818},
     150: {'cw': 1968, 'acw': 1968}}


Now, you can copy and paste (you'll need to do a little reformatting) the two dictionaries to the BrachioGraph definition
that you have been working with in ``custom.py``:

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

