from math import atan2, pi, floor, sin, cos
from typing import List, Tuple
import bezier

import numpy as np
from matplotlib import pyplot as plt
from pygame import Surface, SRCALPHA, transform
from pygame.image import load, save
from pygame.mixer import Sound
from pygame.time import get_ticks
from pygame.transform import flip

import Enums
import colour
import extra
import osureader.objects
import quadHandler
import texture
import vector


class HitCircle:
    def __init__(self, posPVec,
                 circleSizeRadiusP,
                 time,
                 approachRateTimings,
                 hitSoundPath,
                 comboColourTuple,
                 hitCircleTexture,
                 approachCircleTexture,
                 numberCircleTexture,
                 hitWindowData,
                 displayV,
                 sliderMode=False,
                 debugMode=False):

        self.sliderMode = sliderMode
        self.debugMode = debugMode

        self.posVec = posPVec
        self.circleSizeRadiusP = circleSizeRadiusP

        self.time = time
        self.hitOffset = 0

        self.approachRateTimings = approachRateTimings

        self.fadeInStart = self.time - self.approachRateTimings[0]
        self.fadeInEnd = self.time - (self.approachRateTimings[0] - self.approachRateTimings[1])

        self.hitWindowData = hitWindowData

        self.hitSound = Sound(file=hitSoundPath)
        self.comboColourTuple = comboColourTuple
        self.displayV = displayV

        self.hitCircle = quadHandler.QuadWithTransparency(
            extra.generateCircleCorners(self.posVec / self.displayV,
                                        self.circleSizeRadiusP / self.displayV),
            colour.Colour(*self.comboColourTuple, alpha=1),  # NORMAL 0
            hitCircleTexture,
            self.displayV,

            collisionType=Enums.CollisionType.Box,
            collisionRadius=1
        )
        self.hitCircle.tweenTransparencyInfo = (0, 1)
        self.hitCircle.tweenTransparencyInfoChange = 1
        self.hitCircle.tweenTransparencyDirection = 1

        self.hitCircle.tweenSizeInfo = (
            self.circleSizeRadiusP / self.displayV,
            self.circleSizeRadiusP / self.displayV * 1.5
        )
        self.hitCircle.tweenSizeInfoChange = self.hitCircle.tweenSizeInfo[1] - self.hitCircle.tweenSizeInfo[0]
        self.hitCircle.tweenSizeDirection = 1

        self.comboCircle = quadHandler.QuadWithTransparency(
            extra.generateCircleCorners(self.posVec / self.displayV,
                                        self.circleSizeRadiusP / self.displayV),
            colour.Colour(1, 1, 1, alpha=0),
            numberCircleTexture,
            self.displayV,

            collisionType=Enums.CollisionType.Circle,
            collisionRadius=1
        )
        self.comboCircle.tweenTransparencyInfo = (0, 1)
        self.comboCircle.tweenTransparencyInfoChange = 1
        self.comboCircle.tweenTransparencyDirection = 1

        self.approachCircle = quadHandler.QuadWithTransparency(
            extra.generateCircleCorners(self.posVec / self.displayV,
                                        self.circleSizeRadiusP / self.displayV),
            colour.Colour(*self.comboColourTuple, alpha=0),
            approachCircleTexture,
            self.displayV,

            collisionType=Enums.CollisionType.Circle,
            collisionRadius=1
        )

        self.approachCircle.tweenTransparencyInfo = (0, 1)
        self.approachCircle.tweenTransparencyInfoChange = 1
        self.approachCircle.tweenTransparencyDirection = 1

        self.approachCircle.tweenSizeInfo = (
            self.circleSizeRadiusP / self.displayV * 4 * 1.5,
            self.circleSizeRadiusP / self.displayV * 1.4
        )
        self.approachCircle.tweenSizeInfoChange = self.approachCircle.tweenSizeInfo[1] - \
                                                  self.approachCircle.tweenSizeInfo[0]
        self.approachCircle.tweenSizeDirection = 1

        self.clicked = False
        self.enlargeTime = 300
        self.endEnlarge = get_ticks()

        self.checkForCollision = False
        self.kill = False

        self.score = 0

        self.scoreObject = None
        self.scoreEnd = 0
        self.stopStep = False
        self.scored = False

    def clickedFinder(self, time, keyboardHandler):
        if self.clicked or self.kill:
            return

        if self.hitCircle.colliding and any(keyboardHandler.osuKeysPressOnce):
            self.hitSound.play()

            self.clicked = True
            self.checkForCollision = False

            self.endEnlarge = time + self.enlargeTime

            hitTimeDifference = abs(time - self.time)

            self.hitOffset = hitTimeDifference

            self.score = hitTimeDifference <= self.hitWindowData["300"] and "300" or (
                         hitTimeDifference <= self.hitWindowData["100"] and "100" or (
                         hitTimeDifference <= self.hitWindowData["50"]  and "50"  or "X"))

            #print("SCORED", self.score)

    def step(self, time):
        if self.fadeInStart <= time <= self.fadeInEnd:
            timeChange = time - self.fadeInStart

            self.hitCircle.tweenTransparencyStage = timeChange / (self.fadeInEnd - self.fadeInStart)

            self.hitCircle.updateTweenTransparency(0, fullBypass=True)

            self.comboCircle.tweenTransparencyStage = timeChange / (self.fadeInEnd - self.fadeInStart)
            self.comboCircle.updateTweenTransparency(0, fullBypass=True)

            self.approachCircle.tweenTransparencyStage = timeChange / (self.fadeInEnd - self.fadeInStart)
            self.approachCircle.updateTweenTransparency(0, fullBypass=True)

        if self.fadeInStart <= time <= self.time:
            timeChange = self.time - time

            self.approachCircle.tweenSizeStage = 1 - (timeChange / (self.time - self.fadeInStart))
            self.approachCircle.updateTweenSize(0)

        if self.clicked and not self.kill:
            if self.sliderMode:
                self.clicked = True
                self.kill = True

            else:
                timeChange = self.endEnlarge - time

                self.hitCircle.tweenSizeStage = 1 - (timeChange / self.enlargeTime)
                self.hitCircle.tweenSizeDirection = 1

                self.hitCircle.updateTweenSize(0)

                self.hitCircle.tweenTransparencyStage = 1 - self.hitCircle.tweenSizeStage
                self.hitCircle.updateTweenTransparency(0)

                if self.hitCircle.tweenSizeStage >= 1:
                    self.clicked = True
                    self.kill = True

        if time > self.time + self.hitWindowData["50"] and not self.clicked and not self.kill:
            self.kill = True
            self.score = "X"

            #print("MISSED")

    def draw(self, time, keyboardHandler):
        if self.kill:
            return

        if not self.stopStep:
            self.clickedFinder(time, keyboardHandler)
            self.step(time)

        if self.fadeInStart <= time <= self.time + self.hitWindowData["50"] and not self.clicked:
            self.checkForCollision = True

            self.hitCircle.draw()

            if not self.debugMode:
                self.comboCircle.draw()
                self.approachCircle.draw()

            #print(self.time, time, time > self.fadeInEnd, "A", self.approachCircle.tweenTransparencyStage)

        elif self.clicked:
            self.hitCircle.draw()
            self.checkForCollision = False

        else:
            self.checkForCollision = False
            # self.hitCircle.draw()


class Sliders:
    def __init__(self, initialPoint: vector.Vector2,
                 sliderPoints: List[vector.Vector2],
                 curveType: osureader.objects.SliderType,
                 circleRadiusOP: float,
                 displayV: vector.Vector2,
                 time: float,
                 approachRateTimings: tuple,
                 whitecirclePath: str,
                 comboColourTuple: Tuple[int, int, int],
                 pixelExtraData: Tuple[vector.Vector2, vector.Vector2, vector.Vector2, vector.Vector2],

                 hitSoundPath,
                 hitCircleTexture,
                 approachCircleTexture,
                 numberCircleTexture,
                 hitWindowData,

                 # (self.osupixelAdjust2, self.osupixelRatio2, self.osupixel, self.osupixelRatio),
                 index):

        self.pixelExtraData = pixelExtraData
        self.displayV = displayV

        self.startTime = time

        self.startHitCircle = HitCircle(
            pixelExtraData[0] + initialPoint * pixelExtraData[1],
            vector.Vector2(circleRadiusOP / pixelExtraData[2].Y * displayV.X,
                           circleRadiusOP / pixelExtraData[2].Y * displayV.X),
            time,
            approachRateTimings,
            hitSoundPath,
            comboColourTuple,
            hitCircleTexture,
            approachCircleTexture,
            numberCircleTexture,
            hitWindowData,
            displayV,
            sliderMode=True
        )

        self.curveQuad = None
        self.curveSizeAdjOP = vector.Vector2(0, 0)
        self.topleftOP = vector.Vector2(0, 0)
        self.topListToInitialPoint = vector.Vector2(0, 0)

        self.curvePathIntricate = []

        self.sliderImage = None
        self.sliderStartOffset = None

        self.debugPoints = []



        adjCircleSize = circleRadiusOP * 2

        whiteImage = load(whitecirclePath)
        adjWhiteImage = transform.scale(whiteImage, (round(adjCircleSize), round(adjCircleSize)))
        imageOffset = vector.Vector2(circleRadiusOP, circleRadiusOP)

        curvePoints = [initialPoint] + sliderPoints

        if curveType.value == "P":
            if len(curvePoints) != 3:
                raise Exception("This shouldn't happen but Perfect Circle only has 3 points")

            centre, radius = extra.defineCircle(*curvePoints)
            #print("Centre", centre, "Radius", radius)

            # Radians
            startAngle = atan2(*(curvePoints[0] - centre).tuple)
            midAngle = atan2(*(curvePoints[1] - centre).tuple)
            endAngle = atan2(*(curvePoints[2] - centre).tuple)

            if startAngle < 0: startAngle += 2*pi
            if midAngle < 0: midAngle += 2*pi
            if endAngle < 0: endAngle += 2*pi

            if startAngle > endAngle: startAngle, endAngle = endAngle, startAngle

            if not startAngle < midAngle < endAngle:
                startAngle, midAngle, endAngle = endAngle - 2 * pi, midAngle if midAngle < pi else midAngle - 2 * pi, startAngle

            startAngle, midAngle, endAngle = startAngle * 180 / pi, midAngle * 180 / pi, endAngle * 180 / pi

            tempPoints = []
            for angle in range(floor(startAngle), floor(endAngle+1), 1):
                radAngle = angle * pi / 180

                circleOffset = vector.Vector2(sin(radAngle)*radius, cos(radAngle)*radius)
                circleRealPos = centre + circleOffset

                tempPoints.append(circleRealPos)

            xPosMap = list(map(lambda point: point.X, tempPoints))
            yPosMap = list(map(lambda point: point.Y, tempPoints))

            sliderWidth = max(xPosMap) - min(xPosMap)
            sliderHeight = max(yPosMap) - min(yPosMap)

            topLeft = vector.Vector2(min(xPosMap), max(yPosMap))
            topLeftAdj = topLeft + vector.Vector2(-circleRadiusOP, circleRadiusOP)

            sliderWAdj = sliderWidth + adjCircleSize
            sliderHAdj = sliderHeight + adjCircleSize

            self.curveSizeAdjOP = vector.Vector2(sliderWAdj, sliderHAdj)

            #self.topListToInitialPoint = initialPoint - self.topleftOP

            blankSliderSurface = Surface((sliderWAdj, sliderHAdj), SRCALPHA)

            pointDist = 100

            for circleRealPos in tempPoints:
                self.curvePathIntricate.append(circleRealPos - initialPoint)

                relImagePos = circleRealPos - topLeftAdj
                imageBlitOffset = vector.Vector2(relImagePos.X, -relImagePos.Y) - imageOffset

                if imageBlitOffset.magnitude < pointDist:
                    pointDist = imageBlitOffset.magnitude
                    self.sliderStartOffset = imageBlitOffset

                blankSliderSurface.blit(adjWhiteImage, imageBlitOffset.tuple)

            self.sliderImage = blankSliderSurface

        elif curveType.value == "B":
            curvePointsSplit = []

            temp = []
            for i, point in enumerate(curvePoints):
                temp.append(point)

                if i+1 != len(curvePoints) and point == curvePoints[i+1]:
                    curvePointsSplit.append(temp)
                    temp = []

            if temp:
                curvePointsSplit.append(temp)

            curves = []

            for curveSplit in curvePointsSplit:
                nodes = [
                    [point.X for point in curveSplit],
                    [point.Y for point in curveSplit]
                ]

                nodes = np.asfortranarray(nodes)

                curve = bezier.Curve.from_nodes(nodes=nodes)

                curves.append(curve)

            curveStep = 100
            curveRatioStep = [len(split)/len(curvePoints) for split in curvePointsSplit]
            curveStepPerCurve = [floor(ratio*curveStep) for ratio in curveRatioStep]

            curveSmallPoints = []
            for i, curve in enumerate(curves):
                maxStep = curveStepPerCurve[i]
                curveTinyPoints = [curve.evaluate(s/maxStep) for s in range(maxStep+1)]
                curveTinyPoints = map(lambda point: vector.Vector2(point[0][0], point[1][0]), curveTinyPoints)

                curveSmallPoints.extend(curveTinyPoints)

            self.curvePathIntricate = [point - initialPoint for point in curveSmallPoints]

            xPosMap = list(map(lambda point: point.X, curveSmallPoints))
            yPosMap = list(map(lambda point: point.Y, curveSmallPoints))

            sliderWidth = max(xPosMap) - min(xPosMap)
            sliderHeight = max(yPosMap) - min(yPosMap)

            topLeft = vector.Vector2(min(xPosMap), max(yPosMap))
            topLeftAdj = topLeft + vector.Vector2(-circleRadiusOP, circleRadiusOP)

            sliderWAdj = sliderWidth + adjCircleSize
            sliderHAdj = sliderHeight + adjCircleSize

            self.curveSizeAdjOP = vector.Vector2(sliderWAdj, sliderHAdj)
            self.topleftOP = topLeftAdj

            blankSliderSurface = Surface((sliderWAdj, sliderHAdj), SRCALPHA)

            relImagePos = [point - topLeftAdj for point in curveSmallPoints]
            imageBlitOffset = [vector.Vector2(point.X, -point.Y) - imageOffset for point in relImagePos]

            pointDist = 100
            for offset in imageBlitOffset:
                if offset.magnitude < pointDist:
                    pointDist = offset.magnitude
                    self.sliderStartOffset = imageBlitOffset

                blankSliderSurface.blit(adjWhiteImage, offset.tuple)

            #save(blankSliderSurface, f"test{index}.png")

            self.sliderImage = blankSliderSurface

        elif curveType.value == "L":
            totalStep = 100

            magnitudes = [(curvePoints[i] - curvePoints[i+1]).magnitude for i in range(len(curvePoints)-1)]
            totalMagnitude = sum(magnitudes)
            ratioMagnitude = [mag/totalMagnitude for mag in magnitudes]
            stepSplit = [ratio*totalStep for ratio in ratioMagnitude]


            xPosMap = list(map(lambda point: point.X, curvePoints))
            yPosMap = list(map(lambda point: point.Y, curvePoints))

            sliderWidth = max(xPosMap) - min(xPosMap)
            sliderHeight = max(yPosMap) - min(yPosMap)

            topLeft = vector.Vector2(min(xPosMap), max(yPosMap))
            topLeftAdj = topLeft + vector.Vector2(-circleRadiusOP, circleRadiusOP)

            sliderWAdj = sliderWidth + adjCircleSize
            sliderHAdj = sliderHeight + adjCircleSize

            self.curveSizeAdjOP = vector.Vector2(sliderWAdj, sliderHAdj)
            self.topleftOP = topLeftAdj

            blankSliderSurface = Surface((sliderWAdj, sliderHAdj), SRCALPHA)
            pointDist = 100

            for i, point in enumerate(curvePoints[:-1]):
                step = stepSplit[i]

                pointB = curvePoints[i+1]

                subVec = pointB - point

                for stepI in range(floor(step)+1):
                    distDiv = stepI/step
                    newVec = point + (subVec * distDiv)

                    relImagePos = newVec - topLeftAdj
                    imageBlitOffset = vector.Vector2(relImagePos.X, -relImagePos.Y) - imageOffset

                    if imageBlitOffset.magnitude < pointDist:
                        pointDist = imageBlitOffset.magnitude
                        self.sliderStartOffset = imageBlitOffset

                    blankSliderSurface.blit(adjWhiteImage, imageBlitOffset.tuple)

                    self.curvePathIntricate.append(newVec - initialPoint)

        else:
            raise Exception(f"{curveType.value} Curve Type Isn't Valid")

        if len(self.curvePathIntricate) and self.curvePathIntricate[-1].magnitude < self.curvePathIntricate[0].magnitude:
            self.curvePathIntricate = self.curvePathIntricate[::-1]

        blankSliderSurface = flip(blankSliderSurface, False, True)

        self.curveTexture = texture.loadTexture(imagePath="", imageLoad=blankSliderSurface)


        # (self.osupixelAdjust2, self.osupixelRatio2, self.osupixel, self.osupixelRatio),

        print("Point Diff", initialPoint - self.topleftOP)

        point = self.OPToScreen(self.topleftOP)

        newPoints = [point + initialPoint for point in self.curvePathIntricate]
        xPoints = [point.X for point in newPoints]
        yPoints = [point.Y for point in newPoints]

        self.topleftOP = vector.Vector2(min(xPoints), min(yPoints)) - vector.Vector2(round(circleRadiusOP), round(circleRadiusOP))

        #self.topleftOP = vector.Vector2(0, 0)


        #save(blankSliderSurface, f"test{index}.png")
        self.curveQuad = quadHandler.QuadWithTransparency(
            extra.generateRectangleCoordsTopLeft(
                self.OPToScreen(self.topleftOP) / self.displayV,
                self.OPSizeToScreen(self.curveSizeAdjOP) / self.displayV
            ),
            colour.Colour(*comboColourTuple),
            self.curveTexture,
            displayV,
        )

        if False:
            for point in self.curvePathIntricate:
                newPoint = point + initialPoint

                self.debugPoints.append(
                    HitCircle(
                        self.OPToScreen(newPoint),
                        vector.Vector2(circleRadiusOP / pixelExtraData[2].Y * displayV.X,
                                       circleRadiusOP / pixelExtraData[2].Y * displayV.X),
                        time,
                        approachRateTimings,
                        hitSoundPath,
                        comboColourTuple,
                        hitCircleTexture,
                        approachCircleTexture,
                        numberCircleTexture,
                        hitWindowData,
                        displayV,
                        sliderMode=True,
                        debugMode=True
                    )
                )

        print("Corner", self.curveQuad.corners)

        self.curveQuad.tweenTransparencyInfo = (0, 1)
        self.curveQuad.tweenTransparencyInfoChange = 1
        self.curveQuad.tweenTransparencyDirection = 1

        #print(curvePathIntricate)

    def OPToScreen(self, osupixel):
        return self.pixelExtraData[0] + osupixel * self.pixelExtraData[1]

    def OPSizeToScreen(self, osupixel):
        return osupixel / self.pixelExtraData[2].X * self.displayV.Y

    def step(self):
        self.curveQuad.tweenTransparencyStage = self.startHitCircle.hitCircle.tweenTransparencyStage
        self.curveQuad.updateTweenTransparency(0, fullBypass=True)

    def draw(self, time, keyboardHandler):
        if self.curveQuad and self.startHitCircle.checkForCollision:
            self.step()
            #self.curveQuad.draw()

        for dCircle in self.debugPoints:
            dCircle.draw(time, keyboardHandler)

        self.startHitCircle.draw(time, keyboardHandler)


class HealthBar:
    def __init__(self, basePath, whiteImagePath, displayV, healthDrain):
        self.health = 100

        self.origHealthDrain = healthDrain
        self.healthDrain = healthDrain

        self.loadedHealthImages = texture.loadAnimation(basePath)
        self.origSize = vector.Vector2(423/1366, 118/768)

        self.HealthBarQuad = quadHandler.QuadAnimation(
            extra.generateRectangleCoordsTopLeft(vector.Vector2(5/1366, 16/768), self.origSize),
            colour.Colour(1, 1, 1),
            self.loadedHealthImages,
            displayV
        )

        self.dryingQuadDim = 0.5
        self.dyingQuad = quadHandler.QuadWithTransparency(
            extra.generateRectangleCoords(vector.Vector2(0.5, 0.5), vector.Vector2(1, 1)),
            colour.Colour(1, 0, 0, alpha=0),
            texture.loadTexture(whiteImagePath),
            displayV
        )

        self.DEFAULT_MAX_HEALTH_INCREASE = 5
        self.DEFAULT_MAX_HEALTH_DECREASE = 5

        self.objectDensity = 1

    def setHealth(self, newHealth):
        self.health = newHealth
        self.health = max(0, min(self.health, 100))

        self.HealthBarQuad.edit2(
            extra.generateRectangleCoordsTopLeft(vector.Vector2(5/1366, 16/768), self.origSize * vector.Vector2(self.health/100, 1)),
            [(0, 0), (self.health/100, 0), (self.health/100, 1), (0, 1)]
        )

        if self.health <= 20:
            self.dyingQuad.edit(
                self.dyingQuad.corners,
                colour.Colour(1, 0, 0, alpha=extra.translate(self.health, 20, 0, 0, 0.5)),
            )

    def drain(self, objectDensity, tick):
        self.objectDensity = objectDensity

        self.setHealth(self.health - tick / 1000 * self.healthDrain)

    def objectHitMiss(self, hitObject: HitCircle):
        healthChange = 0

        hitType = hitObject.score
        hitTime = hitObject.time

        if hitType == "X":
            healthChange = -self.DEFAULT_MAX_HEALTH_DECREASE
        elif hitType == "50":
            healthChange = -self.DEFAULT_MAX_HEALTH_INCREASE * 0.05
        elif hitType == "100":
            healthChange = self.DEFAULT_MAX_HEALTH_INCREASE * 0.5
        elif hitType == "300":
            healthChange = self.DEFAULT_MAX_HEALTH_INCREASE

        self.setHealth(self.health + healthChange)
        #self.healthDrain -= healthChange

    def step(self):
        self.HealthBarQuad.stepAnimation()

    def draw(self):
        self.HealthBarQuad.draw()

        if self.health <= 20:
            self.dyingQuad.draw()

