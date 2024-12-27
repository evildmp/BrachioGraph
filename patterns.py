import tqdm


class PatternsMixin:

    #  ----------------- pattern-drawing methods -----------------

    def box(
        self, bounds=None, angular_step=None, wait=None, resolution=None, repeat=1, reverse=False
    ):
        """Draw a box marked out by the ``bounds``."""

        bounds = bounds or self.bounds

        if not bounds:
            return "Box drawing is only possible when the bounds attribute is set."

        self.xy(bounds[0], bounds[1], angular_step, wait, resolution)

        for r in tqdm.tqdm(tqdm.trange(repeat), desc="Iteration", leave=False):

            if not reverse:

                self.xy(bounds[2], bounds[1], angular_step, wait, resolution, draw=True)
                self.xy(bounds[2], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[0], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[0], bounds[1], angular_step, wait, resolution, draw=True)

            else:

                self.xy(bounds[0], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[2], bounds[3], angular_step, wait, resolution, draw=True)
                self.xy(bounds[2], bounds[1], angular_step, wait, resolution, draw=True)
                self.xy(bounds[0], bounds[1], angular_step, wait, resolution, draw=True)

        self.park()

    def test_pattern(
        self,
        lines=4,
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        self.vertical_lines(lines, bounds, angular_step, wait, resolution, repeat, reverse, both)
        self.horizontal_lines(lines, bounds, angular_step, wait, resolution, repeat, reverse, both)

    def vertical_lines(
        self,
        lines=4,
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when the bounds attribute is set."

        if not reverse:
            top_y = self.top
            bottom_y = self.bottom
        else:
            bottom_y = self.top
            top_y = self.bottom

        for n in range(repeat):
            step = (self.right - self.left) / lines
            x = self.left
            while x <= self.right:
                self.draw_line((x, top_y), (x, bottom_y), angular_step, wait, resolution, both)
                x = x + step

        self.park()

    def horizontal_lines(
        self,
        lines=4,
        bounds=None,
        angular_step=None,
        wait=None,
        resolution=None,
        repeat=1,
        reverse=False,
        both=False,
    ):

        bounds = bounds or self.bounds

        if not bounds:
            return "Plotting a test pattern is only possible when the bounds attribute is set."

        if not reverse:
            min_x = self.left
            max_x = self.right
        else:
            max_x = self.left
            min_x = self.right

        for n in range(repeat):
            step = (self.bottom - self.top) / lines
            y = self.top
            while y >= self.bottom:
                self.draw_line((min_x, y), (max_x, y), angular_step, wait, resolution, both)
                y = y + step

        self.park()
