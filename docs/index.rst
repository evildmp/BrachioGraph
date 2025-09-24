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

In this documentation
=====================

* **Tutorial**:
  :doc:`tutorial/wiring` • 
  :doc:`tutorial/power` • 
  :doc:`tutorial/start-plotting` • 
  :doc:`tutorial/basic-improvement` • 
  :doc:`tutorial/sophisticated-calibration`

* **Hardware and design**:
  :doc:`Overview <explanation/hardware>` •
  :doc:`Working with limitations <explanation/hardware-limitations>` •
  :doc:`Visualise servo behaviour <how-to/visualise-servo-behaviour>` •
  :doc:`Alternative building techniques <explanation/alternatives>` •
  :doc:`Build a Pantograph <how-to/pantograph>`

* **Mathematics**:
  :doc:`explanation/geometry` •
  :doc:`explanation/geometric-visualisation`

* **Working with the plotter**:
  :doc:`Raspberry Pi Zero quick-start guide <how-to/prepare-pi>` •
  :doc:`reference/brachiograph` •
  :doc:`Run a virtual plotter <how-to/virtual-mode>`

* **Python turtle plotting**:
  :doc:`how-to/use-turtle-draw` •
  :doc:`reference/turtle-plotter`

* **Image processing**:
  :doc:`Vectorise images <how-to/use-linedraw>` •
  :doc:`linedraw.py reference <reference/linedraw>`

* **Development**:
  :doc:`Build the documentation <how-to/development-documentation>` •
  :doc:`Run automated tests <how-to/development-tests>`



How this documentation is organised
===================================

This documentation uses the `Diátaxis documentation structure <https://diataxis.fr/>`_.

* The :doc:`Tutorial <tutorial/index>` takes you step-by-step through the process of building the machine, installing the software and making your first drawings.

* :doc:`How-to guides <how-to/index>` assume you have basic familiarity with the BrachioGraph. They go deeper into problems and explore things you can do with the system.

* :doc:`Reference <reference/index>` provides a guide to APIs, key classes and functions.

* :doc:`Explanation <explanation/index>` includes topic overviews, background and context and detailed discussion.


From bitmap to plot via vectorisation
=====================================

.. rst-class:: clearfix row

.. image:: /images/anselmo.jpg
   :alt: 'Anselmo'

.. image:: /images/prague2.jpg
   :alt: 'Prague'


.. rst-class:: clearfix row


Community contributions
==========================

BrachioGraph is a hobby project, and I have very limited time to work on it. It means that I don't have the capacity to answer the many questions I get, or even to give due consideration the numerous offers of improvement.

Other people in the open-source community have created their own resources for working with BrachioGraph.

* `brachio.me <https://brachio.me>`_: vectorise images with a web version of ``linedraw``
* `3D printed plotter components <https://www.thingiverse.com/thing:4295302>`_, including arms and stand-offs
* **Video**: `Building a BrachioGraph <https://youtu.be/7hI-9dHqTeg>`_


..  toctree::
    :hidden:

    self
    Tutorial <tutorial/index>
    How-to guides <how-to/index>
    Reference <reference/index>
    Explanation <explanation/index>
