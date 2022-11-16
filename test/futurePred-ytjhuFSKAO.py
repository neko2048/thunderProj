import json
import numpy as np
import netCDF4 as nc
import pandas as pd
from os import path
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from fullDateThunderGrid import Config

if __name__ == "__main__":
    caseType = "hist"
    methodName = "fskao"
    hourType, dBZthreshold = 1, 38
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)
    config = Config({
        "hourType": str(hourType), 
        "home": "/home/twsand/fskao/thunderProj/", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy",
        "csJsonDir": "%(home)sdat/varJson/CS-{}.json".format(caseType), 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max-{}.json".format(caseType), 
        "freqMap": "%(home)sdat/freqMap.npy"
        })

    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1980-01-01", end="2005-12-01", freq="1MS")
    dateOptEnd = pd.date_range("1980-01-01", end="2005-12-01", freq="1M")
    taiwanMask = np.load(config["taiwanMaskDir"])
    csConfig = json.load(open(config["csJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    annualFreqMap = np.where(taiwanMask, np.load(config["freqMap"]), np.nan)
    percentileDict = {
        0: 1, 
        10: 1.241379, 
        20: 1.390625, 
        30: 1.515151, 
        40: 1.681818, 
        50: 1.844444, 
        60: 2.027777, 
        70: 2.225806, 
        80: 2.47, 
        90: 2.875, 
        100: 4.6, 
    }
    percentileFunc = { # key for lower bound
         0: lambda x:  0.085 * x + 0.804, 
        10: lambda x:  0.050 * x + 0.906, 
        20: lambda x:  0.027 * x + 1.010, 
        30: lambda x:  0.002 * x + 1.015, 
        40: lambda x:  0.037 * x + 1.113, 
        50: lambda x:  0.135 * x + 0.604, 
        60: lambda x:  0.069 * x + 1.350, 
        70: lambda x:  0.028 * x + 1.325, 
        80: lambda x:  0.038 * x + 1.623, 
        90: lambda x: -0.022 * x + 2.400, 
    }
    percentileMap = np.full(fill_value=np.nan, shape=annualFreqMap.shape)
    for key, val in percentileDict.items():
        percentileMap[annualFreqMap >= val] = key
    #np.save("../test/percentileMapYTJHU.npy", percentileMap)
    existDateOpt = []
    existDateEndOpt = []
    
    for dateIdx in range(len(dateOpt)):
        if path.exists(csConfig["dir"]+"{Y}{M:02d}.nc".\
                       format(Y=dateOpt[dateIdx].year, M=dateOpt[dateIdx].month)) and \
                       dateOpt[dateIdx].month in monthOpt:
           existDateOpt.append(dateOpt[dateIdx])
           existDateEndOpt.append(dateOptEnd[dateIdx])
        else:
            continue
    accumThd = np.full(fill_value=0., shape=(123, 83))

    for dateIdx in range(len(existDateOpt)):
        date = existDateOpt[dateIdx]
        if existDateOpt[dateIdx].month in monthOpt:
            print(date)
            dateData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["time"])
            xlon = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["XLON"])
            xlat = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["XLAT"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
            taiwanMask3D = np.tile(taiwanMask[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
            dateData3D = np.tile(dateData[:, np.newaxis, np.newaxis], reps=[1, dBZData.shape[1], dBZData.shape[2]])
            percentileMap3D = np.tile(percentileMap[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
        else:
            continue

        condition = np.array((dBZData >= dBZthreshold) * \
                             (csData >= 1e-6) * (taiwanMask3D), dtype=bool)
        if np.sum(condition) == 0: continue

        maskCSData = np.where(condition, csData, np.nan)
        predThd = np.zeros(shape=maskCSData.shape)

        for key in np.arange(0, 100, 10):
            predThd[percentileMap3D==key] = percentileFunc[key](maskCSData[percentileMap3D==key])
        predThd[percentileMap3D==100] = percentileFunc[90](maskCSData[percentileMap3D==100])

        accumThd += np.nansum(predThd, axis=0)
    np.save("./test/accumThd-{}-{}.npy".format(caseType, methodName), accumThd)
    print("Saved accumulated Thunder")

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
    FREQ = ax.pcolormesh(xlon, xlat, np.where(taiwanMask, accumThd, np.nan)/len(existDateOpt)*3, vmin=0, vmax=40, cmap="turbo")
    print(len(existDateOpt)/3)
    cbar = plt.colorbar(FREQ, extend="max")
    cbar.ax.tick_params(labelsize=15)
    plt.title("Annual Mean Thunder Frequency", fontsize=20, y=1.05)

    plt.title("{}-{} JJA".format(existDateOpt[0].year, existDateOpt[-1].year), loc="right", fontsize=15)
    plt.title(r"hourType={} | dBZmax$\geq${}".format(hourType, dBZthreshold), loc="left", fontsize=15)
    ax.set_xlim(119, 122.9)
    ax.set_xlabel("Longitude", fontsize=20)
    ax.set_ylabel("Latitude", fontsize=20)
    ax.gridlines(draw_labels=False, alpha=0.75, 
                 xlocs=np.arange(np.min(xlat), np.max(xlat), 1), 
                 ylocs=np.arange(np.min(xlon), np.max(xlon), 1), color="grey")
    ax.set_yticks([round(x, 1) for x in np.arange(np.min(xlat), np.max(xlat), 1)])
    ax.set_xticks([np.ceil(x)+0.5 for x in np.arange(np.min(xlon), np.max(xlon), 1)][:-1])
    ax.tick_params(axis="both", labelsize=15)
    ax.coastlines(resolution="10m")
    plt.savefig("./test/{}Map-{}.jpg".format(caseType, methodName), dpi=250)
    plt.clf()

