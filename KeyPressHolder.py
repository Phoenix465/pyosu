from pygame import event, mouse, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, K_ESCAPE, K_z, K_x, K_LCTRL, K_RCTRL, K_LALT, \
    K_RALT, KEYUP, K_LEFT, K_RIGHT, K_UP, K_DOWN, QUIT


class KeyboardHandler:
    def __init__(self):
        self.osuKeysHeld = [False, False, False, False]
        self.modKeysHold = [False, False, False, False]  # LCTRL RCTRL LALT RALT
        self.arrowKeysHold = [False, False, False, False]  # Left Right Up Down

        self.mouseClick = (False, False, False)
        self.mouseScroll = [False, False]
        self.osuKeysPressOnce = [False, False, False, False]

        self.escapePressedOnce = False
        self.quit = False

        self.keyPressedOnce = []

    def update(self):
        self.mouseClick = (False, False, False)
        self.mouseScroll = [False, False]
        self.osuKeysPressOnce = [False, False, False, False]

        self.escapePressedOnce = False
        self.keyPressedOnce = []

        for currentEvent in event.get():
            if currentEvent.type == QUIT:
                self.quit = True

            elif currentEvent.type == MOUSEBUTTONDOWN or currentEvent.type == MOUSEBUTTONUP:
                self.mouseClick = mouse.get_pressed(num_buttons=3)
                if self.mouseClick[0]:
                    self.osuKeysPressOnce[2] = True
                    self.osuKeysHeld[2] = True
                else:
                    self.osuKeysHeld[2] = False

                if self.mouseClick[2]:
                    self.osuKeysPressOnce[3] = True
                    self.osuKeysHeld[3] = True
                else:
                    self.osuKeysHeld[3] = False

                if currentEvent.type == MOUSEBUTTONDOWN:
                    if currentEvent.button == 4:  # Down
                        self.mouseScroll[0] = True

                    elif currentEvent.button == 5:  # Up
                        self.mouseScroll[1] = True

            elif currentEvent.type == KEYDOWN:
                self.keyPressedOnce.append(currentEvent.key)

                if currentEvent.key == K_ESCAPE:
                    self.escapePressedOnce = True
                    
                elif currentEvent.key == K_z:
                    self.osuKeysPressOnce[0] = True
                    self.osuKeysHeld[0] = True
                elif currentEvent.key == K_x:
                    self.osuKeysPressOnce[1] = True
                    self.osuKeysHeld[1] = True

                elif currentEvent.key == K_LCTRL:
                    self.modKeysHold[0] = True
                elif currentEvent.key == K_RCTRL:
                    self.modKeysHold[1] = True
                elif currentEvent.key == K_LALT:
                    self.modKeysHold[2] = True
                elif currentEvent.key == K_RALT:
                    self.modKeysHold[3] = True

                elif currentEvent.key == K_LEFT:
                    self.arrowKeysHold[0] = True
                elif currentEvent.key == K_RIGHT:
                    self.arrowKeysHold[1] = True
                elif currentEvent.key == K_UP:
                    self.arrowKeysHold[2] = True
                elif currentEvent.key == K_DOWN:
                    self.arrowKeysHold[3] = True

            elif currentEvent.type == KEYUP:
                if currentEvent.key == K_z:
                    self.osuKeysHeld[0] = False
                elif currentEvent.key == K_x:
                    self.osuKeysHeld[1] = False

                elif currentEvent.key == K_LCTRL:
                    self.modKeysHold[0] = False
                elif currentEvent.key == K_RCTRL:
                    self.modKeysHold[1] = False
                elif currentEvent.key == K_LALT:
                    self.modKeysHold[2] = False
                elif currentEvent.key == K_RALT:
                    self.modKeysHold[3] = False

                elif currentEvent.key == K_LEFT:
                    self.arrowKeysHold[0] = False
                elif currentEvent.key == K_RIGHT:
                    self.arrowKeysHold[1] = False
                elif currentEvent.key == K_UP:
                    self.arrowKeysHold[2] = False
                elif currentEvent.key == K_DOWN:
                    self.arrowKeysHold[3] = False
