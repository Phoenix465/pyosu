from os.path import splitext

from pygame.image import load

import colour
import extra
import quadHandler
import texture
import vector


class NumberShower:
    def __init__(self, basePath, digitHeight, topLeftVector, displayV, maxDigitLength: int = 8, defaultNumber: str=None,
                 imageSpacingMultiplier=0.75, extraImagePaths=None):
        self.loadedNumberImages, imageLoadsPaths = texture.loadAnimation(basePath, returnImage=True)
        baseImage = load(imageLoadsPaths[0])

        self.currentNumberString = "0" * maxDigitLength

        self.imageSize = texture.GetImageScaleSize(baseImage, digitHeight, displayV)
        self.imageSpacing = self.imageSize * vector.Vector2(imageSpacingMultiplier, 1)

        self.digitQuads = []
        self.digitShowMask = [1] * maxDigitLength

        self.extraImagePath = extraImagePaths or {}
        self.extraImages = {}
        for key, path in self.extraImagePath.items():
            self.extraImages[key] = texture.loadTexture(path)

        for i in range(maxDigitLength):
            newNumberQuad = quadHandler.Quad(
                extra.generateRectangleCoordsTopLeft(topLeftVector + vector.Vector2(i*self.imageSpacing.X, 0), self.imageSize),
                colour.Colour(1, 1, 1),
                self.loadedNumberImages[i],
                displayV
            )

            self.digitQuads.append(newNumberQuad)

        if defaultNumber:
            self.setNumber(defaultNumber)

    def setNumber(self, num: str):
        for i, char in enumerate(num):
            if char == "-":
                self.digitShowMask[i] = 0
            elif char in self.extraImages:
                self.digitShowMask[i] = 1
                self.digitQuads[i].vbo.texture = self.extraImages[char]
            else:
                self.digitShowMask[i] = 1
                self.digitQuads[i].vbo.texture = self.loadedNumberImages[int(char)]

    def draw(self):
        for i, quad in enumerate(self.digitQuads):
            if self.digitShowMask[i]:
                quad.draw()
