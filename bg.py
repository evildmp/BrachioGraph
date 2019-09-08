from brachiograph import BrachioGraph

# this is an example BrachioGraph definition

# angles in degrees and corresponding pulse-widths for the two arm servos
servo_1_angle_pws = [
    [-162, 2490],
    [-144, 2270],
    [-126, 2070],
    [-108, 1880],
    [ -90, 1680],
    [ -72, 1540],
    [ -54, 1360],
    [ -36, 1190],
    [ -18, 1020],
    [   0,  830],
    [  18,  610],
]

servo_2_angle_pws = [
    [  0,  610],
    [ 18,  810],
    [ 36,  970],
    [ 54, 1140],
    [ 72, 1310],
    [ 90, 1460],
    [108, 1630],
    [126, 1790],
    [144, 1970],
    [180, 2360],
]


bg = BrachioGraph(
    inner_arm=9.0,            # the lengths of the arms
    outer_arm=9.0,            # the lengths of the arms
    bounds=(-8, 3, 8, 15),
    # angles in degrees and corresponding pulse-widths for the two arm servos
    servo_1_angle_pws=servo_1_angle_pws,
    servo_2_angle_pws=servo_2_angle_pws,
)

# angles in degrees and corresponding pulse-widths for the two arm servos
servo_1_angle_pws1 = [
    [-162, 2470],
    [-144, 2250],
    [-126, 2050],
    [-108, 1860],
    [ -90, 1690],
    [ -72, 1530],
    [ -54, 1350],
    [ -36, 1190],
    [ -18, 1010],
    [   0,  840],
    [  18,  640],
]

servo_2_angle_pws2 = [
    [  0,  660],
    [ 18,  840],
    [ 36, 1030],
    [ 54, 1180],
    [ 72, 1340],
    [ 90, 1490],
    [108, 1640],
    [126, 1830],
    [144, 2000],
    [162, 2200],
    [180, 2410],
]


bg2 = BrachioGraph(
    inner_arm=8,            # the lengths of the arms
    outer_arm=8,            # the lengths of the arms
    bounds=(-8, 3, 8, 14),
    # angles in degrees and corresponding pulse-widths for the two arm servos
    servo_1_angle_pws=servo_1_angle_pws1,
    servo_2_angle_pws=servo_2_angle_pws2,
    pw_down=1200,                 # pulse-widths for pen up/down
    pw_up=1850,
)

