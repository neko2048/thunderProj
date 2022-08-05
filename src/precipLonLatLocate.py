import numpy as np
import pandas as pd
import netCDF4 as nc
from matplotlib.pyplot import *
from wrf import ll_to_xy
from utils import PrecipLoader

class PrecipRegrid():
    def __init__(self, precipData, year):
        self.year = year
        self.precipData = precipData

    def locateLonLat(self, xlon, xlat, direction):
        self.precipData["latIdx"] = np.zeros(shape=self.precipData["LON"].shape)
        self.precipData["lonIdx"] = np.zeros(shape=self.precipData["LON"].shape)
        for dotIdx in range(len(self.precipData)):
            if dotIdx % 1000 == 0:
                print("{}: {}/{}".format(direction, dotIdx+1, len(self.precipData["LON"])))
            targetLon, targetLat = self.precipData["LON"][dotIdx], self.precipData["LAT"][dotIdx]
            values = (xlon - targetLon) ** 2 + (xlat - targetLat) ** 2
            latIdx, lonIdx = np.where(values == np.amin(values))
            self.precipData["latIdx"][dotIdx] = latIdx
            self.precipData["lonIdx"][dotIdx] = lonIdx
        return self.precipData

if __name__ == "__main__":
    config = {
    "southDir": "../dat/precip/south/", 
    "eastDir": "../dat/precip/east/", 
    "westDir": "../dat/precip/west/", 
    "northDir": "../dat/precip/north/", 
    "wrfRainDir": "../dat/CFSR-WRF/RAIN/RAIN-", 
    "lonLatIdxOutDir": "../dat/lonlatIdx/"
    }
    wrfData = nc.Dataset(config["wrfRainDir"] + "201006.nc")
    xlon, xlat = wrfData["XLON"], wrfData["XLAT"]

    year = 2020
    precipDataCollect = {}
    for direction in ["west", "east",  "south", "north"]:
        precipLoader = PrecipLoader(config[direction + "Dir"] + "{}.csv".format(year))
        data = precipLoader.loadData()
        precipData = data
        
        precipRegrid = PrecipRegrid(precipData, year=year)
        precipData = precipRegrid.locateLonLat(xlon, xlat, direction)

        precipData.to_csv(config["lonLatIdxOutDir"] + "{}.csv".format(direction), 
                          columns = ("LON", "LAT", "lonIdx", "latIdx"))
