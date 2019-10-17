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


Eject the card and put it into the Pi and start it up.


Connect to the Pi via OTG USB
-----------------------------

Connect a USB cable to the USB port from your own computer.

After a while, your machine's networking configuration should show the Raspberry Pi. On a Macintosh, it will show up
as ``RNDIS/Ethernet Gadget``.

You should be able to SSH into it::

    ssh pi@raspberrypi.local

The password is ``raspberry``.

But better than using a password is to...


Set up SSH key authentication to the Pi
---------------------------------------

Copy your public key to the Pi so you don't have to log in each time you SSH::

    ssh-copy-id pi@raspberrypi.local


Share your Internet conenction to the Pi
----------------------------------------

On a Macintosh, this is available via the Sharing Preference Pane.

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

    sudo pigpiod && source env/bin/activate && cd BachioGraph && python
