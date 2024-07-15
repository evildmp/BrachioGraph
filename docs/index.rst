==========================================================
BrachioGraph
==========================================================

..  rubric:: The world's cheapest, simplest possible pen-plotter.


..  raw:: html

    <iframe src="https://player.vimeo.com/video/372867891" width="696" height="392" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>


---------------

BrachioGraph - *arm-writer* - is an easy-to-build pen-plotter, driven by a library of simple Python applications.

BrachioGraph plots cheerful, low-fi drawings, and can produce robotic sketches using a variety of drawing implements.

A BrachioGraph can be built for about €15 in an hour or so, using a Raspberry Pi computer, hobby servo motors and
household items. The `BrachioGraph library <https://github.com/evildmp/brachiograph>`_ is published on GitHub and
includes simple Python code to drive the plotter and vectorise bit-map images.


Contents
------------

..  grid:: 1 1 2 2

   ..  grid-item:: :doc:`Tutorial <tutorial/index>`

       **Start here**: build the machine, install the software, make your first drawings

   ..  grid-item:: :doc:`How-to guides <how-to/index>`

      Improve the calibration, process images, visualise plotter behaviour, build alternative designs

.. grid:: 1 1 2 2
   :reverse:

   .. grid-item:: :doc:`Reference <reference/index>`

      Guide to key classes and functions

   .. grid-item:: :doc:`Explanation <explanation/index>`

      Understanding the mathematics, choosing hardware


From bitmap to plot via vectorisation
-------------------------------------

.. rst-class:: clearfix row

.. image:: /images/anselmo.jpg
   :alt: 'Anselmo'

.. image:: /images/prague2.jpg
   :alt: 'Prague'




.. rst-class:: clearfix row


The BrachioGraph community
--------------------------

BrachioGraph benefits from contributions from the open-source community, and independently-created :ref:`community
resources <community-resources>`. These include videos, `brachio.me <https://brachio.me>`_, a web version of the
linedraw software used to vectorise images and `3D printed plotter components
<https://www.thingiverse.com/thing:4295302>`_.


About the documentation
-----------------------

This documentation uses the `Diátaxis documentation structure <https://diataxis.fr/>`_


.. toctree::
    :maxdepth: 1
    :hidden:

    self
    Tutorial <tutorial/index>
    How-to guides <how-to/index>
    Reference <reference/index>
    Explanation <explanation/index>
