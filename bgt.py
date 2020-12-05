from turtle_draw import BrachioGraphTurtle

# This is an example BrachioGraphTurtle definition.

bgt = BrachioGraphTurtle(
    inner_arm=8,          # the length of the inner arm (blue)
    outer_arm=8,          # the length of the outer arm (red)

    shoulder_centre_angle=-60,  # the starting angle of the inner arm, relative to straight ahead
    shoulder_sweep=180,     # the arc covered by the shoulder motor

    elbow_centre_angle=90,  # the centre of the outer arm relative to the inner arm
    elbow_sweep=180,        # the arc covered by the elbow motor

    window_size=800,        # width and height of the turtle canvas
    speed=0
)


if __name__ == '__main__':

    bgt.draw_grid()
    bgt.draw_arcs()
    bgt.draw_arms()
    bgt.draw_outline()


    bgt.screen.exitonclick()
