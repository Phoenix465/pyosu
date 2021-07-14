import os
from os import path


class PathHolder:
    def __init__(self):
        self.appdataPath = os.getenv('LOCALAPPDATA')
        self.defaultOsuPath = path.join(self.appdataPath, "osu!")
        # self.defaultOsuPath = path.join(".", "osuFiles")
        # self.defaultOsuPath = r"G:\osu!"

        self.dataPath = path.join(self.defaultOsuPath, "Data")
        self.mainBackgroundsPath = path.join(self.dataPath, "bg")
        self.songBackgroundsPath = path.join(self.dataPath, "bt")

        self.resources = path.join(".", "resources")
        self.iconPath = path.join(self.resources, "icon.png")
        self.playPath = path.join(self.resources, "play.png")
        self.exitPath = path.join(self.resources, "exit.png")
        self.emptyPath = path.join(self.resources, "empty.png")
        self.blackBlockPath = path.join(self.resources, "black.png")
        self.whiteBlockPath = path.join(self.resources, "white.png")
        self.sliderBoarderPath = path.join(self.resources, "sliderboarder.png")
        self.whitecirclePath = path.join(self.resources, "whitecircle.png")
        self.CyberbitFont = path.join(self.resources, "Cyberbit.ttf")
        self.allerPath = path.join(self.resources, "Aller")

        self.allerFont = path.join(self.allerPath, "Aller_BdIt.ttf")
        self.allerFont2 = path.join(self.allerPath, "Aller_Bd.ttf")
        self.allerFont3 = path.join(self.allerPath, "Aller_Rg.ttf")

        self.mainBackgrounds = [file for file in os.listdir(self.mainBackgroundsPath) if path.isfile(path.join(self.mainBackgroundsPath, file))]

        self.mainBackgroundPath = path.join(self.mainBackgroundsPath, self.mainBackgrounds[8])  # choice(mainBackgrounds))

        self.skinsPath = path.join(self.defaultOsuPath, "Skins")
        self.skinName = "Komori - # Hoaqumi+--"

        self.skinPath = path.join(self.skinsPath, self.skinName)
        self.cursorPath = path.join(self.skinPath, "cursor.png")
        self.cursorTrailPath = path.join(self.skinPath, "cursortrail.png")
        self.menuButtonBackgroundPath = path.join(self.skinPath, "menu-button-background.png")
        self.starPath = path.join(self.skinPath, "star.png")
        self.selectionModePath = path.join(self.skinPath, "selection-mode.png")
        self.menuBackPath = path.join(self.skinPath, "menu-back.png")
        self.modeOsuSmallPath = path.join(self.skinPath, "mode-osu-small.png")
        self.hitcirclePath = path.join(self.skinPath, "hitcircle.png")
        self.approachcirclePath = path.join(self.skinPath, "approachcircle.png")
        self.sliderBPath = path.join(self.skinPath, "sliderb0.png")
        self.skinIniPath = path.join(self.skinPath, "skin.ini")

        self.default0Path = path.join(self.skinPath, "default-0.png")
        self.default1Path = path.join(self.skinPath, "default-1.png")
        self.default2Path = path.join(self.skinPath, "default-2.png")
        self.default3Path = path.join(self.skinPath, "default-3.png")
        self.default4Path = path.join(self.skinPath, "default-4.png")
        self.default5Path = path.join(self.skinPath, "default-5.png")
        self.default6Path = path.join(self.skinPath, "default-6.png")
        self.default7Path = path.join(self.skinPath, "default-7.png")
        self.default8Path = path.join(self.skinPath, "default-8.png")
        self.default9Path = path.join(self.skinPath, "default-9.png")

        self.hit50Path = path.join(self.skinPath, "hit50.png")
        self.hit100Path = path.join(self.skinPath, "hit100.png")
        self.hit300Path = path.join(self.skinPath, "hit300.png")
        self.hitXPath = path.join(self.skinPath, "hit0.png")

        self.scoreBarBackgroundPath = path.join(self.skinPath, "scorebar-bg.png")

        self.scoreBasePath = path.join(self.skinPath, "score@2x.png")
        self.comboBasePath = path.join(self.skinPath, "combo@2x.png")

        self.scoreBasePath = path.join(self.skinPath, "score@2x.png")
        self.comboBasePath = path.join(self.skinPath, "combo@2x.png")

        self.percentSignPath = path.join(self.skinPath, "score-PERCENT.png")
        self.commaSignPath = path.join(self.skinPath, "score-COMMA.png")
        self.dotSignPath = path.join(self.skinPath, "score-DOT.png")

        self.scorebarBasePath = path.join(self.skinPath, "scorebar-colour.png")

        self.reverseArrowPath = path.join(self.skinPath, "reversearrow.png")

        self.softHitClapSoundPath = path.join(self.skinPath, "soft-hitclap.ogg")
        self.softHitFinishSoundPath = path.join(self.skinPath, "soft-hitfinish.ogg")
        self.softHitNormalSoundPath = path.join(self.skinPath, "soft-hitnormal.ogg")
        self.softHitWhistleSoundPath = path.join(self.skinPath, "soft-hitwhistle.ogg")

        self.menuHitSoundPath = path.join(self.skinPath, "menuhit.ogg")
        self.menuClickSoundPath = path.join(self.skinPath, "menuclick.ogg")
        self.menuBackSoundPath = path.join(self.skinPath, "menu-back-click.ogg")
        self.songClickSound = path.join(self.skinPath, "menu-direct-click.ogg")

        self.SongsPath = path.join(self.defaultOsuPath, "Songs")

        self.songCachePath = path.join(".", "cache.npy")
