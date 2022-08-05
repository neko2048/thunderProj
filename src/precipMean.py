import numpy as np
import pandas as pd
import netCDF4 as nc
from utils import PrecipLoader
from matplotlib.pyplot import *

def drawNumMap():
    figure(figsize=(12, 12))
    for i in range(len(groupKeys)):
        lonIdx, latIdx = groupKeys[i][0], groupKeys[i][1]
        num = groupVals[i]
        scatter(xlon[latIdx, lonIdx], xlat[latIdx, lonIdx], c=num, vmin=0, vmax=np.max(groupVals))
    colorbar()
    title("# of observation in WRF grid")
    savefig("test.jpg", dpi=200)


if __name__ == "__main__":
    config = {
    "obsPrecip": "../dat/precip/", 
    "lonlatIdx": "../dat/lonlatIdx/", 
    "wrfRainDir": "../dat/CFSR-WRF/RAIN/RAIN-", 
    "dailyPrecipOutDir": "../dat/dailyPrecip/"
    }

    southIdx = pd.read_csv(config["lonlatIdx"] + "south.csv")
    northIdx = pd.read_csv(config["lonlatIdx"] + "north.csv")
    eastIdx = pd.read_csv(config["lonlatIdx"] + "east.csv")
    westIdx = pd.read_csv(config["lonlatIdx"] + "west.csv")
    totalIdx = pd.concat((southIdx, northIdx, eastIdx, westIdx))
    numDict = totalIdx.groupby(["lonIdx", "latIdx"]).groups
    numDictKeys = list(numDict.keys())
    numDictVals = [len(x) for x in list(numDict.values())]
    wrfData = nc.Dataset(config["wrfRainDir"] + "201006.nc")
    xlon, xlat = wrfData["XLON"], wrfData["XLAT"]
    dateOpt = pd.date_range("20200101", "20201231", freq="1d")

    for year in np.unique(dateOpt.year):
        southPrecip = PrecipLoader(config["obsPrecip"] + "south/{}.csv".format(year)).loadData()
        northPrecip = PrecipLoader(config["obsPrecip"] + "north/{}.csv".format(year)).loadData()
        eastPrecip = PrecipLoader(config["obsPrecip"] + "east/{}.csv".format(year)).loadData()
        westPrecip = PrecipLoader(config["obsPrecip"] + "west/{}.csv".format(year)).loadData()
        for date in dateOpt[:1]:
            sumPrecip = np.full(fill_value=np.nan, shape=xlon.shape)
            countMap = np.zeros(shape=xlon.shape)
            for i in range(len(numDictKeys)):
                lonIdx, latIdx = int(numDictKeys[i][0]), int(numDictKeys[i][1])

                southValidPrecip = southPrecip["{:04d}{:02d}{:02d}".format(date.year, date.month, date.day)]\
                                   [np.logical_and(southIdx["lonIdx"] == lonIdx, southIdx["latIdx"] == latIdx)]
                southRainSum = np.nansum(southValidPrecip)
                southValidNum = np.sum(~np.isnan(southValidPrecip))

                northValidPrecip = northPrecip["{:04d}{:02d}{:02d}".format(date.year, date.month, date.day)]\
                                   [np.logical_and(northIdx["lonIdx"] == lonIdx, northIdx["latIdx"] == latIdx)]
                northRainSum = np.nansum(northValidPrecip)
                northValidNum = np.sum(~np.isnan(northValidPrecip))

                westValidPrecip = westPrecip["{:04d}{:02d}{:02d}".format(date.year, date.month, date.day)]\
                                  [np.logical_and(westIdx["lonIdx"] == lonIdx, westIdx["latIdx"] == latIdx)]
                westRainSum = np.nansum(westValidPrecip)
                westValidNum = np.sum(~np.isnan(westValidPrecip))

                eastValidPrecip = eastPrecip["{:04d}{:02d}{:02d}".format(date.year, date.month, date.day)]\
                                  [np.logical_and(eastIdx["lonIdx"] == lonIdx, eastIdx["latIdx"] == latIdx)]
                eastRainSum = np.nansum(eastValidPrecip)
                eastValidNum = np.sum(~np.isnan(eastValidPrecip))

                countMap[latIdx, lonIdx] = southValidNum + northValidNum + westValidNum + eastValidNum
                sumPrecip[latIdx, lonIdx] = southRainSum + northRainSum + westRainSum + eastRainSum

            meanPrecip = sumPrecip / countMap
            np.save(config["dailyPrecipOutDir"] + "{:04d}{:02d}{:02d}.npy".format(date.year, date.month, date.day), meanPrecip)




