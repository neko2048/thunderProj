import numpy as np
import netCDF4 as nc
import pandas as pd
from os import path
import json
from utils import NCwriter
from fullDateThunderGrid import Config

if __name__ == "__main__":
    hourType = 3
    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "rainJsonDir": "%(home)sdat/varJson/threeHourRAIN.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        })

    if hourType == 1:
        config["threeHourRainOutDir"] = "%(home)sdat/CFSR-WRF-new/RAIN-modify/oneHourMidRAIN/"
    elif hourType == 3:
        config["threeHourRainOutDir"] = "%(home)sdat/CFSR-WRF-new/RAIN-modify/threeHourMidRAIN/"

    rainConfig = json.load(open(config["rainJsonDir"]))
    taiwanMask = np.load(config["taiwanMaskDir"])
    ncWriter = NCwriter()
    monthOpt = [3, 4, 5, 6, 7, 8, 9, 10]
    dateOpt = pd.date_range("1989-01-01", end="2008-12-01", freq="1MS")
    existDateOpt = []
    for date in dateOpt:
        if path.exists(rainConfig["dir"]+"{Y}{M:02d}.nc".format(Y=date.year, M=date.month)):
           existDateOpt.append(date)
        else:
            continue


    exampleNC = nc.Dataset(rainConfig["dir"] + "{Y}{M:02d}.nc".format(Y=2005, M=5))
    lonOpt, latOpt = exampleNC["XLON"], exampleNC["XLAT"]

    for previousDate, currentDate, nextDate in zip(existDateOpt[:-2], existDateOpt[1:-1], existDateOpt[2:]): # not count end data as no header term for minus (but OK as we don't use 201010 data)
        rainData = np.array(nc.Dataset(rainConfig["dir"] + "{Y:04d}{M:02d}.nc".format(Y=currentDate.year, M=currentDate.month))[rainConfig["varName"]])
        previousRainData = np.array(nc.Dataset(rainConfig["dir"] + "{Y:04d}{M:02d}.nc".format(Y=previousDate.year, M=previousDate.month))[rainConfig["varName"]])
        nextRainData = np.array(nc.Dataset(rainConfig["dir"] + "{Y:04d}{M:02d}.nc".format(Y=nextDate.year, M=nextDate.month))[rainConfig["varName"]])
        threeHourRain = np.zeros(shape=(rainData.shape[0], rainData.shape[1], rainData.shape[2]))

        if currentDate.month == 12:
            hourOpt = pd.date_range("{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=currentDate.year, M=currentDate.month, D=currentDate.day), \
                                    "{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=int(currentDate.year)+1, M=1, D=currentDate.day), \
                                    freq="3H")
        else:
            hourOpt = pd.date_range("{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=currentDate.year, M=currentDate.month, D=currentDate.day), \
                                    "{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=currentDate.year, M=int(currentDate.month)+1, D=currentDate.day), \
                                    freq="3H")

        threeHourRain[-1, :, :] = ((rainData[-1] + nextRainData[0]) / 2) / (3 / hourType)
        for timeIdx in range(0, rainData.shape[0] - 1):
            threeHourRain[timeIdx, :, :] =((rainData[timeIdx] + rainData[timeIdx+1]) / 2) / (3 / hourType)

        ncWriter.writeToNC(config["threeHourRainOutDir"] + "{Y:04d}{M:02d}.nc".format(Y=currentDate.year, M=currentDate.month), 
                           lonOpt=lonOpt, latOpt=latOpt, hourOpt=hourOpt, 
                           arr=threeHourRain, varName="RAIN", varDescrip="Rain")



