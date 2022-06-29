import numpy as np
import pandas as pd
import netCDF4 as nc
from matplotlib.pyplot import *
from os import path
import string

class Config(dict):
   def __getitem__(self, item):
       return dict.__getitem__(self, item) % self


class ThunderRegrider(object):
    def __init__(self, thdDir):
        self.thdDir = thdDir

    def getDataset(self, year, month):
        data = pd.read_csv(self.thdDir + "{YEAR}{MONTH:02d}.TXT".format(YEAR=year, MONTH=month))
        data.columns = ["time", "nanosec", "lat", "lon", "strength", "type"]
        data.time = pd.to_datetime(data.time, format="%Y/%m/%d %H:%M")
        return data

    def getPeriodData(self, lowBoundDate, highBoundDate):
        if lowBoundDate.month != highBoundDate.month:
            lowData = self.getDataset(lowBoundDate.year, lowBoundDate.month)
            highData = self.getDataset(highBoundDate.year, highBoundDate.month)
            data = pd.concat([lowData, highData])
        else:
            data = self.getDataset(lowBoundDate.year, lowBoundDate.month)
        condition = np.logical_and(data.time >= lowBoundDate, data.time < highBoundDate)
        return data[condition]

    def getFreq(self, year, month, hourType):
        freqArr = np.zeros(shape=(len(hourOpt), lonOpt.shape[0], lonOpt.shape[1]))
        for i in range(len(hourOpt)):
            lowTimeBound = hourOpt[i] - pd.Timedelta(hours=round(hourType/2, 1)) # include
            highTimeBound = hourOpt[i] + pd.Timedelta(hours=round(hourType/2, 1)) # not include
            #print("{} to {}".format(lowTimeBound, highTimeBound))
            selectThunderData = self.getPeriodData(lowTimeBound, highTimeBound)

            if len(selectThunderData) != 0:
                for j in range(len(selectThunderData)):
                    targetLat, targetLon = np.array(selectThunderData.lat)[j], np.array(selectThunderData.lon)[j]
                    if targetLat <= np.max(latOpt) and targetLat >= np.min(latOpt) or targetLon <= np.max(lonOpt) or targetLon >= np.min(lonOpt):
                        values = (latOpt - targetLat) ** 2 + (lonOpt - targetLon) ** 2
                        latIdx, lonIdx = np.where(values == np.amin(values))
                        freqArr[i, latIdx, lonIdx] += 1
        return freqArr

class NCwriter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        pass

    def writeNC(self, year, month, hourType, freqArr):
        fn = self.outputDir + "{YEAR}{MONTH:02d}.nc".\
             format(YEAR=year, MONTH=month)
        ds = nc.Dataset(fn, 'w', format='NETCDF4')
        ds.description = 'Frequency of CG Thunder'
        time = ds.createDimension('time', len(hourOpt))
        LON = ds.createDimension('LON', lonOpt.shape[1])
        LAT = ds.createDimension('LAT', lonOpt.shape[0])

        times = ds.createVariable('time', 'i8', ('time',))
        XLAT = ds.createVariable('XLAT', 'f4', ('LAT', 'LON'))
        XLON = ds.createVariable('XLON', 'f4', ('LAT', 'LON'))
        CGFREQ = ds.createVariable('CGFREQ', 'i8', ('time', 'LAT', 'LON',))
        times[:] = np.array(wrfData["time"])
        XLAT[:, :] = np.array(wrfData["XLON"])
        XLON[:, :] = np.array(wrfData["XLAT"])
        CGFREQ[:, :, :] = freqArr
        ds.close()
        print("    -> {YEAR}{MONTH:02d} NC WRITEN".format(YEAR=year, MONTH=month))

if __name__ ==  "__main__":
    hourType = 3 
    config = Config({
        "hourType": str(hourType), 
        "wrfDir": "../dat/CFSR-WRF/CS/", 
        "thdDir": "../dat/TLDS/",
        "outputDir": "../dat/TDFRQ_%(hourType)sHR/", 
        })

    thunderRegrider = ThunderRegrider(thdDir=config["thdDir"])
    ncWriter = NCwriter(outputDir=config["outputDir"])
    dateRange = pd.date_range("1980-03-01", end="2010-11-01", freq="1m")

    for date in dateRange:
        # ========== file existence check ==========
        wrfFileDir = config["wrfDir"] + "CS-{YEAR}{MON:02d}.nc".format(YEAR=date.year, MON=date.month)
        thdFileDirOpt1 = config["thdDir"] + "{YEAR}{MON:02d}.txt".format(YEAR=date.year, MON=date.month)
        thdFileDirOpt2 = config["thdDir"] + "{YEAR}{MON:02d}.TXT".format(YEAR=date.year, MON=date.month)

        if path.exists(wrfFileDir) and (path.exists(thdFileDirOpt1) or path.exists(thdFileDirOpt2)):
            print("========== {YEAR}{MON:02d} EXISTS ==========".format(YEAR=date.year, MON=date.month))
            thdFileDir = thdFileDirOpt1 if path.exists(thdFileDirOpt1) else thdFileDirOpt2
        else:
            print("========== {YEAR}{MON:02d} 404 NF ==========".format(YEAR=date.year, MON=date.month))
            continue

        wrfData = nc.Dataset(wrfFileDir)
        hourOpt = wrfData["time"]
        hourOpt = pd.to_datetime(np.array(hourOpt), format="%Y%m%d%H")
        lonOpt = np.array(wrfData["XLON"]) # shape = (lat, lon)
        latOpt = np.array(wrfData["XLAT"]) # shape = (lat, lon)


        freqArr = thunderRegrider.getFreq(year = date.year, 
                                          month = date.month, 
                                          hourType = hourType)

        ncWriter.writeNC(year = date.year, 
                         month = date.month, 
                         hourType = hourType, 
                         freqArr = freqArr)

