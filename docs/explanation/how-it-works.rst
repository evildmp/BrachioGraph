==================================================
How a BrachioGraph works
==================================================

BrachioGraph is an *arm-writer* - it moves the pen by adjusting the angles of its arms. All its
movements are rotational - it can only move in curves. This has some consequences that make it
challenging to draw with.

Whether it needs to move one arm or both to move the pen from one point to another,
what it draws will not be a straight line. The shortest distance between two points might be
a straight line, but the simplest movement between them is certainly not. Simply moving the
motors to the correct position for the end-point will draw a curved line rather than a straight
one.

Instead, it's necessary to break down any straight line into a series of much shorter lines along
its length - enough to make the line as straight as possible. The movement of servo motors is
rather coarse, which is why all the lines a BrachioGraph produces are wiggly.
