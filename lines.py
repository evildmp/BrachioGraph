import math
import json


class LinesMixin:

    # filename, lines, bounds, angular_step, wait, resolution, draw, repeat, reverse, both, flip, rotate


    #  ----------------- plotting methods -----------------

    def plot_file(
        self, 
        filename="", 
        bounds=None, 
        angular_step=None, 
        wait=None, 
        resolution=None,
        flip=False, 
        rotate=False,
        ):
        """Plots an image encoded as JSON lines in ``filename``. Passes the lines in the supplied
        JSON file to ``plot_lines()``.
        """

        with open(filename, "r") as line_file:
            lines = json.load(line_file)
        self.plot_lines(lines, bounds, angular_step, wait, resolution, flip, rotate) 

    def plot_lines(
        self,
        lines=[],
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        flip=False,
        rotate=False,
    ):
        """Passes each segment of each line in lines to ``draw_line()``"""

        lines = self.process_lines(lines, bounds, flip, rotate)

        for line in lines:
            x, y = line[0]

            # only if we are not within 1mm of the start of the line, lift pen and go there
            if (round(self.x, 1), round(self.y, 1)) != (round(x, 1), round(y, 1)):
                self.xy(x, y, angular_step, wait, resolution)

            for point in line[1:]:
                x, y = point
                self.xy(x, y, angular_step, wait, resolution, draw=True)

        self.park()
    
    #  ----------------- x/y drawing methods -----------------

    def draw_line(
        self, start=(0, 0), end=(0, 0), angular_step=None, wait=None, resolution=None, both=False
    ):
        """Draws a line between two points"""

        start_x, start_y = start
        end_x, end_y = end

        self.xy(start_x, start_y, angular_step, wait, resolution)
        self.xy(end_x, end_y, angular_step, wait, resolution, draw=True)
        if both:
            self.xy(start_x, start_y, angular_step, wait, resolution, draw=True)

    def xy(self, x=None, y=None, angular_step=None, wait=None, resolution=None, draw=False):
        """Moves the pen to the xy position; optionally draws while doing it. ``None`` for x or y
        means that the pen will not be moved in that dimension.
        """

        resolution = resolution or self.resolution

        x = x if x is not None else self.x
        y = y if y is not None else self.y
        (angle_1, angle_2) = self.xy_to_angles(x, y)

        if draw:

            # calculate how many steps we need for this move, and the x/y length of each
            (x_length, y_length) = (x - self.x, y - self.y)

            length = math.sqrt(x_length**2 + y_length**2)

            no_of_steps = round(length / resolution) or 1

            (length_of_step_x, length_of_step_y) = (x_length / no_of_steps, y_length / no_of_steps)

            for step in range(no_of_steps):

                self.x = self.x + length_of_step_x
                self.y = self.y + length_of_step_y

                angle_1, angle_2 = self.xy_to_angles(self.x, self.y)
                self.move_angles(angle_1, angle_2, angular_step, wait, draw)

        else:
            self.move_angles(angle_1, angle_2, angular_step, wait, draw)
            

    # ----------------- line-processing methods -----------------

    def process_lines(self, lines=[], bounds=None, flip=False, rotate=False):
        """Rotates and scales the lines so that they best fit the available drawing ``bounds``."""

        # get all the x and y values from the lines
        x_values = y_values = set()
        for line in lines:
            xs, ys = zip(*line)
            x_values.update(xs)
            y_values.update(ys)

        source_bounds = (min(x_values), min(y_values), max(x_values), max(y_values))
        target_bounds = bounds or self.bounds 

        rotate, x_mid, y_mid, box_x_mid, box_y_mid, divider = self.map_source_to_target(
            source_bounds, target_bounds, rotate
            )

        for line in lines:
            for point in line:
                point[0], point[1] = self.translate_point(
                    point, 
                    x_mid, 
                    y_mid, 
                    box_x_mid, 
                    box_y_mid, 
                    divider, 
                    flip, 
                    rotate)
        return lines

    def map_source_to_target(self, source_bounds, target_bounds, rotate=False):
        """
        Analyses the co-ordinates in ``lines``, and returns:

        * ``rotate``: ``True`` if the image needs to be rotated by 90˚ in order to fit better
        * ``x_mid_point``, ``y_mid_point``: mid-points of the image
        * ``box_x_mid_point``, ``box_y_mid_point``: mid-points of the ``bounds``
        * ``divider``: the value by which we must divide all x and y so that they will fit safely
          inside the bounds.

        ``lines`` is a tuple itself containing a number of tuples, each of which contains a number
        of 2-tuples::

            [
                [
                    [3, 4],                               # |
                    [2, 4],                               # |
                    [1, 5],  #  a single point in a line  # |  a list of points defining a line
                    [3, 5],                               # |
                    [3, 7],                               # |
                ],
                [            #  all the lines
                    [...],
                    [...],
                ],
                [
                    [...],
                    [...],
                ],
            ]
        """

        # Find the min/max x and y values amongst all the points, and their ranges and mid-points

        source_x_range = abs(source_bounds[2] - source_bounds[0]) 
        source_y_range = abs(source_bounds[3] - source_bounds[1])
        source_x_mid = (source_bounds[0] + source_bounds[2]) / 2 
        source_y_mid = (source_bounds[1] + source_bounds[3]) / 2

        target_x_range = abs(target_bounds[2] - target_bounds[0]) 
        target_y_range = abs(target_bounds[3] - target_bounds[1])
        target_x_mid = (target_bounds[0] + target_bounds[2]) / 2 
        target_y_mid = (target_bounds[1] + target_bounds[3]) / 2

        # Get a 'divider' value for each range - the value by which we must divide all x and y so
        # that they will fit safely inside the bounds.

        # If both image and box are in portrait orientation, or both in landscape, we don't need to
        # rotate the plot.

        if (source_x_range / source_y_range - 1) * (target_x_range / target_y_range - 1) >= 0:

            divider = 10 ** max(
                abs(math.log10(source_x_range / target_x_range)), 
                abs(math.log10(source_y_range / target_y_range))
            )
            rotate = False
            divider = 1 / divider

        else:

            divider = 10 ** max(
                abs(math.log10(source_x_range / target_y_range)), 
                abs(math.log10(source_y_range / target_x_range))
            )
            divider = 1 / divider
            rotate = True
            source_x_mid, source_y_mid = source_y_mid, source_x_mid

        return (rotate, source_x_mid, source_y_mid, target_x_mid, target_y_mid, divider)


    def translate_point(self, point, source_x_mid, source_y_mid, target_x_mid, target_y_mid, divider, flip, rotate):
        if not rotate:
            x, y = point
        else:
            y, x = point

        x = x - source_x_mid  # shift x values so that they have zero as their mid-point
        x = x / divider  # scale x values to fit in our box width

        if flip ^ rotate:  # flip before moving back into drawing pane
            x = -x
        # shift x values so that they have the box x midpoint as their endpoint
        x = x + target_x_mid

        point = (x, target_y_mid + (y - source_y_mid) / divider)
        return point
    