import fiona
from rtree import index
import pandas as pd
import netCDF4 as nc
import numpy as np
from shapely.geometry import shape, Point, Polygon
import matplotlib.pyplot as plt
#import geopandas as gpd
from fullDateThunderGrid import Config

class CountyJudger(object):
    """
    docstring for CountyJudger
    ref: https://op8867555.github.io/posts/2017-09-16-python-getting-town-from-gps-coord.html
    """
    def __init__(self, shpDir):
        self.shpDir = shpDir
        self.taiwanCountryShape = fiona.open(self.shpDir)
        self.shapes = {}
        self.properties = {}
        self.collectData()
        self.countyNumDict = {
            "A": 1, 
            "B": 2, 
            "C": 3, 
            "D": 4, 
            "E": 5, 
            "F": 6, 
            "G": 7, 
            "H": 8, 
            "I": 9, 
            "J": 10, 
            "K": 11, 
            "M": 12, 
            "N": 13, 
            "O": 14, 
            "P": 15, 
            "Q": 16, 
            "T": 17, 
            "U": 18, 
            "V": 19, 
            "W": 20, 
            "X": 21, 
            "Z": 22,
        }
        self.countyMap = {
            "A": "Taipei City", 
            "B": "Taichung City", 
            "C": "Keelung City", 
            "D": "Tainan City", 
            "E": "Kaohsiung City", 
            "F": "New Taipei City", 
            "G": "Yilan County", 
            "H": "Taoyuan City", 
            "I": "Chiayi City", 
            "J": "Hsinchu County", 
            "K": "Miaoli County", 
            "M": "Nantou County", 
            "N": "Changhua County", 
            "O": "Hsinchu City", 
            "P": "Yunlin County", 
            "Q": "Chiayi County", 
            "T": "Pingtung County", 
            "U": "Hualien County", 
            "V": "Taitung County", 
            "W": "Kinmen County", 
            "X": "Penghu County", 
            "Z": "Lienchiang County"}

    def collectData(self):
        for f in self.taiwanCountryShape:
            town_id = int(f['properties']['TOWNCODE'])
            self.shapes[town_id] = shape(f['geometry'])
            self.properties[town_id] = f['properties']
        self.idx = index.Index()
        for town_id, town_shape in self.shapes.items():
            self.idx.insert(town_id, town_shape.bounds)

    def searchTownIdx(self, x, y):
        return next((town_id
                     for town_id in self.idx.intersection((x, y))
                     if self.shapes[town_id].contains(Point(x, y))), None)

    def searchCountyIdx(self, x, y):
        townIdx = self.searchTownIdx(x, y)
        if townIdx != None:
            return self.properties[townIdx]["COUNTYID"]
        return None

    def searchCountyNum(self, x, y):
        townIdx = self.searchTownIdx(x, y)
        if townIdx != None:
            return self.countyNumDict[self.properties[townIdx]["COUNTYID"]]
        return None

    def searchCountyName(self, x, y):
        townIdx = self.searchTownIdx(x, y)
        if townIdx != None:
            return self.countyMap[self.properties[townIdx]["COUNTYID"]]
        return None

    def isInTaiwan(self, x, y):
        taiwanIdx = [x for x in range(1, 20)] # without islands
        townIdx = self.searchCountyNum(x, y)
        if townIdx in taiwanIdx:
            return True
        else: return False

if __name__ == "__main__":

    shpDir = '../dat/taiwanCountyShape/TOWN_MOI_1100415.shp'
    countyJudger = CountyJudger(shpDir)
    countyName = countyJudger.isInTaiwan(y=25.0263075,x=121.543846)
    print(countyName)

    hourType = 1
    config = Config({
        "hourType": str(hourType), 
        "wrfDir": "../dat/CFSR-WRF/CS/", 
        "thdDir": "../dat/TLDS/",
        "outputDir": "../dat/TDFRQ_%(hourType)sHRfull/", 
        })

    #ncWriter = NCwriter(outputDir=config["outputDir"])
    #dateRange = pd.date_range("1989-01-01", end="2022-01-01", freq="1MS")
    dateRange = pd.date_range("2019-06-01", end="2022-01-01", freq="1MS")
    #dateRange = pd.date_range("1989-01-01", end="1989-05-01", freq="1MS")

    initWRFfileDir = config["wrfDir"] + "CS-198003.nc"
    initWRFdata = nc.Dataset(initWRFfileDir)
    lonOpt = np.array(initWRFdata["XLON"]) # shape = (lat, lon)
    latOpt = np.array(initWRFdata["XLAT"]) # shape = (lat, lon)
    inTaiwanMask = np.zeros(shape=lonOpt.shape)
    for i in range(lonOpt.shape[0]):
        for j in range(lonOpt.shape[1]):
            inTaiwanMask[i, j] = countyJudger.isInTaiwan(x=lonOpt[i, j], y=latOpt[i, j])
    np.save("../dat/taiwanMask.npy", inTaiwanMask)
    print("saved")












