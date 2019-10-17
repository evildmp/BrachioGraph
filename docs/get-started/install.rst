.. _install-software:

Install the software
=====================

See also :ref:`prepare-pi`, which gives step-by-step directions specifically for using a Pi Zero as the plotter engine.

``brachiograph.py`` requires a few additional components. It's recommended to use a virtualenv for the Python
packages; either way, make sure you are in a Python 3 environment.


Pip
---

If not already installed::

    sudo apt-get install python3-pip


Convenience software (optional but recommended)
-----------------------------------------------

virtualenv
~~~~~~~~~~

Install virtualenv::

    pip install virtualenv

... and then create a virtualenv to work in::

    virtualenv env
    source env/bin/activate


tmux
~~~~

`tmux <https://thoughtbot.com/blog/a-tmux-crash-course>`_ is a very handy way of managing terminal sessions, so that
even if your connection is broken, you can re-join the session without losing your place.

Install with::

    sudo apt-get install tmux


PIGPIO
------

`PIGPIO <http://abyz.me.uk/rpi/pigpio/index.html>`_ is an excellent library that provides hardware control
of the Pi's GPIO pins - important for accurate timing of pulses. It comes with a Python interface to the
lower-level code.

::

    sudo apt-get install pigpiod
    pip install pigpio


Pillow
------

`Pillow <http://pillow.readthedocs.io>`_ is a Python imaging library. You'll need it to process convert bitmap images
to vectors, but it's not required to drive the plotter.

Install the required system libraries (listed at https://www.piwheels.org/project/Pillow/), followed by
Pillow itself::

    sudo apt install libwebp6 libtiff5 libjbig0 liblcms2-2 libwebpmux3 libopenjp2-7 libzstd1 libwebpdemux2
    pip install pillow


Numpy
-----

`Numpy <numpy>`_ is a Python mathematics library.

Install the required system libraries (listed at https://www.piwheels.org/project/numpy/), followed by
Numpy itself::

    sudo apt install libatlas3-base libgfortran5
    sudo pip3 install numpy


Git
---

If not already installed::

    sudo apt-get install git


Other Python packages
---------------------

Use pip to install Python 3 versions of:

* ``tqdm``      # for the progress indicator while drawing
* ``readchar``  # to allow the ``BrachioGraph.drive()`` methods to accept user input


Clone the BrachioGraph repository
---------------------------------

If you haven't already done so, clone the ``BrachioGraph`` repository::

    git clone git@github.com:evildmp/BrachioGraph.git

or, if you need to use HTTPS instead::

    git clone https://github.com/evildmp/BrachioGraph.git
