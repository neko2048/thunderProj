import pickle
import numpy as np
import netCDF4 as nc
import cartopy.crs as ccrs
import  matplotlib.pyplot as plt
from fullDateThunderGrid import Config

def readDict(dir, mode):
    file = open(dir, mode)
    data = pickle.load(file)
    file.close()
    return data

def drawCorrMap(wrfData, data):
    time = np.array(ncData["time"])
    xlon = np.array(ncData["XLON"])
    xlat = np.array(ncData["XLAT"])
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
    FREQ = ax.pcolormesh(xlon, xlat, data, vmin=-1, vmax=1, cmap="rainbow")
    cbar = plt.colorbar(FREQ)
    cbar.ax.tick_params(labelsize=15)
    plt.title("Correlation", fontsize=20, y=1.05)
    
    plt.title("1989-2008 JJA", loc="right", fontsize=15)
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
    plt.savefig("colCorrelation.jpg", dpi=250)
    plt.clf()

def drawCountMap(wrfData, data):
    time = np.array(ncData["time"])
    xlon = np.array(ncData["XLON"])
    xlat = np.array(ncData["XLAT"])
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
    FREQ = ax.pcolormesh(xlon, xlat, data, vmin=0, vmax=20, cmap="rainbow")
    cbar = plt.colorbar(FREQ)
    cbar.set_ticks([0, 5, 10, 15])
    cbar.ax.tick_params(labelsize=15)
    plt.title("# of valid data", fontsize=20, y=1.05)

    plt.title("1989-2008 JJA", loc="right", fontsize=15)
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
    plt.savefig("colCount.jpg", dpi=250)
    plt.clf()

def drawScatter(x, y):
    fig, ax = plt.subplots(figsize=(10, 10))
    for i in range(x.shape[0]):
        plt.scatter(x[i, :], y[i, :], color="black")

    plt.title("1989-2008 JJA", loc="right", fontsize=15)
    ax.set_xlabel("# of valid data / column", fontsize=20)
    ax.set_ylabel("Correlation", fontsize=20)
    ax.set_xticks(np.arange(0, 15))
    ax.tick_params(axis="both", labelsize=15)
    plt.savefig("colCountCorr.jpg", dpi=300)
    
if __name__ == "__main__":
    hourType = 1
    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        "columnDataDir": "%(home)sdat/columnData/", 
        "wrfExampleDir": "%(home)sdat/CFSR-WRF/CS/CS-"
        })

    validX = readDict(config["columnDataDir"] + "validX_hourType{}.pkl".format(hourType), "rb")
    validY = readDict(config["columnDataDir"] + "validY_hourType{}.pkl".format(hourType), "rb")
    correlation = np.load(config["columnDataDir"] + "coeffCorr{}.npy".format(hourType))
    ncData = nc.Dataset(config["wrfExampleDir"] + "201005.nc")
    countMap = np.zeros(correlation.shape)

    for i in range(countMap.shape[0]):
        for j in range(countMap.shape[1]):
            countMap[i, j] = len(validX["{:03d}{:03d}".format(i, j)])


    drawCorrMap(ncData, correlation)
    drawCountMap(ncData, countMap)
    drawScatter(countMap, correlation)
