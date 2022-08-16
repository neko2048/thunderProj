import numpy as np
import netCDF4 as nc
import pandas as pd
from matplotlib.pyplot import *
from os import path
from scipy import stats
import json
import seaborn as sns
from countyJudge import CountyJudger
from fullDateThunderGrid import Config

class TxtOutputer(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir

    def saveData(self, var, fileName):
        fileDir = self.outputDir + fileName + ".txt"
        np.savetxt(fileDir, var)
        print("Save to: {}".format(fileDir))
        return None

if __name__ == "__main__":
    hourType, dBZthreshold = 1, 40#input().split()
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)

    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "hourType": str(hourType), 
        "wrfDir": "%(home)sdat/CFSR-WRF/CS/", 
        "thdDir": "%(home)sdat/TDFRQ_%(hourType)sHR_UTC0/",
        "csJsonDir": "%(home)sdat/varJson/CS.json", 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        "txtOutputDir": "%(home)sdat/txtDat/"
        })

    if hourType == 1:
        config["rainJsonDir"] = config["home"] + "dat/varJson/oneHourMidRAIN.json"
    elif hourType == 3:
        config["rainJsonDir"] = config["home"] + "dat/varJson/threeHourMidRAIN.json"

    txtOutputer = TxtOutputer(config["txtOutputDir"])
    csConfig = json.load(open(config["csJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    rainConfig = json.load(open(config["rainJsonDir"]))
    taiwanMask = np.load(config["taiwanMaskDir"])
    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1989-01-01", end="2008-12-01", freq="1MS")
    existDateOpt = []
    for date in dateOpt:
        if path.exists(config["thdDir"]+"{Y}{M:02d}.nc".format(Y=date.year, M=date.month)) and \
           path.exists(csConfig["dir"]+"{Y}{M:02d}.nc".format(Y=date.year, M=date.month)):
           existDateOpt.append(date)
        else:
            continue

    validX = []
    validY = []
    validC = []
    validT = []

    figure(figsize=(10, 10), dpi=250)
    for date in existDateOpt:
        if date.month in monthOpt:
            print(date)
            dateData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["time"])
            thdData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["CGFRQ"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
            rainData = np.array(nc.Dataset(rainConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[rainConfig["varName"]])
            taiwanMask3D = np.tile(taiwanMask[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
            dateData3D = np.tile(dateData[:, np.newaxis, np.newaxis], reps=[1, thdData.shape[1], thdData.shape[2]])

        else:
            continue

        condition = np.array((dBZData >= dBZthreshold) * (thdData != 0) * (csData >= 1e-6) * (taiwanMask3D), dtype=bool)
        x = rainData[condition]
        y = thdData[condition]
        c = dBZData[condition]
        t = dateData3D[condition]

        if np.sum(condition != 0):
            validX.extend(x)
            validY.extend(y)
            validC.extend(c)
            validT.extend(t)
        scatter(x, y, c=c, \
                cmap="rainbow", vmin=35, vmax=40, edgecolor="white", \
                linewidths=0.5, s=60)

    print("Calculate Linear Regression")
    lreg = stats.linregress(x=validX, y=validY)
    print("Printing")
    plot(validX, lreg.intercept + lreg.slope*np.array(validX), color="black")
    title("Correlation of {X} and {Y} ".format(X=rainConfig["varName"], Y="CG"), fontsize=25, y=1.075)
    title("Y = {:.3f}X + {:.3f}\nCorr: {:.5f}".format(lreg.slope, lreg.intercept, lreg.rvalue), loc="left", fontsize=15)
    title("JJA from {} to {} ".format(existDateOpt[0].year, existDateOpt[-1].year), loc="right", fontsize=15)
    xlabel("{} [{}]".format(rainConfig["description"], rainConfig["unit"]), fontsize=15)
    ylabel("Frequency of Thunder in {} hr(s)".format(hourType), fontsize=15)
    xticks(fontsize=15)
    yticks(fontsize=15)
    ylim(bottom=0)
    cbar = colorbar(extend="max")
    cbar.set_label("Reflectivity [dBZ]")
    savefig("CG{}_dBZ{}.jpg".format(hourType, dBZthreshold))
    clf()
    #txtOutputer.saveData(var=validX, fileName="csData_Hr{}Thres{}".format(hourType, dBZthreshold))
    #txtOutputer.saveData(var=validY, fileName="thData_Hr{}Thres{}".format(hourType, dBZthreshold))
    #txtOutputer.saveData(var=validC, fileName="dBZData_Hr{}Thres{}".format(hourType, dBZthreshold))
    #txtOutputer.saveData(var=validT, fileName="dateData_Hr{}Thres{}".format(hourType, dBZthreshold))
