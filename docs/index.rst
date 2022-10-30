.. raw:: html

    <style>
        .row {clear: both}
        h2  {border-bottom: 1px solid gray;}

        .column img {border: 1px solid gray;}

        @media only screen and (min-width: 1000px),
               only screen and (min-width: 500px) and (max-width: 768px){

            .column {
                padding-left: 5px;
                padding-right: 5px;
                float: left;
            }

            .column3  {
                width: 33.3%;
            }

            .column2  {
                width: 50%;
            }
        }
    </style>


==========================================================
BrachioGraph - the cheapest, simplest possible pen-plotter
==========================================================

..  raw:: html

    <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-show-count="false">Share on Twitter</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

    <a href="https://twitter.com/BrachioGraph?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="false">Follow @BrachioGraph</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

    <iframe src="https://player.vimeo.com/video/372867891" width="696" height="392" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>


---------------

BrachioGraph - *arm-writer* - is an easy-to-build pen-plotter, driven by a library of simple Python applications.

A BrachioGraph can be built for about €15 in an hour or so, using a Raspberry Pi computer, hobby servo motors and
household items. The `BrachioGraph library <https://github.com/evildmp/brachiograph>`_ is published on GitHub and
includes simple Python code to drive the plotter and vectorise bit-map images.

BrachioGraph plots cheerful, low-fi drawings, and can produce robotic sketches using a variety of drawing implements.

Contents
------------

:doc:`Tutorial <tutorial/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Start here**: build the machine, install the software, make your first drawings


:doc:`How-to guides <how-to/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Improve the calibration, process images, visualise plotter behaviour, alternative designs


:doc:`Explanation <explanation/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understanding the mathematics, choosing hardware.


:doc:`Reference <reference/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Guide to key classes and functions




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

BrachioGraphs benefits from contributions from the open-source community, and independently-created :ref:`community
resources <community-resources>`. These include videos, `brachio.me <https://brachio.me>`_, a web version of the
linedraw software used to vectorise images and `3D printed plotter components
<https://www.thingiverse.com/thing:4295302>`_.


About the documentation
-----------------------

This documentation uses the `Diátaxis documentation structure <https://diataxis.fr/>`_


.. toctree::
    :maxdepth: 1
    :hidden:

    Tutorial <tutorial/index>
    How-to guides <how-to/index>
    Reference <reference/index>
    Explanation <explanation/index>
