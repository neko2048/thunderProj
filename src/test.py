import numpy as np
import netCDF4 as nc
from matplotlib.pyplot import *

data = np.load("../dat/dailyPrecip/20200101.npy")#nc.Dataset("../dat/CFSR-WRF/geo_em.d01.heymanMOD.nc")


pcolormesh(data)
savefig("landMask.jpg")
