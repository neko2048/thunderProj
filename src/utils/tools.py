import numpy as np
import pandas as pd

class Config(dict):
   def __getitem__(self, item):
       return dict.__getitem__(self, item) % self

class ThunderRegrider(object):
    def __init__(self, thdFileDir):
        self.thdFileDir = thdFileDir

    def getDataset(self, year, month):
        try:
            data = pd.read_csv(self.thdFileDir)#, encoding="unicode_escape")
        except UnicodeDecodeError:
            data = pd.read_csv(self.thdFileDir, encoding="unicode_escape") # for data not uniformed e.g. 201907 201010...
            print("Use unicode_escape encoding")

        try:
            data.columns = ["time", "nanosec", "lat", "lon", "strength", "type"]
        except ValueError: # for data not uniformed e.g. 201010
            print("Detect changed data type")
            data = pd.read_csv(self.thdFileDir, encoding="unicode_escape", sep="\t")
            data.columns = ["time", "nanosec", "lat", "lon", "strength", "type"]


        if len(data.time) != 0 and "　" in data.time[0]: # space in the 'time' columne in the data after 2017/01/01
            print("Detect Bad Char.")
            data.time = [x[2:] for x in data.time]

        data.time = pd.to_datetime(data.time, format="%Y/%m/%d %H:%M") - pd.Timedelta(8, "hr")
        return data

    def getPeriodData(self, lowBoundDate, highBoundDate, thunderType="CG"):
        if lowBoundDate.month != highBoundDate.month:
            lowData = self.getDataset(lowBoundDate.year, lowBoundDate.month)
            highData = self.getDataset(highBoundDate.year, highBoundDate.month)
            data = pd.concat([lowData, highData])
        else:
            data = self.getDataset(lowBoundDate.year, lowBoundDate.month)
        condition = np.logical_and(data.time >= lowBoundDate, data.time < highBoundDate)
        condition = np.logical_and(condition, data.type == thunderType)
        return data[condition]

    def getFreq(self, year, month, hourType, thunderType, latOpt, lonOpt, hourOpt):
        freqArr = np.zeros(shape=(len(hourOpt), lonOpt.shape[0], lonOpt.shape[1]))
        for i in range(len(hourOpt)):
            lowTimeBound = hourOpt[i] - pd.Timedelta(hours=round(hourType/2, 1)) # include
            highTimeBound = hourOpt[i] + pd.Timedelta(hours=round(hourType/2, 1)) # not include
            #print("{} to {}".format(lowTimeBound, highTimeBound))
            selectThunderData = self.getPeriodData(lowTimeBound, highTimeBound, thunderType)

            if len(selectThunderData) != 0:
                for j in range(len(selectThunderData)):
                    targetLat, targetLon = np.array(selectThunderData.lat)[j], np.array(selectThunderData.lon)[j]
                    if targetLat <= np.max(latOpt) and targetLat >= np.min(latOpt) and targetLon <= np.max(lonOpt) and targetLon >= np.min(lonOpt):
                        values = (latOpt - targetLat) ** 2 + (lonOpt - targetLon) ** 2
                        latIdx, lonIdx = np.where(values == np.amin(values))
                        freqArr[i, latIdx, lonIdx] += 1
        return freqArr
