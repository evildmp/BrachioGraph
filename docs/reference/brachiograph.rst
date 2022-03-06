.. raw:: html

    <style>
        table.docutils { width: 100%; table-layout: fixed;}
        table.docutils th, table.docutils td { white-space: normal }
    </style>


``brachiograph.py``
==========================

..  module:: brachiograph


..  autoclass:: BrachioGraph
    :members:

..  list-table:: ``BrachioGraph`` attributes
    :header-rows: 1
    :widths: 28, 20, 52

    * - attribute
      - default
      - description

    * - ``inner_arm``, ``outer_arm``
      - 8
      - length of each arm in centimetres

    * - ``servo_1_parked_pw``, ``servo_2_parked_pw``
      - 1500
      - motor centre pulse-widths; ignored if the ``servo_<x>_angle_pws`` arguments (below) are provided

    * - ``servo_1_angle_pws_bidi``, ``servo_2_angle_pws_bidi``
      - ``{}``
      - a list of empirically-derived pulse-width/angle pairs; if provided, will be used to provide a function for
        calculating pulse-widths; see :ref:`tutorial-sophisticated-calibration`

    * - ``servo_1_degree_ms``, ``servo_2_degree_ms``
      - -10, 10
      - microseconds pulse-width change per degree of motor movement; see :ref:`pulse-width-degrees`

    * - ``servo_1_parked_angle``
      - 90
      - angle in degrees of the shoulder motor's centre of movement (i.e. at ``servo_1_parked_pw``) relative to the
        drawing grid

    * - ``servo_2_parked_angle``
      - 90
      - angle in degrees of the elbow motor's centre of movement (i.e. at ``servo_2_parked_pw``) relative to the inner
        arm

    * - ``hysteresis_correction_1``, ``hysteresis_correction_2``
      - 0
      - empirically-derived hardware error compensation values, in µs; see :ref:`hysteresiscompensation`

    * - ``bounds``
      - ``[-8, 4, 6, 13]``
      - the box within which the BrachioGraph will draw; see :ref:`understand_plotter_geometry`

    * - ``virtual``
      - ``False``
      - :ref:`runs the BrachioGraph without attached hardware <virtual-mode>`

    * - ``wait``
      - ``None``
      - a factor that influences the time before the next movement is commanded

    * - ``pw_up``, ``pw_down``
      - 1500, 1100
      - pulse width values at which the pen is in the up/down positions


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
