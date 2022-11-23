# This module is derived from https://github.com/LingDong-/linedraw, by
# Lingdong Huang.

from random import *
import math
import argparse
import json
import time

from PIL import Image, ImageDraw, ImageOps

# file settings
export_path = "images/out.svg"
svg_folder = "images/"
json_folder = "images/"

# CV
no_cv = False

try:
    import numpy as np
    import cv2
except:
    print("Cannot import numpy/openCV. Switching to NO_CV mode.")
    no_cv = True


# -------------- output functions --------------


def image_to_json(
    image_filename,
    resolution=1024,
    draw_contours=False,
    repeat_contours=1,
    draw_hatch=False,
    repeat_hatch=1,
):

    lines = vectorise(
        image_filename,
        resolution,
        draw_contours,
        repeat_contours,
        draw_hatch,
        repeat_hatch,
    )

    filename = json_folder + image_filename + ".json"
    lines_to_file(lines, filename)


def makesvg(lines):
    print("Generating svg file...")
    width = math.ceil(max([max([p[0] * 0.5 for p in l]) for l in lines]))
    height = math.ceil(max([max([p[1] * 0.5 for p in l]) for l in lines]))
    out = '<svg xmlns="http://www.w3.org/2000/svg" height="%spx" width="%spx" version="1.1">' % (
        height,
        width,
    )

    for l in lines:
        l = ",".join([str(p[0] * 0.5) + "," + str(p[1] * 0.5) for p in l])
        out += '<polyline points="' + l + '" stroke="black" stroke-width="1" fill="none" />\n'
    out += "</svg>"
    return out


# we can use turtle graphics to visualise how a set of lines will be drawn
def draw(lines):
    from tkinter import Tk, LEFT
    from turtle import Canvas, RawTurtle, TurtleScreen

    # set up the environment
    root = Tk()
    canvas = Canvas(root, width=800, height=800)
    canvas.pack()

    s = TurtleScreen(canvas)

    t = RawTurtle(canvas)
    t.speed(0)
    t.width(1)

    for line in lines:
        x, y = line[0]
        t.up()
        t.goto(x * 800 / 1024 - 400, -(y * 800 / 1024 - 400))
        for point in line:
            t.down()
            t.goto(point[0] * 800 / 1024 - 400, -(point[1] * 800 / 1024 - 400))

    s.mainloop()


# -------------- conversion control --------------


def vectorise(
    image_filename,
    resolution=1024,
    draw_contours=False,
    repeat_contours=1,
    draw_hatch=False,
    repeat_hatch=1,
):

    image = None
    possible = [
        image_filename,
        "images/" + image_filename,
        "images/" + image_filename + ".jpg",
        "images/" + image_filename + ".png",
        "images/" + image_filename + ".tif",
    ]

    for p in possible:
        try:
            image = Image.open(p)
            break
        except:
            pass
    w, h = image.size

    # convert the image to greyscale
    image = image.convert("L")

    # maximise contrast
    image = ImageOps.autocontrast(image, 5, preserve_tone=True)

    lines = []

    if draw_contours and repeat_contours:
        contours = getcontours(resize_image(image, resolution, draw_contours), draw_contours)
        contours = sortlines(contours)
        contours = join_lines(contours)
        for r in range(repeat_contours):
            lines += contours

    if draw_hatch and repeat_hatch:
        hatches = hatch(resize_image(image, resolution), line_spacing=draw_hatch)
        hatches = sortlines(hatches)
        hatches = join_lines(hatches)
        for r in range(repeat_hatch):
            lines += hatches

    segments = 0
    for line in lines:
        segments = segments + len(line) - 1
    print(len(lines), "lines,", segments, "segments.")

    f = open(svg_folder + image_filename + ".svg", "w")
    f.write(makesvg(lines))
    f.close()

    return lines


def resize_image(image, resolution, divider=1):
    return image.resize(
        (
            int(resolution / divider),
            int(resolution / divider * image.size[1] / image.size[0]),
        )
    )


# -------------- vectorisation options --------------


def getcontours(image, draw_contours=2):
    print("Generating contours...")
    image = find_edges(image)
    IM1 = image.copy()
    IM2 = image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
    dots1 = getdots(IM1)
    contours1 = connectdots(dots1)
    dots2 = getdots(IM2)
    contours2 = connectdots(dots2)

    for i in range(len(contours2)):
        contours2[i] = [(c[1], c[0]) for c in contours2[i]]
    contours = contours1 + contours2

    for i in range(len(contours)):
        for j in range(len(contours)):
            if len(contours[i]) > 0 and len(contours[j]) > 0:
                if distsum(contours[j][0], contours[i][-1]) < 8:
                    contours[i] = contours[i] + contours[j]
                    contours[j] = []

    for i in range(len(contours)):
        contours[i] = [contours[i][j] for j in range(0, len(contours[i]), 8)]

    contours = [c for c in contours if len(c) > 1]

    for i in range(0, len(contours)):
        contours[i] = [(v[0] * draw_contours, v[1] * draw_contours) for v in contours[i]]

    return contours


E = (1, 0)
S = (0, 1)
SE = (1, 1)
NE = (1, -1)


def hatch(image, line_spacing=16):
    lines = []

    lines.extend(get_lines(image, "y", E, line_spacing, 160))
    lines.extend(get_lines(image, "x", S, line_spacing, 80))
    lines.extend(get_lines(image, "y", SE, line_spacing, 40))
    lines.extend(get_lines(image, "x", SE, line_spacing, 40))
    lines.extend(get_lines(image, "y", NE, line_spacing, 20))
    lines.extend(get_lines(image, "x", NE, line_spacing, 20))

    return lines


def get_lines(image, scan, direction, line_spacing, level):
    pixels = image.load()
    width, height = image.size[0], image.size[1]
    i_start = j_start = 0
    lines = []

    if scan == "y":
        i_range = height
    elif scan == "x":
        i_range = width
        # we already have an SE line starting at (0, 0) in the y scan, so skip to the next
        if direction == SE:
            i_start = line_spacing
        elif direction == NE:
            # shift these NE lines down to maintain consistent spacing with the ones in the y scan
            i_start = line_spacing - (height - 1 % line_spacing)
            # these lines start from the bottom of the image
            j_start = height - 1

    for i in range(i_start, i_range, line_spacing):
        start_point = None

        if scan == "y":
            x, y = j_start, i
        elif scan == "x":
            x, y = i, j_start

        while (0 <= x < width) and (0 <= y < height):
            if not start_point:
                if pixels[x, y] < level:
                    start_point = (x, y)
            else:
                if pixels[x, y] >= level:
                    end_point = (x, y)
                    lines.append([start_point, end_point])
                    start_point = None

            end_point = (x, y)
            x += direction[0]
            y += direction[1]

        # if a line has been started, we need to end it now we're at the edge
        if start_point:
            lines.append([start_point, end_point])

    return lines


def join_segments(line_groups):

    print("Making segments into lines...")

    for line_group in line_groups:
        for lines in line_group:
            for lines2 in line_group:

                # do items exist in both?
                if lines and lines2:
                    # if the last point of first is the same as the first point of of the second
                    if lines[-1] == lines2[0]:
                        # then extend the first with all the rest of the points of the second
                        lines.extend(lines2[1:])
                        # and empty the second list
                        lines2.clear()

        # in each line group keep any non-empty lines
        saved_lines = [[line[0], line[-1]] for line in line_group if line]
        line_group.clear()
        line_group.extend(saved_lines)

    lines = [item for group in line_groups for item in group]

    return lines


# -------------- supporting functions for drawing contours --------------


def find_edges(image):
    print("Finding edges...")
    if no_cv:
        # appmask(IM,[F_Blur])
        appmask(image, [F_SobelX, F_SobelY])
    else:
        im = np.array(image)
        im = cv2.GaussianBlur(im, (3, 3), 0)
        im = cv2.Canny(im, 100, 200)
        image = Image.fromarray(im)
    return image.point(lambda p: p > 128 and 255)


def getdots(IM):
    print("Getting contour points...")
    PX = IM.load()
    dots = []
    w, h = IM.size
    for y in range(h - 1):
        row = []
        for x in range(1, w):
            if PX[x, y] == 255:
                if len(row) > 0:
                    if x - row[-1][0] == row[-1][-1] + 1:
                        row[-1] = (row[-1][0], row[-1][-1] + 1)
                    else:
                        row.append((x, 0))
                else:
                    row.append((x, 0))
        dots.append(row)
    return dots


def connectdots(dots):
    print("Connecting contour points...")
    contours = []
    for y in range(len(dots)):
        for x, v in dots[y]:
            if v > -1:
                if y == 0:
                    contours.append([(x, y)])
                else:
                    closest = -1
                    cdist = 100
                    for x0, v0 in dots[y - 1]:
                        if abs(x0 - x) < cdist:
                            cdist = abs(x0 - x)
                            closest = x0

                    if cdist > 3:
                        contours.append([(x, y)])
                    else:
                        found = 0
                        for i in range(len(contours)):
                            if contours[i][-1] == (closest, y - 1):
                                contours[i].append(
                                    (
                                        x,
                                        y,
                                    )
                                )
                                found = 1
                                break
                        if found == 0:
                            contours.append([(x, y)])
        for c in contours:
            if c[-1][1] < y - 1 and len(c) < 4:
                contours.remove(c)
    return contours


# -------------- optimisation for pen movement --------------


def sortlines(lines):
    print("Optimising line sequence...")
    clines = lines[:]
    slines = [clines.pop(0)]
    while clines != []:
        x, s, r = None, 1000000, False
        for l in clines:
            d = distsum(l[0], slines[-1][-1])
            dr = distsum(l[-1], slines[-1][-1])
            if d < s:
                x, s, r = l[:], d, False
            if dr < s:
                x, s, r = l[:], s, True

        clines.remove(x)
        if r == True:
            x = x[::-1]
        slines.append(x)
    return slines


def join_lines(lines, closeness=128):
    # When the start of a new line is close to the end of the previous one, make
    # them one line - this reduces pen up-and-down movement. "Close" means no
    # further away than twice the draw_hatch/draw_contours values.

    previous_line = None
    new_lines = []

    for line in lines:
        if not previous_line:
            new_lines.append(line)
            previous_line = line

        else:

            xdiff = abs(previous_line[-1][0] - line[0][0])
            ydiff = abs(previous_line[-1][1] - line[0][1])
            if xdiff**2 + ydiff**2 <= closeness:
                previous_line.extend(line)

            else:
                new_lines.append(line)
                previous_line = line

    print(f"Reduced {len(lines)} lines to {len(new_lines)} lines.")
    lines = new_lines

    return lines


def lines_to_file(lines, filename):
    with open(filename, "w") as file_to_save:
        json.dump(lines, file_to_save, indent=4)


# -------------- helper functions --------------


def midpt(*args):
    xs, ys = 0, 0
    for p in args:
        xs += p[0]
        ys += p[1]
    return xs / len(args), ys / len(args)


def distsum(*args):
    return sum(
        [
            ((args[i][0] - args[i - 1][0]) ** 2 + (args[i][1] - args[i - 1][1]) ** 2) ** 0.5
            for i in range(1, len(args))
        ]
    )


# -------------- code used when open CV is not available  --------------


def appmask(IM, masks):
    PX = IM.load()
    w, h = IM.size
    NPX = {}
    for x in range(0, w):
        for y in range(0, h):
            a = [0] * len(masks)
            for i in range(len(masks)):
                for p in masks[i].keys():
                    if 0 < x + p[0] < w and 0 < y + p[1] < h:
                        a[i] += PX[x + p[0], y + p[1]] * masks[i][p]
                if sum(masks[i].values()) != 0:
                    a[i] = a[i] / sum(masks[i].values())
            NPX[x, y] = int(sum([v**2 for v in a]) ** 0.5)
    for x in range(0, w):
        for y in range(0, h):
            PX[x, y] = NPX[x, y]


F_Blur = {
    (-2, -2): 2,
    (-1, -2): 4,
    (0, -2): 5,
    (1, -2): 4,
    (2, -2): 2,
    (-2, -1): 4,
    (-1, -1): 9,
    (0, -1): 12,
    (1, -1): 9,
    (2, -1): 4,
    (-2, 0): 5,
    (-1, 0): 12,
    (0, 0): 15,
    (1, 0): 12,
    (2, 0): 5,
    (-2, 1): 4,
    (-1, 1): 9,
    (0, 1): 12,
    (1, 1): 9,
    (2, 1): 4,
    (-2, 2): 2,
    (-1, 2): 4,
    (0, 2): 5,
    (1, 2): 4,
    (2, 2): 2,
}
F_SobelX = {
    (-1, -1): 1,
    (0, -1): 0,
    (1, -1): -1,
    (-1, 0): 2,
    (0, 0): 0,
    (1, 0): -2,
    (-1, 1): 1,
    (0, 1): 0,
    (1, 1): -1,
}
F_SobelY = {
    (-1, -1): 1,
    (0, -1): 2,
    (1, -1): 1,
    (-1, 0): 0,
    (0, 0): 0,
    (1, 0): 0,
    (-1, 1): -1,
    (0, 1): -2,
    (1, 1): -1,
}
