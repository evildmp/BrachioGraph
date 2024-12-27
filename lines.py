import math
import json
import tqdm


class LinesMixin:

    #  ----------------- plotting methods -----------------

    def plot_file(self, filename="", bounds=None, angular_step=None, wait=None, resolution=None):
        """Plots and image encoded as JSON lines in ``filename``. Passes the lines in the supplied
        JSON file to ``plot_lines()``.
        """

        bounds = bounds or self.bounds

        with open(filename, "r") as line_file:
            lines = json.load(line_file)

        self.plot_lines(lines, bounds, angular_step, wait, resolution, flip=True)

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

        bounds = bounds or self.bounds

        lines = self.rotate_and_scale_lines(lines=lines, bounds=bounds, flip=True)

        for line in tqdm.tqdm(lines, desc="Lines", leave=False):
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

        wait = wait if wait is not None else self.wait
        resolution = resolution or self.resolution

        x = x if x is not None else self.x
        y = y if y is not None else self.y
        (angle_1, angle_2) = self.xy_to_angles(x, y)

        if draw:

            # calculate how many steps we need for this move, and the x/y length of each
            (x_length, y_length) = (x - self.x, y - self.y)

            length = math.sqrt(x_length**2 + y_length**2)

            no_of_steps = round(length / resolution) or 1

            if no_of_steps < 100:
                disable_tqdm = True
            else:
                disable_tqdm = False

            (length_of_step_x, length_of_step_y) = (x_length / no_of_steps, y_length / no_of_steps)

            for step in range(no_of_steps):

                self.x = self.x + length_of_step_x
                self.y = self.y + length_of_step_y

                angle_1, angle_2 = self.xy_to_angles(self.x, self.y)
                self.move_angles(angle_1, angle_2, angular_step, wait, draw)

        else:
            self.move_angles(angle_1, angle_2, angular_step, wait, draw)
            
    # ----------------- line-processing methods -----------------

    def rotate_and_scale_lines(self, lines=[], rotate=False, flip=False, bounds=None):
        """Rotates and scales the lines so that they best fit the available drawing ``bounds``."""
        (
            rotate,
            x_mid_point,
            y_mid_point,
            box_x_mid_point,
            box_y_mid_point,
            divider,
        ) = self.analyse_lines(lines, rotate, bounds)

        for line in lines:

            for point in line:
                if rotate:
                    point[0], point[1] = point[1], point[0]

                x = point[0]
                x = x - x_mid_point  # shift x values so that they have zero as their mid-point
                x = x / divider  # scale x values to fit in our box width

                if flip ^ rotate:  # flip before moving back into drawing pane
                    x = -x

                # shift x values so that they have the box x midpoint as their endpoint
                x = x + box_x_mid_point

                y = point[1]
                y = y - y_mid_point
                y = y / divider
                y = y + box_y_mid_point

                point[0], point[1] = x, y

        return lines

    def analyse_lines(self, lines=[], rotate=False, bounds=None):
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

        bounds = bounds or self.bounds

        # First, we create a pair of empty sets for all the x and y values in all of the lines of
        # the plot data.

        x_values_in_lines = set()
        y_values_in_lines = set()

        # Loop over each line and all the points in each line, to get sets of all the x and y
        # values:

        for line in lines:

            x_values_in_line, y_values_in_line = zip(*line)

            x_values_in_lines.update(x_values_in_line)
            y_values_in_lines.update(y_values_in_line)

        # Identify the minimum and maximum values.

        min_x, max_x = min(x_values_in_lines), max(x_values_in_lines)
        min_y, max_y = min(y_values_in_lines), max(y_values_in_lines)

        # Identify the range they span.

        x_range, y_range = max_x - min_x, max_y - min_y
        box_x_range, box_y_range = bounds[2] - bounds[0], bounds[3] - bounds[1]

        # And their mid-points.

        x_mid_point, y_mid_point = (max_x + min_x) / 2, (max_y + min_y) / 2
        box_x_mid_point, box_y_mid_point = (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2

        # Get a 'divider' value for each range - the value by which we must divide all x and y so
        # that they will fit safely inside the bounds.

        # If both image and box are in portrait orientation, or both in landscape, we don't need to
        # rotate the plot.

        if (x_range >= y_range and box_x_range >= box_y_range) or (
            x_range <= y_range and box_x_range <= box_y_range
        ):

            divider = max((x_range / box_x_range), (y_range / box_y_range))
            rotate = False

        else:

            divider = max((x_range / box_y_range), (y_range / box_x_range))
            rotate = True
            x_mid_point, y_mid_point = y_mid_point, x_mid_point

        return (rotate, x_mid_point, y_mid_point, box_x_mid_point, box_y_mid_point, divider)