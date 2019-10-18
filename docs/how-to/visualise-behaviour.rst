How to visualise plotter behaviour
==================================

.. _visualise-servo-behaviour:

Visualise the relationship between pulse-widths and angles
----------------------------------------------------------

``jupyter lab pulse_widths.ipynb`` will help visualise the relationship between pulse-widths and angles, using the same ``numpy.polyfit()`` as used in the BrachioGraph:

.. image:: /images/pw-angles.png
   :alt: 'Pulse-widths to angles'
   :class: 'main-visual'


.. _visualise-area:

Visualise the plotting area
----------------------------

To see how different plotter geometries work in practice, plug them into ``turtle_draw.py``, and run ``python turtle_draw.py`` to see the effect. The grey lines represent possible pen positions; your ``bg.bounds`` value
must fit inside this area.

.. image:: /images/plotting-area.png
   :alt: 'Plotting area'
   :class: 'main-visual'
