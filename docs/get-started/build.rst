.. _build:

Build the plotter
=================

This tutorial takes you through the process of building a plotter with 8cm arms. 8cm arms are
suitable for drawing an area approximately 14cm wide by 9cm high. This fits well onto a sheet of A5
paper.

.. seealso::

  * :ref:`understand_plotter_geometry`
  * :ref:`optimise-geometry`


Components and materials
------------------------

You'll need:

* a Raspberry Pi
* three servo motors (recommended model: TowerPro SG90 - see :ref:`servo motors <hardware-servos>`
  for more information)
* sticks or stiff card to make two arms, each about 10cm long
* jumper wires and GPIO pin header to connect the Pi to the servos
* a clothes peg
* a board or sheet of card, about A4 size
* strong adhesive or a hot glue gun


Assembly
-----------------

The image below shows the basic construction of the BrachioGraph plotter. In this example, the drawing sheet is A5 size.

.. image:: /images/basic-construction.jpg
   :alt:


The shoulder motor
~~~~~~~~~~~~~~~~~~

The servo motor needs to be raised by a few millimetres, for example with a layer or two of card as
shown. Glue it into place.

.. image:: /images/shoulder-servo-mounting.jpg
   :alt:


.. _build-inner-arm:

The inner arm
~~~~~~~~~~~~~

Glue the servo horns to the inner arm, so that the centres of rotation are exactly 8cm apart.

.. image:: /images/arm.jpg
   :alt:


The outer arm, clothes-peg and servos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Glue a servo and a clothes-peg to the outer arm, so that a pen in the clothes-peg and the centre of
rotation of the arm will also be 8cm apart.

Glue the final servo in such a position that its horn
can rotate safely, and will be able to lift the pen clear of the paper.

.. image:: /images/outer-arm.jpg
   :alt: 'The outer arm, clothes-peg and servos'


The assembled BrachioGraph
~~~~~~~~~~~~~~~~~~~~~~~~~~

The BrachioGraph software needs to know the length of each arm. If you measure them carefully, both
should be 8cm. It doesn't matter if they are a few millimetres off, as long as you note the values.

.. image:: /images/brachiograph-top-view-arms.jpg
   :alt: 'Arms and motors'
   :class: 'main-visual'


Video
-----

..  raw:: html

    <iframe width="810" height="456" src="https://www.youtube.com/embed/7hI-9dHqTeg" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>
