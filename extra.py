from vector import Vector2
import ctypes
from math import sin as radSin
from math import cos as radCos
from math import pi


user32 = ctypes.windll.user32


def degSin(angle):
    return radSin(angle * pi / 180)


def degCos(angle):
    return radCos(angle * pi / 180)


def getSquareIntersection(angle, width):
    xD = degCos(angle)
    yD = degSin(angle)

    xMin, xMax = -width, width
    yMin, yMax = -width, width

    if xD > 0:
        xIntersect = "RIGHT"
        tX = xMax / xD
    elif xD < 0:
        xIntersect = "LEFT"
        tX = xMin / xD
    else:
        xIntersect = None
        tX = 0

    if yD > 0:
        yIntersect = "TOP"
        tY = yMax / yD
    elif yD < 0:
        yIntersect = "BOTTOM"
        tY = yMin / yD
    else:
        yIntersect = None
        tY = 0

    if not xIntersect and not yIntersect:
        return None

    elif not xIntersect:
        return yIntersect, tY*xD, tY*yD

    elif not yIntersect:
        return xIntersect, tX*xD, tY*yD

    else:
        if tX < tY:
            return xIntersect, tX*xD, tX*yD
        elif tY < tX:
            return yIntersect, tY*xD, tY*yD
        else:
            return "TOP", xMax, yMax


def defineCircle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """
    temp = p2.X * p2.X + p2.Y * p2.Y
    bc = (p1.X * p1.X + p1.Y * p1.Y - temp) / 2
    cd = (temp - p3.X * p3.X - p3.Y * p3.Y) / 2
    det = (p1.X - p2.X) * (p2.Y - p3.Y) - (p2.X - p3.X) * (p1.Y - p2.Y)

    if abs(det) < 1.0e-6:
        raise Exception("Points Are Collinear")

    # Center of circle
    cx = (bc * (p2.Y - p3.Y) - cd * (p1.Y - p2.Y)) / det
    cy = ((p1.X - p2.X) * cd - (p2.X - p3.X) * bc) / det

    radius = ((cx - p1.X) ** 2 + (cy - p1.Y) ** 2) ** 0.5
    return Vector2(cx, cy), radius


def generateCircleCorners(circlePos: Vector2, cursorSize: float):
    return [circlePos + Vector2(-1, 1) * (cursorSize / 2),  # Top Left
            circlePos + Vector2(1, 1) * (cursorSize / 2),  # Top Right
            circlePos + Vector2(1, -1) * (cursorSize / 2),  # Bottom Right
            circlePos + Vector2(-1, -1) * (cursorSize / 2)  # Bottom Left
            ]


def generateRectangleCoords(anchorPoint: Vector2, size: Vector2):
    return [anchorPoint + Vector2(-1, 1) * (size / 2),
            anchorPoint + Vector2(1, 1) * (size / 2),
            anchorPoint + Vector2(1, -1) * (size / 2),
            anchorPoint + Vector2(-1, -1) * (size / 2)
            ]


def generateRectangleCoordsTopLeft(offset, size):
    return [
               offset + Vector2(0, size.Y),
               offset + Vector2(size.X, size.Y),
               offset + Vector2(size.X, 0),
               offset + Vector2(0, 0)
    ]


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def getMonitorSize():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
