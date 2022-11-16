import numpy as np
import pandas as pd
import netCDF4 as nc
from matplotlib.pyplot import *

#data = np.load("../dat/dailyPrecip/20200101.npy")
#data = nc.Dataset("../dat/CFSR-WRF-new/W_max/W-198903.nc")
#print(data)
fig, axs = subplots(1, 2)
data = np.load("../dat/dailyPrecip/2007/0710.npy")
axs[0].pcolormesh(data, vmin=0, vmax=50)
for direct in ["west", "south", "east", "north"]:
	data2 = pd.read_csv("../dat/precip/{}/2007.csv".format(direct), index_col=False)
#xlon, xlat = np.array(data["XLON"]), np.array(data["XLAT"])
#arr = np.array(data["W"])
	print(data2.iloc[:, 0])
	axs[1].scatter(data2[" LON"], data2[" LAT"], c=data2["20070711"], vmin=0, vmax=50, s=1)
#pcolormesh(data)
savefig("test2.jpg", dpi=250)
