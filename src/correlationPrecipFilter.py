import numpy as np
import netCDF4 as nc
import pandas as pd
from os import path
import json
from matplotlib.pyplot import *
from scipy import stats
from fullDateThunderGrid import Config

if __name__ == "__main__":
    hourType, dBZthreshold = input().split()#3, 40
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)
    config = Config({
        "hourType": str(hourType), 
        "home": "/home/twsand/fskao/thunderProj/",
        "obsPrecipDir": "%(home)sdat/dailyPrecip/", 
        "wrfPrecipDir": "%(home)sdat/CFSR-WRF-new/RAIN-modify/threeHourRAIN/", 
        "thdDir": "%(home)sdat/TDFRQ_%(hourType)sHR_UTC0/",
        "csJsonDir": "%(home)sdat/varJson/CS.json", 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        })

    year = 1990
    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1989-01-01", end="2008-12-01", freq="1MS")
    dateOptEnd = pd.date_range("1989-01-01", end="2008-12-01", freq="1M")
    obsPrecipThres = 1 # mm
    taiwanMask = np.load(config["taiwanMaskDir"])
    csConfig = json.load(open(config["csJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    
    existDateOpt = []
    existDateEndOpt = []
    
    for dateIdx in range(len(dateOpt)):
        if path.exists(config["wrfPrecipDir"]+"{Y}{M:02d}.nc".\
                       format(Y=dateOpt[dateIdx].year, M=dateOpt[dateIdx].month)) and \
                       dateOpt[dateIdx].month in monthOpt:
           existDateOpt.append(dateOpt[dateIdx])
           existDateEndOpt.append(dateOptEnd[dateIdx])
        else:
            continue

    validX = []
    validY = []
    validC = []
    validT = []

    figure(figsize=(10, 10), dpi=250)
    for dateIdx in range(len(existDateOpt)):
        wrfPrecipData = nc.Dataset(config["wrfPrecipDir"] + "{Y:04d}{M:02d}.nc".\
                               format(Y=existDateOpt[dateIdx].year, M=existDateOpt[dateIdx].month))
        wrfDate = pd.to_datetime(np.array(wrfPrecipData["time"]), format="%Y%m%d%H") + pd.Timedelta(8, "hr")
        # turn wrf date to UTC + 8
        wrfPrecip = wrfPrecipData["RAIN"]

        validPrecip = np.full(wrfPrecip.shape, False)
        #for day in np.unique(wrfDate.day):
        #    dayObsPrecip = np.load(config["obsPrecipDir"] + "{:04d}/{:02d}{:02d}.npy".format(wrfDate[0].year, wrfDate[0].month, day))
        #    wrfCumPrecip = np.sum(wrfPrecip[np.logical_and(wrfDate.day == day, wrfDate.month == wrfDate[0].month)], axis=0)
        #    print(wrfDate[np.logical_and(wrfDate.day == day, wrfDate.month == wrfDate[0].month)])
        for dayIdx in range(len(wrfDate)):
            dayObsPrecip = np.load(config["obsPrecipDir"] + "{:04d}/{:02d}{:02d}.npy".format(wrfDate[dayIdx].year, wrfDate[dayIdx].month, wrfDate[dayIdx].day))
            validPrecip[dayIdx][dayObsPrecip >= obsPrecipThres] = wrfPrecip[dayIdx][dayObsPrecip >= obsPrecipThres] > obsPrecipThres

        date = existDateOpt[dateIdx]
        if existDateOpt[dateIdx].month in monthOpt:
            print(date)
            dateData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["time"])
            thdData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["CGFRQ"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
            taiwanMask3D = np.tile(taiwanMask[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
            dateData3D = np.tile(dateData[:, np.newaxis, np.newaxis], reps=[1, thdData.shape[1], thdData.shape[2]])

        else:
            continue

        condition = np.array((dBZData >= dBZthreshold) * (thdData != 0) * (csData >= 1e-6) * (taiwanMask3D) * validPrecip, dtype=bool)
        if np.sum(condition) == 0: continue

        x = csData[condition]
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
    title("Correlation of {X} and {Y} ".format(X=csConfig["varName"], Y="CG"), fontsize=25, y=1.075)
    title("Y = {:.3f}X + {:.3f}\nCorr: {:.5f}".format(lreg.slope, lreg.intercept, lreg.rvalue), loc="left", fontsize=15)
    title("JJA from {} to {} ".format(existDateOpt[0].year, existDateOpt[-1].year), loc="right", fontsize=15)
    xlabel("{} [{}]".format(csConfig["description"], csConfig["unit"]), fontsize=15)
    ylabel("Frequency of Thunder in {} hr(s)".format(hourType), fontsize=15)
    xticks(fontsize=15)
    yticks(fontsize=15)
    ylim(bottom=0)
    cbar = colorbar(extend="max")
    cbar.set_label("Reflectivity [dBZ]")
    savefig("CG{}_dBZ{}.jpg".format(hourType, dBZthreshold))
    clf()





