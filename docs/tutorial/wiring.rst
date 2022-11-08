.. _connect-servos:

Wire up the plotter
=============================

..  important:: **Make sure the Raspberry Pi is turned off while you're wiring it up.**

    Although the Raspberry Pis can take a frankly amazing amount of abuse, you run the risk of causing damage if you
    get the wiring wrong. Do it with the power off, take your time, and **double-check your work**.

The three servos need to be connected to the Raspberry Pi. Each servo has three wires:

* 5V (power) - usually orange or red
* Ground - usually brown
* Signal - usually yellow

5V and ground are required to power the servo; the signal wire carries a pulse, whose width (its length in
microseconds) determines the position of the motor.

**At least two of the servos will need to share a 5V connection**, since the Raspberry Pi
has only two available. How you achieve this will depend on what you have available.

..  tab-set:: 
  
  ..  tab-item:: Use a breadboard

      If you have a breadboard, you can wire the servos up so:

      .. image:: /images/wiring.png
         :alt:

  ..  tab-item:: Solder a wiring loom

      I prefer to solder a little wiring loom out of jumper cables, that the servo's leads connect to,
      so that they all share a single connector for 5V, and a single connector for Ground. That way,
      you can use just 5 pins on the Raspberry Pi, all next to each other. It looks like this:

      .. image:: /images/loom.jpg
         :alt:

      This connects to the Raspberry Pi like so:

      .. image:: /images/pin-connections.jpg
         :alt:


Check the connections
---------------------

**Double-check** each connection all the way from the servo to the Raspberry Pi.

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - servo lead
     - GPIO pin
     - physical pin
   * - all 5V leads
     - any 5V power pin
     - 2 or 4
   * - all Ground leads
     - any Ground pin
     - 6, 9, 14, 20, 25, 30, 34, 36, 39
   * - shoulder motor signal
     - 14
     - 8
   * - elbow motor signal
     - 15
     - 10
   * - lifting motor signal
     - 18
     - 12

..  note:: https://pinout.xyz has some useful information about the pins.
