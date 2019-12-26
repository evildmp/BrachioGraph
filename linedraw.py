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
    image_filename, resolution=1024,
    draw_contours=False, repeat_contours=1,
    draw_hatch=False, repeat_hatch=1,
    ):

    lines=vectorise(
        image_filename, resolution,
        draw_contours, repeat_contours,
        draw_hatch, repeat_hatch,
        )

    filename = json_folder + image_filename + ".json"
    lines_to_file(lines, filename)


def makesvg(lines):
    print("generating svg file...")
    width = math.ceil(max([max([p[0]*0.5 for p in l]) for l in lines]))
    height = math.ceil(max([max([p[1]*0.5 for p in l]) for l in lines]))
    out = '<svg xmlns="http://www.w3.org/2000/svg" height="%spx" width="%spx" version="1.1">' % (height, width)

    for l in lines:
        l = ",".join([str(p[0]*0.5)+","+str(p[1]*0.5) for p in l])
        out += '<polyline points="'+l+'" stroke="black" stroke-width="1" fill="none" />\n'
    out += '</svg>'
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
        t.goto(x*800/1024-400,-(y*800/1024-400))
        for point in line:
            t.down()
            t.goto(point[0]*800/1024-400,-(point[1]*800/1024-400))

    s.mainloop()


# -------------- conversion control --------------

def vectorise(
    image_filename, resolution=1024,
    draw_contours=False, repeat_contours=1,
    draw_hatch=False, repeat_hatch=1,
    ):

    image = None
    possible = [
        image_filename,
        "images/"+image_filename,
        "images/"+image_filename+".jpg",
        "images/"+image_filename+".png",
        "images/"+image_filename+".tif"
    ]

    for p in possible:
        try:
            image = Image.open(p)
            break
        except:
            pass
    w,h = image.size

    # convert the image to greyscale
    image = image.convert("L")

    # maximise contrast
    image=ImageOps.autocontrast(image, 10)

    lines = []

    if draw_contours and repeat_contours:
        contours = sortlines(getcontours(
            image.resize((int(resolution/draw_contours), int(resolution/draw_contours*h/w))),
            draw_contours
        ))
        for r in range(repeat_contours):
            lines += contours

    if draw_hatch and repeat_hatch:
        hatches = sortlines(
            hatch(
                # image,
                image.resize((int(resolution/draw_hatch), int(resolution/draw_hatch*h/w))),
                draw_hatch
        ))
        for r in range(repeat_hatch):
            lines += hatches


    f = open(svg_folder + image_filename + ".svg", 'w')
    f.write(makesvg(lines))
    f.close()
    segments = 0
    for line in lines:
        segments = segments + len(line)
    print(len(lines), "strokes,", segments, "points.")
    print("done.")
    return lines


# -------------- vectorisation options --------------

def getcontours(image, draw_contours=2):
    print("generating contours...")
    image = find_edges(image)
    IM1 = image.copy()
    IM2 = image.rotate(-90,expand=True).transpose(Image.FLIP_LEFT_RIGHT)
    dots1 = getdots(IM1)
    contours1 = connectdots(dots1)
    dots2 = getdots(IM2)
    contours2 = connectdots(dots2)

    for i in range(len(contours2)):
        contours2[i] = [(c[1],c[0]) for c in contours2[i]]
    contours = contours1+contours2

    for i in range(len(contours)):
        for j in range(len(contours)):
            if len(contours[i]) > 0 and len(contours[j])>0:
                if distsum(contours[j][0],contours[i][-1]) < 8:
                    contours[i] = contours[i]+contours[j]
                    contours[j] = []

    for i in range(len(contours)):
        contours[i] = [contours[i][j] for j in range(0,len(contours[i]),8)]


    contours = [c for c in contours if len(c) > 1]

    for i in range(0,len(contours)):
        contours[i] = [(v[0]*draw_contours,v[1]*draw_contours) for v in contours[i]]

    return contours


# improved, faster and easier to understand hatching
def hatch(image, draw_hatch=16):

    t0 = time.time()

    print("hatching using hatch()...")
    pixels = image.load()
    w, h = image.size
    lg1 = []
    lg2 = []
    for x0 in range(w):
        # print("reading x", x0)
        for y0 in range(h):
            # print("    reading y", x0)
            x = x0 * draw_hatch
            y = y0 * draw_hatch

            # don't hatch above a certain level of brightness
            if pixels[x0, y0] > 144:
                pass

            # above 64, draw horizontal lines
            elif pixels[x0,y0] > 64:
                lg1.append([(x,y+draw_hatch/4),(x+draw_hatch,y+draw_hatch/4)])

            # above 16, draw diagonal lines also
            elif pixels[x0,y0] > 16:
                lg1.append([(x,y+draw_hatch/4),(x+draw_hatch,y+draw_hatch/4)])
                lg2.append([(x+draw_hatch,y),(x,y+draw_hatch)])

            # below 16, draw diagonal lines and a second horizontal line
            else:
                lg1.append([(x,y+draw_hatch/4),(x+draw_hatch,y+draw_hatch/4)])  # horizontal lines
                lg1.append([(x,y+draw_hatch/2+draw_hatch/4),(x+draw_hatch,y+draw_hatch/2+draw_hatch/4)])  # horizontal lines with additional offset
                lg2.append([(x+draw_hatch,y),(x,y+draw_hatch)])                 # diagonal lines, left

    t1 = time.time()

    print("wrangling points...")

    # Make segments into lines
    line_groups = [lg1, lg2]

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

    t2 = time.time()

    print("hatching   : ", t1 - t0)
    print("wrangling:   ", t2 - t1)
    print("total:       ", t2 - t0)

    return lines


# -------------- supporting functions for drawing contours --------------

def find_edges(image):
    print("finding edges...")
    if no_cv:
        #appmask(IM,[F_Blur])
        appmask(image,[F_SobelX,F_SobelY])
    else:
        im = np.array(image)
        im = cv2.GaussianBlur(im,(3,3),0)
        im = cv2.Canny(im,100,200)
        image = Image.fromarray(im)
    return image.point(lambda p: p > 128 and 255)


def getdots(IM):
    print("getting contour points...")
    PX = IM.load()
    dots = []
    w,h = IM.size
    for y in range(h-1):
        row = []
        for x in range(1,w):
            if PX[x,y] == 255:
                if len(row) > 0:
                    if x-row[-1][0] == row[-1][-1]+1:
                        row[-1] = (row[-1][0],row[-1][-1]+1)
                    else:
                        row.append((x,0))
                else:
                    row.append((x,0))
        dots.append(row)
    return dots


def connectdots(dots):
    print("connecting contour points...")
    contours = []
    for y in range(len(dots)):
        for x,v in dots[y]:
            if v > -1:
                if y == 0:
                    contours.append([(x,y)])
                else:
                    closest = -1
                    cdist = 100
                    for x0,v0 in dots[y-1]:
                        if abs(x0-x) < cdist:
                            cdist = abs(x0-x)
                            closest = x0

                    if cdist > 3:
                        contours.append([(x,y)])
                    else:
                        found = 0
                        for i in range(len(contours)):
                            if contours[i][-1] == (closest,y-1):
                                contours[i].append((x,y,))
                                found = 1
                                break
                        if found == 0:
                            contours.append([(x,y)])
        for c in contours:
            if c[-1][1] < y-1 and len(c)<4:
                contours.remove(c)
    return contours


# -------------- optimisation for pen movement --------------

def sortlines(lines):
    print("optimizing stroke sequence...")
    clines = lines[:]
    slines = [clines.pop(0)]
    while clines != []:
        x,s,r = None,1000000,False
        for l in clines:
            d = distsum(l[0],slines[-1][-1])
            dr = distsum(l[-1],slines[-1][-1])
            if d < s:
                x,s,r = l[:],d,False
            if dr < s:
                x,s,r = l[:],s,True

        clines.remove(x)
        if r == True:
            x = x[::-1]
        slines.append(x)
    return slines



def lines_to_file(lines, filename):
    with open(filename, "w") as file_to_save:
        json.dump(lines, file_to_save, indent=4)


# -------------- helper functions --------------

def midpt(*args):
    xs,ys = 0,0
    for p in args:
        xs += p[0]
        ys += p[1]
    return xs/len(args),ys/len(args)


def distsum(*args):
    return sum([ ((args[i][0]-args[i-1][0])**2 + (args[i][1]-args[i-1][1])**2)**0.5 for i in range(1,len(args))])


# -------------- code used when open CV is not available  --------------


def appmask(IM,masks):
    PX = IM.load()
    w,h = IM.size
    NPX = {}
    for x in range(0,w):
        for y in range(0,h):
            a = [0]*len(masks)
            for i in range(len(masks)):
                for p in masks[i].keys():
                    if 0<x+p[0]<w and 0<y+p[1]<h:
                        a[i] += PX[x+p[0],y+p[1]] * masks[i][p]
                if sum(masks[i].values())!=0:
                    a[i] = a[i] / sum(masks[i].values())
            NPX[x,y]=int(sum([v**2 for v in a])**0.5)
    for x in range(0,w):
        for y in range(0,h):
            PX[x,y] = NPX[x,y]

F_Blur = {
    (-2,-2):2,(-1,-2):4,(0,-2):5,(1,-2):4,(2,-2):2,
    (-2,-1):4,(-1,-1):9,(0,-1):12,(1,-1):9,(2,-1):4,
    (-2,0):5,(-1,0):12,(0,0):15,(1,0):12,(2,0):5,
    (-2,1):4,(-1,1):9,(0,1):12,(1,1):9,(2,1):4,
    (-2,2):2,(-1,2):4,(0,2):5,(1,2):4,(2,2):2,
}
F_SobelX = {(-1,-1):1,(0,-1):0,(1,-1):-1,(-1,0):2,(0,0):0,(1,0):-2,(-1,1):1,(0,1):0,(1,1):-1}
F_SobelY = {(-1,-1):1,(0,-1):2,(1,-1):1,(-1,0):0,(0,0):0,(1,0):0,(-1,1):-1,(0,1):-2,(1,1):-1}
