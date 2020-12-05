.. _calibrate:

How to improve the plotter calibration
======================================

Each servo motor is different, so the BrachioGraph can be calibrated exactly for your servos. To get you started
however, it makes some assumptions about the servos.

For `SG90 motors <http://www.towerpro.com.tw/product/sg90-analog/>`_ or similar:

* they have almost 180˚ of rotation, though they are specified for 120˚ and that's the better value to assume
* they operate on pulse-widths from about 500µS to about 2600µS, though the official values are 1000µS to 2000µS and those are better values to use
* the centre of their travel is around 1500µS
* one degree of travel corresponds a difference of about 10µS

This is what the default ``angles_to_pw_1`` and ``angles_to_pw_2`` methods assume when the BrachioGraph is initialised.

This is sufficient to get started, but since the values above are nominal values only, they won't provide the best
results. In addition, the correspondence between pulse-widths and angles is not actually linear, and worse, mechanical
hysteresis in the system means that the quality of your drawings will be much lower than it ought to be.

All of these issues can be addressed however. In this section:

* :ref:`basic-calibration`, for quick improvements to reduce distortion
* :ref:`advanced-calibration`, to counteract non-linearity using real-world data
* :ref:`hysteresiscompensation`, for huge improvements in output quality
* :ref:`calibrate-pen-lifting`

So, you can supply some values to improve upon these assumptions.


.. _basic-calibration:

Basic calibration
---------------------

Find the centre angle pulse-widths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the BrachioGraph is initialised with::

    servo_1_centre = 1500  # shoulder motor centre pulse-width
    servo_2_centre = 1500  # elbow motor centre pulse-width

Probably, at the nominal "zero" angles (-90 and 90 degrees respectively) the arms will probably not be quite at the
those angles. You can use ``bg.drive()`` to discover what pulse-widths correspond to the centre positions.

Controls:

* 0: ``exit``
* a: ``decrease shoulder motor pulse-width 10µS`` (A: 1µS)
* s: ``increase shoulder motor pulse-width 10µS`` (S: 1µS)
* k: ``decrease elbow motor pulse-width 10µS`` (K: 1µS)
* l: ``increase elbow motor pulse-width 10µS`` (L: 1µS)

Now you can initialise the BrachioGraph with the two zero-position values you have discovered, adding ``servo_1_centre``
and ``servo_2_centre`` to the ``bg = BrachioGraph`` instantiation, for example:

..  code-block:: python
    :emphasize-lines: 4

    bg = BrachioGraph(
        inner_arm=9, outer_arm=9,
        bounds=bounds=(-8, 3, 8, 15),
        servo_1_centre=1695, servo_2_centre=1480
    )

Getting the ``servo_1_centre`` right will align the drawing better with your paper. Getting the ``servo_2_centre``
right will help reduce some distortion.


.. _pulse-width-degrees:

Adjust pulse-width to movement factor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``servo_1_degree_ms`` and ``servo_2_degree_ms`` values by default assume that a 10µS change in pulse-width will
produce a 1˚ change in angle. This is close, but you can usually discover better values through trial and error.


.. _advanced-calibration:
.. _polyfit:

Advanced calibration
--------------------------------------------

Improving values for the motors as described above is a good start. However, it still leaves us with the problem of the
motors' *non-linearity* - which requires a non-linear function to address.

If we obtain a number of angles and their corresponding pulse-widths for each servo, ``numpy.polyfit()`` can be used to
determine a polynomial non-linear function for each one.

You can supply a ``servo_1_angle_pws`` or ``servo_2_angle_pws`` in the BrachioGraph definition, for example::

    servo_2_angle_pws = [
        [ 36,  950],
        [ 54, 1130],
        [ 72, 1310],
        [ 90, 1500],
        [108, 1700],
        [126, 1880],
        [144, 2070],
    ]

The first values are different angles of the motor. The second values are the corresponding pulse-widths. (If you use
these in the :ref:`provided Jupyter Notebook <visualise-servo-behaviour>`, you will see that the curve is not linear.)

Servo motors' horns generally attach in positions with 18˚ (for smaller motors with 20 splines) or 14.4˚ (larger motors
with 25 splines) between each one, a property we can make use of.


Collect the angles and pulse-widths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are various ways of collecting the angles and pulse-widths, but the BrachioGraph includes a ``calibrate()``
method to help gather them.

Mount the protractor
^^^^^^^^^^^^^^^^^^^^

Two protractors are provided, for servos with 20 and 25 splines.

* :download:`protractor for servos with 20 splines </supporting-files/20-splines.pdf>`
* :download:`protractor for servos with 25 splines </supporting-files/25-splines.pdf>`

You will need to mount the protractor such that its centre is exactly at the axis of the motor.

.. image:: /images/protractor.jpg
   :alt: 'The protractor mounted for the shoulder servo'
   :class: 'main-visual'


.. _collect-pw-angles:

Collect pulse-widths and angles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next, create a BrachioGraph definition with the appropriate arm-lengths supplied. The actual arms don't need to be
attached at this stage.

Import the definition and invoke ``calibrate()``::

    from my_calibrated_bg import bg
    bg.calibrate()

The servo will move to its centre position (1500µS, unless you have specified otherwise). Mount the arm on the servo at
a position as close as possible to 0˚ (if you are working on the inner arm) or 90˚ (if you are working on the outer
arm).

Now drive the arm over the paper. Controls:

* 0: *exit*
* 1: *record an angle*
* 2: *report collected angles*
* a: *increase shoulder motor pulse-width 10µS*
* s: *decrease shoulder motor pulse-width 10µS*
* A: *increase shoulder motor pulse-width 1µS*
* S: *decrease shoulder motor pulse-width 1µS*

When you reach a precise angle, record it: press *1*, then enter the angle. Do this for as many angles as possible.
press *2* when you have finished collecting them. The angles and pulse-widths will be displayed.

**Important**: for best results, always collect these values while driving the motor in the same direction (either
increasing or decreasing the pulse-width values), because the exact pulse-width at which the arms move to a particular
position depends on whether motor is moving in one direction ot another, due to :ref:`hysteresis
<hysteresiscompensation>`.


Supply the offset angle
^^^^^^^^^^^^^^^^^^^^^^^

The arm should now be re-attached (if required) to the servo as close as possible to its optimal angle (i.e. the one
that gives you the best drawing area.) You can use the turtle graphics module provided to help calculate this, but as a
rule of thumb, if the two servo arms are of equal length, you can use:

* -60˚ for the inner arm
* 90˚ for the outer arm

You won't be able to attach the arm at exactly the right angle, but a few degrees off won't matter. You will need to
provide the angle by which you have offset the arm. Do this by counting the splines you had to move it by, and
multiplying that by the angle between each spline - for example, 4 splines to the left times 14.4˚ is ``-56.7``.

You'll now be given a value for that servo that you can incorporate into the BrachioGraph definition, for example::

    servo_1_angle_pws = [[-86.4, 1970], [-72.0, 1820], [-57.6, 1680], [-43.2, 1510], [-28.8, 1320], [-14.4, 1190], [0.0, 1030], [13.4, 890], [28.8, 760]]

Repeat the process for the other servo.


Include the values in the BrachioGraph definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the collected values to your BrachioGraph definition, for example:

..  code-block:: python
    :emphasize-lines: 1, 2

    servo_1_angle_pws = [[-86.4, 1970], [-72.0, 1820], [-57.6, 1680], [-43.2, 1510], [-28.8, 1320], [-14.4, 1190], [0.0, 1030], [13.4, 890], [28.8, 760]]
    servo_2_angle_pws = [[18.0, 760], [36.0, 960], [54.0, 1120], [72.0, 1290], [90.0, 1470], [108.0, 1670], [126.0, 1870], [144.0, 2050], [162.0, 2230]]


    bg = BrachioGraph(
        # the lengths of the arms
        inner_arm=9,
        outer_arm=7,
        servo_1_angle_pws=servo_1_angle_pws,
        servo_2_angle_pws=servo_2_angle_pws,
        [...]
    )

Next time you use definition, it will be optimised for the servos' actual characteristics.

You can use the included Jupyter notebook to :ref:`visualise the relationship between pulse-widths and servo angles
<visualise-servo-behaviour>`.


.. _hysteresiscompensation:

Hysteresis compensation
--------------------------

The BrachioGraph is subject to mechanical :ref:`hysteresis <about-hysteresis>`, which causes the actual position of the pen
to be slightly different for a particular target point, depending on which direction it moved there from. This causes
strokes to be misaligned with each other. In this image, the grid has been drawn twice, in two different directions;
the two versions of the grid overlay each other very imperfectly:

.. image:: /images/hysteresis.jpg
   :alt: 'The effect of hysteresis'
   :class: 'main-visual'

Hysteresis needs to be compensated for in order to achieve the best results. The dead-band of hysteresis is usually a
few µS. Although a motor *itself* may not have a large dead-band, you will find that the system itself has larger
dead-bands, especially affecting the shoulder motor.


Use the grid to identify misalignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Draw a grid::

    bg.grid_lines(interpolate=400, both=True)

``both`` draws each line in both directions.

Watch carefully to see where the drawing is misaligned; mark misaligned segments with a direction arrow to help you
remember which line is which. You will find that the errors occur when the pen lags behind the position at which it
ought to be.


Test compensation values
~~~~~~~~~~~~~~~~~~~~~~~~

The solution is to push it forwards by a corresponding amount. That is: if a motor has been moving in a particular
direction, command it to a position just a little further in that direction to compensate, until it's time to change
direction.

The only way to obtain the right compensation values is by experiment. While recording the pulse-width/angles you may
have had a good idea of the dead-band of the motor, but now we have to deal with hysteresis in the entire system.

Start with the value for the shoulder motor. Any adjustment made by this motor has to be transmitted through both arms,
both joints and the pen-holding mechanism, and it has more weight and a longer arm to displace, so it's likely to be
the most significant correction that needs to be made.

Try adding::

    hysteresis_correction_1=10

to the BrachioGraph definition, and plot the grid forwards and backwards again, again watching carefully to see where
the errors occur. Pay particular attention to those parts of the lines where the *elbow* motor is *not* changing its
position, because it's at these positions that you'll most clearly see where the shoulder motor needs to be adjusted
to improve alignment.

Once you have got the best result possible for these parts of the lines, try a similar adjustment for the elbow motor,
say::

    hysteresis_correction_2=2

Since the elbow motor has less weight and a shorter arm of movement to displace, it's likely to need a smaller
correction value.

*You are very unlikely to get perfect results!* But, with a little trial and error The BrachioGraph can compensate for
hysteresis very effectively:

.. image:: /images/hysteresis-correction.jpg
   :alt: 'Hysteresis corrected'
   :class: 'main-visual'

In practice, this correction improves the quality of drawings enormously, capturing far more detail and eliminating
many errors that spoil images.


Collect more precise pulse-width/angle values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In :ref:`collect-pw-angles` above, we only collected the values going in one direction. In the other direction, they
will all be slightly different. You could collect them both, and then use an average of the pair for each position.

Given the inherent imprecision of the system, *this is unlikely to have any visible effect*. But if you're determined to
wring our every last drop of possible precision from the system - try it.


.. _calibrate-pen-lifting:

Calibrate the pen lifting motor
-------------------------------

To calibrate the pen motor, run the ``Pen.calibrate()`` method. The ``Pen`` object is an attribute of the
``BrachioGraph`` object, so the best way to do this is::

    from my_calibrated_bg import bg
    bg.pen.calibrate()

Controls:

* 0: *exit*
* z: *decrease pen motor pulse-width 10µS*
* x: *increase pen motor pulse-width 10µS*
* u: *record this as the pen-up position*
* d: *record this as the pen-down position*
* t: *toggle between the two positions*

In addition, to check the pen at different positions over the paper (usually the middle of the paper is fine):

* a: *increase shoulder motor pulse-width 10µS*
* s: *decrease shoulder motor pulse-width 10µS*

Try to fix the horn for the motor at a position where 1500µS is about half-way between the up and down values.

You can copy the values reported by the calibration method into your BrachioGraph definition, e.g.:

..  code-block:: python
    :emphasize-lines: 3,4

    bg = BrachioGraph(
        [...]
        pw_down=1400,
        pw_up=1650,
    )
