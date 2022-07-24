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
    def __init__(self, thdFileDir):
        self.thdFileDir = thdFileDir

    def getDataset(self, year, month):
        data = pd.read_csv(self.thdFileDir)
        data.columns = ["time", "nanosec", "lat", "lon", "strength", "type"]
        if "　" in data.time[0]: # space in the 'time' columne in the data after 2017/01/01
            data.time = [x[2:] for x in data.time]

        data.time = pd.to_datetime(data.time, format="%Y/%m/%d %H:%M")
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

    def getFreq(self, year, month, hourType, thunderType):
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

class NCwriter(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        pass

    def writeNC(self, ncOutputName, hourOpt, hourType, freqArr):
        ds = nc.Dataset(ncOutputName, 'w', format='NETCDF4')
        ds.description = 'Frequency of CG Thunder'
        time = ds.createDimension('time', len(hourOpt))
        LON = ds.createDimension('LON', lonOpt.shape[1])
        LAT = ds.createDimension('LAT', lonOpt.shape[0])

        times = ds.createVariable('time', 'i8', ('time',))
        XLAT = ds.createVariable('XLAT', 'f4', ('LAT', 'LON'))
        XLON = ds.createVariable('XLON', 'f4', ('LAT', 'LON'))
        CGFREQ = ds.createVariable('CGFRQ', 'i8', ('time', 'LAT', 'LON',))

        intHourOpt = np.array([("{:04d}{:02d}{:02d}{:02d}").\
                      format(t.year, t.month, t.day, t.hour) for t in hourOpt], dtype=int)
        times[:] = np.array(intHourOpt)#np.array(wrfData["time"])
        XLAT[:, :] = np.array(lonOpt)#np.array(wrfData["XLON"])
        XLON[:, :] = np.array(latOpt)#np.array(wrfData["XLAT"])
        CGFREQ[:, :, :] = freqArr
        ds.close()
        print("    -> {FN} WRITEN".format(FN=ncOutputName))
        return False


if __name__ ==  "__main__":
    hourType = 1
    config = Config({
        "hourType": str(hourType), 
        "wrfDir": "../dat/CFSR-WRF/CS/", 
        "thdDir": "../dat/TLDS/",
        "outputDir": "../dat/TDFRQ_%(hourType)sHRfull/", 
        })

    ncWriter = NCwriter(outputDir=config["outputDir"])
    #dateRange = pd.date_range("1989-01-01", end="2022-01-01", freq="1MS")
    dateRange = pd.date_range("2017-01-01", end="2022-01-01", freq="1MS")
    #dateRange = pd.date_range("1989-01-01", end="1989-05-01", freq="1MS")

    initWRFfileDir = config["wrfDir"] + "CS-198003.nc"
    initWRFdata = nc.Dataset(initWRFfileDir)
    lonOpt = np.array(initWRFdata["XLON"]) # shape = (lat, lon)
    latOpt = np.array(initWRFdata["XLAT"]) # shape = (lat, lon)

    for date in dateRange:
        # ========== file existence check ==========
        wrfFileDir = config["wrfDir"] + "CS-{YEAR}{MON:02d}.nc".format(YEAR=date.year, MON=date.month)
        thdFileDirOpt1 = config["thdDir"] + "{YEAR}{MON:02d}.txt".format(YEAR=date.year, MON=date.month)
        thdFileDirOpt2 = config["thdDir"] + "{YEAR}{MON:02d}.TXT".format(YEAR=date.year, MON=date.month)

        if (path.exists(thdFileDirOpt1) or path.exists(thdFileDirOpt2)):
            print("========== {YEAR}{MON:02d} EXISTS ==========".format(YEAR=date.year, MON=date.month))
            thdFileDir = thdFileDirOpt1 if path.exists(thdFileDirOpt1) else thdFileDirOpt2
            thunderRegrider = ThunderRegrider(thdFileDir=thdFileDir)
        else:
            print("========== {YEAR}{MON:02d} 404 NF ==========".format(YEAR=date.year, MON=date.month))
            continue

        if date.month == 12:
            hourOpt = pd.date_range("{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=date.year, M=date.month, D=date.day), \
                                    "{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=int(date.year)+1, M=1, D=date.day), \
                                    freq="3H")
        else:
            hourOpt = pd.date_range("{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=date.year, M=date.month, D=date.day), \
                                    "{Y:04d}-{M:02d}-{D:02d} 0:00".format(Y=date.year, M=int(date.month)+1, D=date.day), \
                                    freq="3H")

        ncOutputName = config["outputDir"] + "{YEAR}{MONTH:02d}.nc".\
                       format(YEAR=date.year, MONTH=date.month)

        if not path.exists(ncOutputName):
            freqArr = thunderRegrider.getFreq(year = date.year, 
                                              month = date.month, 
                                              hourType = hourType, 
                                              thunderType = "CG")

            ncWriter.writeNC(ncOutputName = ncOutputName, 
                             hourOpt = hourOpt, 
                             hourType = hourType, 
                             freqArr = freqArr)
        else:
            print("    -> File Exists")

