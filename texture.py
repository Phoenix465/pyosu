from math import floor, ceil

import numpy as np
import pygame
import pygame.image as image
from PIL import Image
from pygame import BLEND_RGBA_MULT, Surface, SRCALPHA
from OpenGL.GL import *
from os.path import exists, splitext
from pygame import surfarray
from time import time

from pygame.transform import scale

from vector import Vector2

DEBUG_MODE = False


class Texture:
    def __init__(self, texture, textureIncrement, program, altName):
        self.texture = texture
        self.increment = textureIncrement
        self.altName = altName
        self.program = program


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def loadTexture(imagePath, alpha=255, middlePart: float = None, repeatMode=False, imageLoad=None, removeBlack=False,
                blackThreshold=0, blackYThreshold=None, blackIgnoreArea=None, blackRemoveArea=None, removeArea=None,
                hueAdjust=None, useNearest=False):
    if DEBUG_MODE:
        print(f"Loading: '{imagePath}'")

    s = time()
    oldTextureSurface = imageLoad or image.load(imagePath).convert_alpha()

    if removeArea:
        for area in removeArea:
            pygame.draw.rect(oldTextureSurface, (0, 0, 0, 0), area)
            removeBlack = True
            # s.fill((0, 0, 0, 255))  # notice the alpha value in the color

    width = oldTextureSurface.get_width()
    height = oldTextureSurface.get_height()

    if removeBlack:
        mainImage = Image.frombytes("RGBA", (width, height), pygame.image.tostring(oldTextureSurface, "RGBA", False))

        pixels = mainImage.load()

        for j in range(mainImage.size[1]):
            for i in range(mainImage.size[0]):
                ignore = False

                if blackYThreshold is not None and j < blackYThreshold:
                    ignore = True

                if blackIgnoreArea is not None:
                    for area in blackIgnoreArea:
                        if area[0] <= i <= area[0] + area[2] and area[1] <= j <= area[1] + area[3]:
                            ignore = True
                            break

                if blackRemoveArea is not None:
                    for area in blackRemoveArea:
                        if area[0] <= i <= area[0] + area[2] and area[1] <= j <= area[1] + area[3]:
                            ignore = False
                            break

                if ignore:
                    continue

                pixelColour = pixels[i, j]

                if pixelColour[0] <= blackThreshold and pixelColour[1] <= blackThreshold and pixelColour[
                    2] <= blackThreshold:
                    pixels[i, j] = (0, 0, 0, 0)

        # mainImage.show()
        oldTextureSurface = image.fromstring(mainImage.tobytes(), mainImage.size, mainImage.mode).convert_alpha()
        mainImage.close()

    if hueAdjust:
        mainImage = Image.frombytes("RGBA", (width, height), pygame.image.tostring(oldTextureSurface, "RGBA", False))
        imageArray = np.array(mainImage)
        newImage = Image.fromarray(shift_hue(imageArray, hueAdjust), "RGBA")
        oldTextureSurface = image.fromstring(newImage.tobytes(), newImage.size, newImage.mode).convert_alpha()

    textureSurface = oldTextureSurface.copy()
    if alpha != 255:
        textureSurface.fill((255, 255, 255, alpha), None, special_flags=BLEND_RGBA_MULT)
    # textureSurface.fill((0, 255, 100))

    if middlePart:
        midDist = width * middlePart
        area = (width / 2 - midDist / 2, 0, midDist, height)
        textureSurface = textureSurface.subsurface(area)
        image.save(textureSurface, "Test.png")

    textureData = image.tostring(textureSurface, "RGBA", True)

    # glEnable(GL_TEXTURE_2D)
    textureId = glGenTextures(1)
    # https://learnopengl.com/Advanced-OpenGL/Anti-Aliasing

    glBindTexture(GL_TEXTURE_2D, textureId)

    # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    if not repeatMode:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    else:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    if removeBlack:
        glTexEnvf(GL_TEXTURE_ENV,
                  GL_COMBINE_RGB,
                  GL_ADD)

    if not useNearest:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    else:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_NEAREST)

    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)
    e = time() - s

    if DEBUG_MODE:
        print(imagePath, f"Time Load: {round(e * 1000)}ms")

    return textureId


def loadAnimation(imageFirstPath, returnImage=False):  # Example: menu-back@2x.png
    pathSplit = splitext(imageFirstPath)
    imageFormat = pathSplit[0] + "{||}" + pathSplit[1]

    if "@2x" in imageFormat:
        imageFormat = imageFormat.replace("@2x{||}", "{||}@2x", 1)

    imageLoads = []  # Ignore First
    animationTextures = []

    i = 0
    while True:
        newImagePath = imageFormat.replace(r"{||}", f"-{i}", 1)

        if not exists(newImagePath):
            break

        imageLoads.append(newImagePath)

        i += 1

    for imageLoadPath in imageLoads:
        animationTextures.append(loadTexture(imageLoadPath))

    if not returnImage:
        return animationTextures
    else:
        return animationTextures, imageLoads


def GenerateDifficultyTexture(difficulty: float, starPath):
    difficulty = max(0, min(difficulty, 10))

    starSurface = image.load(starPath).convert_alpha()
    starHeight, starWidth = starSurface.get_height(), starSurface.get_width()

    smallStarSurfaceSize = int(starWidth / 2), int(starHeight / 2)
    smallStarSurfaceScale = scale(starSurface, smallStarSurfaceSize)

    smallStarSurface = pygame.Surface((starWidth, starHeight), pygame.SRCALPHA)
    smallStarSurface.blit(smallStarSurfaceScale, (int(starWidth / 4), int(starHeight / 4)))

    smallStarSurfaceDim = pygame.Surface((starWidth, starHeight), pygame.SRCALPHA)
    smallStarSurfaceDim.blit(smallStarSurface, (0, 0))
    smallStarSurfaceDim.fill((255, 255, 255, 100), None, special_flags=BLEND_RGBA_MULT)

    gap = 5  # Pixels

    # 280 16
    mainSize = (10 * starWidth + 9 * gap, starHeight)

    mainSurface = pygame.Surface(mainSize, pygame.SRCALPHA)
    for i in range(10):
        offsetX = (starWidth + gap) * i

        if i < difficulty < i + 1:
            object = smallStarSurface  # smallStarSurface
        elif i + 1 <= floor(difficulty):
            object = starSurface
        else:
            object = smallStarSurfaceDim

        mainSurface.blit(object, (offsetX, 0))

    return mainSurface


def GenFontSurface(text, fontPath, fontLoad=None, customColour=None):
    font = fontLoad or pygame.font.Font(fontPath, 64)
    textSurface = font.render(text, True, customColour or (255, 255, 255, 255))

    return textSurface


def GenTextureForText(text, fontPath, fontLoad=None):
    ## https://stackoverflow.com/questions/29015999/pygame-opengl-how-to-draw-text-after-glbegin

    font = fontLoad or pygame.font.Font(fontPath, 64)
    textSurface = font.render(text, True, (255, 255, 255, 255))

    width, height = textSurface.get_width(), textSurface.get_height()
    textureData = pygame.image.tostring(textSurface, "RGBA", True)
    # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    textureId = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureId)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glGenerateMipmap(GL_TEXTURE_2D)

    # glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    return textureId


def GetImageScaleSize(image, scale, displayV, heightWidthScale=True, tuple=False):
    if heightWidthScale:
        lengthP = scale * displayV.Y

        sizeRatio = image.get_width() / image.get_height()
        oLengthP = sizeRatio * lengthP
        oLength = oLengthP / displayV.X

        if tuple:
            return oLength, scale
        else:
            return Vector2(oLength, scale)

    else:
        lengthP = scale * displayV.X
        sizeRatio = image.get_height() / image.get_width()

        oLengthP = sizeRatio * lengthP
        oLength = oLengthP / displayV.Y

        if tuple:
            return scale, oLength
        else:
            return Vector2(scale, oLength)


def GenTextTextureSize(title, heightScale, displayV, fontPath, fontLoad=None, customColour=None):
    titleRender = GenFontSurface(title, fontPath, fontLoad=fontLoad, customColour=customColour)  # 22/90 height
    titleHeight = heightScale
    titleHeightP = titleHeight * displayV.Y
    titleRatio = titleRender.get_width() / titleRender.get_height()
    titleWidthP = titleRatio * titleHeightP
    titleWidth = titleWidthP / displayV.X
    titleSize = Vector2(titleWidth, titleHeight)

    titleTexture = loadTexture("", imageLoad=titleRender)

    return titleTexture, titleSize


def rgb_to_hsv(rgb):
    # Translated from source of colorsys.rgb_to_hsv
    # r,g,b should be a numpy arrays with values between 0 and 255
    # rgb_to_hsv returns an array of floats between 0.0 and 1.0.
    rgb = rgb.astype('float')
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select(
        [r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc)
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv


def hsv_to_rgb(hsv):
    # Translated from source of colorsys.hsv_to_rgb
    # h,s should be a numpy arrays with values between 0.0 and 1.0
    # v should be a numpy array with values between 0.0 and 255.0
    # hsv_to_rgb returns an array of uints between 0 and 255.
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype('uint8')
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 0] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 1] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype('uint8')


def shift_hue(arr, hout):
    hsv = rgb_to_hsv(arr)
    hsv[..., 0] = hout
    rgb = hsv_to_rgb(hsv)
    return rgb


def shift_saturation(arr, sout):
    hsv = rgb_to_hsv(arr)
    hsv[..., 1] *= sout
    rgb = hsv_to_rgb(hsv)
    return rgb
