.. _optimise-geometry:

How to optimise your plotter's geometry and drawing area
========================================================

The geometry of the plotter - the length of its arms, the arcs they can sweep through, the relation of those arcs to
other aspects of the machine - and its drawing area are closely related. The former determines the latter.

:ref:`understand_plotter_geometry` will help make clearer the relationship between the two by visualising them.

Optimising the plotter's geometry means designing it so that:

* the length of the arms is suited to the power of the motors and the system's mechanical limitations
* you obtain a drawing area that is useful in both *size* and *shape*
* the movement of the motors to cover that shape is around their *centre positions* (and not at the extremes of their
  sweep), and uses *not too much or too little of their sweep*.

The ``turtle_draw.py`` module will help you do this.


Decide on the length of the arms
--------------------------------

As the arms are made longer, the more power is required to drive them, and the more mechanical limitations of the
system will affect the results (i.e. the more the arms will droop and twist). You will always have to trade off
accuracy and size.

Experience shows that arms of about 8cm work well even with the cheapest of servos, and produce drawings of an adequate
size - 14 x 9cm - which works well on sheets of A5 paper.

The arms don't need to be exactly the same length. See :ref:`understand_plotter_geometry` for examples of how this
makes a difference to the plotter.


Measure the actual arms
-----------------------

Unless you're a very accurate worker, the actual length of each arm is likely to be a little off. Measure these
values (in cm) - we will use them in the next step.


Model your BrachioGraph using ``turtle_draw.py``
------------------------------------------------

The ``turtle_draw.py`` contains a ``BrachioGraphTurtle`` class. The file ``bgt.py`` contains a module with an example
instance of a ``BrachioGraphTurtle``, that you can use in different ways (you may prefer to copy this file and leave
the original untouched).

You can use the class and the example instance:

* as a script, by running ``python bgt.py``, which will execute all the commands in the file
* interactively in a Python shell, executing commands one by one, e.g.::

      >>> from turtle_draw import BrachioGraphTurtle
      >>> bgt = BrachioGraphTurtle(inner_arm=9, shoulder_centre_angle=-45, shoulder_sweep=120, outer_arm=7.5,  elbow_centre_angle=95, elbow_sweep=120)
      >>> bgt.draw_grid()

The examples below will use the script, but you can equally well use the shell to do the same
things.


Draw the model
~~~~~~~~~~~~~~~~~~~~~~~

An example definition is provided in ``bgt.py``. Edit its ``inner_arm`` and ``outer_arm`` values, then run ``python
bgt.py``.


You can choose what to draw by editing the commands in the script:

* a *grid*
* *arcs* representing sweeps of the outer arm for positions within the sweep of the inner arm
* the inner and outer *arms* at various positions within the sweep of the inner arm
* an *outline* of the plotting area

The ``bgt.py`` module draws all of these by default:

.. image:: /images/plotter-geometry/understanding-the-plot.png
   :alt: 'Plotting area'
   :class: 'main-visual'


The grid
^^^^^^^^

Draw a grid with the ``draw_grid()`` method. The grid is based on the dimensions of the plotter at the moment it was
initialised; *although you can can change its arm lengths afterwards, the grid will not reflect this*.


The arcs
^^^^^^^^

Use ``draw_arcs()`` to fill in the drawing area with a series of arcs.


The arms
^^^^^^^^

Use ``draw_arms()`` to show the positions of the arms at various intervals.


The outline
^^^^^^^^^^^^^^^^

``draw_outline()`` will trace an outline of the drawing area.


Discover the optimum configuration for your BrachioGraph
-----------------------------------------------------------

Start by defining your ``BrachioGraphTurtle`` instance with the exact arm lengths you have built, or the ones you
propose to build.

120˚ sweep values for the inner and outer arms are a safe starting-point, along with values of -60˚ and 90˚ for
the inner and outer centre positions respectively (if the arms are of equal length)::

    >>> from turtle_draw import BrachioGraphTurtle
    >>> bgt = BrachioGraphTurtle(inner_arm=8, shoulder_centre_angle=-60, shoulder_sweep=120, outer_arm=8,  elbow_centre_angle=90, elbow_sweep=120)

Draw the grid and an outline::

    >>> bgt.draw_grid()
    >>> bgt.draw_outline()

See :ref:`understand_plotter_geometry` for how to interpret the output.
