import numpy as np
import netCDF4 as nc
from matplotlib.pyplot import *

data = nc.Dataset("../dat/CFSR-WRF/geo_em.d01.heymanMOD.nc")
LM = data["LANDMASK"][0]
XLON = data["XLONG_M"][0]
XLAT = data["XLAT_M"][0]

pcolormesh(XLON, XLAT, LM)
savefig("landMask.jpg")
