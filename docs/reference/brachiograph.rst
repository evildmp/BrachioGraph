.. raw:: html

    <style>
        table.docutils { width: 100%; table-layout: fixed;}
        table.docutils th, table.docutils td { white-space: normal }
    </style>


``brachiograph.py``
==========================

The ``BrachioGraph`` class
---------------------------


::

    class BrachioGraph:

        def __init__(
            self,
            inner_arm=8,                # the lengths of the arms
            outer_arm=8,
            servo_1_centre=1500,        # shoulder motor centre pulse-width
            servo_2_centre=1500,        # elbow motor centre pulse-width
            servo_1_angle_pws=[],       # pulse-widths for various angles
            servo_2_angle_pws=[],
            servo_1_degree_ms=-10,      # milliseconds pulse-width per degree
            servo_2_degree_ms=10,       # reversed for the mounting of the elbow servo
            arm_1_centre=-60,
            arm_2_centre=90,
            hysteresis_correction_1=0,  # hardware error compensation
            hysteresis_correction_2=0,
            bounds=[-8, 4, 6, 13],      # the maximum rectangular drawing area
            wait=None,
            virtual_mode = False,
            pw_up=1500,                 # pulse-widths for pen up/down
            pw_down=1100,
        ):


..  list-table:: ``BrachioGraph`` attributes
    :header-rows: 1
    :widths: 28, 20, 52

    * - attribute
      - default
      - description

    * - ``inner_arm``, ``outer_arm``
      - 8
      - length of each arm in centimetres

    * - ``servo_1_centre``, ``servo_2_centre``
      - 1500
      - motor centre pulse-widths; ignored if the ``servo_<x>_angle_pws`` arguments (below) are provided

    * - ``servo_1_angle_pws``, ``servo_2_angle_pws``
      - ``[]``
      - a list of empirically-derived pulse-width/angle pairs; if provided, will be used to provide a function for
        calculating pulse-widths; see :ref:`advanced-calibration`

    * - ``servo_1_degree_ms``, ``servo_2_degree_ms``
      - -10, 10
      - milliseconds pulse-width change per degree of motor movement; see :ref:`pulse-width-degrees`

    * - ``arm_1_centre``
      - -60
      - angle in degrees of the shoulder motor's centre of movement (i.e. at ``servo_1_centre``) relative to the
        drawing grid; see :ref:`basic-calibration`

    * - ``arm_2_centre``
      - 90
      - angle in degrees of the elbow motor's centre of movement (i.e. at ``servo_2_centre``) relative to the inner
        arm; see :ref:`basic-calibration`

    * - ``hysteresis_correction_1``, ``hysteresis_correction_2``
      - 0
      - empirically-derived hardware error compensation values, in mS; see :ref:`hysteresiscompensation`

    * - ``bounds``
      - ``[-8, 4, 6, 13]``
      - the box within which the BrachioGraph will draw; see :ref:`understand_plotter_geometry`

    * - ``virtual_mode``
      - ``False``
      - :ref:`runs the BrachioGraph without attached hardware <virtual-mode>`

    * - ``wait``
      - ``None``
      - a factor that influences the time before the next movement is commanded

    * - ``pw_up``, ``pw_down``
      - 1500, 1100
      - pulse width values at which the pen is in the up/down positions



Management methods
~~~~~~~~~~~~~~~~~~

``park()``
^^^^^^^^^^^^

Sends the arms to the parking position, with the inner arm at -90˚ and the outer arm at 90˚ to it.
This corresponds to an x/y position:

* x: ``-inner_arm``
* y: ``outer_arm``


Image drawing methods
~~~~~~~~~~~~~~~~~~~~~~~

``plot_file(image)``
^^^^^^^^^^^^^^^^^^^^

* ``image``: path to image file


Drawing utility methods
~~~~~~~~~~~~~~~~~~~~~~~

``box()``
^^^^^^^^^^^^

Draw a box marked out by the ``bounds``.


``grid_lines()``
^^^^^^^^^^^^^^^^^

Draws a grid within the box area marked out by the ``bounds``.


Reporting methods
~~~~~~~~~~~~~~~~~

``report()``
^^^^^^^^^^^^

The BrachioGraph instance has four attributes, ``angles_used_1``, ``angles_used_2``, ``pulse_widths_used_1``,
``pulse_widths_used_2``. They are all Python sets. Each time the ``set_angles`` method is called, it records the angle
and pulse-width recorded for each of the two arm servos.

This creates a running record of all the positions the arms have been in.

After the arm has finished drawing, you can find the minimums, maximums and mid-points::

    >>> bg.report()
                   min   max   mid    min   max   mid
          angles  -124     7   -59     43   154    99
    pulse-widths   771  2048  1410   1047  2063  1555

In this case, it's good to know that the mid-points in the range both servos have covered while plotting all over the
paper are not too far from 1500ms - which means that their range is reasonably well centred.


The ``Pen`` class
---------------------------

A ``BrachioGraph`` instance has an instance of a ``Pen`` class, as ``BrachioGraph.pen``.

::

    class BrachioGraph:

        def __init__(
            self,
            bg,                         # the BrachioGraph instance to which the Pen is attached
            pw_up=1500, pw_down=1100,   # pen up and pen down pulse-widths
            pin=18,                     # the GPIO pin
            transition_time=0.25        # how long to wait for up/down movements
            ):
