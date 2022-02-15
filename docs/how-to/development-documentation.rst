How to build the documentation
==================================

The BrachioGraph documentation is intended to be of the highest possible quality. This is important for any project,
and especially crucial in one with an educational purpose.


The basics
----------

The documentation is written in `Restructured Text
<https://docutils.readthedocs.io/en/sphinx-docs/user/rst/quickstart.html>`_, built with `Sphinx
<https://www.sphinx-doc.org/en/master/>`_ and hosted at `Read the Docs <https://readthedocs.com>`_.

The documentation uses the `Diátaxis framework <https://diataxis.fr>`_:

* :doc:`tutorials </get-started/index>`
* :doc:`how-to guides </how-to/index>`
* :doc:`reference material </reference/index>`
* :doc:`explanation </explanation/index>`

from each other.

Please keep that in mind when contributing any new documentation.


Working with the documentation locally
--------------------------------------

Install the required software
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build the documentation locally, ``cd`` into the ``docs`` directory and run::

    make install

to install the required components into a new virtualenv.


Build the documentation
~~~~~~~~~~~~~~~~~~~~~~~

You can then execute::

    make run

and you'll find the documentation built at http://localhost:8004 (the port is set in ``docs/Makefile``). The builder
watches the documentation directory, so any saved changes will be immediately built.

Another option is to use::

    make html

which will save the published HTML to ``docs/_build/html``.

To run a spelling check::

    make spelling


Contributing to the documentation
---------------------------------

Documentation improvements and corrections can be submitted as pull requests.

Please check spelling, as described above. Any special words should be added to ``docs/spelling_wordlist``. The
documentation uses British English spelling.
