import os
from vector import Vector2
from extra import getMonitorSize, translate
import PygameWindowInfo
from pyautogui import position


class MouseData:
    def __init__(self, displayV: Vector2):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "128,128"

        self.displayV = displayV

        self.monitor = getMonitorSize()
        self.monitorV = Vector2(*self.monitor)

        self.winInfo = None

        self.rawMousePos = Vector2(0, 0)
        self.rawMousePosR = Vector2(0, 0)
        self.mouseAdjust = Vector2(0, 0)

        self.mousePos = Vector2(0, 0)
        self.cursorPos = Vector2(0, 0)

    def update(self, halfExtraSize):
        self.winInfo.update()

        self.rawMousePos = Vector2(*position())
        self.rawMousePosR = self.rawMousePos / self.monitorV

        self.mouseAdjust = Vector2(
            translate(self.rawMousePosR.X, 0, 1, -halfExtraSize, halfExtraSize),
            translate(self.rawMousePosR.Y, 0, 1, -halfExtraSize, halfExtraSize)
        )

        self.mousePos = self.rawMousePos - Vector2(self.winInfo.getScreenPosition()["left"],
                                                   self.winInfo.getScreenPosition()["top"])

        self.cursorPos = self.mousePos / self.displayV

    def setWinInfo(self):
        self.winInfo = PygameWindowInfo.PygameWindowInfo()


