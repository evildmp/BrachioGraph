.. _prepare-pi:

How to prepare a Raspberry Pi Zero to drive the plotter
========================================================

The Raspberry Pi Zero is ideal as the engine for the plotter, but can present a few challenges. Here's a recipe
for a quick set-up.

Download the latest Raspbian Lite (minimal image) from the `Raspbian downloads page <https://www.raspberrypi.org/downloads/raspbian>`_.

Do whatever needs to be done to put it onto a micro SD card using your machine.

The SD card should have a ``boot`` volume. Create a file called ``ssh`` at the root (this enables ssh access).

Edit ``config.txt``, adding::

     dtoverlay=dwc2

to a new line at the end.

Edit ``cmdline.txt``, adding::

    modules-load=dwc2,g_ether

just after ``rootwait``.

These two changes enable OTG Ethernet access (Ethernet over USB to the Raspberry Pi).

Eject the card and put it into the Pi and start it up.

Connect a USB cable to the USB port from your own computer.

After a while, your machine's networking configuration should show the Raspberry Pi. On a Macintosh, it will show up
as ``RNDIS/Ethernet Gadget``.

You should be able to shh into it::

    ssh pi@raspberrypi.local

The password is ``raspberry``.

Run::

    sudo apt-get update && apt-get -y upgrade

to update the software.

::

    sudo apt-get install pigpio python3-pip git

::

    sudo pip3 install virtualenv

(if you care enough to use a virtualenv...)

Copy your public key to the Pi so you don't have to log in each time you SSH::

    ssh-copy-id  pi@raspberrypi.local

Install netatalk, to make working on the Pi easier::

     sudo apt-get install netatalk
