BrachioGraph - the cheapest, simplest possible pen-plotter
=========================================================

BrachioGraph - *arm-writer* - is an easy-to-build pen-plotter, driven by a library of simple Python applications.

.. image:: /images/brachiograph.jpg
   :alt: 'The BrachioGraph plotter'
   :class: 'main-visual'

The hardware:

* two pieces of stiff card
* a ballpoint pen
* 3 servo motors
* a Raspberry Pi, to drive the servos and run the custom code

The software:

* ``brachiograph.py``, to draw images using the servos
* ``linedraw``, a fork of a library to vectorise bit-map images
* ``turtle_draw.py``, to help visualise the drawing area of the plotter
* ``pulse_widths.ipynb``, a Jupyter notebook to help understand the characteristics of a servo motor
* ``pantograph.py``, to draw images using an alternative plotter design

Tools required:

* a knife
* glue
* a ruler


.. toctree::
    :maxdepth: 1

    get-started
    how-to
    reference
    explanation
