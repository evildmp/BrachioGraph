BrachioGraph - the cheapest, simplest possible pen-plotter
==========================================================

`BrachioGraph <https://www.brachiograph.art/>`_ is an ultra-cheap (total cost of materials: ~€14) plotter that can be built with minimal skills.

At its heart is a Raspberry Pi Zero and some relatively simple custom software, driving three servo motors.

The mechanical hardware can be built from nothing but two sticks, a pen or pencil and some glue. No tools are required.

Almost everything required can be found in a desk or kitchen drawer. The entire device can be built with no special skills in about an hour.


.. image:: docs/images/readme_combined_image.png
    :width: 100%

`BrachioGraph can be found on Twitter <https://twitter.com/BrachioGraph>`_.


Documentation
-------------

`Complete documentation for the project, with detailed instructions on how to build and use it <https://www.brachiograph.art/>`_

Adafruit PCA9685
----------------

Support for `Adafruit PCA9685 servo controller <https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all>`_ has been implemented.

A PCA9685 based Brachiograph can be instantiated this way::

  from brachiograph import BrachioGraph
  bg = BrachioGraph(mode="PCA9685")

Github: https://github.com/adafruit/Adafruit_CircuitPython_PCA9685

Servos
------

The Adafruit PCA9685 mod has been done primarily as an attempt to fix jitter in what apparently are 'bad' servos.
After adapting the code it turned out that such servos would jitter using the PCA9685 controller anyways.
Specifically, the issue was that each movement of an arm servo would cause the arm to shake uncontrollably, until stopped by hand.

Using 'good' servos worked, however they haven't been tested without the controller.

**Bad servos**

- 9g Microservo SG90:

  - Robbe RoVoR S0009 Micro-Servo
  - Velleman Servo VMA600

**Good servos**

- 12g ES08MA:

  - ZHITING
