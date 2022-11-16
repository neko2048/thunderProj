import json
import numpy as np
import pandas as pd
from os import path
import netCDF4 as nc
from scipy import stats
from matplotlib.pyplot import *
from fullDateThunderGrid import Config

class Evaluator:
    def __init__(self, precipThres):
        self.precipThres = precipThres
        self.meanError = []
        self.RMSE = []
        self.corrCoef = 0
        self.hits = 0
        self.falseAlarms = 0
        self.misses = 0
        self.correctNegatives = 0
        self.listObsPrecip = []
        self.listModPrecip = []

    def updateRMSE(self, obsPrecip, modPrecip):
        self.RMSE.append(np.sqrt(np.nanmean((modPrecip - obsPrecip) ** 2)) ** (1/2))

    def updateMeanError(self, obsPrecip, modPrecip):
        self.meanError.append(np.nanmean(modPrecip - obsPrecip))

    def updateCorrCoef(self, obsPrecip, modPrecip):
        self.listObsPrecip.append(obsPrecip)
        self.listModPrecip.append(modPrecip)

    def getCorrCoef(self):
        oneDimObsPrecip = np.array(self.listObsPrecip).flatten()
        oneDimModPrecip = np.array(self.listModPrecip).flatten()
        corrCoef = np.ma.corrcoef(np.ma.masked_invalid(oneDimObsPrecip), np.ma.masked_invalid(oneDimModPrecip))[0, 1]
        self.corrCoef = corrCoef
        return corrCoef

    def updateEvaluation(self, obsPrecip, modPrecip):
        self.hits += np.sum(np.logical_and(obsPrecip >= self.precipThres, modPrecip >= self.precipThres))
        self.falseAlarms += np.sum(np.logical_and(obsPrecip < self.precipThres, modPrecip >= self.precipThres))
        self.misses += np.sum(np.logical_and(obsPrecip >= self.precipThres, modPrecip < self.precipThres))
        self.correctNegatives += np.sum(np.logical_and(obsPrecip < self.precipThres, modPrecip < self.precipThres))

    def getBiasScore(self):
        return (self.hits + self.falseAlarms) / (self.hits + self.misses)

    def getPOD(self):
        """POD: probability of Detection"""
        return (self.hits) / (self.hits + self.misses)

    def getFAR(self):
        """FAR: false alarm ratio"""
        return (self.falseAlarms) / (self.hits + self.falseAlarms)

    def getThreatScore(self):
        return (self.hits) / (self.hits + self.falseAlarms)

    def getETS(self):
        """ETS: equitable threat score"""
        hits_random = (self.hits + self.misses) * (self.hits + self.falseAlarms) / (self.hits + self.falseAlarms + self.correctNegatives)
        return (self.hits - hits_random) / (self.hits + self.misses + self.falseAlarms - hits_random)

    def getPOFD(self):
        """POFD: probability of False Dection"""
        return (self.falseAlarms) / (self.falseAlarms + self. correctNegatives)

    def printSummaryTable(self):
        print("ME:   {:.5f}".format(np.mean(self.meanError)))
        print("RMSE: {:.5f}".format(np.mean(self.RMSE)))
        print("Corr: {:.5f}".format(self.corrCoef))
        print("BS:   {:.5f}".format(self.getBiasScore()))
        print("POD:  {:.5f}".format(self.getPOD()))
        print("FAR:  {:.5f}".format(self.getFAR()))
        print("TS:   {:.5f}".format(self.getThreatScore()))
        print("EST:  {:.5f}".format(self.getETS()))
        print("POFD: {:.5f}".format(self.getPOFD()))

if __name__ == "__main__":
    hourType, dBZthreshold = 3, 40#input().split()
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)
    precipThres = 1 # mm / day
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
    dateOpt = pd.date_range("1989-01-01", end="2008-12-01", freq="1MS") # 2008-12-01
    dateOptEnd = pd.date_range("1989-01-01", end="2008-12-01", freq="1M")
    obsPrecipThres = 1 # mm
    taiwanMask = np.load(config["taiwanMaskDir"])
    csConfig = json.load(open(config["csJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    
    existDateOpt = []
    existDateEndOpt = []
    figDate = []

    evaluator = Evaluator(precipThres)
    
    for dateIdx in range(len(dateOpt)):
        if path.exists(config["wrfPrecipDir"]+"{Y}{M:02d}.nc".\
                       format(Y=dateOpt[dateIdx].year, M=dateOpt[dateIdx].month)) and \
                       dateOpt[dateIdx].month in monthOpt:
           existDateOpt.append(dateOpt[dateIdx])
           existDateEndOpt.append(dateOptEnd[dateIdx])
        else:
            continue

    figure(figsize=(10, 10), dpi=250)
    for dateIdx in range(len(existDateOpt)):
        wrfPrecipData = nc.Dataset(config["wrfPrecipDir"] + "{Y:04d}{M:02d}.nc".\
                               format(Y=existDateOpt[dateIdx].year, M=existDateOpt[dateIdx].month))
        # turn wrf date to UTC + 8
        wrfDate = pd.to_datetime(np.array(wrfPrecipData["time"]), format="%Y%m%d%H") + pd.Timedelta(8, "hr")
        wrfPrecip = wrfPrecipData["RAIN"]


        for day in (pd.date_range(wrfDate[0], wrfDate[-1], freq="1d")):
            print(day)
            figDate.append(day)
            dayObsPrecip = np.load(config["obsPrecipDir"] + "{:04d}/{:02d}{:02d}.npy".format(day.year, day.month, day.day))
            dayObsPrecip = np.ma.masked_array(dayObsPrecip, taiwanMask == 0)
            wrfCumPrecip = np.sum(wrfPrecip[np.logical_and(wrfDate.day == day.day, day.month == wrfDate.month)], axis=0)
            wrfCumPrecip = np.ma.masked_array(wrfCumPrecip, taiwanMask == 0)

            evaluator.updateEvaluation(obsPrecip = dayObsPrecip, modPrecip = wrfCumPrecip)
            evaluator.updateRMSE(obsPrecip = dayObsPrecip, modPrecip = wrfCumPrecip)
            evaluator.updateMeanError(obsPrecip = dayObsPrecip, modPrecip = wrfCumPrecip)
            evaluator.updateCorrCoef(obsPrecip = dayObsPrecip, modPrecip = wrfCumPrecip)

    evaluator.getCorrCoef()
    evaluator.printSummaryTable()







