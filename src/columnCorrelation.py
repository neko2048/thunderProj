import numpy as np
import netCDF4 as nc
import pandas as pd
from os import path
from scipy import stats
import json
import pickle
from fullDateThunderGrid import Config

if __name__ == "__main__":
    hourType, dBZthreshold = 1, 40#input().split()
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)

    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "hourType": str(hourType), 
        "wrfDir": "%(home)sdat/CFSR-WRF/CS/", 
        "thdDir": "%(home)sdat/TDFRQ_%(hourType)sHR_UTC0/",
        "csJsonDir": "%(home)sdat/varJson/CS.json", 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        "columnDataOutputDir": "%(home)sdat/columnData/", 
        })

    #txtOutputer = TxtOutputer(config["txtOutputDir"])
    csConfig = json.load(open(config["csJsonDir"]))
    dBZConfig = json.load(open(config["dBZJsonDir"]))
    taiwanMask = np.load(config["taiwanMaskDir"])
    monthOpt = [6, 7, 8]
    dateOpt = pd.date_range("1989-01-01", end="2008-12-01", freq="1MS")
    existDateOpt = []
    for date in dateOpt:
        if path.exists(config["thdDir"]+"{Y}{M:02d}.nc".format(Y=date.year, M=date.month)) and \
           path.exists(csConfig["dir"]+"{Y}{M:02d}.nc".format(Y=date.year, M=date.month)):
           existDateOpt.append(date)
        else:
            continue

    validXMapDict = {}
    validYMapDict = {}
    coeffSlope = np.full(fill_value = np.nan, shape=taiwanMask.shape)
    coeffIntercept = np.full(fill_value = np.nan, shape=taiwanMask.shape)
    coeffCorr = np.full(fill_value = np.nan, shape=taiwanMask.shape)
    for i in range(taiwanMask.shape[0]):
        for j in range(taiwanMask.shape[1]):
            validXMapDict["{:03d}{:03d}".format(i, j)] = []
            validYMapDict["{:03d}{:03d}".format(i, j)] = []

    for date in existDateOpt:
        if date.month in monthOpt:
            print(date)
            dateData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["time"])
            thdData = np.array(nc.Dataset(config["thdDir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))["CGFRQ"])
            csData = np.array(nc.Dataset(csConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[csConfig["varName"]])
            dBZData = np.array(nc.Dataset(dBZConfig["dir"] + "{Y}{M:02d}.nc".format(Y=date.year, M=date.month))[dBZConfig["varName"]])
            taiwanMask3D = np.tile(taiwanMask[np.newaxis, :, :], reps=[dBZData.shape[0] ,1, 1])
            dateData3D = np.tile(dateData[:, np.newaxis, np.newaxis], reps=[1, thdData.shape[1], thdData.shape[2]])

        else:
            continue

        condition = np.array((dBZData >= dBZthreshold) * (thdData != 0) * (csData >= 1e-6) * (taiwanMask3D), dtype=bool)
        

        if np.sum(condition != 0):
            conditionIdx = np.where(condition)
            for t in range(np.sum(condition)):
                validXMapDict["{:03d}{:03d}".format(conditionIdx[1][t], conditionIdx[2][t])].append(csData[conditionIdx[0][t], conditionIdx[1][t], conditionIdx[2][t]])
                validYMapDict["{:03d}{:03d}".format(conditionIdx[1][t], conditionIdx[2][t])].append(thdData[conditionIdx[0][t], conditionIdx[1][t], conditionIdx[2][t]])

    for i in range(taiwanMask.shape[0]):
        for j in range(taiwanMask.shape[1]):
            if len(validXMapDict["{:03d}{:03d}".format(i, j)]) >= 2:
                #print(validXMapDict["{:03d}{:03d}".format(i, j)])
                #print(validYMapDict["{:03d}{:03d}".format(i, j)])
                lreg = stats.linregress(x=validXMapDict["{:03d}{:03d}".format(i, j)], \
                                        y=validYMapDict["{:03d}{:03d}".format(i, j)])
                coeffSlope[i, j] = lreg.slope
                coeffIntercept[i, j] = lreg.intercept
                coeffCorr[i, j] = lreg.rvalue
    np.save(config["columnDataOutputDir"] + "coeffCorr{}.npy".format(hourType), coeffCorr)
    np.save(config["columnDataOutputDir"] + "coeffSlope{}.npy".format(hourType), coeffSlope)
    np.save(config["columnDataOutputDir"] + "coeffIntercept{}.npy".format(hourType), coeffIntercept)


    file = open(config["columnDataOutputDir"] + "validX_hourType{}.pkl".format(hourType), "wb")
    pickle.dump(validXMapDict, file)
    file.close()

    file = open(config["columnDataOutputDir"] + "validY_hourType{}.pkl".format(hourType), "wb")
    pickle.dump(validYMapDict, file)
    file.close()