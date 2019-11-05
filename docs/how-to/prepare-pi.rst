.. _prepare-pi:

How to prepare a Raspberry Pi Zero to drive the plotter
========================================================

The Raspberry Pi Zero is ideal as the engine for the plotter. Here's a recipe for a quick set-up, from scratch.

Download the latest Raspbian Lite (minimal image) from the `Raspbian downloads page
<https://www.raspberrypi.org/downloads/raspbian>`_.

Do whatever needs to be done to put it onto a micro SD card.


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

By default, the Pi will generate a new MAC addresss and appear as a new device to the host each time
it reboots, which is annoying.

To fix the address, add a file ``/etc/modprobe.d/rndis.conf``. In it, add::

    options g_ether host_addr=ae:ad:f5:9d:9f:ba dev_addr=7a:26:9f:3e:97:6c

See `How can I make a Pi Zero appear as the same RNDIS/Ethernet Gadget device to the host OS each time it restarts?
<https://raspberrypi.stackexchange.com/a/104749/42583>`_ on StackExchange for more information.


Eject the card and put it into the Pi and start it up.


Connect to the Pi via OTG USB
-----------------------------

Connect a USB cable to the USB port from your own computer, using the center most usb port on the Raspberry Pi.

After a while, your machine's networking configuration should show the Raspberry Pi. On a Macintosh, it will show up
as ``RNDIS/Ethernet Gadget``. On Ubuntu it will show up as an ethernet device named "Wired connection #", and you will need to go into the `IPv4 Settings` configuration tab and set the method to `Shared to other computers`.

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

On a Macintosh, this is available via the Sharing Preference Pane.

On Ubuntu this was taken care of earlier with the `Shared to other computers` setting.

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


Start it all up
---------------

::

    sudo pigpiod && source env/bin/activate && cd BrachioGraph && python
