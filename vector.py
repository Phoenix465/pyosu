from errors import VectorError
from math import sqrt
from dataclasses import dataclass

functionDict = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}

operationText = {
    "+": ["Added", "Addition"],
    "-": ["Subtracted", "Subtraction"],
    "*": ["Multiplied", "Multiplication"],
    "/": ["Divided", "Division"],
}

@dataclass()
class Vector2:
    def __init__(self, X, Y):
        if not isinstance(X, (int, float)):
            raise VectorError("X Has To Be Of Class int/float")
        if not isinstance(Y, (int, float)):
            raise VectorError("Y Has To Be Of Class int/float")

        self._X = X
        self._Y = Y

        self.list = [self.X, self.Y]
        self.tuple = tuple(self.list)

        self.magnitude = sqrt(sum(map(lambda num: num ** 2, self.list)))

    @property
    def X(self):
        return self._X

    @property
    def Y(self):
        return self._Y

    @X.setter
    def X(self, newVal):
        raise VectorError("X Cannot Be Reassigned")

    @Y.setter
    def Y(self, newVal):
        raise VectorError("Y Cannot Be Reassigned")

    def operationHandler(self, other, operation):
        if type(other) == int or type(other) == float:
            return Vector2(functionDict[operation](self.X, other), functionDict[operation](self.Y, other))

        elif type(other) == Vector2:
            return Vector2(functionDict[operation](self.X, other.X), functionDict[operation](self.Y, other.Y))

        else:
            raise VectorError(f"{type(other)} Is Not Supported For Vector {operationText[operation][1]}")

    def equals(self, newVector):
        return self.X == newVector.X and self.Y == newVector.Y

    def __eq__(self, other):
        return self.equals(other)

    def __add__(self, other):
        return self.operationHandler(other, "+")

    def __sub__(self, other):
        return self.operationHandler(other, "-")

    def __mul__(self, other):
        return self.operationHandler(other, "*")

    def __truediv__(self, other):
        return self.operationHandler(other, "/")

    def __repr__(self):
        return f"Vector2 X:{self.X} Y:{self.Y}"

    def __key(self):
        return self.tuple

    def __hash__(self):
        return hash(self.__key())


@dataclass()
class Vector3:
    def __init__(self, X, Y, Z):
        if not isinstance(X, (int, float)):
            raise VectorError("X Has To Be Of Class int/float")
        if not isinstance(Y, (int, float)):
            raise VectorError("Y Has To Be Of Class int/float")
        if not isinstance(Z, (int, float)):
            raise VectorError("Z Has To Be Of Class int/float")

        self._X = X
        self._Y = Y
        self._Z = Z

        self.list = [self.X, self.Y, self.Z]
        self.tuple = tuple(self.list)

        self.magnitude = sqrt(sum(map(lambda num: num ** 2, self.list)))

    @property
    def X(self):
        return self._X

    @property
    def Y(self):
        return self._Y

    @property
    def Z(self):
        return self._Z

    @X.setter
    def X(self, newVal):
        raise VectorError("X Cannot Be Reassigned")

    @Y.setter
    def Y(self, newVal):
        raise VectorError("Y Cannot Be Reassigned")

    @Z.setter
    def Z(self, newVal):
        raise VectorError("Z Cannot Be Reassigned")

    def operationHandler(self, other, operation):
        operationFunc = functionDict[operation]
        if type(other) == int or type(other) == float:
            return Vector3(operationFunc(self.X, other), operationFunc(self.Y, other), operationFunc(self.Z, other))

        elif type(other) == Vector3:
            return Vector3(operationFunc(self.X, other.X), operationFunc(self.Y, other.Y), operationFunc(self.Z, other.Z))

        else:
            raise VectorError(f"{type(other)} Is Not Supported For Vector3 {operationText[operation][1]}")

    def __add__(self, other):
        return self.operationHandler(other, "+")

    def __sub__(self, other):
        return self.operationHandler(other, "-")

    def __mul__(self, other):
        return self.operationHandler(other, "*")

    def __truediv__(self, other):
        return self.operationHandler(other, "/")

    def __repr__(self):
        return f"Vector3 X:{self.X} Y:{self.Y} Z:{self.Z}"

    def __key(self):
        return self.tuple

    def __hash__(self):
        return hash(self.__key())
