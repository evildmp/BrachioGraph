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


BrachioGraph - the cheapest, simplest possible pen-plotter
==========================================================

..  raw:: html

    <iframe src="https://player.vimeo.com/video/372867891" width="696" height="392" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>

BrachioGraph - *arm-writer* - is an easy-to-build pen-plotter, driven by a library of simple Python applications.


.. raw:: html

    <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-show-count="false">Tweet</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

    <a href="https://twitter.com/BrachioGraph?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="false">Follow @BrachioGraph</a><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

---------------

A BrachioGraph can be built in an hour or so without any special skills. The total cost of all components can be as low
as €15 or so. Apart from a Raspberry Pi computer and some hobby servo motors, the plotter can be built with everyday
household items such as a clothes-peg. The software in the `BrachioGraph <https://github.com/evildmp/BrachioGraph>`_
library includes code to :ref:`drive the hardware <start-plotting>` and :ref:`vectorise bit-map images <use-linedraw>`.

BrachioGraphs benefits from contributions from the open-source community, and independently-created :ref:`community
resources <community-resources>`. These include videos, `brachio.me <https://brachio.me>`_, a web version of the
linedraw software used to vectorise images and `3D printed plotter components
<https://www.thingiverse.com/thing:4295302>`_.

.. rst-class:: clearfix row

From bitmap to plot via vectorisation
-------------------------------------

.. rst-class:: clearfix row

.. image:: /images/anselmo.jpg
   :alt: 'Anselmo'

.. image:: /images/prague2.jpg
   :alt: 'Prague'


Contents
------------

.. rst-class:: clearfix row

.. rst-class:: column column2

:doc:`Get started <get-started/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build the machine, install the software, make basic tests

.. rst-class:: column column2

:doc:`How-to guides <how-to/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Improve the calibration, process images, visualise plotter behaviour, alternative designs

.. rst-class:: clearfix row

.. rst-class:: column column2

:doc:`Explanation <explanation/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understanding the mathematics, choosing hardware.

.. rst-class:: column column2

:doc:`Reference <reference/index>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Guide to key classes and functions


.. rst-class:: clearfix row

About the documentation
~~~~~~~~~~~~~~~~~~~~~~~

This documentation uses the `Diátaxis documentation structure <https://diataxis.fr/>`_


.. toctree::
    :maxdepth: 1
    :hidden:

    Get started <get-started/index>
    How-to guides <how-to/index>
    Reference <reference/index>
    Explanation <explanation/index>
