import numpy as np
import netCDF4 as nc
import pandas as pd
from os import path
import json
from matplotlib.pyplot import *
from scipy import stats
from fullDateThunderGrid import Config

if __name__ == "__main__":
    hourType, dBZthreshold = 3, 40#input().split()
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

    for dateIdx in range(len(existDateOpt))[-4:-3]:
        wrfPrecipData = nc.Dataset(config["wrfPrecipDir"] + "{Y:04d}{M:02d}.nc".\
                               format(Y=existDateOpt[dateIdx].year, M=existDateOpt[dateIdx].month))
        # turn wrf date to UTC + 8
        wrfDate = pd.to_datetime(np.array(wrfPrecipData["time"]), format="%Y%m%d%H") + pd.Timedelta(8, "hr")
        wrfPrecip = wrfPrecipData["RAIN"]


        for day in (pd.date_range(wrfDate[0], wrfDate[-1], freq="1d"))[4:6]:
            fig, axs = subplots(1, 2, figsize=(20, 10), dpi=250)
            print(day)
            dayObsPrecip = np.load(config["obsPrecipDir"] + "{:04d}/{:02d}{:02d}.npy".format(day.year, day.month, day.day))
            wrfCumPrecip = np.sum(wrfPrecip[np.logical_and(wrfDate.day == day.day, day.month == wrfDate.month)], axis=0)
            wrfCumPrecip = np.ma.masked_array(wrfCumPrecip, taiwanMask == 0)
            axs[0].pcolormesh(wrfCumPrecip, vmin=0, vmax=50, cmap='jet')
            WRFRAIN = axs[1].pcolormesh(dayObsPrecip, vmin=0, vmax=50, cmap='jet')


            fig.subplots_adjust(right=0.8)
            cbar_ax = fig.add_axes([0.82, 0.1, 0.025, 0.8])
            fig.colorbar(WRFRAIN, cax=cbar_ax, extend="max")
            axs[0].set_xticks([])
            axs[0].set_yticks([])
            axs[1].set_xticks([])
            axs[1].set_yticks([])
            suptitle("Daily Precipitation [mm/day]\nDate: {:04d}/{:02d}/{:02d}".format(day.year, day.month, day.day), fontsize=25)
            savefig("compare{:04d}{:02d}{:02d}.jpg".format(day.year, day.month, day.day))
            clf()








