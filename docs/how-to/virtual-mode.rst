.. _virtual-mode:

How to run a virtual plotter in software
=============================================

In virtual mode, a :class:`~plotter.Plotter` behaves as though it had hardware attached,
but doesn't actually attempt to set pulse-widths on the servo motors.  

If a :class:`~plotter.Plotter` is unable to connect to ``pigpiod`` to communicate with the hardware,
it will revert to virtual mode automatically.

It's also possible to force a plotter to run in virtual mode, by instantiating it with the 
``virtual`` argument, for example:

.. code-block:: python

    bg = BrachioGraph(virtual=True)

Whether or not the plotter runs in virtual mode, it's also possible to use Python's turtle graphics to 
run a graphical turtle on-screen to represent the physical behaviour, with the ``turtle`` argument::

    bg = BrachioGraph(turtle=True)

