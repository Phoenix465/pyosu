import configparser
from os import path

import numpy as np
from pygame.image import load
from pygame.mixer import music
from pygame.time import get_ticks

import Enums
import MapObjects
import colour
import extra
import gamePaths
import osureader.reader
import quadHandler
import songs
import texture
import volumeOverlayHandler
from numberShower import NumberShower
from osureader.beatmap import Beatmap
from osureader.objects import HitObjectType, SliderCircle, HitCircle
from vector import Vector2

BeatmapParser = osureader.reader.BeatmapParser()


class SceneHolder:
    class Menu:
        def __init__(self, GamePaths, displayV):
            self.displayV = displayV

            self.mainIconHitSound = volumeOverlayHandler.loadSound(GamePaths.menuHitSoundPath)
            self.menuPlayClickSound = volumeOverlayHandler.loadSound(GamePaths.menuClickSoundPath)
            self.menuExitClickSound = volumeOverlayHandler.loadSound(GamePaths.menuClickSoundPath)

            mainBackgroundTexture = texture.loadTexture(GamePaths.mainBackgroundPath)
            playButtonTexture = texture.loadTexture(GamePaths.playPath)
            exitButtonTexture = texture.loadTexture(GamePaths.exitPath)
            playFontTexture = texture.GenTextureForText("Play", GamePaths.allerFont)
            exitFontTexture = texture.GenTextureForText("Exit", GamePaths.allerFont)
            mainIconTexture = texture.loadTexture(GamePaths.iconPath)

            iconSizeY = 0.7  # Of Screen
            iconSizeReal = Vector2(iconSizeY * displayV.Y, iconSizeY * displayV.Y)
            iconSize = iconSizeReal / displayV

            self.extraSize = 0.01
            self.halfExtraSize = self.extraSize / 2

            self.backgroundQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.5, .5), Vector2(1 + self.extraSize, 1 + self.extraSize)),
                colour.Colour(255, 255, 255, convertToDecimal=True),
                mainBackgroundTexture,
                displayV
            )

            self.backgroundDimQuad = quadHandler.QuadColour(
                extra.generateRectangleCoords(Vector2(.5, .5), Vector2(1, 1)),
                colour.Colour(0, 0, 0, alpha=0),
            )

            self.mainIconQuad = quadHandler.Quad(
                extra.generateCircleCorners(Vector2(0.5, 0.5), iconSize),
                colour.Colour(255, 255, 255, convertToDecimal=True),
                mainIconTexture,
                displayV,

                collisionType=Enums.CollisionType.Circle,
                collisionRadius=1
            )
            self.mainIconQuad.tweenSizeInfo = (iconSize, iconSize * Vector2(1.1, 1.1))
            self.mainIconQuad.tweenSizeInfoChange = self.mainIconQuad.tweenSizeInfo[1] - self.mainIconQuad.tweenSizeInfo[0]
            self.mainIconQuad.tweenPosInfo = (Vector2(0.5, 0.5), Vector2(0.35, 0.5))
            self.mainIconQuad.tweenPosInfoChange = self.mainIconQuad.tweenPosInfo[1] - self.mainIconQuad.tweenPosInfo[0]

            self.playFontQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.65, .43), Vector2(0.09, 0.08)),
                colour.Colour(255, 255, 255, convertToDecimal=True),
                playFontTexture,
                displayV,
            )
            self.playQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.65, .43), Vector2(0.3, 0.12)),
                colour.Colour(102, 76, 178, convertToDecimal=True),
                playButtonTexture,
                displayV,

                collisionType=Enums.CollisionType.Box,
            )
            self.playQuad.tweenPosInfo = (Vector2(0.65, 0.43), Vector2(0.67, 0.43))
            self.playQuad.tweenPosInfoChange = self.playQuad.tweenPosInfo[1] - self.playQuad.tweenPosInfo[0]
            self.playQuad.tweenColourInfo = (
            colour.Colour(102, 76, 178, convertToDecimal=True), colour.Colour(227, 96, 154, convertToDecimal=True))
            self.playQuad.tweenColourInfoChange = self.playQuad.tweenColourInfo[1] - self.playQuad.tweenColourInfo[0]

            self.exitFontQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.65, .57), Vector2(0.09, 0.08)),
                colour.Colour(1, 1, 1),
                exitFontTexture,
                displayV,
            )
            self.exitQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.65, .57), Vector2(0.3, 0.12)),
                colour.Colour(102, 76, 178, convertToDecimal=True),
                exitButtonTexture,
                displayV,

                collisionType=Enums.CollisionType.Box,
            )
            self.exitQuad.tweenPosInfo = (Vector2(0.65, 0.57), Vector2(0.67, 0.57))
            self.exitQuad.tweenPosInfoChange = self.exitQuad.tweenPosInfo[1] - self.exitQuad.tweenPosInfo[0]
            self.exitQuad.tweenColourInfo = (
                colour.Colour(102, 76, 178, convertToDecimal=True),
                colour.Colour(227, 96, 154, convertToDecimal=True))
            self.exitQuad.tweenColourInfoChange = self.exitQuad.tweenColourInfo[1] - self.exitQuad.tweenColourInfo[0]

            self.exit = False
            self.changeMode = None

        def draw(self, MouseDataHandler, keyboardHandler):
            if music.get_busy():
                music.stop()

            self.backgroundQuad.edit(
                extra.generateRectangleCoords(Vector2(.5, .5) + MouseDataHandler.mouseAdjust, Vector2(1 + self.extraSize, 1 + self.extraSize)),
                colour.Colour(255, 255, 255, convertToDecimal=True),
            )

            self.backgroundQuad.draw()

            self.backgroundDimQuad.edit(colour.Colour(0, 0, 0, alpha=extra.translate(self.mainIconQuad.tweenPosStage, 0, 1, 0, 0.6)))
            self.backgroundDimQuad.draw()
            if self.mainIconQuad.tweenPosStage != 0:
                self.playQuad.mouseHit(MouseDataHandler.cursorPos, self.displayV, ignoreList=[self.mainIconQuad])

                if self.playQuad.collidingOnce:
                    if self.playQuad.colliding:
                        self.playQuad.tweenPosDirection = 1
                        self.playQuad.tweenColourDirection = 1

                        if self.playQuad.tweenPosStage == 0:
                            self.menuPlayClickSound.play()
                    else:
                        self.playQuad.tweenPosDirection = -1
                        self.playQuad.tweenColourDirection = -1

                if self.playQuad.colliding and keyboardHandler.mouseClick[0]:
                    self.changeMode = "select"

                if self.playQuad.tweenPosDirection == 1 and self.mainIconQuad.colliding:
                    self.playQuad.tweenPosDirection = -1
                    self.playQuad.tweenColourDirection = -1

                if not self.playQuad.colliding and self.playQuad.tweenColourStage != 0:
                    self.playQuad.tweenColourDirection = -1

                self.playQuad.updateTweenColour(0.2)
                self.playQuad.updateTweenPositionRect(0.2)
                self.playQuad.draw()

                self.playFontQuad.edit(extra.generateRectangleCoords(self.playQuad.getMiddle(), Vector2(0.09, 0.08)), self.playFontQuad.colours[0])
                self.playFontQuad.draw()

                self.exitQuad.mouseHit(MouseDataHandler.cursorPos, self.displayV, ignoreList=[self.mainIconQuad])

                if self.exitQuad.collidingOnce:
                    if self.exitQuad.colliding:
                        self.exitQuad.tweenPosDirection = 1
                        self.exitQuad.tweenColourDirection = 1

                        if self.exitQuad.tweenPosStage == 0:
                            self.menuExitClickSound.play()
                    else:
                        self.exitQuad.tweenPosDirection = -1
                        self.exitQuad.tweenColourDirection = -1

                if self.exitQuad.colliding and keyboardHandler.mouseClick[0]:
                    self.exit = True

                if self.exitQuad.tweenPosDirection == 1 and self.mainIconQuad.colliding:
                    self.exitQuad.tweenPosDirection = -1
                    self.exitQuad.tweenColourDirection = -1

                if not self.exitQuad.colliding and self.exitQuad.tweenColourStage != 0:
                    self.exitQuad.tweenColourDirection = -1

                self.exitQuad.updateTweenColour(0.2)
                self.exitQuad.updateTweenPositionRect(0.2)
                self.exitQuad.draw()
                #print(self.playQuad.tweenColourStage)

                self.exitFontQuad.edit(extra.generateRectangleCoords(self.exitQuad.getMiddle(), Vector2(0.09, 0.08)), self.exitFontQuad.colours[0])
                self.exitFontQuad.draw()

            self.mainIconQuad.mouseHit(MouseDataHandler.cursorPos, self.displayV)
            if self.mainIconQuad.collidingOnce:
                if self.mainIconQuad.colliding:
                    self.mainIconQuad.tweenSizeDirection = 1
                else:
                    self.mainIconQuad.tweenSizeDirection = -1

            if self.mainIconQuad.colliding and keyboardHandler.mouseClick[0]:
                self.mainIconQuad.tweenPosDirection = 1
                if self.mainIconQuad.tweenPosStage == 0:
                    self.mainIconHitSound.play()

            self.mainIconQuad.updateTweenSize(0.2)
            self.mainIconQuad.updateTweenPositionCircle(0.1)

            self.mainIconQuad.draw()

    class SelectSong:
        def __init__(self, GamePaths, songCache, displayV):
            self.changeMode = None

            self.songCache = songCache
            self.menuBackSound = volumeOverlayHandler.loadSound(GamePaths.menuBackSoundPath)
            self.displayV = displayV

            self.songsData = songs.loadAllSongs(GamePaths.SongsPath, cache=self.songCache)
            self.songGrouper = songs.SongHolder(self.songsData,
                                           GamePaths.menuButtonBackgroundPath,
                                           GamePaths.songBackgroundsPath,
                                           GamePaths.SongsPath,
                                           self.displayV,
                                           GamePaths.emptyPath,
                                           GamePaths.allerFont2,
                                           GamePaths.allerFont3,
                                           GamePaths.CyberbitFont,
                                           GamePaths.starPath,
                                           GamePaths.menuClickSoundPath,
                                           GamePaths.songClickSound)

            self.songGrouper.loadSongGroup(GamePaths.mainBackgroundsPath,
                                           GamePaths.mainBackgrounds)

            selectionModeImage = load(GamePaths.selectionModePath)
            selectionModeWidth, selectionModeHeight = texture.GetImageScaleSize(selectionModeImage, 0.835, displayV, heightWidthScale=False, tuple=True)

            selectionModeTexture = texture.loadTexture(GamePaths.selectionModePath, imageLoad=selectionModeImage, removeBlack=False)
            self.selectionModeQuad = quadHandler.Quad(
                [
                    Vector2(1-selectionModeWidth, 1),
                    Vector2(1, 1),
                    Vector2(1, 1-selectionModeHeight),
                    Vector2(1-selectionModeWidth, 1-selectionModeHeight),
                ],
                colour.Colour(255, 255, 255, convertToDecimal=True),
                selectionModeTexture,
                displayV
            )

            menuBackWidth = 0.18
            menuBackHeight = 0.144

            menuBackTextures = texture.loadAnimation(GamePaths.menuBackPath)
            self.menuBackQuad = quadHandler.QuadAnimation(
                [
                    Vector2(0, 1),
                    Vector2(menuBackWidth, 1),
                    Vector2(menuBackWidth, 1 - menuBackHeight),
                    Vector2(0, 1 - menuBackHeight)
                ],
                colour.Colour(255, 255, 255, convertToDecimal=True),
                menuBackTextures,
                displayV,

                collisionType=Enums.CollisionType.Box,
            )
            self.menuBackQuad.tweenColourInfo = (colour.Colour(255, 255, 255, convertToDecimal=True), colour.Colour(254, 192, 192, convertToDecimal=True))
            self.menuBackQuad.tweenColourInfoChange = self.menuBackQuad.tweenColourInfo[1] - self.menuBackQuad.tweenColourInfo[0]

            modeOsuSmallTexture = texture.loadTexture(GamePaths.modeOsuSmallPath, removeBlack=True, blackThreshold=60, blackYThreshold=118, blackIgnoreArea=[(413, 105, 380, 24)], blackRemoveArea=[(1120, 48, 265, 75)], removeArea=[(675, 721, 45, 45)])
            self.modeOsuSmallQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(0.200, 0.949), Vector2(1.005, 2)),
                colour.Colour(255, 255, 255, convertToDecimal=True),
                modeOsuSmallTexture,
                displayV
            )

            blackBlockTexture = texture.loadTexture(GamePaths.blackBlockPath)
            self.blackBlockQuad = quadHandler.Quad(
                extra.generateRectangleCoordsTopLeft(Vector2(0, 0), Vector2(1, 0.1)),
                colour.Colour(255, 255, 255, convertToDecimal=True),
                blackBlockTexture,
                displayV
            )

            self.mapData = None

        def draw(self, MouseDataHandler, keyboardHandler):
            self.songGrouper.checkBackgroundAndMusic()
            self.songGrouper.step(MouseDataHandler.cursorPos, keyboardHandler.osuKeysPressOnce, MouseDataHandler.mouseAdjust)
            self.songGrouper.searchSongs(keyboardHandler.keyPressedOnce)

            self.songGrouper.scroll(keyboardHandler.mouseScroll,
                               isRightClick=keyboardHandler.osuKeysHeld[3],
                               mouseR=MouseDataHandler.cursorPos,
                               modKeys=keyboardHandler.modKeysHold,
                               arrowKeys=keyboardHandler.arrowKeysHold
                               )

            if self.songGrouper.playMap:
                self.songGrouper.playMap = False
                self.changeMode = "playmap"
                songObject = self.songGrouper.mapObject
                songData = songObject.metadata

                self.mapData = {
                    "MapPath": songData.get('MapPath'),
                    "FolderPath": songData.get('FolderPath'),
                    "AudioFilename": songData.get('AudioFilename'),
                    "AudioLeadIn": songData.get('AudioLeadIn'),
                    "ThumbnailPath": songObject.thumbnailPath
                }

            self.menuBackQuad.stepAnimation()

            self.selectionModeQuad.mouseHit(MouseDataHandler.cursorPos, self.displayV)
            self.menuBackQuad.mouseHit(MouseDataHandler.cursorPos, self.displayV, ignoreList=[self.selectionModeQuad])

            if self.menuBackQuad.collidingOnce:
                if self.menuBackQuad.colliding:
                    self.menuBackQuad.tweenColourDirection = 1

                else:
                    self.menuBackQuad.tweenColourDirection = -1

            if self.menuBackQuad.colliding and keyboardHandler.mouseClick[0]:
                self.changeMode = "menu"
                self.menuBackSound.play()

            self.menuBackQuad.updateTweenColour(0.2)

            self.songGrouper.draw()
            self.blackBlockQuad.draw()

            self.menuBackQuad.draw()
            self.selectionModeQuad.draw()
            self.modeOsuSmallQuad.draw()
            self.songGrouper.drawSongData()

    class PlayMap:
        def __init__(self, GamePaths: gamePaths.PathHolder, displayV, mapData):
            # TODO: Add Texture Cleanup Function

            self.changeMode = None

            self.mapData = mapData
            self.displayV = displayV
            self.osupixel = Vector2(640, 480)

            self.GamePaths = GamePaths

            #screenSizeAdjustHeight = 0.85 * self.displayV.Y
            #osuScreenRatio = self.osupixel.X / self.osupixel.Y
            #screenSizeAdjustWidth = screenSizeAdjustHeight * osuScreenRatio
            screenSizeAdjust = Vector2(0.6, 0.8) * self.displayV

            self.osupixelRatio = self.displayV / Vector2(640, 480)
            self.osupixelRatio2 = screenSizeAdjust / Vector2(640, 480)
            self.osupixelAdjust2 = self.displayV/2 - screenSizeAdjust/2

            self.AudioLeadIn = int(mapData["AudioLeadIn"])
            self.audioPath = path.join(self.mapData["FolderPath"], self.mapData["AudioFilename"])

            self.backgroundTexture = texture.loadTexture(mapData["ThumbnailPath"])
            self.backgroundDim = 0.8
            self.backgroundDimStage = 0

            self.scoreBarBackgroundTexture = texture.loadTexture(GamePaths.scoreBarBackgroundPath)

            mapResult = BeatmapParser.parse(self.mapData["MapPath"])
            self.beatmap = Beatmap(mapResult)

            self.ConfigParser = configparser.ConfigParser(strict=False, comment_prefixes="=", inline_comment_prefixes="//")
            self.ConfigParser.read(GamePaths.skinIniPath)

            self.comboRange = (1, 8)
            self.comboData = []

            for comboI in range(self.comboRange[0], self.comboRange[1] + 1):
                comboName = f"Combo{comboI}"

                if self.ConfigParser.has_option("Colours", comboName):
                    comboData = self.ConfigParser.get("Colours", comboName)
                    self.comboData.append(tuple([int(data.strip()) for data in comboData.split(",")]))

            self.hitCircleTexture = texture.loadTexture(GamePaths.hitcirclePath)
            self.approachCircleTexture = texture.loadTexture(GamePaths.approachcirclePath)
            self.sliderFollowCircleTexture = texture.loadTexture(GamePaths.sliderBPath)
            self.whiteImageTexture = texture.loadTexture(GamePaths.whitecirclePath, useNearest=True)
            self.sliderBoarderPath = GamePaths.sliderBoarderPath
            self.sliderBoarderTexture = texture.loadTexture(GamePaths.sliderBoarderPath, useNearest=True)
            self.reverseArrowTexture = texture.loadTexture(GamePaths.reverseArrowPath)

            self.HitCircleObjects = []
            self.TimingPointObjects = self.beatmap.timing_objects
            self.CheckTimingPoints = self.TimingPointObjects[:]

            firstTimingPoint = self.CheckTimingPoints[0]
            self.beatLength = firstTimingPoint.beat_length
            self.meter = firstTimingPoint.meter
            self.volume = firstTimingPoint.volume
            self.sliderVelocity = 1
            self.sliderMultiplier = self.beatmap.difficult_settings.slider_multiplier


            self.ApproachRate = self.beatmap.difficult_settings.approach_rate
            self.ApproachRatePreEmpt = 0
            self.ApproachRateFadeIn = 0

            self.HealthDrain = self.beatmap.difficult_settings.hp_drain_rate
            self.score = 0
            self.scoreCombo = 0
            self.targetScore = 0
            self.scoreChange = 0

            self.newComboCount = 0

            difficultySettings = self.beatmap.difficult_settings
            hitObjects = self.beatmap.hit_objects
            breaks = self.beatmap.events_settings.breaks
            drainTime = hitObjects[-1].time - hitObjects[0].time - sum(obj.length for obj in breaks)
            self.difficultyMultiplier = round(
                (difficultySettings.hp_drain_rate +
                 difficultySettings.circle_size +
                 difficultySettings.overall_difficulty +
                 max(0, min(len(self.beatmap.hit_objects) / drainTime * 8, 16))) / 38 * 5
            )

            self.modMultiplier = 1

            if self.ApproachRate < 5:
                self.ApproachRatePreEmpt = 1200 + 600 * (5-self.ApproachRate) / 5
                self.ApproachRateFadeIn = 800 + 400 * (5-self.ApproachRate) / 5

            elif self.ApproachRate == 5:
                self.ApproachRatePreEmpt = 1200
                self.ApproachRateFadeIn = 800

            elif self.ApproachRate > 5:
                self.ApproachRatePreEmpt = 1200 - 750 * (self.ApproachRate-5) / 5
                self.ApproachRateFadeIn = 800 - 500 * (self.ApproachRate-5) / 5

            self.ApproachRateTimings = (self.ApproachRatePreEmpt, self.ApproachRateFadeIn)

            self.CircleSize = self.beatmap.difficult_settings.circle_size
            self.CircleSizeRadiusOP = 54.4 - 4.48 * self.CircleSize

            circleSizeRadiusR = self.CircleSizeRadiusOP / self.osupixel.Y
            self.circleSizeReal = Vector2(circleSizeRadiusR * displayV.X,
                                          circleSizeRadiusR * displayV.X)

            #self.CircleSizeRadiusP = Vector2(self.CircleSizeRadiusOP, self.CircleSizeRadiusOP) * self.osupixelRatio

            self.HitWindowData = {
                "50": 400 - 20 * self.beatmap.difficult_settings.overall_difficulty,
                "100": 280 - 16 * self.beatmap.difficult_settings.overall_difficulty,
                "300": 160 - 12 * self.beatmap.difficult_settings.overall_difficulty
            }

            self.DefaultValues = [
                texture.loadTexture(GamePaths.default0Path),
                texture.loadTexture(GamePaths.default1Path),
                texture.loadTexture(GamePaths.default2Path),
                texture.loadTexture(GamePaths.default3Path),
                texture.loadTexture(GamePaths.default4Path),
                texture.loadTexture(GamePaths.default5Path),
                texture.loadTexture(GamePaths.default6Path),
                texture.loadTexture(GamePaths.default7Path),
                texture.loadTexture(GamePaths.default8Path),
                texture.loadTexture(GamePaths.default9Path),
            ]

            self.ScoreTextures = {
                "300": texture.loadTexture(GamePaths.hit300Path),
                "100": texture.loadTexture(GamePaths.hit100Path),
                "50":  texture.loadTexture(GamePaths.hit50Path),
                "X":   texture.loadAnimation(GamePaths.hitXPath)
            }

            self.hitCount = {
                "X": 0,
                "50": 0,
                "100": 0,
                "300": 0,
            }

            self.hitSounds = [
                GamePaths.softHitNormalSoundPath,
                GamePaths.softHitWhistleSoundPath,
                GamePaths.softHitFinishSoundPath,
                GamePaths.softHitClapSoundPath
            ]

            self.accuracyValue = "100.00"

            currentCombo = 0

            for hitObject in self.beatmap.hit_objects:
                currentCombo += 1

                if HitObjectType.NEW_COMBO in hitObject.type:
                    self.comboData = self.comboData[1:] + [self.comboData[0]]
                    currentCombo = 0
                    self.newComboCount += 1

                if isinstance(hitObject, HitCircle):
                    hitObjectPV = hitObject.point

                    objectHitSoundType = hitObject.hitsound

                    posOP = Vector2(hitObjectPV.x, hitObjectPV.y)
                    posP = self.osupixelAdjust2 + posOP * self.osupixelRatio2

                    newHitObject = MapObjects.HitCircle(posP,
                                                        self.circleSizeReal,
                                                        hitObject.time,
                                                        self.ApproachRateTimings,
                                                        self.hitSounds[objectHitSoundType if objectHitSoundType < 4 else 0] ,
                                                        self.comboData[0],
                                                        self.hitCircleTexture,
                                                        self.approachCircleTexture,
                                                        self.DefaultValues[currentCombo % 9 + 1],
                                                        self.HitWindowData,
                                                        self.displayV)

                    self.HitCircleObjects.append(newHitObject)

                elif isinstance(hitObject, SliderCircle):
                    hitObjectPV = hitObject.point
                    objectHitSoundType = hitObject.hitsound


                    newHitObject = MapObjects.Sliders(
                        Vector2(hitObjectPV.x, hitObjectPV.y),
                        [Vector2(point.x, point.y) for point in hitObject.curve_points] ,
                        hitObject.curve_type,
                        float(hitObject.length),
                        self.CircleSizeRadiusOP,
                        displayV,
                        hitObject.time,
                        int(hitObject.slides),
                        self.ApproachRateTimings,
                        self.sliderBoarderPath,
                        self.whiteImageTexture,
                        self.sliderFollowCircleTexture,
                        self.sliderBoarderTexture,
                        self.reverseArrowTexture,
                        self.comboData[0],
                        (self.osupixelAdjust2, self.osupixelRatio2, self.osupixel, self.osupixelRatio),

                        objectHitSoundType,
                        self.hitSounds[objectHitSoundType if objectHitSoundType < 4 else 0],
                        self.hitSounds,
                        hitObject.edge_sounds,
                        self.hitCircleTexture,
                        self.approachCircleTexture,
                        self.DefaultValues[currentCombo % 9 + 1],
                        self.HitWindowData,
                    )
                    self.HitCircleObjects.append(newHitObject)


            self.objectDensity = self.newComboCount / len(self.HitCircleObjects)
            print("Object Density", self.objectDensity)
            
            backgroundH = 1
            backgroundHP = backgroundH * self.displayV.Y
            backgroundWP = backgroundHP * 16 / 9
            backgroundW = backgroundWP / self.displayV.X

            self.backgroundQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.5, .5), Vector2(backgroundW, backgroundH)),
                colour.Colour(255, 255, 255, convertToDecimal=True),
                self.backgroundTexture,
                displayV
            )

            self.backgroundDimQuad = quadHandler.QuadColour(
                extra.generateRectangleCoords(Vector2(.5, .5), Vector2(1, 1)),
                colour.Colour(0, 0, 0, alpha=self.backgroundDim),
            )

            self.scoreBarBackgroundQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(.5, .5), Vector2(1, 1)),
                colour.Colour(1, 1, 1),
                self.scoreBarBackgroundTexture,
                displayV
            )

            self.scoreNumberShower = NumberShower(GamePaths.scoreBasePath,
                                                  40/768,
                                                  Vector2(1190/1336, 0),
                                                  self.displayV,
                                                  defaultNumber="00000000")

            self.comboNumberShower = NumberShower(GamePaths.comboBasePath,
                                                  60/768,
                                                  Vector2(0, 1 - 60/768),
                                                  self.displayV,
                                                  maxDigitLength=4,
                                                  defaultNumber="0---",
                                                  imageSpacingMultiplier=0.5)

            self.accuracyNumberShower = NumberShower(GamePaths.scoreBasePath,
                                                  27/768,
                                                  Vector2(1260/1336, 45/768),
                                                  self.displayV,
                                                  defaultNumber="100.00%",
                                                  maxDigitLength=7,
                                                  extraImagePaths={
                                                      "%": GamePaths.percentSignPath,
                                                      ",": GamePaths.commaSignPath,
                                                      ".": GamePaths.dotSignPath,
                                                  })

            self.HealthBar = MapObjects.HealthBar(
                GamePaths.scorebarBasePath,
                GamePaths.whiteBlockPath,
                self.displayV,
                self.HealthDrain
            )

            self.musicPlayTime = get_ticks() + self.AudioLeadIn
            self.currentTime = get_ticks()
            self.playedMusic = False

            self.whiteTexture = texture.loadTexture(GamePaths.whiteBlockPath)
            self.extraHits = []

        def step(self, time, MouseDataHandler, delta):
            self.HealthBar.step()

            if self.backgroundDimStage <= 1:
                self.backgroundDimStage += 0.02

                self.backgroundDimQuad.edit(colour.Colour(0, 0, 0, alpha=self.backgroundDimStage*self.backgroundDim))

            if self.backgroundDimStage >= 1:
                self.HealthBar.drain(self.objectDensity, delta)

                if not self.playedMusic and self.currentTime >= self.musicPlayTime:
                    self.playedMusic = True

                    music.unload()
                    music.load(self.audioPath)
                    music.set_volume(100)
                    music.play(fade_ms=1000)

                    self.musicPlayTime = get_ticks()

            self.currentTime = get_ticks()

            if not self.playedMusic:
                return

            if len(self.CheckTimingPoints):
                timingPoint = self.CheckTimingPoints[0]
                if timingPoint.time <= time:
                    if timingPoint.uninherited:
                        self.beatLength = timingPoint.beat_length
                        self.volume = timingPoint.volume
                        self.meter = timingPoint.meter
                        self.sliderVelocity = self.sliderMultiplier
                    else:
                        # Inverse Relationship
                        self.sliderVelocity = -100/timingPoint.beat_length * self.sliderMultiplier

                    del self.CheckTimingPoints[0]

            checkHitList = []

            for i, hitObject in enumerate(self.HitCircleObjects):
                if isinstance(hitObject, MapObjects.Sliders):
                    hitObject = hitObject.startHitCircle
                
                if not hitObject.checkForCollision:
                    continue

                previousCircle = self.HitCircleObjects[i-1]
                if isinstance(previousCircle, MapObjects.Sliders):
                    previousCircle = previousCircle.startHitCircle
                
                if (i == 0 or previousCircle.clicked or previousCircle.kill or time > previousCircle.time) and not (hitObject.clicked or hitObject.kill):
                    hitObject.hitCircle.mouseHit(MouseDataHandler.cursorPos,
                                                 self.displayV,
                                                 ignoreList=checkHitList)

                    checkHitList.append(hitObject.hitCircle)
                else:
                    hitObject.hitCircle.mouseReset()

            self.score += self.scoreChange
            self.score = round(min(self.score, self.targetScore))

            scoreString = str(min(self.score, 99_999_999))
            self.scoreNumberShower.setNumber(
                "0" * (8 - len(scoreString)) + scoreString
            )

            for i, hitObject in enumerate(self.HitCircleObjects[::-1]):
                if isinstance(hitObject, MapObjects.Sliders):
                    hitObject = hitObject.startHitCircle if not hitObject.startHitCircle.kill else hitObject
                
                if hitObject.score != 0:
                    self.HealthBar.objectHitMiss(hitObject)

                    self.hitCount[hitObject.score] += 1

                    if not isinstance(hitObject, MapObjects.Sliders):
                        self.accuracyValue = (
                            self.hitCount["50"]  * 50  +
                            self.hitCount["100"] * 100 +
                            self.hitCount["300"] * 300
                        ) / (300 * (
                            self.hitCount["X"] +
                            self.hitCount["50"] +
                            self.hitCount["100"] +
                            self.hitCount["300"]
                        )) * 100

                        accuracyString = '{0:.2f}'.format(round(self.accuracyValue, 2))
                        self.accuracyNumberShower.setNumber(
                            "-"*(6-len(accuracyString)) + accuracyString + "%"
                        )

                    if hitObject.score != "X":
                        comboMultiplier = max(self.scoreCombo - 1, 0)
                        hitValue = int(hitObject.score)

                        scoreAdd = hitValue + (
                                hitValue * ((comboMultiplier * self.difficultyMultiplier * self.modMultiplier) / 25)
                        )

                        self.targetScore += scoreAdd
                        self.targetScore = round(self.targetScore)

                        self.scoreChange = (self.targetScore - self.score) / 50

                    if hitObject.score == "X":
                        self.scoreCombo = 0
                    else:
                        self.scoreCombo += 1
                        #print("COMBO NEW", hitObject.score)

                    #print(f"Score: {self.targetScore}, Combo: {self.scoreCombo}")

                    scoreString = str(min(self.scoreCombo, 9999))
                    self.comboNumberShower.setNumber(
                        scoreString + "-" * (4 - len(scoreString))
                    )

                    if hitObject.score != "300":
                        currentTexture = self.ScoreTextures[hitObject.score]

                        if isinstance(currentTexture, list):  # Animation
                            currentQuad = quadHandler.QuadAnimation(
                                extra.generateRectangleCoords(hitObject.posVec / self.displayV,
                                                              self.circleSizeReal * Vector2(1, 2) / self.displayV
                                                              ),
                                colour.Colour(1, 1, 1),
                                currentTexture,
                                self.displayV
                            )
                        else:
                            currentQuad = quadHandler.Quad(
                                extra.generateRectangleCoords(hitObject.posVec / self.displayV,
                                                              self.circleSizeReal / self.displayV
                                                              ),
                                colour.Colour(1, 1, 1),
                                currentTexture,
                                self.displayV
                            )

                       # hitObject.stopStep = True
                        hitObject.scoreObject = currentQuad
                        hitObject.scoreEnd = time + 1000

                        """self.extraHits.append(
                            quadHandler.Quad(
                                extra.generateRectangleCoords(hitObject.posVec / self.displayV,
                                                              self.circleSizeReal / self.displayV / 4
                                                              ),
                                colour.Colour(1, 1, 1),
                                self.whiteTexture,
                                self.displayV
                            )
                        )"""

                    hitObject.score = 0

                if isinstance(hitObject.scoreObject, quadHandler.QuadAnimation):
                    hitObject.scoreObject.stepAnimation(canKill=True)

                if hitObject.scoreObject and time > hitObject.scoreEnd:
                    hitObject.scoreObject = None

        def draw(self, MouseDataHandler, keyboardHandler, tick):
            if keyboardHandler.escapePressedOnce:
                self.changeMode = "select"

            time = self.currentTime - self.musicPlayTime
            #print(self.currentTime - self.musicPlayTime)
            self.step(time, MouseDataHandler, tick)

            self.backgroundQuad.draw()
            self.backgroundDimQuad.draw()
            self.scoreBarBackgroundQuad.draw()
            self.scoreNumberShower.draw()
            self.comboNumberShower.draw()
            self.accuracyNumberShower.draw()

            if not self.playedMusic:
                return

            for obj in self.extraHits:
                obj.draw()

            for i, hitObject in enumerate(self.HitCircleObjects[::-1]):
                if isinstance(hitObject, MapObjects.HitCircle):
                    hitObject.draw(self.currentTime - self.musicPlayTime,
                                   keyboardHandler)

                    if hitObject.scoreObject:
                        hitObject.scoreObject.draw()

                else:
                    hitObject.draw(self.currentTime - self.musicPlayTime,
                                   keyboardHandler,
                                   self.beatLength,
                                   self.sliderVelocity)

            self.HealthBar.draw()


    def __init__(self, GamePaths, displayV):
        self.GamePaths = GamePaths
        self.displayV = displayV

        self.songCache = None
        songCachePath = path.join(".", "cache.npy")
        if path.exists(songCachePath):
            self.songCache = np.load(songCachePath, allow_pickle=True)

        self.mode = "select"

        self.menu = self.Menu(GamePaths, displayV)
        self.select = self.SelectSong(GamePaths, self.songCache, displayV)
        self.playMapScene = None

        self.quit = False
        self.fps = 60

    def changeMode(self):
        self.quit = self.menu.exit

        if self.mode == "menu" and self.menu.changeMode:
            self.mode = self.menu.changeMode
            self.menu.changeMode = None
            self.select.menuBackQuad.stepAnimation(customFrame=0)

            self.select.songGrouper.playOnce = True

        elif self.mode == "select" and self.select.changeMode:
            self.mode = self.select.changeMode
            self.select.changeMode = None

            self.menu.mainIconQuad.tweenPosDirection = -1

        if self.mode == "playmap" and self.playMapScene is None:
            self.playMapScene = self.PlayMap(self.GamePaths,
                                             self.displayV,
                                             self.select.mapData)
            self.fps = 120

        if self.mode == "playmap" and self.playMapScene.changeMode:
            self.mode = self.playMapScene.changeMode
            self.playMapScene.changeMode = None

            self.playMapScene = None

    def draw(self, MouseDataHandler, keyboardHandler, tick):
        if self.mode == "menu":
            self.menu.draw(MouseDataHandler, keyboardHandler)

        elif self.mode == "select":
            self.select.draw(MouseDataHandler, keyboardHandler)

        elif self.mode == "playmap":
            self.playMapScene.draw(MouseDataHandler, keyboardHandler, tick)
