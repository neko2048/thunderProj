import numpy as np
import netCDF4 as nc
import pandas as pd
from matplotlib.pyplot import *
from os import path
from scipy import stats
import json
import seaborn as sns

if __name__ == "__main__":
    thdHour, dBZthreshold = input().split()
    thdHour = int(thdHour)
    dBZthreshold = int(dBZthreshold)
    home = "/home/twsand/fskao/thunderProj/"
    thdFreqDir = home + "dat/TDFRQ_{}HR/".format(thdHour) # CGFRQ
    csConfig = json.load(open(home + "dat/varJson/CS.json"))
    dBZConfig = json.load(open(home + "dat/varJson/dBZ_max.json"))
    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1989-01-01", end="2010-12-31", freq="1m")
    existDateOpt = []

    for date in dateOpt:
        if path.exists(thdFreqDir+"{Y}{M:02d}.nc".format(Y=date.year, M=date.month)) and \
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
            thdData = np.array(nc.Dataset(thdFreqDir + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["CGFRQ"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
        else:
            continue

        condition = dBZData >= dBZthreshold
        x = thdData[condition]
        y = csData[condition]
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
    title("Correlation of {X} and {Y}".format(X="CG", Y=csConfig["varName"]), fontsize=25, y=1.05)
    title("Corr: {:.3f}".format(lreg.rvalue), loc="left", fontsize=15)
    title("JJA from {} to {} ".format(existDateOpt[0].year, existDateOpt[-1].year), loc="right", fontsize=15)
    xlabel("Frequency of Thunder in {} hr(s)".format(thdHour), fontsize=15)
    ylabel("{} [{}]".format(csConfig["description"], csConfig["unit"]), fontsize=15)
    xticks(fontsize=15)
    yticks(fontsize=15)
    ylim(bottom=-5)
    cbar = colorbar(extend="max")
    cbar.set_label("Reflectivity [dBZ]")
    savefig("CG{}_dBZ{}.jpg".format(thdHour, dBZthreshold))
    clf()

