"""
Handler for the VBO

Class
-----
VBOHandler - Handles a Single VBO
"""

from ctypes import c_void_p

import OpenGL.arrays.vbo as glVBO
import numpy as np
from OpenGL.GL import *

"""
class VBO:
    def __init__(self, combinedData):
        self.combinedData = combinedData
        self.combinedData = np.array(self.combinedData, np.float32)

        self.vbo = glVBO.VBO(self.combinedData)
        self.vbo.bind()

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        stride = (2 + 3) * self.combinedData.itemsize

        glVertexPointer(2, GL_FLOAT, stride, None)
        glColorPointer(3, GL_FLOAT, stride, c_void_p(8))

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_QUADS, 0, len(self.combinedData))
        glBindVertexArray(0)

    def delete(self):
        if hasattr(self, "vao"):
            del self.vao

        if hasattr(self, "vbo"):
            del self.vbo
"""


class VBOImage:
    def __init__(self, combinedData, texture):
        self.combinedData = combinedData
        self.combinedData = np.array(self.combinedData, np.float32)

        self.texture = texture

        self.vbo = glVBO.VBO(self.combinedData)
        self.vbo.bind()

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        stride = (2 + 3 + 2) * self.combinedData.itemsize

        glVertexPointer(2, GL_FLOAT, stride, None)
        glColorPointer(3, GL_FLOAT, stride, c_void_p(8))

        glTexCoordPointer(2, GL_FLOAT, stride, c_void_p(20))

        glBindVertexArray(0)

    def edit(self, newCombinedData):
        #  IMPORTANT: IF TEXTURES SEEM LIKE THE SWITCH WITH OTHER QUADS THEN THIS FUNCTION IS WHY - THE VAO I ASSUME ISN'T UPDATED AND THIS CAUSES MESSY THIGNS!!
        newCombinedData = np.array(newCombinedData, np.float32)

        self.vbo.bind()
        self.vbo.implementation.glBufferSubData(self.vbo.target, 0, newCombinedData)

        glBindVertexArray(self.vao)

        glBindVertexArray(0)

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glBindVertexArray(self.vao)

        glDrawArrays(GL_QUADS, 0, len(self.combinedData))

        glBindVertexArray(0)

        #https://stackoverflow.com/questions/15672720/pyopengl-dynamically-updating-values-in-a-vertex-buffer-object

    def delete(self):
        if hasattr(self, "vao"):
            del self.vao

        if hasattr(self, "vbo"):
            del self.vbo


class VBOImageTransparency:
    def __init__(self, combinedData, texture):
        self.combinedData = combinedData
        self.combinedData = np.array(self.combinedData, np.float32)

        self.texture = texture

        self.vbo = glVBO.VBO(self.combinedData)
        self.vbo.bind()

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        stride = (2 + 4 + 2) * self.combinedData.itemsize

        glVertexPointer(2, GL_FLOAT, stride, None)
        glColorPointer(4, GL_FLOAT, stride, c_void_p(8))

        glTexCoordPointer(2, GL_FLOAT, stride, c_void_p(24))

        glBindVertexArray(0)

    def edit(self, newCombinedData):
        #  IMPORTANT: IF TEXTURES SEEM LIKE THE SWITCH WITH OTHER QUADS THEN THIS FUNCTION IS WHY - THE VAO I ASSUME ISN'T UPDATED AND THIS CAUSES MESSY THIGNS!!
        newCombinedData = np.array(newCombinedData, np.float32)

        self.vbo.bind()
        self.vbo.implementation.glBufferSubData(self.vbo.target, 0, newCombinedData)

        glBindVertexArray(self.vao)

        glBindVertexArray(0)

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glBindVertexArray(self.vao)

        glDrawArrays(GL_QUADS, 0, len(self.combinedData))

        glBindVertexArray(0)

        #https://stackoverflow.com/questions/15672720/pyopengl-dynamically-updating-values-in-a-vertex-buffer-object

    def delete(self):
        if hasattr(self, "vao"):
            del self.vao

        if hasattr(self, "vbo"):
            del self.vbo


class VBOColour:
    def __init__(self, combinedData):
        self.combinedData = combinedData
        self.combinedData = np.array(self.combinedData, np.float32)

        self.vbo = glVBO.VBO(self.combinedData)
        self.vbo.bind()

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        stride = (2 + 4) * self.combinedData.itemsize

        glVertexPointer(2, GL_FLOAT, stride, None)
        glColorPointer(4, GL_FLOAT, stride, c_void_p(8))

        glBindVertexArray(0)

    def edit(self, newCombinedData):
        newCombinedData = np.array(newCombinedData, np.float32)

        self.vbo.bind()
        self.vbo.implementation.glBufferSubData(self.vbo.target, 0, newCombinedData)

        glBindVertexArray(self.vao)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_QUADS, 0, len(self.combinedData))
        glBindVertexArray(0)

    def delete(self):
        if hasattr(self, "vao"):
            del self.vao

        if hasattr(self, "vbo"):
            del self.vbo