.. _connect-servos:

Wire up the plotter to the Pi
=============================

The three servos need to be connected to the Raspberry Pi

The Raspberry Pi doesn't have enough 5V pins to use one for each servo, so you will either need to solder together a
wiring loom from some strands of ribbon cable as shown below, or use a breadboard.

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
destroy your Raspberry Pi.

On the other hand it seems that these devices can take a great deal of abuse very well.
