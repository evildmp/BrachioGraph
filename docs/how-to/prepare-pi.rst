.. _prepare-pi:

How to prepare a Raspberry Pi Zero to drive the plotter
========================================================

The Raspberry Pi Zero is ideal as the engine for the plotter. Here's a recipe for a quick set-up, from scratch.

Download the latest Raspbian Lite (minimal image) from the `Raspbian downloads page
<https://www.raspberrypi.org/downloads/raspbian>`_.

Do whatever `needs to be done
<https://www.raspberrypi.org/documentation/installation/installing-images/>`_ to put it onto a micro SD card.


Enable SSH and OTG Ethernet access
----------------------------------

SSH access
~~~~~~~~~~

The SD card should have a ``boot`` volume. Create a file called ``ssh`` at the root.


OTG Ethernet access
~~~~~~~~~~~~~~~~~~~

"On-the-go" power/Ethernet connectivity allows you to power a Raspberry Pi Zero, and connect to it via Ethernet over
USB, on the same port (the Pi's USB port).

Edit ``config.txt``, adding::

   dtoverlay=dwc2

to a new line at the end.

Edit ``cmdline.txt``, adding::

    modules-load=dwc2,g_ether

just after ``rootwait``.


Set a fixed MAC address
^^^^^^^^^^^^^^^^^^^^^^^

By default, the Pi will generate a new MAC address and appear as a new device to the host each time
it reboots, which is annoying.

To fix the address, add a file ``/etc/modprobe.d/rndis.conf``. In it, add::

    options g_ether host_addr=ae:ad:f5:9d:9f:ba dev_addr=7a:26:9f:3e:97:6c

See `How can I make a Pi Zero appear as the same RNDIS/Ethernet Gadget device to the host OS each time it restarts?
<https://raspberrypi.stackexchange.com/a/104749/42583>`_ on StackExchange for more information.


Eject the card and put it into the Pi and start it up.


Connect to the Pi via OTG USB
-----------------------------

Connect a USB cable to the USB port (marked *USB*, not to be confused with the *PWR* port next to it) from your own
computer. This will provide power *and* establish an Ethernet connection to the Pi.

After a while, your machine's networking configuration should show the Raspberry Pi.

Macintosh: the Pi will appear as ``RNDIS/Ethernet Gadget`` (you can rename this).

Ubuntu: the Pi will show up as an ethernet device named ``Wired connection #``

You should be able to SSH into it::

    ssh pi@raspberrypi.local

The password is ``raspberry``.

But better than using a password is to...


Set up SSH key authentication to the Pi
---------------------------------------

Copy your public key to the Pi so you don't have to log in each time you SSH::

    ssh-copy-id pi@raspberrypi.local


Share your Internet connection to the Pi
----------------------------------------

Macintosh: this is available via the Sharing Preference Pane.

Ubuntu: go to the `IPv4 Settings` networking configuration tab, and set the method to `Shared to other computers`.

Check that you can ping an external site from the Pi.


Update everything
-----------------

Run::

    sudo apt-get update
    sudo apt-get -y upgrade

to update the software.

This will take a while.


Install key software components
-------------------------------

Refer to the :ref:`install-software` section.


Add a pin header
----------------

If you don't already have them, you will need a GPIO (general-purpose input/output) pin header
to connect the Raspberry Pi to the jumper wires that will connect to the servo motors.
Different pin headers are available that can be snapped or soldered into place.


Start it all up
---------------

::

    sudo pigpiod && source env/bin/activate && cd BrachioGraph && python
