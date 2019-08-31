The hardware
------------

The Raspberry Pi
~~~~~~~~~~~~~~~~

A Raspberry Pi Zero is perfectly adequate to control and power the servos. The Pi can be connected to a host by USB,
using the OTG mode (RNDIS), and powered that way, along with all three servos - but this arrangement is not wholly
reliable and you may find that the machine occasionally reboots, because of lack of power. A separate power supply for
the Pi is much more reliable.


The servo motors
~~~~~~~~~~~~~~~~

`SG90 motors <http://www.towerpro.com.tw/product/sg90-analog/>`_ are ideal. They are extremely cheap (though beware of
even cheaper counterfeits) and perfectly adequate.

More powerful and more accurate motors will give you better results.

SG90 motors are **analog**, and use a small circuit to convert the pulse-widths into motor angles. **Digital** servo
motors also exist; they tend to be faster and more powerful. However, *small digital motors do not work well*. They are
twitchy and try to correct for errors much faster than analog motors. This means that in a mechanism such as this, they
quickly start oscillating wildly, as each movement overshoots and corrects (this is made worse by having two motors
affecting each other).


The cardboard
~~~~~~~~~~~~~

The card for the arms (and the base) needs to be stiff in both directions. Picture-mounting board is ideal. A
picture-framing shop will almost certainly give you free off-cuts.
