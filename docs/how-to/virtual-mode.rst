.. _virtual-mode:

How to run a virtual plotter in software
=============================================

If a :class:`~plotter.Plotter` is unable to connect to ``pigpiod`` to communicate with the hardware,
it will revert to virtual mode, in which it behaves as though it had hardware attached,
but doesn't actually attempt to set pulse-widths on the servo motors.


Invoke virtual mode manually
-----------------------------

To force a plotter to run in virtual mode, instantiate it with the ``virtual`` argument, for
example:

.. code-block:: python

    bg = BrachioGraph(virtual=True)

