import numpy as np
import pandas as pd
import netCDF4 as nc
from matplotlib.pyplot import *
from os import path
import string
from utils import Config, ThunderRegrider, NCwriter


if __name__ ==  "__main__":
    hourType = 3
    config = Config({
        "hourType": str(hourType), 
        "wrfDir": "../dat/CFSR-WRF/CS/", 
        "thdDir": "../dat/TLDS/",
        "outputDir": "../dat/TDFRQ_%(hourType)sHR_UTC0/", 
        })

    ncWriter = NCwriter(outputDir=config["outputDir"])
    dateRange = pd.date_range("1989-06-01", end="2022-01-01", freq="1MS")
    #dateRange = pd.date_range("2019-07-01", end="2022-01-01", freq="1MS")
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
                                              thunderType = "CG", 
                                              latOpt = latOpt, 
                                              lonOpt = lonOpt, 
                                              hourOpt = hourOpt)

            ncWriter.writeNC(ncOutputName = ncOutputName, 
                             lonOpt = lonOpt, 
                             latOpt = latOpt, 
                             hourOpt = hourOpt, 
                             hourType = hourType, 
                             freqArr = freqArr)
        else:
            print("    -> File Exists")

