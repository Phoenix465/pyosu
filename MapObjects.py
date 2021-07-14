from math import pi, floor, sin, cos, ceil, atan2
from typing import List, Tuple

import bezier
import numpy as np
from pygame import Surface, SRCALPHA, transform
from pygame.image import load
from pygame.mixer import Sound
from pygame.time import get_ticks

import Enums
import colour
import extra
import osureader.objects
import quadHandler
import texture
import vector


class HitCircle:
    def __init__(self,
                 posPVec,
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

        self.reached = False

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
                    hitTimeDifference <= self.hitWindowData["50"] and "50" or "X"))

            # print("SCORED", self.score)

    def step(self, time):
        if self.fadeInStart <= time <= self.fadeInEnd or (
                time > self.fadeInEnd and self.hitCircle.tweenTransparencyStage < 1 and not self.reached):
            timeChange = time - self.fadeInStart
            stage = min(timeChange / (self.fadeInEnd - self.fadeInStart), 1)

            if stage == 1:
                self.reached = True

            self.hitCircle.tweenTransparencyStage = stage

            self.hitCircle.updateTweenTransparency(0, fullBypass=True)

            self.comboCircle.tweenTransparencyStage = stage
            self.comboCircle.updateTweenTransparency(0, fullBypass=True)

            self.approachCircle.tweenTransparencyStage = stage
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

            # print("MISSED")

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

            # print(self.time, time, time > self.fadeInEnd, "A", self.approachCircle.tweenTransparencyStage)

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
                 length: float,
                 circleRadiusOP: float,
                 displayV: vector.Vector2,
                 time: float,
                 slideCount: int,
                 approachRateTimings: tuple,
                 sliderBoarderPath: str,
                 whiteImageTexture,
                 sliderFollowTexture,
                 sliderBoarderTexture,
                 reverseArrowTexture,
                 comboColourTuple: Tuple[int, int, int],
                 pixelExtraData: Tuple[vector.Vector2, vector.Vector2, vector.Vector2, vector.Vector2],

                 objectHitSoundType,
                 hitSoundPath,
                 allHitSounds,
                 edgeSounds,
                 hitCircleTexture,
                 approachCircleTexture,
                 numberCircleTexture,
                 hitWindowData):

        self.pixelExtraData = pixelExtraData
        self.displayV = displayV

        self.length = length
        self.slides = slideCount
        self.slidesRegistered = 0

        self.startTime = time

        self.allHitSounds = allHitSounds
        self.edgeSounds = [int(sound) for sound in (edgeSounds or [objectHitSoundType]*slideCount).split("|")]
        self.loadedEdgeSounds = {edgeSound: Sound(file=self.allHitSounds[edgeSound if edgeSound < 4 else 0]) for edgeSound in self.edgeSounds}

        self.drawSlider = False

        self.initialPoint = initialPoint

        self.circleSize = vector.Vector2(circleRadiusOP / pixelExtraData[2].Y * displayV.X,
                                         circleRadiusOP / pixelExtraData[2].Y * displayV.X)

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
            # sliderMode=True
        )

        self.curveQuad = None
        self.curveSizeAdjOP = vector.Vector2(0, 0)
        self.topleftOP = vector.Vector2(0, 0)
        self.topListToInitialPoint = vector.Vector2(0, 0)

        self.curveDrawPoints = []
        self.curvePathIntricate = []

        self.sliderImage = None
        self.sliderStartOffset = None

        self.debugPoints = []

        self.score = 0
        self.scoreObject = None

        curvePoints = [initialPoint] + sliderPoints

        totalStep = ceil(length / 12)
        totalPathStep = ceil(length)

        if curveType.value == "P":
            if len(curvePoints) != 3:
                raise Exception("This shouldn't happen but Perfect Circle only has 3 points")

            centre, radius = extra.defineCircle(*curvePoints)
            # print("Centre", centre, "Radius", radius)

            # Radians
            startAngle = atan2(*(curvePoints[0] - centre).tuple)
            midAngle = atan2(*(curvePoints[1] - centre).tuple)
            endAngle = atan2(*(curvePoints[2] - centre).tuple)

            if startAngle < 0: startAngle += 2 * pi
            if midAngle < 0: midAngle += 2 * pi
            if endAngle < 0: endAngle += 2 * pi

            if startAngle > endAngle: startAngle, endAngle = endAngle, startAngle

            if not startAngle < midAngle < endAngle:
                startAngle, midAngle, endAngle = endAngle - 2 * pi, midAngle if midAngle < pi else midAngle - 2 * pi, startAngle

            startAngle, midAngle, endAngle = startAngle * 180 / pi, midAngle * 180 / pi, endAngle * 180 / pi

            jump = (endAngle - startAngle) / totalStep

            for i in range(totalStep):
                radAngle = (startAngle + i * jump) * pi / 180

                circleOffset = vector.Vector2(sin(radAngle) * radius, cos(radAngle) * radius)
                circleRealPos = centre + circleOffset

                self.curveDrawPoints.append(circleRealPos - initialPoint)

            pathJump = (endAngle - startAngle) / totalPathStep
            for i in range(totalPathStep):
                radAngle = (startAngle + i * pathJump) * pi / 180

                circleOffset = vector.Vector2(sin(radAngle) * radius, cos(radAngle) * radius)
                circleRealPos = centre + circleOffset

                self.curvePathIntricate.append(circleRealPos - initialPoint)

        elif curveType.value == "B":
            curvePointsSplit = []

            temp = []
            for i, point in enumerate(curvePoints):
                temp.append(point)

                if i + 1 != len(curvePoints) and point == curvePoints[i + 1]:
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

            curveRatioStep = [len(split) / len(curvePoints) for split in curvePointsSplit]
            curveStepPerCurve = [floor(ratio * totalStep) for ratio in curveRatioStep]
            curveIntricateStepPerCurve = [floor(ratio * totalPathStep) for ratio in curveRatioStep]

            curveSmallPoints = []
            curveIntricatePoints = []

            for i, curve in enumerate(curves):
                maxStep = curveStepPerCurve[i]
                curveTinyPoints = [curve.evaluate(s / maxStep) for s in range(maxStep + 1)]
                curveTinyPoints = map(lambda point: vector.Vector2(point[0][0], point[1][0]), curveTinyPoints)
                curveSmallPoints.extend(curveTinyPoints)

                maxIntricateStep = curveIntricateStepPerCurve[i]
                curveIntricatePoint = [curve.evaluate(s / maxIntricateStep) for s in range(maxIntricateStep + 1)]
                curveIntricatePoint = map(lambda point: vector.Vector2(point[0][0], point[1][0]), curveIntricatePoint)
                curveIntricatePoints.extend(curveIntricatePoint)

            self.curveDrawPoints = [point - initialPoint for point in curveSmallPoints]
            self.curvePathIntricate = [point - initialPoint for point in curveIntricatePoints]

        elif curveType.value == "L":
            magnitudes = [(curvePoints[i] - curvePoints[i + 1]).magnitude for i in range(len(curvePoints) - 1)]

            for i, mag in enumerate(magnitudes[:]):
                if mag == 0:
                    del magnitudes[i]
                    del curvePoints[i]

            totalMagnitude = sum(magnitudes)
            ratioMagnitude = [mag / totalMagnitude for mag in magnitudes]
            stepSplit = [ratio * totalStep for ratio in ratioMagnitude]
            stepIntricateSplit = [ratio * totalPathStep for ratio in ratioMagnitude]

            for i, point in enumerate(curvePoints[:-1]):
                step = stepSplit[i]
                stepIntricate = stepIntricateSplit[i]

                pointB = curvePoints[i + 1]

                subVec = pointB - point

                for stepI in range(ceil(step) + 1):
                    distDiv = stepI / step
                    newVec = point + (subVec * distDiv)

                    self.curveDrawPoints.append(newVec - initialPoint)

                for stepIntricateI in range(ceil(stepIntricate) + 1):
                    distDiv = stepIntricateI / stepIntricate
                    newVec = point + (subVec * distDiv)

                    self.curvePathIntricate.append(newVec - initialPoint)

        else:
            raise Exception(f"{curveType.value} Curve Type Isn't Valid")

        if len(self.curveDrawPoints) and self.curveDrawPoints[-1].magnitude < self.curveDrawPoints[0].magnitude:
            self.curveDrawPoints = self.curveDrawPoints[::-1]

        if len(self.curvePathIntricate) and self.curvePathIntricate[-1].magnitude < self.curvePathIntricate[
            0].magnitude:
            self.curvePathIntricate = self.curvePathIntricate[::-1]

        # print(time, len(self.curvePathIntricate), self.curvePathIntricate)

        self.drawPoints = []
        self.kill = False

        currentInitialPoint = initialPoint
        tempRealPoints = [point + currentInitialPoint for point in self.curvePathIntricate]
        xPoints = [point.X for point in tempRealPoints]
        yPoints = [point.Y for point in tempRealPoints]
        normalSize = vector.Vector2(max(xPoints) - min(xPoints),
                                    max(yPoints) - min(yPoints)) + vector.Vector2(floor(2 * circleRadiusOP),
                                                                                  floor(2 * circleRadiusOP))

        topLeftPoint = vector.Vector2(min(xPoints), min(yPoints))

        mainSurface = Surface((normalSize * 2).tuple, SRCALPHA)
        boarderSurface = Surface((normalSize * 2).tuple, SRCALPHA)

        whiteCircleImage = load(sliderBoarderPath)
        size = vector.Vector2(floor(circleRadiusOP * 2), floor(circleRadiusOP * 2)) * 2
        realSize = vector.Vector2(circleRadiusOP * 2, circleRadiusOP * 2)

        boarderImage = Surface(size.tuple, SRCALPHA)
        boarderSize = vector.Vector2(floor(size.X * 0.95), floor(size.Y * 0.95))
        boarderScale = transform.scale(whiteCircleImage, boarderSize.tuple)
        boarderImage.blit(boarderScale, (size / 2 - boarderSize / 2).tuple)

        insideImage = Surface(size.tuple, SRCALPHA)
        imageSize = vector.Vector2(floor(size.X * 0.85), floor(size.Y * 0.85))
        insideScale = transform.scale(whiteCircleImage, imageSize.tuple)
        insideImage.blit(insideScale, (size / 2 - imageSize / 2).tuple)

        for point in tempRealPoints:
            imageRelPoint = point - topLeftPoint

            mainSurface.blit(insideImage, (imageRelPoint * 2).tuple)
            boarderSurface.blit(boarderImage, (imageRelPoint * 2).tuple)

        topLeftPointAdj = topLeftPoint + vector.Vector2(3, 3)
        self.sliderMainQuad = quadHandler.QuadWithTransparency(
            extra.generateRectangleCoordsTopLeft(
                self.OPToScreen(topLeftPointAdj - realSize / 2) / displayV,
                self.OPSizeToScreen(normalSize) / displayV
            ),
            colour.Colour(0, 0, 0, convertToDecimal=True),
            texture.loadTexture("", imageLoad=mainSurface),
            displayV
        )

        self.sliderMainQuad.tweenTransparencyInfo = (0, 1)
        self.sliderMainQuad.tweenTransparencyInfoChange = 1
        self.sliderMainQuad.tweenTransparencyDirection = 1

        self.sliderBoarderQuad = quadHandler.QuadWithTransparency(
            extra.generateRectangleCoordsTopLeft(
                self.OPToScreen(topLeftPointAdj - realSize / 2) / displayV,
                self.OPSizeToScreen(normalSize) / displayV
            ),
            colour.Colour(102, 100, 99, convertToDecimal=True),
            texture.loadTexture("", imageLoad=boarderSurface),
            displayV
        )

        self.sliderBoarderQuad.tweenTransparencyInfo = (0, 1)
        self.sliderBoarderQuad.tweenTransparencyInfoChange = 1
        self.sliderBoarderQuad.tweenTransparencyDirection = 1

        self.repeatSliderQuad = quadHandler.Quad(
            extra.generateCircleCorners(
                self.OPToScreen(initialPoint) / displayV,
                self.circleSize / displayV
            ),
            colour.Colour(1, 1, 1),
            reverseArrowTexture,
            displayV
        )
        self.drawRepeat = False

        #self.repeatSliderQuad.tweenTransparencyInfo = (0, 1)
        #self.repeatSliderQuad.tweenTransparencyInfoChange = 1
        #self.repeatSliderQuad.tweenTransparencyDirection = 1

        self.sliderBQuad = quadHandler.Quad(
            extra.generateCircleCorners(
                self.OPToScreen(initialPoint) / displayV,
                self.circleSize / displayV
            ),
            colour.Colour(*comboColourTuple),
            sliderFollowTexture,
            displayV
        )

        self.sliderBIndexHistory = []


        DRAW = False

        if DRAW:
            for point in self.curveDrawPoints:
                newPoint = point + initialPoint

                newQuad = quadHandler.QuadWithTransparency(
                    extra.generateCircleCorners(
                        self.OPToScreen(newPoint) / displayV,
                        self.circleSize * 0.9 / displayV
                    ),
                    colour.Colour(102, 100, 99, convertToDecimal=True),
                    sliderBoarderTexture,
                    displayV
                )

                newQuad.tweenTransparencyInfo = (0, 1)
                newQuad.tweenTransparencyInfoChange = 1
                newQuad.tweenTransparencyDirection = 1

                self.drawPoints.append(newQuad)

            for point in self.curveDrawPoints:
                newPoint = point + initialPoint

                newQuad = quadHandler.QuadWithTransparency(
                    extra.generateCircleCorners(
                        self.OPToScreen(newPoint) / displayV,
                        self.circleSize * 0.8 / displayV
                    ),
                    colour.Colour(50, 50, 50, convertToDecimal=True),
                    whiteImageTexture,
                    displayV
                )

                newQuad.tweenTransparencyInfo = (0, 1)
                newQuad.tweenTransparencyInfoChange = 1
                newQuad.tweenTransparencyDirection = 1

                self.drawPoints.append(newQuad)

        # print(curveDrawPoints)

    def OPToScreen(self, osupixel):
        return self.pixelExtraData[0] + osupixel * self.pixelExtraData[1]

    def OPSizeToScreen(self, osupixel):
        return osupixel / self.pixelExtraData[2].X * self.displayV.Y

    def step(self, time, beatLength, sliderMultiplier):
        extraTime = self.length / (sliderMultiplier * 100) * beatLength
        endTime = self.startTime + extraTime * self.slides

        timeLeft = endTime - time
        timeLeftSlide = timeLeft % extraTime

        if time >= self.startTime:
            tempSliderRegistered = (time - self.startTime) // extraTime

            if tempSliderRegistered != self.slidesRegistered:
                self.score = "300"
                self.loadedEdgeSounds[self.edgeSounds[floor(self.slidesRegistered)]].play()

            self.slidesRegistered = tempSliderRegistered

            if self.slidesRegistered+1 < self.slides:
                self.drawRepeat = True

                posIndex = 0 if self.slidesRegistered % 2 else len(self.curvePathIntricate) - 1
                pointA = self.curvePathIntricate[posIndex]
                pointB = self.curvePathIntricate[posIndex + (1 if self.slidesRegistered % 2 else -1)]

                angle = atan2(pointB.Y - pointA.Y, pointB.X - pointA.X) * 180 / pi

                self.repeatSliderQuad.edit(
                    [point/self.displayV for point in extra.generateCircleCornersRotation(
                        self.OPToScreen(pointA + self.initialPoint),
                        self.circleSize.X,
                        angle
                    )],
                    colour.Colour(1, 1, 1)
                )
                self.repeatSliderPos = pointA + self.initialPoint

        if time > endTime:
            self.drawSlider = False
            self.kill = True

        if self.startTime < time <= endTime:
            if self.slidesRegistered % 2:  # Even
                currentPositionIndex = floor(timeLeftSlide / extraTime * len(self.curvePathIntricate))
            else:
                currentPositionIndex = floor((1 - timeLeftSlide / extraTime) * len(self.curvePathIntricate))

            currentPosition = self.curvePathIntricate[currentPositionIndex] + self.initialPoint

            self.sliderBQuad.edit(
                extra.generateCircleCorners(
                    self.OPToScreen(currentPosition) / self.displayV,
                    self.circleSize / self.displayV
                ),
                colour.Colour(1, 1, 1),
            )

        if not self.startHitCircle.reached and self.startHitCircle.hitCircle.tweenTransparencyStage != 0:
            for quad in self.drawPoints:
                quad.tweenTransparencyStage = self.startHitCircle.hitCircle.tweenTransparencyStage
                quad.updateTweenTransparency(0, fullBypass=True)

            self.sliderMainQuad.tweenTransparencyStage = self.startHitCircle.hitCircle.tweenTransparencyStage
            self.sliderMainQuad.updateTweenTransparency(0, fullBypass=True)

            self.sliderBoarderQuad.tweenTransparencyStage = self.startHitCircle.hitCircle.tweenTransparencyStage
            self.sliderBoarderQuad.updateTweenTransparency(0, fullBypass=True)

    def draw(self, time, keyboardHandler, beatLength, sliderMultiplier):
        if self.kill:
            return

        if self.drawSlider:
            self.step(time, beatLength, sliderMultiplier)
            for point in self.drawPoints:
                point.draw()

            self.sliderBoarderQuad.draw()
            self.sliderMainQuad.draw()

            if self.drawRepeat:
                self.repeatSliderQuad.draw()

            self.sliderBQuad.draw()

        if self.startHitCircle.checkForCollision:
            self.drawSlider = True

        self.startHitCircle.draw(time, keyboardHandler)


class HealthBar:
    def __init__(self, basePath, whiteImagePath, displayV, healthDrain):
        self.health = 100

        self.origHealthDrain = healthDrain
        self.healthDrain = healthDrain

        self.loadedHealthImages = texture.loadAnimation(basePath)
        self.origSize = vector.Vector2(423 / 1366, 118 / 768)

        self.HealthBarQuad = quadHandler.QuadAnimation(
            extra.generateRectangleCoordsTopLeft(vector.Vector2(5 / 1366, 16 / 768), self.origSize),
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
            extra.generateRectangleCoordsTopLeft(vector.Vector2(5 / 1366, 16 / 768),
                                                 self.origSize * vector.Vector2(self.health / 100, 1)),
            [(0, 0), (self.health / 100, 0), (self.health / 100, 1), (0, 1)]
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

        if hitType == "X":
            healthChange = -self.DEFAULT_MAX_HEALTH_DECREASE
        elif hitType == "50":
            healthChange = -self.DEFAULT_MAX_HEALTH_INCREASE * 0.05
        elif hitType == "100":
            healthChange = self.DEFAULT_MAX_HEALTH_INCREASE * 0.5
        elif hitType == "300":
            healthChange = self.DEFAULT_MAX_HEALTH_INCREASE

        self.setHealth(self.health + healthChange)
        # self.healthDrain -= healthChange

    def step(self):
        self.HealthBarQuad.stepAnimation()

    def draw(self):
        self.HealthBarQuad.draw()

        if self.health <= 20:
            self.dyingQuad.draw()
