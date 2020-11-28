.. _hardware:

The hardware
------------

.. _hardware-pi:

The Raspberry Pi
~~~~~~~~~~~~~~~~

A Raspberry Pi Zero is perfectly adequate to control and power the servos. The Pi can be connected to a host by USB,
using the OTG mode (RNDIS), and powered that way, along with all three servos. :ref:`A guide specifically for setting
up a Pi Zero <prepare-pi>` is included.

When using OTG power with larger servos, you may find that the machine occasionally reboots, because of lack of power.
A separate power supply for the Pi will be more reliable.


.. _hardware-servos:

The servo motors
~~~~~~~~~~~~~~~~

..  important:: Read :ref:`digital-motors`, below.

There are basically two kinds of servos:

* fixed-range; you can control their position
* continuous rotation (sometimes described as 360-degree); you can control their speed

You need fixed-range servos. About 180 degrees of rotation is fine. You can do with less - but the drawing area will
be smaller.


Servos for the arms
^^^^^^^^^^^^^^^^^^^

"Micro" servos or "9g [i.e. gramme]" models are fine.

* `SG90 analog motors <http://www.towerpro.com.tw/product/sg90-analog/>`_ are ideal to get started with. There are many
  motors from different manufacturers in this class, that weigh about 9g and have approximately 180 degrees rotation.
* *Futaba S3001* motors, which are larger, more powerful and more accurate, worked well and produced even better
  results.
* *Miuzei SG90 9G* is another small cheap model that has performed well.

Note that while more powerful motors produce better results, they will also draw more current and your
Raspberry Pi may struggle to meet the demand.


Servos for the pen
^^^^^^^^^^^^^^^^^^

For the pen-lifting servo, the lighter and smaller the better ("sub-micro" servos are available). Power and accuracy
are not required.

.. _digital-motors:

Why more expensive digital motors are worse
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SG90 motors are **analog**. Analog motors use a small circuit to convert the pulse-widths into motor angles.
**Digital** servo motors also exist, including digital versions of the SG90; they tend to be faster and more powerful.

However, *small digital motors do not work well*, for example the TowerPro SG92R. They are twitchy and try to correct
for errors much faster than analog motors. This means that in a mechanism such as this, they quickly start oscillating
wildly, as each movement overshoots and corrects (this is made worse by having two motors affecting each other).

More powerful digital servo motors have not been tested. `Please share your experiences using other motors
<https://github.com/evildmp/BrachioGraph/issues/31>`_.


Beware of fakes
^^^^^^^^^^^^^^^

Counterfeit motors are very common. Many of the motors sold as Tower Pro SG90 are in fact fakes. They are cheaper and
of lower quality. If motors sold as SG90s are priced below €3 or $3 each, they are probably fake. It's recommended to
buy them from a reputable retailer rather from than Amazon or eBay.


.. _hardware-arms:

The arms
~~~~~~~~~~~~~

If you're using card for the arms, it needs to be stiff in both directions. Picture-mounting board is ideal. A
picture-framing shop will almost certainly give you free off-cuts.

:ref:`Wooden sticks as illustrated <get_started>` don't require cutting and are easy to obtain.
