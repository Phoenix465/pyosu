from math import floor
from time import time

import pygame
from OpenGL.GL import *
from pygame import GL_MULTISAMPLEBUFFERS, GL_MULTISAMPLESAMPLES
from pygame.locals import DOUBLEBUF, OPENGL

import cursor
import gamePaths
import mouseHandler
from KeyPressHolder import KeyboardHandler
from numberShower import NumberShower
from scenes import SceneHolder
from vector import Vector2
from volumeOverlayHandler import VolumeOverlay


def main():
    # Initialisation
    pygame.init()
    pygame.mixer.init()

    display = 1366, 768
    displayV = Vector2(*display)

    MouseDataHandler = mouseHandler.MouseData(displayV)

    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 2)

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)

    pygame.display.set_caption("osu!")

    MouseDataHandler.setWinInfo()

    GamePaths = gamePaths.PathHolder()

    iconSurface = pygame.image.load(GamePaths.iconPath)
    pygame.display.set_icon(iconSurface)

    volumeController = VolumeOverlay(
        GamePaths.resources,
        displayV,
        GamePaths.allerFont
    )

    cursorObject = cursor.Cursor(displayV, GamePaths.cursorPath, GamePaths.cursorTrailPath)

    pygame.display.flip()

    # OpenGL Settings
    glViewport(0, 0, *display)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # Coordinates are 0 1
    # https://cyrille.rossant.net/2d-graphics-rendering-tutorial-with-pyopengl/
    glOrtho(0, 1, 1, 0, 0, 1)

    times = [0]
    running = True
    clock = pygame.time.Clock()

    MainScene = SceneHolder(GamePaths, displayV)
    keyboardHandler = KeyboardHandler()

    fpsCounter = NumberShower(GamePaths.scoreBasePath,
                              60 / 768,
                              Vector2(1-(3*10/768), 1 - 60 / 768),
                              displayV,
                              maxDigitLength=3,
                              defaultNumber="000",
                              imageSpacingMultiplier=0.5)

    while running:
        deltaT = clock.tick(MainScene.fps)
        s = time() * 1000

        keyboardHandler.update()
        if keyboardHandler.quit or MainScene.quit:
            running = False

        glClear(GL_COLOR_BUFFER_BIT)

        if keyboardHandler.escapePressedOnce:
            MainScene.menu.mainIconQuad.tweenPosDirection = -1

        MouseDataHandler.update(MainScene.menu.halfExtraSize)
        MainScene.changeMode()
        MainScene.draw(MouseDataHandler, keyboardHandler, deltaT)

        if MainScene.mode == "menu" or MainScene.mode == "playmap" or (
                MainScene.mode == "select" and any(keyboardHandler.modKeysHold[2:])):
            if keyboardHandler.mouseScroll[0]:
                volumeController.forceJump()
                volumeController.volumeDirection = 1
                volumeController.volumeStage = 0
            elif keyboardHandler.mouseScroll[1]:
                volumeController.forceJump()
                volumeController.volumeDirection = -1
                volumeController.volumeStage = 0

        volumeController.step()
        volumeController.draw()
        volumeController.setVolumeChannels()
        volumeController.setVolumeMixer()

        cursorObject.update(MouseDataHandler.cursorPos, keyboardHandler.osuKeysPressOnce, keyboardHandler.osuKeysHeld)
        cursorObject.draw()

        fps = str(floor(clock.get_fps()))
        fpsCounter.setNumber(fps + "-"*(3-len(fps)))
        fpsCounter.draw()

        pygame.display.flip()

        e = time() * 1000
        ft = e - s

        times.append(ft)

    print(sum(times) / len(times))


if __name__ == "__main__":
    main()
