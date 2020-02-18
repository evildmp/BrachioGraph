``brachiograph.py``
==========================

The ``BrachioGraph`` class
---------------------------

::

    class BrachioGraph:

      def __init__(
          self,
          inner_arm,
          outer_arm,
          virtual_mode=False,
          bounds=None,
          servo_1_centre=1500,
          servo_2_centre=1500,
          servo_1_degree_ms = 10,
          servo_2_degree_ms = -10,
          arm_1_centre=-60,
          arm_2_centre=90,
          servo_1_angle_pws=[],
          servo_2_angle_pws=[],
          pw_up=1500,
          pw_down=1100,
      ):

* ``inner_arm``, ``outer_arm`` need to be measured from the actual plotter. They don't need to be equal, but some
  combinations are uselessly restrictive. Use the ``turtle_draw.py`` script to :ref:`see how different geometries
  affect the plottable area <understand-plotter-geometry>`.
* ``virtual_mode`` allows you to :ref:`run a BrachioGraph without hardware attached <virtual-mode>`
* ``bounds`` needs to be determined empirically. Or possibly, `computed
  <https://math.stackexchange.com/questions/3293200/how-can-i-calculate-the-area-reachable-by-the-tip-of-an-articulated-
  arm#comment6773872_3293200>`_.
* ``servo_1_centre`` and ``servo_2_centre``: the pulse-width at which each servo arm is exactly on the plotting grid's x
  or y axis. Ignored if the ``servo_<x>_angle_pws`` arguments are provided.
* ``servo_1_degree_ms`` and ``servo_2_degree_ms``: how many ms per degree of movement. Reverse the sign to reverse the
  direction.
* ``arm_1_centre`` and ``arm_2_centre``: the angles of the arms when the servo is at
  ``servo_1_centre``/``servo_1_centre`` respectively
* ``servo_1_angle_pws`` and ``servo_2_angle_pws``: lists of pulse-width/angle pairs. If provided, then
  :ref:`numpy.polyfit <polyfit>` will be used to produce a function for calculating required pulse-widths. If not, a
  more naive formula will be used.
* ``pw_up`` and ``pw_down``: pulse width values at which the pen is up/down. It makes more sense to attach the lifting
  servo horn at a different angle than to change these.


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
