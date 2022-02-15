.. _install-software:

Install the software
=====================

``brachiograph.py`` requires a few additional components, and needs to be run in a Python 3 environment, using
Python 3.6 or later.


Install system packages
-----------------------

You may have some of these installed already, but that shouldn't matter.

::

    sudo apt install -y python3-venv pigpiod libjbig0 libjpeg-dev liblcms2-2 libopenjp2-7 libtiff5 libwebp6 libwebpdemux2 libwebpmux3 libzstd1 libatlas3-base libgfortran5 git

The packages include:

* ``venv``, for managing virtual environments under Python 3
* `PIGPIO <http://abyz.me.uk/rpi/pigpio/index.html>`_, an excellent library that provides hardware control of the
  Pi's GPIO pins - important for accurate timing of pulses. It comes with a Python interface to the lower-level code.
* various system libraries required by the Pillow Python imaging library
* ``libatlas3-base`` and ``libgfortran5``, required by the Numpy Python mathematics library
* Git

.. _set-up-venv:

Set up a virtual environment
----------------------------

Create and activate a `Python virtual environment <https://docs.python.org/3/library/venv.html>`_ to work in::

    python3 -m venv env
    source env/bin/activate

You will need to ensure the environment is activated by running ``source env/bin/activate`` - in this directory - if
you return to it later.


Clone the BrachioGraph repository
---------------------------------

Clone the ``BrachioGraph`` repository::

    git clone git@github.com:evildmp/BrachioGraph.git

You will need to have set up a public key using ``ssh-keygen`` and `added your public key to your GitHub account
<https://github.com/settings/ssh/new>`_ for this to work. Or, you can use HTTPS instead::

    git clone https://github.com/evildmp/BrachioGraph.git

Install Python packages
-----------------------

Pinned versions of the Python packages are listed in ``requirements.txt`` in the BrachioGraph directory; install with::

    cd BrachioGraph
    pip install -r requirements.txt

This will install:

* `Numpy <numpy>`_, a Python mathematics library
* PIGPIO's Python library
* `Pillow <http://pillow.readthedocs.io>`_, the most widely-used Python imaging library.
* ``tqdm``, for the progress indicator while drawing
* ``readchar``, to allow the ``BrachioGraph.drive()`` methods to accept user input
