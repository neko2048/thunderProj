import numpy as np
import netCDF4 as nc
from matplotlib.pyplot import *

#data = np.load("../dat/dailyPrecip/20200101.npy")
data = nc.Dataset("../dat/CFSR-WRF-new/W_max/W-198903.nc")
#print(data)

xlon, xlat = np.array(data["XLON"]), np.array(data["XLAT"])
arr = np.array(data["W"])
