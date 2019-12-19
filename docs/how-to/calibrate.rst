.. _calibrate:

Improve the plotter calibration
===============================

Each servo motor is different, so the BrachioGraph can be calibrated exactly for your servos. To get you started
however, it makes some assumptions about the servos.

For `SG90 motors <http://www.towerpro.com.tw/product/sg90-analog/>`_ or similar:

* they have almost 180˚ of rotation, though they are specified for 120˚ and that's the better value to assume
* they operate on pulse-widths from about 500µS to about 2600µS, though the official values are 1000µS to 2000µS and those are better values to use
* the centre of their travel is around 1500µS
* one degree of travel corresponds a difference of about 10µS

This is what the default ``angles_to_pw_1`` and ``angles_to_pw_2`` methods assume when the BrachioGraph is initialised.
This is sufficient to get started.

However, the correspondence between pulse-widths and angles is not actually linear, and 1500µS in practice will be
unlikely to coincide with the arms' positions at the optimal centre of their sweep range. So, you can supply some
values to improve upon these assumptions. This section describes how to do that.


Basic calibration
---------------------

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

Getting the ``servo_1_centre`` right will align the drawing better with your paper. Getting the ``servo_2_centre``
right will help reduce some distortion.


Adjust ``servo_1_degree_ms`` and ``servo_2_degree_ms``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``servo_1_degree_ms`` and ``servo_2_degree_ms`` values by default assume that a 10µS change in pulse-width will
produce a 1˚ change in angle. This is close, but you can usually discover better values through trial and error.


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

The first values are different angles of the motor. The second values are the corresponding pulse-widths. (If you
use these in the :ref:`provided Jupyter Notebook`, you will see that the curve is not linear.)

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


Calibrate the pen motor
-----------------------

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

You can copy the values reported by the calibration method into your BrachioGraph definition, e.g.::

    bg = BrachioGraph(
        [...]
        pw_down=1400,
        pw_up=1650,
    )
