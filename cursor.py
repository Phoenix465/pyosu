from math import sqrt

import quadHandler
from colour import Colour
from extra import generateCircleCorners
from texture import loadTexture
from vector import Vector2


class Cursor:
    def __init__(self, displayV, cursorPath, cursorTrailPath):
        self.displayV = displayV

        self.cursorSize = Vector2(60, 60)  # Pixels
        self.trailSize = self.cursorSize * 0.9

        self.cursorPos = Vector2(0, 0)  # In Pixels?

        self.cursorPath = cursorPath
        self.cursorTexture = loadTexture(self.cursorPath)

        self.cursor = quadHandler.Quad(
            generateCircleCorners(self.cursorPos, self.cursorSize / self.displayV),
            Colour(255, 255, 255, convertToDecimal=True),
            self.cursorTexture,
            self.displayV
        )

        self.cursor.tweenSizeInfo = (self.cursorSize / displayV, (self.cursorSize / displayV) * 1.2)
        self.cursor.tweenSizeInfoChange = self.cursor.tweenSizeInfo[1] - self.cursor.tweenSizeInfo[0]

        self.cursorTrails = []
        self.maxTrail = 50

        for i in range(self.maxTrail):
            cursortrailTexture = loadTexture(cursorTrailPath,
                                             alpha=int(255 * (self.maxTrail - i) / self.maxTrail))

            self.cursorTrails.append(quadHandler.Quad(
                generateCircleCorners(Vector2(2, 2), self.trailSize / displayV),
                Colour(1, 1, 1),
                cursortrailTexture,
                displayV,
            ))

    def update(self, cursorPos, osuKeysPressOnce, osuKeysHeld):
        self.cursor.edit(
            generateCircleCorners(cursorPos, self.cursorSize / self.displayV),
            Colour(1, 1, 1)
        )

        if any(osuKeysPressOnce):
            self.cursor.tweenSizeStage = 0.01
            self.cursor.tweenSizeDirection = 1

        if not any(osuKeysHeld):
            self.cursor.tweenSizeDirection = -1

        self.cursor.updateTweenSize(0.2)

        lastPosition = self.cursorTrails[0].getMiddle()

        if cursorPos != lastPosition or True:
            for i in range(self.maxTrail - 1, 0, -1):
                behind = self.cursorTrails[i - 1]
                self.cursorTrails[i].edit(behind.corners, Colour(1, 1, 1))

            self.cursorTrails[0].edit(
                generateCircleCorners(cursorPos, self.trailSize / self.displayV),
                Colour(1, 1, 1)
            )
        else:
            for i, cursorTrail in enumerate(self.cursorTrails[:-1]):
                if self.cursorTrails[i + 1].getMiddle() == Vector2(2, 2):
                    self. cursorTrails[i].edit(
                        generateCircleCorners(Vector2(2, 2), self.trailSize / self.displayV),
                        Colour(1, 1, 1)
                    )

                    #break

    def draw(self):
        for i, cursorTrail in enumerate(self.cursorTrails[::-1]):
            realIndex = len(self.cursorTrails) - i - 1

            if realIndex > 1 and False:  # Discontinued the Trail
                currentPos = self.cursorTrails[realIndex].getMiddle()
                newPos = self.cursorTrails[realIndex - 1].getMiddle()

                if not currentPos.equals(Vector2(2, 2)) and not newPos.equals(Vector2(2, 2)):
                    distance = (newPos - currentPos).magnitude
                    # repeat = floor(distance / jump)

                    delta = newPos - currentPos

                    if delta.magnitude != 0:
                        rectCoords = []
                        thickness = (self.cursorSize / self.displayV).X
                        addV = Vector2(0, 0)

                        if delta.X == 0:
                            addV = Vector2(thickness / 2, 0)
                            rectCoords = [newPos - addV, newPos + addV, currentPos + addV, currentPos - addV]

                        elif delta.Y == 0:
                            addV = Vector2(0, thickness / 2)
                            rectCoords = [newPos - addV, newPos + addV, currentPos + addV, currentPos - addV]

                        else:
                            m1 = delta.Y / delta.X
                            m2 = -1 / m1
                            dx = sqrt(thickness ** 2 / (1 + m2 ** 2)) / 2
                            dy = m2 * dx

                            addV = Vector2(dx, dy)

                            rectCoords = [newPos - addV, newPos + addV, currentPos + addV, currentPos - addV]

                        # [(0, 0), (1, 0), (1, 1), (0, 1)] OLD
                        # ]
                        jump = 0.001
                        tempQuad = quadHandler.Quad(
                            rectCoords,
                            Colour(1, 1, 1),
                            self.cursorTrails[realIndex].extraTexture1,
                            self.displayV,
                            customTextureCorner=[(0, 1), (0, 0), (distance / jump, 0), (distance / jump, 1)]
                        )

                        tempQuad.draw()
                        # trailVBO = vbohandler.VBOImage(, cursorTrails[realIndex].texture)
                        # trailVBO.draw()

            cursorTrail.draw()

        self.cursor.draw()
