.. _get_started:

Get started
===========

This section describes building the plotter, and driving it using the ``brachiograph.py`` library.

Build the plotter
-----------------

Cut out two arms from your card, say 10cm long x 2cm wide each.

As illustrated:

* glue the servo horns to the arms
* make a hole for the pen, or you could use a pencil and glue it to the lifting servo
* glue the elbow motor to the pen arm
* glue the shoulder motor to the base

.. image:: /images/arms-and-motors.jpg
   :alt: 'Arms and motors'
   :class: 'main-visual'

The system uses centimetres as its basic unit of length. Measure the distance between the axis of the two servo horns
on the upper arm (``inner_arm``), and the distance between the axis of the servo motor and the pen on the other
(``outer_arm``).


Install the required software on the Raspberry Pi
-------------------------------------------------

:ref:`prepare-pi` gives step-by-step directions specifically for using a Pi Zero as the plotter engine.

``brachiograph.py`` requires a few additional components:

Use ``apt`` to install:

* ``pigpiod``

Use pip to install Python 3 versions of:

* ``pigpio``
* ``tqdm``
* ``readchar``
* ``numpy``
* ``tqdm``
* ``readchar``

If you haven't already done so, clone the ``BrachioGraph`` repository::

    git clone git@github.com:evildmp/BrachioGraph.git

or, if you need to use HTTPS instead::

    git clone https://github.com/evildmp/BrachioGraph.git

.. _connect-servos:

Wire up the the three servos to the Raspberry Pi
------------------------------------------------

The Raspberry Pi doesn't have enough 5V pins to use one for each servo, so you will either need to solder together a wiring loom from some strands of ribbon cable as shown below, or use a breadboard.

.. image:: /images/loom.jpg
   :alt: 'Wiring loom'
   :class: 'main-visual'

We connect:

* shoulder motor: GPIO pin 14
* elbow motor: GPIO pin 15
* lifting motor: GPIO pin 18

These correspond to pins 2-12 on the Pi's header. See https://pinout.xyz.

.. image:: /images/pin-connections.jpg
   :alt: 'Pin connections'
   :class: 'main-visual'

It's wise to do this with the Pi turned off until you become confident that you're doing the right thing and won't
destroy your Raspberry Pi. On the other hand it seems that these devices can take a great deal of abuse very well.


Start up the BrachioGraph
-------------------------

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

Attach the arms in the configuration shown, or as close as possible.

.. image:: /images/starting-position.jpg
   :alt: 'Starting position'
   :class: 'main-visual'

Attach the horn to the lifting motor so that it points straight down.

.. image:: /images/pen-and-lift.jpg
   :alt: 'Pen-lifting mechanism'
   :class: 'main-visual'

Of course your arms may be a few degrees off. Don't worry about that now.


Take the BrachioGraph for a drive
---------------------------------

::

    bg.drive_xy()

Controls:

* 0: ``exit``
* a: ``increase x position 1cm``
* a: ``decrease x position 1cm``
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


Test it
-------

Draw a box, using the ``bounds``::

    bg.box()

and a test pattern::

    bg.test_pattern()

If the lines are reasonably straight and the box is reasonably square, try plotting a file::

    bg.plot_file("test_file.json")
