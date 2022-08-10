import numpy as np
import netCDF4 as nc
from matplotlib.pyplot import *

#data = np.load("../dat/dailyPrecip/20200101.npy")
data = nc.Dataset("./198903.nc")
print(data)

xlon, xlat = np.array(data["XLON"]), np.array(data["XLAT"])
arr = np.array(data["RAIN"])


for i in range(arr.shape[0])[:1]:
    figure(figsize=(10, 10))
    pcolormesh(xlon, xlat, arr[i])
    colorbar()
    savefig("test{}.jpg".format(i))
    clf()