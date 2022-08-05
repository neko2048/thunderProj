import numpy as np
import pandas as pd

class PrecipLoader(object):
    """Read observational precipitation data"""
    def __init__(self, dataDir):
        super(PrecipLoader, self).__init__()
        self.dataDir = dataDir

    def loadData(self):
        data =  pd.read_csv(self.dataDir)
        data[data == -99.9] = np.nan
        return data