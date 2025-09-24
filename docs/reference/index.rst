.. _reference:

=========================================================
Reference
=========================================================

The core Python modules.

``plotter`` is the base module, and contains the basic concepts for driving an x/y drawing machine using the rotational position of servo motors.

``brachiograph`` provides a particular case of a plotter with a shoulder-elbow arm geometry. (An alternative implementation as a pantograph is provided in the ``pantograph`` module, but the only current documentation is in :ref:`how-to-pantograph`.)

.. toctree::
    :maxdepth: 1

    brachiograph
    turtle-plotter

``linedraw`` is for vectorising bitmap images into lines for the plotter to draw.

.. toctree::
    :maxdepth: 1

    linedraw
