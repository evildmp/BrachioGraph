.. raw:: html

    <style>
        .row {clear: both}
        h2  {border-bottom: 1px solid gray;}

        .column img {border: 1px solid gray;}

        @media only screen and (min-width: 1000px),
               only screen and (min-width: 500px) and (max-width: 768px){

            .column {
                padding-left: 5px;
                padding-right: 5px;
                float: left;
            }

            .column3  {
                width: 33.3%;
            }

            .column2  {
                width: 50%;
            }
        }
    </style>


BrachioGraph - the cheapest, simplest possible pen-plotter
==========================================================

BrachioGraph - *arm-writer* - is an easy-to-build pen-plotter, driven by a library of simple Python applications.

.. image:: /images/brachiograph-with-pencil.jpg
   :alt: 'The BrachioGraph plotter'
   :class: 'main-visual'


.. rst-class:: clearfix row

.. rst-class:: column column2

The hardware
------------

* two sticks or pieces of stiff card
* a pencil or ballpoint pen
* a clothespin
* 3 servo motors
* a Raspberry Pi, to drive the servos and run the custom code

Tools required:

* glue
* a ruler
* a knife (if you need to cut the card)


.. rst-class:: column column2

The software
------------

* ``brachiograph.py``, to draw images using the servos
* ``linedraw``, a fork of a library to vectorise bit-map images
* ``turtle_draw.py``, to help visualise the drawing area of the plotter
* ``pulse_widths.ipynb``, a Jupyter notebook to help understand the characteristics of a servo motor
* ``pantograph.py``, to draw images using an alternative plotter design


.. rst-class:: clearfix row

From bitmap to plot via vectorisation
-------------------------------------

.. rst-class:: clearfix row

.. image:: /images/anselmo.jpg
   :alt: 'Anselmo'

.. image:: /images/prague2.jpg
   :alt: 'Prague'


Contents
------------

.. rst-class:: clearfix row

.. rst-class:: column column2

:doc:`Get started <get-started/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build the machine, install the software, make basic tests

.. rst-class:: column column2

:doc:`How-to guides <how-to/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Improve the calibration, process images, visualise plotter behaviour, alternative designs

.. rst-class:: clearfix row

.. rst-class:: column column2

:doc:`Explanation <explanation/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understanding the mathematics, choosing hardware.

.. rst-class:: column column2

:doc:`Reference <reference>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Guide to key classes and functions


.. rst-class:: clearfix row

About the documentation
~~~~~~~~~~~~~~~~~~~~~~~

`Why is the documentation structured this way? <https://www.divio.com/blog/documentation>`_


.. toctree::
    :maxdepth: 1
    :hidden:

    Get started <get-started/index>
    How-to guides <how-to/index>
    Reference <reference>
    Explanation <explanation/index>
