from math import floor

from OpenGL.GL import glDeleteTextures
from pygame.font import Font
from pygame.mixer import get_num_channels, Channel, Sound

import colour
import quadHandler
import texture
import extra
from os import path
from vector import Vector2
from pygame import image, Surface, draw, BLEND_RGBA_MULT, SRCALPHA
from time import time
from pygame import mixer


def loadSound(file):
    return Sound(file=file)


class VolumeOverlay:
    def __init__(self, resourcesPath, displayV: Vector2, fontPath):
        self.volumeOverlayBackPath = path.join(resourcesPath, "volumeOverlayBack.png")
        self.volumeOverlayFrontPath = path.join(resourcesPath, "volumeOverlayFront.png")

        self.fontPath = fontPath
        self.font = Font(self.fontPath, 64)

        self.normalFrontSurface = image.load(self.volumeOverlayFrontPath)
        self.width, self.height = self.normalFrontSurface.get_width(), self.normalFrontSurface.get_height()

        self.volumeOverlayBackTexture = texture.loadTexture(self.volumeOverlayBackPath, alpha=230)
        self.volumeOverlayFrontTexture = texture.loadTexture("", imageLoad=self.normalFrontSurface)

        self.displayV = displayV

        self.mainSizeX = 0.1
        mainSizeXP = self.mainSizeX * displayV.X
        self.mainSizeY = mainSizeXP / displayV.Y
        self.mainSize = Vector2(self.mainSizeX, self.mainSizeY)

        self.offsetX = 0.1
        offsetXP = self.offsetX * displayV.X
        self.offsetY = offsetXP / displayV.Y
        self.offset = Vector2(1 - self.offsetX, 1 - self.offsetY)

        self.oldVol = 0
        self.volume = .5

        self.volumeStage = 1
        self.volumeDirection = 0

        self.edgeMap = {"TOP": 0, "RIGHT": 1, "BOTTOM": 2, "LEFT": 3}

        self.volumeOverlayBackQuad = quadHandler.Quad(
            extra.generateRectangleCoords(self.offset, self.mainSize),
            colour.Colour(1, 1, 1),
            self.volumeOverlayBackTexture,
            displayV
        )

        self.volumeOverlayFrontQuad = quadHandler.Quad(
            extra.generateRectangleCoords(self.offset, self.mainSize),
            colour.Colour(1, 1, 1),
            self.volumeOverlayFrontTexture,
            displayV
        )

        volumeTexture, volumeTextSize = texture.GenTextTextureSize(f"{floor(self.volume * 100)}%", 0.04, displayV, "",
                                                                   fontLoad=self.font)

        self.volumeTextQuad = quadHandler.Quad(
            extra.generateRectangleCoords(self.offset, volumeTextSize),
            colour.Colour(1, 1, 1),
            volumeTexture,
            displayV
        )

        self.show = False
        self.end = time()
        self.hideDelay = 1

    def setVolumeMixer(self):
        mixer.music.set_volume(self.volume)

    def setVolumeChannels(self):
        for i in range(get_num_channels()):
            #print(f"Adjust Channel {i}")
            c = Channel(i)
            c.set_volume(self.volume)

    def draw(self):
        self.show = time() < self.end

        if self.show:
            self.volumeOverlayBackQuad.draw()
            self.volumeOverlayFrontQuad.draw()
            self.volumeTextQuad.draw()

    def step(self):
        if not self.volumeStage >= 1:
            self.volumeStage += 0.2
            self.adjustVolumeFront(self.volume + 0.01 * self.volumeDirection)

            self.end = time() + self.hideDelay

    def adjustVolumeFront(self, newVol: float = 0):
        self.oldVol = self.volume

        if newVol == self.oldVol:
            return

        self.volume = newVol
        self.volume = max(0, min(self.volume, 1))

        if self.volume != 1:
            newSurface = Surface((self.width, self.height), SRCALPHA)
            polygonShape = [(self.width / 2, self.height / 2), (self.width / 2, 0)]  # In terms of Top Left as ORIGIN

            newAngle = 0 - ((self.volume * 360) - 90)
            if newAngle < 0:
                newAngle = 360 + newAngle

            edgeHit, *finalPoint = extra.getSquareIntersection(newAngle, 50)
            edgeValue = self.edgeMap[edgeHit]
            if edgeValue == 0 and finalPoint[0] < 0:
                edgeValue = 4

            finalPointAdj = (finalPoint[0] + self.width / 2, self.height / 2 - finalPoint[1])

            if edgeValue > 0:
                polygonShape.append((self.width, 0))
            if edgeValue > 1:
                polygonShape.append((self.width, self.height))
            if edgeValue > 2:
                polygonShape.append((0, self.height))
            if edgeValue > 3:
                polygonShape.append((0, 0))

            polygonShape.append(finalPointAdj)

            draw.polygon(newSurface, (255, 255, 255), polygonShape)
            draw.aalines(newSurface, (255, 255, 255), True, polygonShape)  # moderately helps with ugly aliasing
            newSurface.blit(self.normalFrontSurface, (0, 0), None, BLEND_RGBA_MULT)
        else:
            newSurface = self.normalFrontSurface

        glDeleteTextures(1, [self.volumeOverlayFrontQuad.texture])
        self.volumeOverlayFrontTexture = texture.loadTexture("", imageLoad=newSurface)
        self.volumeOverlayFrontQuad.texture = self.volumeOverlayFrontTexture
        self.volumeOverlayFrontQuad.vbo.texture = self.volumeOverlayFrontTexture

        volumeTexture, volumeTextSize = texture.GenTextTextureSize(f"{round(self.volume * 100)}%", 0.04, self.displayV,
                                                                   "", fontLoad=self.font)

        self.volumeTextQuad.edit(
            extra.generateRectangleCoords(self.offset, volumeTextSize),
            colour.Colour(1, 1, 1),
        )

        glDeleteTextures(1, [self.volumeTextQuad.texture])

        self.volumeTextQuad.texture = volumeTexture
        self.volumeTextQuad.vbo.texture = volumeTexture

    def forceJump(self):
        self.adjustVolumeFront(self.volume + (0.01 * self.volumeDirection) * ((1 - self.volumeStage) / 0.2))
