import os

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

    string = "dynamic_gpu " + xyz + " -k " + key + " " + str(numSteps) + " " + str(stepSize) + " " \
             + str(saveInterval) + " " + str(ensemble) + " " + str(temp) + " " + str(pressure) + " N > out.txt"
    return string


def run_tinker(command):
    print("Executing command: " + command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return 0


def get_bar1_cmd(arc1, arc2):
    temp = 298
    string = "bar_gpu 1 " + arc1 + " " + str(temp) + " " + arc2 + " " + str(temp) + " N > out.txt"
    return string


def getBar2Command(bar1):
    string = "bar_gpu 2 " + bar1 + "1 1000 1 1 1000 1"
    return string


def getFreeEnergy(trajFolder, xyzPath, keyPath, lastFE):
    baseDir = os.getwd()

    # Identify latest trajectory folder, and make one for next trajectory
    lastTraj = -1
    for dir in os.listdir(trajFolder):
        if int(dir) > lastTraj:
            lastTraj = dir
    lastTrajFolder = os.path.join(trajFolder, str(lastTraj))
    currentTrajFolder = os.path.join(trajFolder, str(lastTraj+1))
    os.mkdir(currentTrajFolder)

    # copy parameters file to current traj directory
    subprocess.run("mv amoeba09_la.prm " + os.path.join(currentTrajFolder, "amoeba09_la.prm"), shell=True)
    # copy xyz
    xyzName = os.path.basename(xyzPath)
    subprocess.run("cp " + xyzPath + " " + os.path.join(currentTrajFolder, xyzName), shell=True)
    # copy key
    keyName = os.path.basename(keyPath)
    subprocess.run("cp " + keyPath + " " + os.path.join(currentTrajFolder, keyName), shell=True)

    arc1path = os.path.join(lastTrajFolder, xyzName.replace(".xyz", ".arc"))
    arc2path = xyzPath.replace(".xyz", ".arc")
    barpath = xyzPath.replace(".xyz", ".bar")
    logpath = os.path.join(lastTrajFolder, "bar2.log")
    # run traj
    os.chdir(currentTrajFolder)
    print("Running dynamic...")
    run_tinker(getDynCommand())
    print("Running bar1...")
    run_tinker(get_bar1_cmd(arc1path, arc2path))
    print("Running bar2...")
    run_tinker(getBar2Command(barpath))
    os.chdir(baseDir)

    # extract traj FE
    lines = open(logpath).readlines()
    stageFE = -100000
    for line in lines:
        fields = line.split()
        if line.contains("Free Energy via BAR Bootstrap"):
            stageFE = float(fields[5])
    if stageFE == -100000.0:
        print("Warning: bar2 failed")

    return stageFE



