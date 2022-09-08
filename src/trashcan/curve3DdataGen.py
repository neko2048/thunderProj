import numpy as np
import pandas as pd
from fullDateThunderGrid import Config
from scipy import stats
from matplotlib.pyplot import *

if __name__ == "__main__":
    hourType = 3
    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "dBZthreshold": "40", 
        "hourType": str(hourType), 
        "txtDataDir": "%(home)sdat/txtDat/", 
        "sepDateTime": "2009-01-01", 
        "txtOutputDir": "%(home)sdat/txtDat/", 
        })

    thData = np.loadtxt(config["txtDataDir"] + "thData_Hr{}Thres{}.txt".format(config["hourType"], config["dBZthreshold"]))
    csData = np.loadtxt(config["txtDataDir"] + "csData_Hr{}Thres{}.txt".format(config["hourType"], config["dBZthreshold"]))
    dateData = np.loadtxt(config["txtDataDir"] + "dateData_Hr{}Thres{}.txt".format(config["hourType"], config["dBZthreshold"]))
    dateData = pd.to_datetime(dateData, format="%Y%m%d%H")
    #print(len(dateData[]))
    trainCondition = dateData < config["sepDateTime"]
    testCondition = dateData >= config["sepDateTime"]
    print("Train/Test/Total: {}/{}/{}".format(np.sum(trainCondition), np.sum(testCondition), len(dateData)))

    trainDate = dateData[trainCondition]
    trainCS = csData[trainCondition]
    trainTH = thData[trainCondition]
    testDate = dateData[testCondition]
    testCS = csData[testCondition]
    testTH = thData[testCondition]

    trainDataset = pd.DataFrame(data={
        "Fake": np.zeros(trainCS.shape), 
        "CS": trainCS, 
        "TH": trainTH, 
        })

    trainDataset.to_csv(config["txtOutputDir"] + "trainDataset_Hr{}Thres{}.txt".\
                        format(config["hourType"], config["dBZthreshold"]), 
                        index=None, header=None)

    testDataset = pd.DataFrame(data={
        "Fake": np.zeros(testCS.shape), 
        "CS": testCS, 
        "TH": testTH, 
        })

    testDataset.to_csv(config["txtOutputDir"] + "testDataset_Hr{}Thres{}.txt".\
                        format(config["hourType"], config["dBZthreshold"]), 
                        index=None, header=None)
