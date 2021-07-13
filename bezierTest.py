import bezier
import numpy as np
import matplotlib.pyplot as plt

origNodes = [
    [361, 346],
    [121, 167],
]

nodes = np.asfortranarray(origNodes)

print("OrigNodes", origNodes)

print("Nodes", nodes)

curve = bezier.Curve.from_nodes(nodes=nodes)

curveSteps = 100
curvePointStepped = [curve.evaluate(s / curveSteps) for s in range(curveSteps + 1)]
print("21",  curve.evaluate(1.0))
print(list(map(lambda point: (point[0][0], point[1][0]), curvePointStepped)))
curve.plot(curveSteps)
plt.show()
input("Yield: ")
