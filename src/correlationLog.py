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

if __name__ == "__main__":
    hourType, dBZthreshold = input().split()
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
        })
    csConfig = json.load(open(config["csJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    taiwanMask = np.load(config["taiwanMaskDir"])
    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1989-01-01", end="2010-12-01", freq="1MS")
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
    
    figure(figsize=(10, 10), dpi=250)
    for date in existDateOpt:
        if date.month in monthOpt:
            print(date)
            thdData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["CGFRQ"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
            taiwanMask3D = np.tile(taiwanMask[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
        else:
            continue

        condition = np.array((dBZData >= dBZthreshold) * (thdData != 0) * (csData >= 1e-6) * (taiwanMask3D), dtype=bool)
        x = np.log10(csData[condition])
        y = thdData[condition]
        c = dBZData[condition]
        if np.sum(condition != 0):
            validX.extend(x)
            validY.extend(y)
            validC.extend(c)
        scatter(x, y, c=c, \
                cmap="rainbow", vmin=35, vmax=40, edgecolor="white", \
                linewidths=0.5, s=60)

    print("Calculate Linear Regression")
    lreg = stats.linregress(x=validX, y=validY)
    print("Printing")
    plot(validX, lreg.intercept + lreg.slope*np.array(validX), color="black")
    title("Correlation of log({X}) and {Y} ".format(X=csConfig["varName"], Y="CG"), fontsize=25, y=1.075)
    title("Y = {:.3f}X + {:.3f}\nCorr: {:.5f}".format(lreg.slope, lreg.intercept, lreg.rvalue), loc="left", fontsize=15)
    title("JJA from {} to {} ".format(existDateOpt[0].year, existDateOpt[-1].year), loc="right", fontsize=15)
    xlabel("{} [{}]".format(csConfig["description"], csConfig["unit"]), fontsize=15)
    ylabel("Frequency of Thunder in {} hr(s)".format(hourType), fontsize=15)
    xticks([x for x in range(-7, 3)], fontsize=15)
    yticks(fontsize=15)
    xlim(right=2)
    cbar = colorbar(extend="max")
    cbar.set_label("Reflectivity [dBZ]")
    savefig("CG{}_dBZ{}Log.jpg".format(hourType, dBZthreshold))
    clf()

