# program for multi-variable optimization

import subprocess
import numpy as np
from scipy.optimize import least_squares
from subMM import *
from dynamic import *

totalHFE = 0.0
trajFolder = ""
xyzPath = ""
keyPath = ""

def costFUNC(params):
    QM = np.loadtxt('QM-energy.dat', usecols=(-1,), unpack=True)
    MM = getEnergy(params, 'filelist')

    my_file = open("filelist", "r")
    filenames = my_file.readlines()
    print("filelist length = " + str(len(filenames)))
    curveCost = 0
    i = 0
    while i < len(filenames):
        weight = costWeight(filenames[i])
        print(filenames[i] + ": " + str(weight))
        curveCost += ((QM[i] - MM[i]) ** 2) * weight
        i += 1
    print("Cost from ion-ligand curve = " + str(curveCost))

    stageHFE = getFreeEnergy(trajFolder, xyzPath, keyPath, lastFE)
    global totalHFE
    totalHFE += stageHFE
    HFECost = totalHFE - targetHFE
    print("Cost from HFE = " + str(totalHFE))

    totalCost = 0.25 * curveCost + 0.75 * HFECost

    return totalCost


def costWeight(filename):
    base_file_name = filename.split(".")[0]
    fields = base_file_name.split("_")
    number = int(fields[len(fields) - 1])  # the number of the file in its series (001-020, equilibrium point = 005)
    cost = 1.0  # base cost
    if number < 5:  # data points > 0 thrown out
        cost = 0
    elif number > 17:  # trailing data points thrown out
        cost = 0

    return cost


def main():
    x0 = np.loadtxt("p0.txt", usecols=(-1,))
    myBounds = [[1.62682348, 0.01, 3, 0], [1.62682350, 1, 5, 1]]
    ret = least_squares(costFUNC, x0, bounds=myBounds, diff_step=0.000001)
    np.savetxt("p1.txt", ret.x, fmt='%15.10f')
    subprocess.run("paste p0.txt p1.txt >temp && mv temp p0.txt", shell=True)

    my_file = open("result.p", "r")
    lines = my_file.readlines()
    out_file = open("MM-energy.dat", "w")
    for line in lines:
        fields = line.split()
        if len(fields) > 6:
            out_file.write(fields[5] + "\n")


if __name__ == "__main__":
    main()
