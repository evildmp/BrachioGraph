.. _virtual-mode:

How to run a virtual BrachioGraph in software
=============================================

Sometimes, you might want to run the BrachioGraph class and its methods without actually plotting anything. For
example, you might:

* not have the hardware connected
* not be running it on a Raspberry Pi
* want to run some tests using a 'virtual' plotter

*Virtual mode* makes this possible.

To invoke virtual mode, instantiate your ``BrachioGraph`` with the ``virtual_mode`` argument:

.. code-block:: python
    :emphasize-lines: 3

    bg = BrachioGraph(
       [...]
       virtual_mode=True,
       [...]
       )

Virtual mode will also be set automatically if the ``BrachioGraph`` module runs into an ``ImportError`` when trying
to load the ``pigpio`` library.
