.. _drive:

Start up the BrachioGraph
=========================

Create a ``BrachioGraph`` instance
----------------------------------

Power up the Raspberry Pi. Run::

    sudo pigpiod
    cd BrachioGraph
    python3

And then, using the ``inner_arm`` and ``outer_arm`` measurements you noted earlier::

    from brachiograph import BrachioGraph

    bg = BrachioGraph(inner_arm=<inner_arm>, outer_arm=<outer_arm>)

The system will create a BrachioGraph instance and initialise itself, adjusting the motors so that the pen will be at
a nominal:

* x = ``-inner_arm``
* y = ``outer_arm``

And this will correspond to:

* the upper arm at -90 degrees, 1500µS pulse-width
* the lower arm at 90 degrees to it, 1500µS pulse-width
* the lifting motor in the pen up position, 1700µS pulse width


Attach the arms
---------------

Attach the arms in the configuration shown, or as close as possible. Of course the arms may be a
few degrees off the perpendicular, but don't worry about that now.


.. image:: /images/starting-position.jpg
   :alt: 'Starting position'
   :class: 'main-visual'

Attach the horn to the lifting motor.

.. image:: /images/lifting-mechanism.jpg
   :alt: 'Pen-lifting mechanism'

You need the pen to be just clear of the paper in the *up* position. The lifting movement can cause
unwanted movement of the pen, so you need to minimise that. You can experiment with::

    bg.pen.rpi.set_servo_pulsewidth(18, <value>)

to find a good pair of up/down values. Then you can include them in your initialisation of the
BrachioGraph, by supplying ``pw_up`` and ``pw_down``

Of course your arms may be a few degrees off. Don't worry about that now.


Take the BrachioGraph for a drive
---------------------------------

::

    bg.drive_xy()

Controls:

* 0: ``exit``
* a: ``increase x position 1cm``
* s: ``decrease x position 1cm``
* A: ``increase x position .1cm``
* S: ``decrease x position .1cm``
* k: ``increase y position 1cm``
* l: ``decrease y position 1cm``
* K: ``increase y position .1cm``
* L: ``decrease y position .1cm``

Use this to discover the bounds of the box the BrachioGraph can draw.

Take a note of the ``bounds`` - the box described by ``[<minimum x>, <minimum y, <maximum x>, <maximum y>]``.

Reinitialise your plotter with these values::

    bg = BrachioGraph(inner_arm=<inner_arm>, outer_arm=<outer_arm>, bounds=<bounds)


.. _start-plotting:

Test it
-------

Draw a box, using the ``bounds``::

    bg.box()

and a test pattern::

    bg.test_pattern()

If the lines are reasonably straight and the box is reasonably square, try plotting a file::

    bg.plot_file("test_file.json")


Save your BrachioGraph definition
---------------------------------

The file ``bg.py`` is a good place to save your defined ``BrachioGraph`` instances  for future use. It
already contains examples for units built during the development process.
