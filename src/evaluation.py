import numpy as np
import pandas as pd
from scipy import stats
from matplotlib.pyplot import *
from examineMethod import ExamineMethod
from fullDateThunderGrid import Config

if __name__ == "__main__":
    hourType, dBZthreshold = 3, 40#input().split()
    hourType = int(hourType)
    dBZthreshold = int(dBZthreshold)

    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "hourType": str(hourType), 
        "dBZthreshold": str(dBZthreshold),
        "txtDataDir": "%(home)sdat/txtDat/", 
        })


    trainData = pd.read_csv(config["txtDataDir"] + "trainDataset_Hr{}Thres{}.txt".format(config["hourType"], config["dBZthreshold"]), \
                            sep=",", header=None)
    testData = pd.read_csv(config["txtDataDir"] + "testDataset_Hr{}Thres{}.txt".format(config["hourType"], config["dBZthreshold"]), \
                           sep=",", header=None)

    print("# of train data: {}".format(len(trainData)))
    print("# of test data: {}".format(len(testData)))
    trainX = trainData.iloc[:, 1]
    trainY = trainData.iloc[:, 2]
    lreg = stats.linregress(x=trainX, y=trainY)
    print("y = {:.5f} x + {:.5f}".format(lreg.slope, lreg.intercept))
    print("Corr: {:.5f}".format(lreg.rvalue))


    print("-"*20)
    testX = testData.iloc[:, 1]
    testY = testData.iloc[:, 2]
    #predY = lreg.intercept + lreg.slope*np.array(testX)
    predY = 1 + 1 * np.array(testX)

    figure(figsize=(10, 10))
    scatter(testY, predY)
    title("Freq. of Thunder", fontsize=20)
    xlabel("Observation", fontsize=15)
    ylabel("Prediction", fontsize=15)
    #xlim(0, np.max(np.concatenate((testY, predY))))
    #ylim(0, np.max(np.concatenate((testY, predY))))
    savefig('test.jpg', dpi=250)

    evaluator = ExamineMethod(obsData=testY, predData=predY, threshold=0)
    print("ME: {:.5f}".format(evaluator.getMeanError()))
    print("RMSE: {:.5f}".format(evaluator.getRMSE()))
    print("Corr: {:0.5f}".format(evaluator.getCorrelation(x=testY, y=predY)[1, 0]))
    


