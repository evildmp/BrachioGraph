.. _calibrate:

Improve the plotter calibration
-------------------------------

Each servo motor is different, so the BrachioGraph can be calibrated exactly for your servos.

For each servo, you need to obtain the pulse-widths corresponding to a range of angles.

If you are using `SG90 motors <http://www.towerpro.com.tw/product/sg90-analog/>`_ or similar:

* they have almost 180˚ of rotation, though they are specified for 120˚ and that's the better value to assume
* they operate on pulse-widths from about 500µS to about 2600µS, though the official values are 1000µS to 2000µS and those are better values to use
* the centre of their travel is around 1500µS
* one degree of travel corresponds a difference of about 10µS

This is what the default ``angles_to_pw_1`` and ``angles_to_pw_2`` methods assume when the BrachioGraph is initialised.

However, the correspondence between pulse-widths and angles is not actually linear, and 1500µS in practice will be
unlikely to coincide with the arms' positions at the optimal cebtre of their sweep range. So, you can supply some
values to improve upon these assumptions.


Find the centre angle pulse-widths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the BrachioGraph is initialised with::

    servo_1_centre=1500  # shoulder motor centre pulse-width
    servo_2_centre=1500  # elbow motor centre pulse-width

Probably, at the nominal "zero" angles (-90 and 90 degrees respectively) the arms will probably not be quite at the
those angles. You can use ``bg.drive()`` to discover what pulse-widths correspond to the centre positions.

Controls:

* 0: ``exit``
* a: ``increase shoulder motor pulse-width 10µS``
* s: ``decrease shoulder motor pulse-width 10µS``
* A: ``increase shoulder motor pulse-width 1µS``
* S: ``decrease shoulder motor pulse-width 1µS``
* k: ``increase elbow motor pulse-width 10µS``
* l: ``decrease elbow motor pulse-width 10µS``
* K: ``increase elbow motor pulse-width 1µS``
* L: ``decrease elbow motor pulse-width 1µS``

Now you can initialise the BrachioGraph with the two zero-position values you have discovered, adding ``servo_1_centre``
and ``servo_2_centre`` to the ``bg = BrachioGraph`` instantiation, for example:

..  code-block:: python
    :emphasize-lines: 4

    bg = BrachioGraph(
        inner_arm=9, outer_arm=9,
        bounds=bounds=(-8, 3, 8, 15),
        servo_1_centre=1695, servo_2_centre=1480
    )

This will reduce some distortion.


.. _polyfit:

Create better angle-to-pulse-width functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifying a precise value for the motors so that they align with the x and y axes when initialised is a good start.
However, it still leaves us with the problem of the motors' non-linearity - which requires a non-linear function to
address.

If we obtain a number of angles and their corresponding pulse-widths for each servo, ``numpy.polyfit()`` can be used to
determine a polynomial non-linear function for each one.

These can be determined by testing, using ``bg.drive()``.

Servo motors' horns generally attach in positions with 18 degrees between each one, so a good way to do this is to mark
a reference point on paper, and align the arms with that, removing them and replacing at a different angle each time.
Or you could just use a protractor and measure from that.

Then, these values can be supplied in the definition, with ``servo_1_angle_pws`` and ``servo_2_angle_pws``,

The ``brachiograph.py`` file contains an example, a definition for the actual machine depicted in this documentation::

    # angles in degrees and corresponding pulse-widths for the two arm servos
    servo_1_angle_pws = [
        [-162, 2490],
        [-144, 2270],
        [-126, 2070],
        [-108, 1880],
        [ -90, 1680],
        [ -72, 1540],
        [ -54, 1360],
        [ -36, 1190],
        [ -18, 1020],
        [   0,  830],
        [  18,  610],
    ]

    servo_2_angle_pws = [
        [  0,  610],
        [ 18,  810],
        [ 36,  970],
        [ 54, 1140],
        [ 72, 1310],
        [ 90, 1460],
        [108, 1630],
        [126, 1790],
        [144, 1970],
        [180, 2360],
    ]


    bg = BrachioGraph(
        inner_arm=9.0,            # the lengths of the arms
        outer_arm=9.0,            # the lengths of the arms
        bounds=(-8, 3, 8, 15),
        # angles in degrees and corresponding pulse-widths for the two arm servos
        servo_1_angle_pws=servo_1_angle_pws
        servo_2_angle_pws=servo_2_angle_pws
        # pulse-widths for pen up/down
        pw_up=1700,
        pw_down=1300,
    )

This visibly helps reduce distortion when the machine is drawing.

It's tempting to try to find optimum mathematical solutions to improve the precision and accuracy of the plotter, but
in practice the imprecision of the motors themselves and the play in the mechanical system make this rather futile.

You can use the included Jupyter notebook to :ref:`visualise the relationship between pulse-widths and servo angles
<visualise-servo-behaviour>`.
