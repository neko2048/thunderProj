import numpy as np
import netCDF4 as nc
import pandas as pd
from matplotlib.pyplot import *
from os import path
from scipy import stats
import json
import seaborn as sns

if __name__ == "__main__":
    #thdHour, dBZthreshold = input().split()
    thdHour = 1#int(thdHour)
    dBZthreshold = 40#int(dBZthreshold)
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

    validThd = []
    validCS = []
    validdBZ = []
    
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
        print(np.sum(condition))
        x = thdData[condition]
        y = csData[condition]
        c = dBZData[condition]

        if np.sum(thdData != 0):
            validThd.extend(x)
            validCS.extend(y)
        scatter(x, y, c=c, \
                cmap="rainbow", vmin=40, edgecolor="white", \
                linewidths=0.5, s=60)

    #STR = scatter([0]*6, [-100]*6, c=np.arange(35, 41), 
    #        cmap="rainbow", vmin=35, vmax=40, edgecolor="white", \
    #        linewidths=0.5, s=60, alpha=0.7)
    print("Calculate Linear Regression")
    lreg = stats.linregress(x=validThd, y=validCS)
    print("Printing")
    plot(validThd, lreg.intercept + lreg.slope*np.array(validThd), color="black")
    title("Correlation of {X} and {Y}".format(X="CG", Y=csConfig["varName"]), fontsize=25, y=1.05)
    title("Corr: {:.3f}".format(lreg.rvalue), loc="left", fontsize=15)
    title("JJA from {} to {} ".format(existDateOpt[0].year, existDateOpt[-1].year), loc="right", fontsize=15)
    xlabel("Frequency of Thunder in {} hr(s)".format(thdHour), fontsize=15)
    ylabel("{} [{}]".format(csConfig["description"], csConfig["unit"]), fontsize=15)
    xticks(fontsize=15)
    yticks(fontsize=15)
    #legend(handles=STR.legend_elements()[0], title="dBZ", loc="upper right", \
    #       labels=["35", "36", "37", "38", "39", ">=40"], fontsize=15, title_fontsize=15)
    ylim(bottom=-5)
    cbar = colorbar(extend="max")
    cbar.set_label("Reflectivity [dBZ]")
    savefig("CG{}_dBZ{}.jpg".format(thdHour, dBZthreshold))
    clf()

