.. _build:

Build the plotter
=================

Components and materials
------------------------

You'll need: :ref:`a Raspberry Pi <hardware-pi>`, three :ref:`servo motors <hardware-servos>`, two :ref:`arms
<hardware-arms>` and other small items mentioned below (such as a clothes-peg) depending on exactly how you build the
machine. You'll also need some strong adhesive.

If you are using SG90 motors as suggested, arms of about 8cm are suitable for drawing an area approximately 16cm wide
by 11cm high. This fits well onto a sheet of A5 paper. To help understand the relationship betweem arm geometry and the
drawing area, this can be visualised using the :ref:`script provided <visualise-area>`.


Assembly
-----------------

As illustrated:

* glue the servo horns to the inner arm, so that the centres of rotation are about 8cm (or whatever you have selected)
  apart
* glue a servo and a clothes-peg to the outer arm, so that a pen in the clothes-peg and the centre of rotation of the
  arm will also be the appropriate distance apart (or, use an :ref:`alternative arrangement <no-clothes-peg>`)
* attach the shoulder motor to the base

.. image:: /images/brachiograph-top-view-arms.jpg
   :alt: 'Arms and motors'
   :class: 'main-visual'

The system uses centimetres as its basic unit of length. Measure the distance between the axis of the two servo horns
on the upper arm (``inner_arm``), and the distance between the axis of the servo motor and the pen on the other
(``outer_arm``).
