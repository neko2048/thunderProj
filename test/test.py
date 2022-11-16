import numpy as np
import netCDF4 as nc
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm

if __name__ == "__main__":
    caseType = "end21" # mid21 / end21
    methodName = "fskao" # fskao / ytjhu
    NyearHist = 26 # 1980 - 2005
    NyearMid = 26 # 2040 - 2065
    NyearEnd = 25 # 2975 - 2099
    histMeanFreq = np.load("./accumThd-hist-{}.npy".format(methodName)) / NyearHist
    midMeanFreq = np.load("./accumThd-mid21-{}.npy".format(methodName)) / NyearMid
    endMeanFreq = np.load("./accumThd-end21-{}.npy".format(methodName)) / NyearEnd
    taiwanMask = np.load("../dat/taiwanMask.npy")
    xlon = nc.Dataset("../dat/CFSR-WRF-end21/CS/CS-208010.nc")["XLON"]
    xlat = nc.Dataset("../dat/CFSR-WRF-end21/CS/CS-208010.nc")["XLAT"]

    midChange = np.ma.masked_array(midMeanFreq - histMeanFreq, 1 - taiwanMask)
    endChange = np.ma.masked_array(endMeanFreq - histMeanFreq, 1 - taiwanMask)
    
    fig, ax = plt.subplots(1, 3, figsize=(30, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax[0].pcolormesh(xlon, xlat, histMeanFreq, vmin=0, vmax=40, cmap='turbo')
    ax[1].pcolormesh(xlon, xlat, midMeanFreq, vmin=0, vmax=40, cmap='turbo')
    ax[2].pcolormesh(xlon, xlat, endMeanFreq, vmin=0, vmax=40, cmap='turbo')
    plt.savefig("{}Three-{}.jpg".format(caseType, methodName), dpi=250)
    plt.clf()
