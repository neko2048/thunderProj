import json
import numpy as np
from os import path
import pandas as pd
import netCDF4 as nc
from matplotlib.pyplot import *
import statsmodels.formula.api as sm
from fullDateThunderGrid import Config

if __name__ == "__main__":
    hourType, dBZthreshold = 1, 38#input().split()#3, 40
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)
    config = Config({
        "hourType": str(hourType), 
        "home": "/home/twsand/fskao/thunderProj/",
        "obsPrecipDir": "%(home)sdat/dailyPrecip/", 
        "wrfPrecipDir": "%(home)sdat/CFSR-WRF-new/RAIN-modify/threeHourRAIN/", 
        "thdDir": "%(home)sdat/TDFRQ_%(hourType)sHR_UTC0/",
        "csJsonDir": "%(home)sdat/varJson/CS.json", 
        "ccJsonDir": "%(home)sdat/varJson/CC.json", 
        "crJsonDir": "%(home)sdat/varJson/CR.json", 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max.json", 
        "wMaxJsonDir": "%(home)sdat/varJson/W_max.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        })

    year = 1990
    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1989-01-01", end="2008-12-01", freq="1MS")
    dateOptEnd = pd.date_range("1989-01-01", end="2008-12-01", freq="1M")
    obsPrecipThres = 1 # mm
    taiwanMask = np.load(config["taiwanMaskDir"])
    csConfig = json.load(open(config["csJsonDir"]))
    ccConfig = json.load(open(config["ccJsonDir"]))
    crConfig = json.load(open(config["crJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    wMaxConfig = json.load(open(config["wMaxJsonDir"]))
    
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

    validX1 = []
    validY = []
    validX2 = []
    validT = []

    figure(figsize=(10, 10), dpi=250)
    for dateIdx in range(len(existDateOpt)):
        wrfPrecipData = nc.Dataset(config["wrfPrecipDir"] + "{Y:04d}{M:02d}.nc".\
                               format(Y=existDateOpt[dateIdx].year, M=existDateOpt[dateIdx].month))
        wrfDate = pd.to_datetime(np.array(wrfPrecipData["time"]), format="%Y%m%d%H") + pd.Timedelta(8, "hr")
        # turn wrf date to UTC + 8
        wrfPrecip = wrfPrecipData["RAIN"]


        validPrecip = np.full(wrfPrecip.shape, False)
        for dayIdx in range(len(wrfDate)):
            dayObsPrecip = np.load(config["obsPrecipDir"] + "{:04d}/{:02d}{:02d}.npy".format(wrfDate[dayIdx].year, wrfDate[dayIdx].month, wrfDate[dayIdx].day))
            validPrecip[dayIdx][dayObsPrecip >= obsPrecipThres] = wrfPrecip[dayIdx][dayObsPrecip >= obsPrecipThres] > obsPrecipThres

        date = existDateOpt[dateIdx]
        if existDateOpt[dateIdx].month in monthOpt:
            print(date)
            dateData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["time"])
            thdData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["CGFRQ"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            ccData = np.array(nc.Dataset(ccConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[ccConfig["varName"]])
            crData = np.array(nc.Dataset(crConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[crConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
            wMaxData = np.array(nc.Dataset(wMaxConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[wMaxConfig["varName"]])
            taiwanMask3D = np.tile(taiwanMask[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
            dateData3D = np.tile(dateData[:, np.newaxis, np.newaxis], reps=[1, thdData.shape[1], thdData.shape[2]])

        else:
            continue

        condition = np.array((dBZData >= dBZthreshold) * (thdData != 0) * (csData >= 1e-6) * (taiwanMask3D) * validPrecip, dtype=bool)
        if np.sum(condition) == 0: continue

        x1 = csData[condition]
        y = thdData[condition]
        x2 = (ccData + crData)[condition] # LWP
        t = dateData3D[condition]

        if np.sum(condition != 0):
            validX1.extend(x1)
            validY.extend(y)
            validX2.extend(x2)
            validT.extend(t)

    df = pd.DataFrame({"Y": np.array(validY), 
                       "X1": np.array(validX1), 
                       "X2": np.array(validX2)})

    result = sm.ols(formula="Y ~ X1 + X2", data = df).fit()

    print(result.params)
    print("=="*10)
    print(result.summary())


