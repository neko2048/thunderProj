import numpy as np


class ExamineMethod(object):
    def __init__(self, obsData, predData, threshold=None):
        self.obsData = obsData
        self.predData = predData

        if threshold != None:
            self.hit = np.sum(np.logical_and(self.obsData >= threshold, self.predData >= threshold))
            self.falseAlarm = np.sum(np.logical_and(self.obsData < threshold, self.predData >= threshold))
            self.miss = np.sum(np.logical_and(self.obsData >= threshold, self.predData < threshold))
            self.correctNegatives = np.sum(np.logical_and(self.obsData < threshold, self.predData < threshold))
            
    def getMeanError(self):
        return np.mean(self.predData - self.obsData)

    def getRMSE(self):
        return np.sqrt(np.mean((self.predData - self.obsData) ** 2))

    def getCorrelation(self, x, y):
        corr = np.corrcoef(x, y)
        return corr

    def getBiasScore(self):
        BS = (self.hit + self.falseAlarm) / (self.hit + self.miss)
        return BS

    def getPOD(self):
        """POD: probability of Detection"""
        POD = (self.hit) / (self.hit + self.miss)
        return POD

    def getFAR(self):
        """FAR: false alarm ratio"""
        FAR = (self.falseAlarm) / (self.hit + self.falseAlarm)
        return FAR

    def getThreatScore(self):
        TS = (self.hit) / (self.hit + self.miss + self.falseAlarm)
        return TS

    def getETS(self):
        """ETS: Equitable Threat Score"""
        hitRandom = (self.hit + self.miss) * (self.hit + self.falseAlarm) / (self.hit + self.miss + self.falseAlarm + self.correctNegatives)
        ETS = (self.hit - hitRandom) / (self.hit + self.miss + self.falseAlarm - hitRandom)
        return ETS

    def getPOFD(self):
        """POFD: Probability of False Detection"""
        POFD = self.falseAlarm / (self.falseAlarm + self.correctNegatives)
        return POFD