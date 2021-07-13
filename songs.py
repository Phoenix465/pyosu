import os
from math import floor
from random import randint, choice

from time import time

from OpenGL.GL import glDeleteTextures
from pygame import sndarray, mixer
from pygame.key import name
from pygame.mixer import music
from pygame.font import Font
from pygame.image import load

import Enums
import texture
import extra
import quadHandler
from osuSRCalculator import calculateStarRating
from osureader.beatmap import Beatmap
from osureader.objects import SliderCircle, HitObjectType, HitCircle
from osureader.reader import BeatmapParser
from vector import Vector2
import colour
import os.path as path
import numpy as np

from volumeOverlayHandler import loadSound

sectionType = [
    'General',
    'Editor',
    'Metadata',
    'Difficulty',
    'Events',
    'TimingPoints',
    'Colours',
    'HitObjects'
]
validImages = [".jpg", ".gif", ".png", ".tga"]


def loadFolder(folderPath, cache):
    folderSongData = []

    for file in os.listdir(folderPath):
        if file.endswith(".osu"):
            lookMeta = False
            lookVideoBackground = False
            lookVideoBackgroundCommentCount = 0
            lookVideoBackgroundLineCount = 0
            lookDiff = False
            validFile = False
            metadata = {}

            mapPath = os.path.join(folderPath, file)

            fileData = open(mapPath, 'r', encoding="utf8").readlines()
            for line in fileData:
                if sectionType[1] in line:
                    lookMeta = False

                elif sectionType[3] in line:
                    lookMeta = False

                elif sectionType[4] in line:
                    lookDiff = False

                elif sectionType[5] in line:
                    break

                if (lookMeta or lookDiff) and line != "\n" and line[0] != "[":
                    line = line.replace("\n", "")

                    currentData = line.split(":", 1)
                    metadata[currentData[0]] = currentData[1].strip()

                elif lookVideoBackground and line != "\n":
                    if "//" in line:
                        lookVideoBackgroundCommentCount += 1

                        if lookVideoBackgroundCommentCount >= 2:
                            break

                        continue

                    lookVideoBackgroundLineCount += 1

                    metadata[f"Event{lookVideoBackgroundLineCount}"] = line.replace("\n", "")

                if sectionType[0] in line:
                    lookMeta = True

                elif sectionType[1] in line:
                    lookMeta = True

                elif sectionType[3] in line:
                    lookDiff = True

                elif sectionType[4] in line:
                    lookVideoBackground = True

                elif "Mode" in line and "0" in line:
                    validFile = True

            if validFile and metadata:
                # s = time()
                # print(mapPath, metadata)
                if not cache or file not in cache:
                    try:
                        actualBeatmapDifficulty = calculateStarRating(filepath=mapPath)
                        cache[file] = actualBeatmapDifficulty
                    except Exception as e:
                        continue
                else:
                    actualBeatmapDifficulty = cache[file]

                metadata["RealStarDifficulty"] = round(actualBeatmapDifficulty["nomod"], 2)
                metadata["MapPath"] = mapPath
                metadata["FolderPath"] = folderPath
                # print("Real Star Diff", mapPath, actualBeatmapDifficulty, round(1000 * (time() - s)))

                if not "ApproachRate" in metadata:
                    metadata["ApproachRate"] = metadata["OverallDifficulty"]

                folderSongData.append((file, metadata))

                # print(file, metadata["OverallDifficulty"])

    return folderSongData


def loadAllSongs(songsPath, cache=None):
    s = time()

    songsData = {}

    songFolders = os.listdir(songsPath)
    currentCache = cache or np.array([{}])

    for songFolder in songFolders:
        songPath = os.path.join(songsPath, songFolder)

        if os.path.isdir(songPath):
            songData = loadFolder(songPath, cache=currentCache[0])
            if len(songData):
                songsData[songFolder] = songData

    print("Saving Cache")
    np.save('./cache', currentCache)
    print("Finished Saving Cache")

    e = time() - s
    print(f"Load All Songs Took: {round(e * 1000)}ms")

    return songsData


def getResizedSound(sound, seconds):
    frequency, bits, channels = mixer.get_init()

    # Determine silence value
    silence = 0 if bits < 0 else (2 ** bits / 2) - 1

    # Get raw sample array of original sound
    oldArray = sndarray.array(sound)

    # Create silent sample array with desired length
    newSampleCount = int(seconds * frequency)
    newShape = (newSampleCount,) + oldArray.shape[1:]
    newArray = np.full(newShape, silence, dtype=oldArray.dtype)

    # Copy original sound to the beginning of the
    # silent array, clipping the sound if it is longer
    newArray[:oldArray.shape[0]] = oldArray[:newArray.shape[0]]

    return mixer.Sound(newArray)


class SongButton:
    def __init__(self, songTitle, miniTitle, songData, displayV, defaultTexture, thumbnailPath, emptyTexture,
                 buttonSize, fontPath, songFolder, clickSound, isSong=False, version="", xOffset=0, difficulty="0",
                 starPath="", metadata=None, mapPath=""):
        self.title = songTitle
        self.mini = miniTitle

        self.emptyTexture = emptyTexture
        self.thumbnailPath = thumbnailPath
        self.songData = songData
        self.songFolder = songFolder

        self.metadata = metadata
        self.mapPath = mapPath

        self.clickSound = clickSound

        self.xOffset = xOffset
        self.difficulty = difficulty

        self.starPath = starPath

        self.isSong = isSong
        self.version = version

        # print("Path", self.thumbnailPath)
        self.buttonSize = buttonSize
        self.thumbnailSize = self.buttonSize * Vector2(1 / 6, 0.925)

        self.buttonQuad = quadHandler.Quad(
            extra.generateRectangleCoords(Vector2(0.2015, 0.5), self.buttonSize),
            colour.Colour(1, 1, 1),
            defaultTexture,
            displayV,

            customTextureCorner=[(0, 8 / 110), (1, 8 / 110), (1, 102 / 110), (0, 102 / 110)],
            collisionType=Enums.CollisionType.Box
        )

        self.thumbnailQuad = quadHandler.Quad(
            extra.generateRectangleCoords(Vector2(0.2015, 0.5), self.thumbnailSize),
            colour.Colour(1, 1, 1),
            emptyTexture,
            displayV
        )

        self.collideStage = 0

        self.titleRender = texture.GenFontSurface(self.title, fontPath)  # 22/90 height
        titleHeight = 22 / 90 * self.buttonSize.Y
        titleHeightP = titleHeight * displayV.Y
        titleRatio = self.titleRender.get_width() / self.titleRender.get_height()
        titleWidthP = titleRatio * titleHeightP
        titleWidth = titleWidthP / displayV.X
        self.titleSize = Vector2(titleWidth, titleHeight)

        self.miniTitleRender = texture.GenFontSurface(self.mini, fontPath)  # 16/90
        miniHeight = 16 / 90 * self.buttonSize.Y
        miniHeightP = miniHeight * displayV.Y
        miniRatio = self.miniTitleRender.get_width() / self.miniTitleRender.get_height()
        miniWidthP = miniRatio * miniHeightP
        miniWidth = miniWidthP / displayV.X
        self.miniSize = Vector2(miniWidth, miniHeight)

        self.versionTitleRender = texture.GenFontSurface(self.version, fontPath)  # 16/90
        versionHeight = 16 / 90 * self.buttonSize.Y
        versionHeightP = versionHeight * displayV.Y
        versionRatio = self.versionTitleRender.get_width() / self.versionTitleRender.get_height()
        versionWidthP = versionRatio * versionHeightP
        versionWidth = versionWidthP / displayV.X
        self.versionSize = Vector2(versionWidth, versionHeight)

        if self.starPath != "":
            self.difficultyTitleRender = texture.GenerateDifficultyTexture(float(self.difficulty), starPath)  # 16/90
            difficultyHeight = 16 / 90 * self.buttonSize.Y
            difficultyHeightP = difficultyHeight * displayV.Y
            difficultyRatio = self.difficultyTitleRender.get_width() / self.difficultyTitleRender.get_height()
            difficultyWidthP = difficultyRatio * difficultyHeightP
            difficultyWidth = difficultyWidthP / displayV.X
            self.difficultySize = Vector2(difficultyWidth, difficultyHeight)

        self.displayV = displayV

        self.titleRenderTexture = texture.loadTexture("", imageLoad=self.titleRender)
        self.miniTitleRenderTexture = texture.loadTexture("", imageLoad=self.miniTitleRender)
        self.versionTitleRenderTexture = texture.loadTexture("", imageLoad=self.versionTitleRender)

        if self.starPath != "":
            self.difficultyTitleRenderTexture = texture.loadTexture("", imageLoad=self.difficultyTitleRender)

        # 620 width 129 maybe dist
        self.titleQuad = quadHandler.Quad(
            extra.generateRectangleCoords(Vector2(0.2015, 0.5), self.titleSize),
            colour.Colour(1, 1, 1),
            self.titleRenderTexture,
            displayV
        )

        self.miniQuad = quadHandler.Quad(
            extra.generateRectangleCoords(Vector2(0.2015, 0.5), self.miniSize),
            colour.Colour(1, 1, 1),
            self.miniTitleRenderTexture,
            displayV
        )

        self.versionQuad = quadHandler.Quad(
            extra.generateRectangleCoords(Vector2(0.2015, 0.5), self.versionSize),
            colour.Colour(1, 1, 1),
            self.versionTitleRenderTexture,
            displayV
        )

        if self.starPath != "":
            self.difficultyQuad = quadHandler.Quad(
                extra.generateRectangleCoords(Vector2(0.2015, 0.5), self.difficultySize),
                colour.Colour(1, 1, 1),
                self.difficultyTitleRenderTexture,
                displayV
            )

        # 93 86 0.925
        # 685 114 0.1666 (1/6)

    def update(self, newCentre):
        self.buttonQuad.edit(
            extra.generateRectangleCoords(newCentre, self.buttonSize),
            colour.Colour(1, 1, 1),
        )

        self.thumbnailQuad.edit(
            extra.generateRectangleCoords(newCentre - Vector2(0.1, 0), self.thumbnailSize),
            colour.Colour(1, 1, 1),
        )

        self.titleQuad.edit(
            extra.generateRectangleCoords(
                newCentre - Vector2(0.35 * self.buttonSize.X - self.titleSize.X / 2, 0.275 * self.buttonSize.Y),
                self.titleSize),
            colour.Colour(1, 1, 1),
        )

        self.miniQuad.edit(
            extra.generateRectangleCoords(
                newCentre - Vector2(0.34 * self.buttonSize.X - self.miniSize.X / 2, 0.075 * self.buttonSize.Y),
                self.miniSize),
            colour.Colour(1, 1, 1),
        )

        self.versionQuad.edit(
            extra.generateRectangleCoords(
                newCentre - Vector2(0.34 * self.buttonSize.X - self.versionSize.X / 2, -0.125 * self.buttonSize.Y),
                self.versionSize),
            colour.Colour(1, 1, 1),
        )

        if self.starPath != "":
            self.difficultyQuad.edit(
                extra.generateRectangleCoords(
                    newCentre - Vector2(0.34 * self.buttonSize.X - self.difficultySize.X / 2, -0.3 * self.buttonSize.Y),
                    self.difficultySize),
                colour.Colour(1, 1, 1),
            )

    def draw(self):
        self.buttonQuad.draw()
        self.titleQuad.draw()
        self.miniQuad.draw()

        if self.version != "":
            self.versionQuad.draw()

        if self.starPath != "":
            self.difficultyQuad.draw()

        # self.thumbnailQuad.draw()

    def __repr__(self):
        return f"SongButton(title='{self.title}')"


class SongHolder:
    def __init__(self, songData, menuButtonBackgroundPath, songBackgroundPaths, songsPath, displayV, emptyTexturePath,
                 fontPath, fontPath2, unicodeFontPath, starPath, clickSoundPath, songClickSoundPath):
        self.songData: dict = songData
        self.songBackgroundPaths = songBackgroundPaths
        self.displayV = displayV
        self.songsPath = songsPath
        self.buttonSize = Vector2(0.5, 0.12)
        self.fontPath = fontPath
        self.fontPath2 = fontPath2

        self.clickSoundPath = clickSoundPath

        self.songClickSound = loadSound(songClickSoundPath)

        self.unicodeFontPath = unicodeFontPath
        self.unicodeFont = Font(self.unicodeFontPath, 64)
        self.unicodeFont.set_bold(True)

        self.normalFont = Font(self.fontPath, 64)
        self.normalFont2 = Font(self.fontPath2, 64)

        self.starPath = starPath

        self.beatmapParser = BeatmapParser()

        # 770 93 ~ 0.12

        self.newImage = texture.loadTexture(menuButtonBackgroundPath, alpha=240)
        self.oldImage = texture.loadTexture(menuButtonBackgroundPath, alpha=240, hueAdjust=40 / 360)
        self.songImage = texture.loadTexture(menuButtonBackgroundPath, alpha=240, hueAdjust=220 / 360)
        self.emptyTexture = texture.loadTexture(emptyTexturePath)

        self.backgroundPath = emptyTexturePath
        self.backgroundTexture = texture.loadTexture(emptyTexturePath)

        self.extraSize = 0.01
        self.halfExtraSize = self.extraSize / 2

        self.backgroundQuad = quadHandler.Quad(
            extra.generateRectangleCoords(Vector2(.5, .5), Vector2(1 + self.extraSize, 1 + self.extraSize)),
            colour.Colour(255, 255, 255, convertToDecimal=True),
            self.backgroundTexture,
            displayV
        )
        self.backgroundSize = Vector2(1 + self.extraSize, 1 + self.extraSize)

        self.backgroundDimQuad = quadHandler.QuadColour(
            extra.generateRectangleCoords(Vector2(.5, .5), Vector2(1, 1)),
            colour.Colour(0, 0, 0, alpha=0.4),
        )

        self.songDataQuad = []

        self.allSongOrderObjects = []
        self.origSongOrderObjects = []
        self.songOrderObjects = []

        self.scrollStage = 0

        self.scrollAccel = 0
        self.scrollVel = 0

        self.scrollAccelValue = 0
        self.currentSongIndex = 0

        self.loadSongScrollStage = 0
        self.loadSongScrollAccel = 0
        self.oldScrollSongObj = []
        self.onceClick = True

        self.volume = 1
        self.currentSongPath = ""
        self.playOnce = False

        self.renderObjects = []

        self.oldCurrentSongIndex = 0
        self.songIndex = 0
        self.topRender = 0
        self.bottomRender = 0

        self.collisionData = (None, None)
        self.searchString = ""
        self.oldSearchString = ""
        self.firstSearch = True

        searchTexture, self.searchSize = texture.GenTextTextureSize(self.searchString, 0.03, self.displayV, "",
                                                                         fontLoad=self.normalFont2)

        self.searchPos = Vector2(0.795, 0.115)
        self.searchQuad = quadHandler.Quad(
            extra.generateRectangleCoordsTopLeft(self.searchPos, self.searchSize),
            colour.Colour(1, 1, 1),
            searchTexture,
            displayV
        )

        self.mapObject = None
        self.playMap = False

    def loadSongGroup(self, backgroundPath, backgroundList):
        for songGroup, songData in self.songData.items():
            songId = songGroup.split(" ", 1)[0]
            songThumbnail = f"{songId}.jpg"
            songThumbnailPath = path.join(self.songBackgroundPaths, songThumbnail)

            songFolder = path.join(self.songsPath, songGroup)

            names = []
            for mapData in songData:
                metaData = mapData[1]
                backgroundString = ""

                if "Event1" in metaData and "Video" not in metaData["Event1"]:
                    backgroundString = metaData["Event1"]
                elif "Event2" in metaData and "Video" not in metaData["Event2"]:
                    backgroundString = metaData["Event2"]

                # print(metaData)
                if backgroundString != "":
                    backgroundPath = backgroundString.split('"')[1]

                    if backgroundPath not in names:
                        names.append(backgroundPath)

            pathExists = path.exists(songThumbnailPath)

            if not pathExists and len(names) > 0:
                songThumbnailPath = path.join(songFolder, names[0])
            elif pathExists and len(names) > 0:
                songThumbnailPath = path.join(songFolder, names[0])
            else:
                songThumbnailPath = path.join(backgroundPath, choice(backgroundList))
                print("Flagged", songGroup, songThumbnailPath, names)
                continue

            """s = time()
            test = texture.loadTexture(songThumbnailPath)
            e = time() - s
            print(f"Background Load: {round(e*1000)}ms")"""

            firstSongData = songData[0][1]
            songTitle = firstSongData["Title"].strip()
            miniTitle = f"{firstSongData['Artist']} // {firstSongData['Creator']}".strip()

            self.songOrderObjects.append(
                #     def __init__(self, songData, menuButtonBackgroundPath, songBackgroundPaths, songsPath, displayV, emptyTexturePath, fontPath):
                SongButton(songTitle, miniTitle, songData, self.displayV, self.oldImage, songThumbnailPath,
                           self.emptyTexture, self.buttonSize, self.fontPath, songFolder,
                           loadSound(self.clickSoundPath))
            )

        self.origSongOrderObjects = sorted(self.songOrderObjects, key=lambda obj: obj.title.lower())[::-1]
        self.allSongOrderObjects = self.origSongOrderObjects

        self.songOrderObjects = self.origSongOrderObjects

        self.scrollAccelValue = 1 / len(self.songOrderObjects) / 5

        self.oldCurrentSongIndex = len(self.songOrderObjects) + 1
        self.currentSongIndex = 0  # randint(0, len(self.songOrderObjects)-1)
        self.clickCurrentSongIndex = 0
        self.scrollStage = self.currentSongIndex / len(self.songOrderObjects)

        # from pprint import pprint
        # pprint(self.songOrderObjects)

    def drawSongData(self):
        for quad in self.songDataQuad:
            quad.draw()

        self.searchQuad.draw()

    def checkBackgroundAndMusic(self):
        if self.oldCurrentSongIndex != self.currentSongIndex:
            songObj = self.songOrderObjects[self.currentSongIndex]

            if songObj.thumbnailPath != self.backgroundPath:
                self.backgroundPath = songObj.thumbnailPath
                backgroundH = 1 + self.extraSize
                backgroundHP = backgroundH * self.displayV.Y
                backgroundWP = backgroundHP * 16 / 9
                backgroundW = backgroundWP / self.displayV.X

                glDeleteTextures(1, [self.backgroundQuad.vbo.texture])
                self.backgroundTexture = texture.loadTexture(self.backgroundPath)
                self.backgroundQuad.edit(
                    extra.generateRectangleCoordsTopLeft(Vector2(0, 0), Vector2(backgroundW, backgroundH)),
                    colour.Colour(1, 1, 1),
                )
                self.backgroundSize = Vector2(backgroundW, backgroundH)

                self.backgroundQuad.vbo.texture = self.backgroundTexture

        if self.playOnce and self.currentSongPath != "":
            self.playOnce = False

            music.unload()
            music.load(self.currentSongPath)
            music.set_volume(self.volume)
            music.play(loops=-1, fade_ms=1000)

    def step(self, cursorPos, osuClickState, mouseAdjust):
        self.backgroundQuad.edit(
            extra.generateRectangleCoords(Vector2(.5, .5) + mouseAdjust,
                                          self.backgroundSize),
            colour.Colour(255, 255, 255, convertToDecimal=True),
        )

        self.oldCurrentSongIndex = self.currentSongIndex

        self.songIndex = self.scrollStage * len(self.songOrderObjects)

        self.topRender = min(floor(self.songIndex) + 4, len(self.songOrderObjects))
        self.bottomRender = max(floor(self.songIndex) - 4, 0)

        self.renderObjects = self.songOrderObjects[self.bottomRender:self.topRender]
        self.oldScrollSongObj = self.renderObjects

        self.collisionData = None

        # Check for MAP playing
        for songObj in self.renderObjects:
            if songObj.buttonQuad.colliding and osuClickState[2] and songObj.buttonQuad.vbo.texture is self.newImage:
                self.playMap = True
                self.mapObject = songObj

        # Collision Etc
        for songI, songObj in enumerate(self.renderObjects, start=self.bottomRender):
            songObj.buttonQuad.mouseHit(cursorPos, self.displayV)
            if songObj.buttonQuad.colliding:
                if songObj.collideStage == 0:
                    songObj.clickSound.play()
                songObj.collideStage += 0.05
            else:
                songObj.collideStage -= 0.05

            if songObj.buttonQuad.colliding and osuClickState[2] or self.onceClick:
                self.songClickSound.play()

                self.onceClick = False

                if len(self.songOrderObjects) > self.currentSongIndex:
                    oldClickObject = self.songOrderObjects[self.currentSongIndex]
                    oldClickObject.buttonQuad.vbo.texture = oldClickObject.buttonQuad.texture

                if not songObj.isSong:
                    for songObj2 in self.songOrderObjects:
                        if songObj2 not in self.origSongOrderObjects:
                            if songObj2.starPath != "":
                                glDeleteTextures(4, [songObj2.titleRenderTexture, songObj2.miniTitleRenderTexture,
                                                     songObj2.versionTitleRenderTexture,
                                                     songObj2.difficultyTitleRenderTexture])
                            else:
                                glDeleteTextures(3, [songObj2.titleRenderTexture, songObj2.miniTitleRenderTexture,
                                                     songObj2.versionTitleRenderTexture])

                            del songObj2

                    self.songOrderObjects = self.origSongOrderObjects
                    adjSongI = self.songOrderObjects.index(songObj)
                    leftSide, rightSide = self.songOrderObjects[:adjSongI], self.songOrderObjects[adjSongI + 1:]
                    middleSide = []

                    # print(songObj.songData)

                    for (mapLongName, mapMetadata) in songObj.songData[::-1]:
                        backgroundString = ""

                        if "Event1" in mapMetadata and "Video" not in mapMetadata["Event1"]:
                            backgroundString = mapMetadata["Event1"]
                        elif "Event2" in mapMetadata and "Video" not in mapMetadata["Event2"]:
                            backgroundString = mapMetadata["Event2"]

                        backgroundPath = ""
                        if backgroundString != "":
                            backgroundPath = backgroundString.split('"')[1]

                        #     def __init__(self, songData, menuButtonBackgroundPath, songBackgroundPaths, songsPath, displayV, emptyTexturePath, fontPath):
                        # print("Star Diff", mapMetadata["RealStarDifficulty"])
                        newSongObj = SongButton(songObj.title + "", songObj.mini, songObj.songData, self.displayV,
                                                self.songImage, path.join(songObj.songFolder, backgroundPath),
                                                self.emptyTexture, self.buttonSize, self.fontPath, songObj.songFolder,
                                                loadSound(self.clickSoundPath), isSong=True,
                                                version=mapMetadata["Version"], xOffset=0.02,
                                                difficulty=mapMetadata["RealStarDifficulty"],
                                                starPath=self.starPath, metadata=mapMetadata,
                                                mapPath=mapMetadata["MapPath"])

                        # newSongObj.buttonQuad.vbo.texture = self.songImage
                        middleSide.append(newSongObj)

                    middleSide = sorted(middleSide, key=lambda obj: float(obj.difficulty))[::-1]

                    self.songOrderObjects = leftSide + middleSide + rightSide
                    self.scrollAccelValue = 1 / len(self.songOrderObjects) / 5 if len(self.songOrderObjects) > 0 else 0

                    self.currentSongIndex = len(leftSide) + randint(0, len(middleSide) - 1)

                    self.loadSongScrollAccel = (self.currentSongIndex - self.songIndex) / len(
                        self.songOrderObjects) / 60
                    self.loadSongScrollStage = 0

                else:
                    self.currentSongIndex = songI

                oldClickObject = self.songOrderObjects[self.currentSongIndex]
                oldClickObject.buttonQuad.vbo.texture = self.newImage

                if oldClickObject.metadata:
                    songMetadata = oldClickObject.metadata
                    longTitle = f"{songMetadata['Source']} ({songMetadata['Artist']}) - {songMetadata['Title']} [{songMetadata['Version']}]"

                    mapPath = songMetadata["MapPath"]
                    mapResult = self.beatmapParser.parse(mapPath)
                    beatmap = Beatmap(mapResult)

                    hitCircleTypeCounter = {"Slider": 0, "Circle": 0, "Spinner": 0}

                    for hitCircle in beatmap.hit_objects:
                        if isinstance(hitCircle, SliderCircle):
                            hitCircleTypeCounter["Slider"] += 1
                        elif isinstance(hitCircle, HitCircle):
                            if HitObjectType.CIRCLE in hitCircle.type:
                                hitCircleTypeCounter["Circle"] += 1

                            elif HitObjectType.SPINNER in hitCircle.type:
                                hitCircleTypeCounter["Spinner"] += 1
                        else:
                            raise Exception("Hit Circle Type Non-Existant...")

                    BPMs = []
                    for timingPoint in beatmap.timing_objects:
                        if timingPoint.uninherited:
                            BPMs.append(1 / timingPoint.beat_length * 1000 * 60)

                    BPMs = list(set(BPMs))
                    BPM = round(BPMs[0]) if len(
                        BPMs) == 1 else f"{round(min(BPMs))}-{round(max(BPMs))} ({round(BPMs[len(BPMs) // 2] if len(BPMs) % 2 else (BPMs[len(BPMs) // 2] + BPMs[len(BPMs) // 2]) / 2)})"

                    lengthSeconds = round((beatmap.timing_objects[-1].time) / 1000)  # Approx Can be a few seconds off
                    mappedBy = f"Mapped by {songMetadata['Creator']}"
                    firstInfoRow = f"Length: {lengthSeconds // 60}:{lengthSeconds % 60} BPM: {BPM} Objects: {len(beatmap.hit_objects)}"
                    secondInfoRow = f"Circles: {hitCircleTypeCounter['Circle']} Sliders: {hitCircleTypeCounter['Slider']} Spinners: {hitCircleTypeCounter['Spinner']}"
                    thirdInfoRow = f"CS:{songMetadata['CircleSize']} AR:{songMetadata['ApproachRate']} OD:{songMetadata['OverallDifficulty']} HP:{songMetadata['HPDrainRate']} Stars:{songMetadata['RealStarDifficulty']}"

                    # print("--- ", longTitle, '\n--- ', mappedBy, '\n--- ', firstInfoRow, '\n--- ', secondInfoRow, '\n--- ', thirdInfoRow)

                    displayV = self.displayV
                    # 773
                    longTitleTexture, longTitleSize = texture.GenTextTextureSize(longTitle, 0.04, displayV, "",
                                                                                 fontLoad=self.unicodeFont)
                    mappedByTexture, mappedBySize = texture.GenTextTextureSize(mappedBy, 0.03, displayV, "",
                                                                               fontLoad=self.normalFont2)
                    firstInfoRowTexture, firstInfoRowSize = texture.GenTextTextureSize(firstInfoRow, 0.03, displayV, "",
                                                                                       fontLoad=self.normalFont)
                    secondInfoRowTexture, secondInfoRowSize = texture.GenTextTextureSize(secondInfoRow, 0.03, displayV,
                                                                                         "", fontLoad=self.normalFont2)
                    thirdInfoRowTexture, thirdInfoRowSize = texture.GenTextTextureSize(thirdInfoRow, 0.03, displayV, "",
                                                                                       fontLoad=self.normalFont2)

                    longTitleQuad = quadHandler.Quad(
                        extra.generateRectangleCoordsTopLeft(Vector2(0.005, -0.0075), longTitleSize),
                        colour.Colour(1, 1, 1),
                        longTitleTexture,
                        displayV
                    )

                    mappedByQuad = quadHandler.Quad(
                        extra.generateRectangleCoordsTopLeft(Vector2(0.005, 0.04), mappedBySize),
                        colour.Colour(1, 1, 1),
                        mappedByTexture,
                        displayV
                    )

                    firstInfoRowQuad = quadHandler.Quad(
                        extra.generateRectangleCoordsTopLeft(Vector2(0.005, 0.075), firstInfoRowSize),
                        colour.Colour(1, 1, 1),
                        firstInfoRowTexture,
                        displayV
                    )

                    secondInfoRowQuad = quadHandler.Quad(
                        extra.generateRectangleCoordsTopLeft(Vector2(0.005, 0.11), secondInfoRowSize),
                        colour.Colour(1, 1, 1),
                        secondInfoRowTexture,
                        displayV
                    )

                    thirdInfoRowQuad = quadHandler.Quad(
                        extra.generateRectangleCoordsTopLeft(Vector2(0.005, 0.145), thirdInfoRowSize),
                        colour.Colour(1, 1, 1),
                        thirdInfoRowTexture,
                        displayV
                    )

                    if len(self.songDataQuad) > 0:
                        glDeleteTextures(len(self.songDataQuad), [obj.texture for obj in self.songDataQuad])

                    self.songDataQuad = [longTitleQuad, mappedByQuad, firstInfoRowQuad, secondInfoRowQuad,
                                         thirdInfoRowQuad]
                    print(songMetadata)
                    musicPath = path.join(songMetadata['FolderPath'], songMetadata['AudioFilename'])

                    if musicPath == self.currentSongPath:
                        continue

                    self.currentSongPath = musicPath

                    music.unload()
                    music.load(musicPath)
                    music.set_volume(self.volume)
                    print("Preview", float(songMetadata.get("PreviewTime", 0)) / 1000)
                    music.play(loops=-1, start=float(songMetadata.get("PreviewTime", 0)) / 1000, fade_ms=1000)

                    # songObj.buttonQuad.vbo.texture = self.newImage

            songObj.collideStage = max(0, min(songObj.collideStage, 1))

            if songObj.collideStage != 0:
                if (self.collisionData and self.collisionData[1] < songObj.collideStage) or not self.collisionData:
                    self.collisionData = (songI, songObj.collideStage)

    def searchSongs(self, keyPressedOnce):
        self.oldSearchString = self.searchString

        for key in keyPressedOnce:
            keyName = name(key)

            if keyName.isalnum() and len(keyName) == 1:
                self.searchString += keyName

            elif keyName == "space":
                self.searchString += " "

            elif keyName == "backspace":
                self.searchString = self.searchString[:-1]

        if self.searchString != self.oldSearchString or self.firstSearch:
            self.firstSearch = False

            if self.searchString == "":
                self.origSongOrderObjects = self.allSongOrderObjects

                searchTexture, self.searchSize = texture.GenTextTextureSize("Type to search!", 0.03, self.displayV, "", fontLoad=self.normalFont2)
                glDeleteTextures(1, [self.searchQuad.vbo.texture])
                self.searchQuad.vbo.texture = searchTexture
                self.searchQuad.edit(
                    extra.generateRectangleCoordsTopLeft(self.searchPos, self.searchSize),
                    colour.Colour(1, 1, 1),
                )

            else:
                tempSongObject = []
                searchStringSplit = self.searchString.lower().split(" ")
                for song in self.allSongOrderObjects:
                    for mapName, mapData in song.songData:
                        tagString = f"{mapName} {mapData['Artist']} {mapData['Tags']} {mapData['Source']}".lower()

                        if any([searchItem in tagString for searchItem in searchStringSplit]):
                            tempSongObject.append(song)
                            break

                self.songOrderObjects = tempSongObject
                self.origSongOrderObjects = tempSongObject

                searchTexture, self.searchSize = texture.GenTextTextureSize(self.searchString, 0.03, self.displayV, "", fontLoad=self.normalFont2)
                glDeleteTextures(1, [self.searchQuad.vbo.texture])
                self.searchQuad.vbo.texture = searchTexture
                self.searchQuad.edit(
                    extra.generateRectangleCoordsTopLeft(self.searchPos, self.searchSize),
                    colour.Colour(1, 1, 1),
                )

            self.scrollAccelValue = 1 / len(self.songOrderObjects) / 5 if len(self.songOrderObjects) > 0 else 0

    def draw(self):
        self.backgroundQuad.draw()
        self.backgroundDimQuad.draw()

        self.oldScrollSongObj = self.renderObjects

        for songI, songObj in enumerate(self.renderObjects, start=self.bottomRender):
            yDistance = self.songIndex - songI

            yScreenDist = yDistance * self.buttonSize.Y
            xScreenDist = 0

            if self.collisionData:
                if songI != self.collisionData[0]:
                    yScreenDist += 0.02 * self.collisionData[1] * (1 if self.collisionData[0] > songI else -1)
                else:
                    xScreenDist = 0.05 * self.collisionData[1]

            songObj.update(Vector2(0.88 + abs(yDistance * 0.01) - xScreenDist - songObj.xOffset, yScreenDist + 0.5))

            songObj.draw()

    def scroll(self, mouseScroll, isRightClick=False, mouseR=None, modKeys=None, arrowKeys=None):
        if modKeys and any(modKeys[2:]):
            return

        if not isRightClick:
            if mouseScroll[0]:
                self.scrollAccel = self.scrollAccelValue
            elif mouseScroll[1]:
                self.scrollAccel = -self.scrollAccelValue
            elif arrowKeys[2]:
                self.scrollAccel = self.scrollAccelValue / 5
            elif arrowKeys[3]:
                self.scrollAccel = -self.scrollAccelValue / 5
            else:
                self.scrollAccel = 0
        else:
            targetScrollStage = max(0, min(extra.translate(mouseR.Y, 0.2, 0.8, 1, 0), 1))
            self.scrollVel = (targetScrollStage - self.scrollStage) / 4

        self.loadSongScrollStage += 0.1
        self.loadSongScrollStage = max(0, min(self.loadSongScrollStage, 1))
        if 0 < self.loadSongScrollStage < 1:
            self.scrollAccel += self.loadSongScrollAccel

        self.scrollVel += self.scrollAccel
        self.scrollVel *= 0.85

        self.scrollStage += self.scrollVel

        self.scrollStage = max(0, min(self.scrollStage, 1))
