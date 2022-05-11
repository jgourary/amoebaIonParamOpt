import os
import time
import subprocess
import numpy as np
import concurrent.futures


def writeprm():
    keys = [line.split()[0] for line in open("p0.txt").readlines()]
    oFile = open("temp.prm", 'w')
    lines = open("template.prm").readlines()
    for line in lines:
        if "PRM_" in line:
            for i in range(len(keys)):
                search = "PRM_" + keys[i] + "_"
                if search in line and (line[0:1] != "#"):
                    params[i] = "%10.8f" % (float(params[i]))
                    line = line.replace(search, str(params[i]))
        oFile.write(line)
    oFile.close()
    return


def submit(dirname):
    os.system(f"cp amoeba09.prm_ {dirname}")
    homedir = "/home/liuchw/autoBAR-demo"
    os.chdir(os.path.join(homedir, dirname))
    subcmd = "python $AUTOBAR/autoBAR.py auto"
    subprocess.run(subcmd, shell=True)
    return


def getHFE():
    homedir = "/home/liuchw/autoBAR-demo"
    dirnames = list(np.loadtxt("hfe_expt.txt", usecols=(0,), dtype="str", unpack=True))
    for dirname in dirnames:
        os.system(
            f"rm -f {homedir}/amoeba09.prm_ {homedir}/{dirname}/amoeba09.prm_ {homedir}/{dirname}/result.txt; wait")
        os.system(
            f"rm -f {homedir}/{dirname}/gas/gas-e200-v200.* {homedir}/{dirname}/liquid/liquid-e200-v200.* {homedir}/{dirname}/liquid/liquid-e100-v100.bar {homedir}/{dirname}/liquid/liquid-e100-v100.ene; wait")
    writeprm()

    jobs = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(submit, dirname) for dirname in dirnames]
        for f in concurrent.futures.as_completed(results):
            jobs.append(f.result())

    while True:
        hfes_calc = []
        for dirname in dirnames:
            resultfile = os.path.join(homedir, dirname, "result.txt")
            if os.path.isfile(resultfile):
                lines = open(resultfile).readlines()
                if len(lines) == 38:
                    hfes_calc.append(float(lines[-1].split()[-2]))
        if len(hfes_calc) == len(dirnames):
            break
        else:
            time.sleep(5)
    print("Current HFEs", hfes_calc)
    return hfes_calc