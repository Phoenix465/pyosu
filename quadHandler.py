from typing import List

import vbohandler
import vector
import colour
import Enums
import extra

VectorList = List[vector.Vector2]
counter = 0


class Quad:
    def __init__(self,
                 cornerPos: VectorList,
                 mainColour,
                 texture,
                 displayV: vector.Vector2,
                 extraTexture1=None,
                 customTextureCorner=None,
                 collisionType: Enums.CollisionType = Enums.CollisionType.NoCollision,
                 collisionRadius: float = 0):

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)
        self.textureCorners = customTextureCorner or [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.texture = texture
        self.extraTexture1 = extraTexture1
        self.texturePathData = None
        self.collisionType = collisionType
        self.collisionRadius = collisionRadius

        self.displayV = displayV

        self.collisionOld = False
        self.colliding = False
        self.collidingOnce = False

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

        self.tweenSizeStage = 0
        self.tweenSizeInfo = (vector.Vector2(0, 0), vector.Vector2(0, 0))
        self.tweenSizeInfoChange = self.tweenSizeInfo[1] - self.tweenSizeInfo[0]
        self.tweenSizeDirection = 0

        self.tweenPosStage = 0
        self.tweenPosInfo = (vector.Vector2(0, 0), vector.Vector2(0, 0))
        self.tweenPosInfoChange = self.tweenPosInfo[1] - self.tweenPosInfo[0]
        self.tweenPosDirection = 0

        self.tweenColourStage = 0
        self.tweenColourInfo = tuple(self.colours[:2])
        self.tweenColourInfoChange = self.tweenColourInfo[1] - self.tweenColourInfo[0]
        self.tweenColourDirection = 0

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo = vbohandler.VBOImage(combinedVBOData, texture)

    def updateTweenSize(self, tweenDelta):
        self.tweenSizeStage += tweenDelta * self.tweenSizeDirection
        self.tweenSizeStage = 0 if self.tweenSizeStage < 0 else 1 if self.tweenSizeStage > 1 else self.tweenSizeStage

        if (self.tweenSizeStage == 0 or self.tweenSizeInfo == 1 or self.tweenSizeDirection == 0) and self.diffV.equals(
                self.tweenSizeInfoChange):
            self.tweenSizeDirection = 0
            return

        start = self.tweenSizeInfo[0]

        self.edit(
            extra.generateCircleCorners(self.getMiddle(), start + self.tweenSizeInfoChange * self.tweenSizeStage),
            self.colours[0],
        )

    def updateTweenPositionCircle(self, tweenDelta):
        self.tweenPosStage += tweenDelta * self.tweenPosDirection
        self.tweenPosStage = 0 if self.tweenPosStage < 0 else 1 if self.tweenPosStage > 1 else self.tweenPosStage

        if self.tweenPosStage == 0 or self.tweenPosInfo == 1 or self.tweenPosDirection == 0:
            self.tweenPosDirection = 0
            return

        start = self.tweenPosInfo[0]

        self.edit(
            extra.generateCircleCorners(start + self.tweenPosInfoChange * self.tweenPosStage,
                                        self.corners[1] - self.corners[3]),
            self.colours[0],
        )

    def updateTweenPositionRect(self, tweenDelta):
        self.tweenPosStage += tweenDelta * self.tweenPosDirection
        self.tweenPosStage = 0 if self.tweenPosStage < 0 else 1 if self.tweenPosStage > 1 else self.tweenPosStage

        if (
                self.tweenPosStage == 0 or self.tweenPosInfo == 1 or self.tweenPosDirection == 0) and self.getMiddle().equals(
            self.tweenPosInfo[0]):
            self.tweenPosDirection = 0
            return

        start = self.tweenPosInfo[0]
        newMiddle = start + self.tweenPosInfoChange * self.tweenPosStage

        self.edit(
            extra.generateRectangleCoords(newMiddle, vector.Vector2(self.diffX, self.diffY)),
            self.colours[0],
        )

    def updateTweenColour(self, tweenDelta):
        self.tweenColourStage += tweenDelta * self.tweenColourDirection

        self.tweenColourStage = 0 if self.tweenColourStage < 0 else 1 if self.tweenColourStage > 1 else self.tweenColourStage

        if (self.tweenColourStage == 0 or self.tweenColourInfo == 1 or self.tweenColourDirection == 0) and self.colours[
            0].equals(self.tweenColourInfo[0]):
            self.tweenColourDirection = 0
            return

        start = self.tweenColourInfo[0]
        newColour = start + (self.tweenColourInfoChange * self.tweenColourStage)

        self.edit(
            self.corners,
            newColour,
        )

    def mouseHit(self, mousePositionRatio: vector.Vector2, displayV: vector.Vector2, ignoreList: list = None):
        if ignoreList:
            for quadIgnore in ignoreList:
                if quadIgnore.colliding:
                    return

        self.collisionOld = self.colliding

        if self.collisionType == Enums.CollisionType.NoCollision:
            self.colliding = False

        elif self.collisionType == Enums.CollisionType.Box:
            self.colliding = self.minX < mousePositionRatio.X < self.maxX and self.minY < mousePositionRatio.Y < self.maxY

        elif self.collisionType == Enums.CollisionType.Circle:
            self.colliding = ((
                                      mousePositionRatio - self.getMiddle()) * displayV).magnitude < self.collisionRadius * self.radiusPixel

        self.collidingOnce = self.colliding != self.collisionOld

    def getMiddle(self):
        return (self.corners[0] + self.corners[2]) / 2

    def edit(self, cornerPos, mainColour):
        if mainColour == self.colours[0] and self.corners == cornerPos and False:
            return

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo.edit(combinedVBOData)

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

    def draw(self):
        self.vbo.draw()


class QuadWithTransparency:
    def __init__(self,
                 cornerPos: VectorList,
                 mainColour,
                 texture,
                 displayV: vector.Vector2,
                 extraTexture1=None,
                 customTextureCorner=None,
                 collisionType: Enums.CollisionType = Enums.CollisionType.NoCollision,
                 collisionRadius: float = 0):

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)
        self.textureCorners = customTextureCorner or [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.texture = texture
        self.extraTexture1 = extraTexture1
        self.texturePathData = None
        self.collisionType = collisionType
        self.collisionRadius = collisionRadius

        self.displayV = displayV

        self.collisionOld = False
        self.colliding = False
        self.collidingOnce = False

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

        self.tweenSizeStage = 0
        self.tweenSizeInfo = (vector.Vector2(0, 0), vector.Vector2(0, 0))
        self.tweenSizeInfoChange = self.tweenSizeInfo[1] - self.tweenSizeInfo[0]
        self.tweenSizeDirection = 0

        self.tweenTransparencyStage = 0
        self.tweenTransparencyInfo = (0, 1)
        self.tweenTransparencyInfoChange = self.tweenTransparencyInfo[1] - self.tweenTransparencyInfo[0]
        self.tweenTransparencyDirection = 0

        """self.tweenColourStage = 0
        self.tweenColourInfo = tuple(self.colours[:2])
        self.tweenColourInfoChange = self.tweenColourInfo[1] - self.tweenColourInfo[0]
        self.tweenColourDirection = 0"""

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBAList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo = vbohandler.VBOImageTransparency(combinedVBOData, texture)

    def updateTweenSize(self, tweenDelta):
        self.tweenSizeStage += tweenDelta * self.tweenSizeDirection
        self.tweenSizeStage = 0 if self.tweenSizeStage < 0 else 1 if self.tweenSizeStage > 1 else self.tweenSizeStage

        if (self.tweenSizeStage == 0 or self.tweenSizeInfo == 1 or self.tweenSizeDirection == 0) and self.diffV.equals(
                self.tweenSizeInfoChange):
            self.tweenSizeDirection = 0
            return

        start = self.tweenSizeInfo[0]

        self.edit(
            extra.generateCircleCorners(self.getMiddle(), start + self.tweenSizeInfoChange * self.tweenSizeStage),
            self.colours[0],
        )

    def updateTweenTransparency(self, tweenDelta, fullBypass=False):
        self.tweenTransparencyStage += tweenDelta * self.tweenTransparencyDirection

        self.tweenTransparencyStage = 0 if self.tweenTransparencyStage < 0 else 1 if self.tweenTransparencyStage > 1 else self.tweenTransparencyStage

        if not fullBypass and (self.tweenTransparencyStage == 0 or self.tweenTransparencyInfo == 1 or self.tweenTransparencyDirection == 0):
            self.tweenTransparencyDirection = 0
            return

        start = self.tweenTransparencyInfo[0]

        currentColour: colour.Colour = self.colours[0]
        self.edit(
            self.corners,
            colour.Colour(r=currentColour.r, g=currentColour.g, b=currentColour.b, alpha=start + self.tweenTransparencyInfoChange * self.tweenTransparencyStage),
        )

    def edit(self, cornerPos, mainColour):
        if mainColour == self.colours[0] and self.corners == cornerPos and False:
            return

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBAList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo.edit(combinedVBOData)

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

    """def updateTweenColour(self, tweenDelta):
        self.tweenColourStage += tweenDelta * self.tweenColourDirection

        self.tweenColourStage = 0 if self.tweenColourStage < 0 else 1 if self.tweenColourStage > 1 else self.tweenColourStage

        if (self.tweenColourStage == 0 or self.tweenColourInfo == 1 or self.tweenColourDirection == 0) and self.colours[
            0].equals(self.tweenColourInfo[0]):
            self.tweenColourDirection = 0
            return

        start = self.tweenColourInfo[0]
        newColour = start + (self.tweenColourInfoChange * self.tweenColourStage)

        self.edit(
            self.corners,
            newColour,
        )"""

    def mouseReset(self):
        self.colliding = False
        self.collidingOnce = False

    def mouseHit(self, mousePositionRatio: vector.Vector2, displayV: vector.Vector2, ignoreList: list = None):
        if ignoreList:
            for quadIgnore in ignoreList:
                if quadIgnore.colliding:
                    return

        self.collisionOld = self.colliding

        if self.collisionType == Enums.CollisionType.NoCollision:
            self.colliding = False

        elif self.collisionType == Enums.CollisionType.Box:
            self.colliding = self.minX < mousePositionRatio.X < self.maxX and self.minY < mousePositionRatio.Y < self.maxY

        elif self.collisionType == Enums.CollisionType.Circle:
            self.colliding = ((
                                      mousePositionRatio - self.getMiddle()) * displayV).magnitude < self.collisionRadius * self.radiusPixel

        self.collidingOnce = self.colliding != self.collisionOld

    def getMiddle(self):
        return (self.corners[0] + self.corners[2]) / 2

    def draw(self):
        self.vbo.draw()


class QuadAnimation:
    def __init__(self,
                 cornerPos: VectorList,
                 mainColour,
                 textureAnimations,
                 displayV: vector.Vector2,
                 customTextureCorner=None,
                 collisionType: Enums.CollisionType = Enums.CollisionType.NoCollision,
                 collisionRadius: float = 0):

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)
        self.textureCorners = customTextureCorner or [(0, 0), (1, 0), (1, 1), (0, 1)]

        self.animationFrame = 0
        self.textureAnimations = textureAnimations

        self.collisionType = collisionType
        self.collisionRadius = collisionRadius

        self.displayV = displayV

        self.collisionOld = False
        self.colliding = False
        self.collidingOnce = False

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

        self.tweenSizeStage = 0
        self.tweenSizeInfo = (vector.Vector2(0, 0), vector.Vector2(0, 0))
        self.tweenSizeInfoChange = self.tweenSizeInfo[1] - self.tweenSizeInfo[0]
        self.tweenSizeDirection = 0

        self.tweenPosStage = 0
        self.tweenPosInfo = (vector.Vector2(0, 0), vector.Vector2(0, 0))
        self.tweenPosInfoChange = self.tweenPosInfo[1] - self.tweenPosInfo[0]
        self.tweenPosDirection = 0

        self.tweenColourStage = 0
        self.tweenColourInfo = tuple(self.colours[:2])
        self.tweenColourInfoChange = self.tweenColourInfo[1] - self.tweenColourInfo[0]
        self.tweenColourDirection = 0

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo = vbohandler.VBOImage(combinedVBOData, self.textureAnimations[0])

        self.kill = False

    def updateTweenSize(self, tweenDelta):
        self.tweenSizeStage += tweenDelta * self.tweenSizeDirection
        self.tweenSizeStage = 0 if self.tweenSizeStage < 0 else 1 if self.tweenSizeStage > 1 else self.tweenSizeStage

        if (self.tweenSizeStage == 0 or self.tweenSizeInfo == 1 or self.tweenSizeDirection == 0) and self.diffV.equals(
                self.tweenSizeInfoChange):
            self.tweenSizeDirection = 0
            return

        start = self.tweenSizeInfo[0]

        self.edit(
            extra.generateCircleCorners(self.getMiddle(), start + self.tweenSizeInfoChange * self.tweenSizeStage),
            self.colours[0],
        )

    def updateTweenPositionCircle(self, tweenDelta):
        self.tweenPosStage += tweenDelta * self.tweenPosDirection
        self.tweenPosStage = 0 if self.tweenPosStage < 0 else 1 if self.tweenPosStage > 1 else self.tweenPosStage

        if self.tweenPosStage == 0 or self.tweenPosInfo == 1 or self.tweenPosDirection == 0:
            self.tweenPosDirection = 0
            return

        start = self.tweenPosInfo[0]

        self.edit(
            extra.generateCircleCorners(start + self.tweenPosInfoChange * self.tweenPosStage,
                                        self.corners[1] - self.corners[3]),
            self.colours[0],
        )

    def updateTweenPositionRect(self, tweenDelta):
        self.tweenPosStage += tweenDelta * self.tweenPosDirection
        self.tweenPosStage = 0 if self.tweenPosStage < 0 else 1 if self.tweenPosStage > 1 else self.tweenPosStage

        if (
                self.tweenPosStage == 0 or self.tweenPosInfo == 1 or self.tweenPosDirection == 0) and self.getMiddle().equals(
            self.tweenPosInfo[0]):
            self.tweenPosDirection = 0
            return

        start = self.tweenPosInfo[0]
        newMiddle = start + self.tweenPosInfoChange * self.tweenPosStage

        self.edit(
            extra.generateRectangleCoords(newMiddle, vector.Vector2(self.diffX, self.diffY)),
            self.colours[0],
        )

    def updateTweenColour(self, tweenDelta):
        self.tweenColourStage += tweenDelta * self.tweenColourDirection

        self.tweenColourStage = 0 if self.tweenColourStage < 0 else 1 if self.tweenColourStage > 1 else self.tweenColourStage

        if (self.tweenColourStage == 0 or self.tweenColourInfo == 1 or self.tweenColourDirection == 0) and self.colours[
            0].equals(self.tweenColourInfo[0]):
            self.tweenColourDirection = 0
            return

        start = self.tweenColourInfo[0]
        newColour = start + (self.tweenColourInfoChange * self.tweenColourStage)

        self.edit(
            self.corners,
            newColour,
        )

    def mouseHit(self, mousePositionRatio: vector.Vector2, displayV: vector.Vector2, ignoreList: list = None):
        if ignoreList:
            for quadIgnore in ignoreList:
                if quadIgnore.colliding:
                    return

        self.collisionOld = self.colliding

        if self.collisionType == Enums.CollisionType.NoCollision:
            self.colliding = False

        elif self.collisionType == Enums.CollisionType.Box:
            self.colliding = self.minX < mousePositionRatio.X < self.maxX and self.minY < mousePositionRatio.Y < self.maxY

        elif self.collisionType == Enums.CollisionType.Circle:
            self.colliding = ((
                                          mousePositionRatio - self.getMiddle()) * displayV).magnitude < self.collisionRadius * self.radiusPixel

        self.collidingOnce = self.colliding != self.collisionOld

    def getMiddle(self):
        return (self.corners[0] + self.corners[2]) / 2

    def stepAnimation(self, customFrame: int = None, canKill=False):
        if self.kill:
            return

        self.animationFrame += 1
        self.animationFrame = customFrame or self.animationFrame

        if self.animationFrame >= len(self.textureAnimations):
            if canKill:
                self.kill = True

            self.animationFrame = 0

        self.vbo.texture = self.textureAnimations[self.animationFrame]

    def edit2(self, cornerPos, textureCorners):
        self.corners = cornerPos
        self.textureCorners = textureCorners

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo.edit(combinedVBOData)

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

    def edit(self, cornerPos, mainColour):
        if mainColour == self.colours[0] and self.corners == cornerPos and False:
            return

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours) + len(self.textureCorners))
        combinedVBODataTemp[::3] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::3] = [colourObj.RGBList for colourObj in self.colours]
        combinedVBODataTemp[2::3] = self.textureCorners

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo.edit(combinedVBOData)

        self.minX = min(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.maxX = max(self.corners[0].X, self.corners[1].X, self.corners[2].X, self.corners[3].X)
        self.minY = min(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.maxY = max(self.corners[0].Y, self.corners[1].Y, self.corners[2].Y, self.corners[3].Y)
        self.diffX = self.maxX - self.minX
        self.diffY = self.maxY - self.minY
        self.diffV = vector.Vector2(self.minX, self.minY)
        self.radiusPixel = (self.displayV.X * (self.maxX - self.minX) / 2)

    def draw(self):
        if self.kill:
            return

        self.vbo.draw()


class QuadColour:
    def __init__(self,
                 cornerPos: VectorList,
                 mainColour):

        self.corners = cornerPos
        self.colours = [mainColour] * len(cornerPos)

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours))
        combinedVBODataTemp[::2] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::2] = [colourObj.RGBAList for colourObj in self.colours]

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo = vbohandler.VBOColour(combinedVBOData)

    def getMiddle(self):
        return (self.corners[0] + self.corners[2]) / 2

    def edit(self, mainColour):
        if mainColour == self.colours[0] and False:
            return

        self.colours = [mainColour] * len(self.corners)

        combinedVBODataTemp = [None] * (len(self.corners) + len(self.colours))
        combinedVBODataTemp[::2] = [corner.list for corner in self.corners]
        combinedVBODataTemp[1::2] = [colourObj.RGBAList for colourObj in self.colours]

        combinedVBOData = []
        for data in combinedVBODataTemp:
            for part in data:
                combinedVBOData.append(part)

        self.vbo.edit(combinedVBOData)

    def draw(self):
        self.vbo.draw()
