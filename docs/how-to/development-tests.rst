How to run automated tests
==================================

The BrachioGraph library includes a (minimal, at this point) test suite.

The tests use `pytest <https://docs.pytest.org>`.

To run the tests, ``pytest`` needs to be installed (``pip install pytest``).

Executing ``pytest`` in the root directory will run the tests::

    ➜  pytest
    ========================== test session starts ==========================
    platform darwin -- Python 3.7.3, pytest-5.2.4, py-1.8.0, pluggy-0.13.0
    rootdir: /Users/daniele/Repositories/BrachioGraph
    collected 8 items

    test_brachiograph.py ........                                       [100%]
    =========================== 8 passed in 11.02s ===========================

The tests use the BrachioGraph in :ref:`virtual mode <virtual-mode>`.
