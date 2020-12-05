.. _build:

Build the plotter
=================

..  raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/7hI-9dHqTeg" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>


Components and materials
------------------------

You'll need:

* a Raspberry Pi
* three :ref:`servo motors <hardware-servos>`
* sticks or stiff card to make two arms, each about 10cm long (to give you 8cm arms with a centimetre to spare at each
  end)
* jumper wires and GPIO pin header to connect the Pi to the servos
* other small items mentioned below (such as a clothes-peg) depending on exactly how you build the machine.

You'll also need some strong adhesive or a hot glue gun.

See :ref:`the hardware section <hardware>` for details on what components and materials to obtain.

The system uses centimetres as its basic unit of length. 8cm arms are suitable for drawing an area approximately 14cm
wide by 9cm high. This fits well onto a sheet of A5 paper. (See :ref:`understand_plotter_geometry` and
:ref:`optimise-geometry`.)


Assembly
-----------------

The shoulder motor
~~~~~~~~~~~~~~~~~~

Attach a servo to the base, either by gluing it or attaching it some other way; two ways are shown below. It needs to
be raised a little above the level of the base.

.. image:: /images/shoulder-servo-mounting.jpg
   :alt: 'Options for mounting the shoulder servo'


The inner arm
~~~~~~~~~~~~~

Glue the servo horns to the inner arm, so that the centres of rotation are exactly 8cm apart (you can use other
dimensions, but for a first build, use 8cm).

.. image:: /images/arm.jpg
   :alt: 'the horns glued to the inner arm'


The outer arm, clothes-peg and servos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Glue a servo and a clothes-peg to the outer arm, so that a pen in the clothes-peg and the centre of rotation of the arm
will also be 8cm apart. Glue the final servo in such a position that its horn can rotate safely, and will be able to
lift the pen clear of the paper. (See also an :ref:`alternative arrangement <no-clothes-peg>`.)

.. image:: /images/outer-arm.jpg
   :alt: 'The outer arm, clothes-peg and servos'


The assembled BrachioGraph
~~~~~~~~~~~~~~~~~~~~~~~~~~

The BrachioGraph software needs to know the length of each arm, in values provided as ``inner_arm`` and ``outer_arm``.
If you measure them carefully, both should be 8cm.

.. image:: /images/brachiograph-top-view-arms.jpg
   :alt: 'Arms and motors'
   :class: 'main-visual'
