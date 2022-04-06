
def getDynCommand():

    simulationLength = 1  # ns
    stepSize = 2  # ps
    saveInterval = 3  # fs
    ensemble = 4   # 4 = NPT
    temp = 298  # K
    pressure = 1  # bar
    numSteps = int(simulationLength * (1 / 1e9) / (stepSize * (1 / 1e15)))

    name = "la_water50"
    xyz = name + ".xyz"
    key = name + ".key"

    string = "dynamic_gpu -i " + xyz + " -k " + key + " " + str(numSteps) + " " + str(stepSize) + " " \
             + str(saveInterval) + " " + str(ensemble) + " " + str(temp) + " " + str(pressure) + " N > out.txt"
    return string


def getBar1Command(arc1, arc2):
    temp = 298
    string = "bar_gpu 1 " + arc1 + " " + str(temp) + " " + arc2 + " " + str(temp) + " N > out.txt"
    return string


def getBar2Command(bar1)
    string = "bar_gpu 2 " +
