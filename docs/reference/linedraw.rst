``linedraw.py``
===================

.. _vectorise:

``vectorise()``
---------------

::

    def vectorise(
        image_filename,
        resolution=1024,
        draw_contours=False,  # suggested value: 2
        repeat_contours=1,    # increase to draw the contours multiple times
        draw_hatch=False,     # suggested value: 16
        repeat_contours=1,    # increase to draw the hatching multiple times
        ):

* ``image_filename``:  all images are expected to be found in the ``images`` directory
* ``resolution``: the number of points that will be processed across the largest dimension of the image - larger is
  more detailed, but slower - and you're unlikely to find that the resolution of the plotter itself merits increasing
  this value
* ``draw_contours``: find and draw outlines, using the value provided (smaller is more detailed, and slower)
* ``repeat_contours``: how many times should the contours be drawn?
* ``draw_hatch``: hatch (shade) the processed image, using the value provided (smaller is more detailed, and slower).
* ``repeat_contours``: how many times should the hatching be drawn?

At least one of ``draw_hatch`` and ``draw_contours`` must be given otherwise nothing will be drawn.

``vectorise`` returns a list of ``lines``, each of which is a list of points. It also creates an SVG file at ``images/<image_filename>.svg``, to give you an idea of the vectorised version.


``image_to_json()``
-------------------

``image_to_json()`` takes the same parameters, but saves the result as a JSON file.

``image_to_json("africa.jpg", draw_hatch=16, draw_contours=2)`` will save a file at ``images/africa.jpg.json`` (and
also creates an SVG file, at ``images/africa.jpg.svg``).
