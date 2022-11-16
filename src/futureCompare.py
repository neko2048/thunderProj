import numpy as np
import netCDF4 as nc
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.cm as cm

if __name__ == "__main__":
    caseType = "end21" # mid21 / end21
    methodName = "ytjhu" # fskao / ytjhu
    NyearHist = 26 # 1980 - 2005
    NyearMid = 26 # 2040 - 2065
    NyearEnd = 25 # 2975 - 2099
    histMeanFreq = np.load("./accumThd-hist-{}.npy".format(methodName)) / NyearHist
    midMeanFreq = np.load("./accumThd-mid21-{}.npy".format(methodName)) / NyearMid
    endMeanFreq = np.load("./accumThd-end21-{}.npy".format(methodName)) / NyearEnd
    taiwanMask = np.load("../dat/taiwanMask.npy")
    xlon = nc.Dataset("../dat/CFSR-WRF-end21/CS/CS-208010.nc")["XLON"]
    xlat = nc.Dataset("../dat/CFSR-WRF-end21/CS/CS-208010.nc")["XLAT"]

    midChange = (midMeanFreq - histMeanFreq) / histMeanFreq * 100
    endChange = (endMeanFreq - histMeanFreq) / histMeanFreq * 100

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
    if caseType == "mid21":
        data = midChange
    elif caseType == "end21":
        data = endChange
    cmap = cm.get_cmap("seismic", lut=20)
    FREQ = ax.pcolormesh(xlon, xlat, data, vmin=-100, vmax=100, cmap=cmap)
    cbar = plt.colorbar(FREQ)
    cbar.ax.tick_params(labelsize=15)
    plt.title("Change between {} and hist [%]".format(caseType), fontsize=20, y=1.05)
    plt.title("Max/Min: {:.1f}/{:.1f} %".format(np.nanmax(data), np.nanmin(data)), fontsize=15, loc='right')
    ax.set_xlim(119, 122.9)
    ax.set_xlabel("Longitude", fontsize=20)
    ax.set_ylabel("Latitude", fontsize=20)
    ax.gridlines(draw_labels=False, alpha=0.75, 
                 xlocs=np.arange(np.min(xlat), np.max(xlat), 1), 
                 ylocs=np.arange(np.min(xlon), np.max(xlon), 1), color="grey")
    ax.set_yticks([round(x, 1) for x in np.arange(np.min(xlat), np.max(xlat), 1)])
    ax.set_xticks([np.ceil(x)+0.5 for x in np.arange(np.min(xlon), np.max(xlon), 1)][:-1])
    ax.tick_params(axis="both", labelsize=15)
    ax.coastlines(resolution="10m")
    plt.savefig("{}Change-{}.jpg".format(caseType, methodName), dpi=250)
    plt.clf()
