import pickle
import numpy as np
import netCDF4 as nc
from scipy import stats
import cartopy.crs as ccrs
import  matplotlib.pyplot as plt
from fullDateThunderGrid import Config

def readDict(dir, mode):
    file = open(dir, mode)
    data = pickle.load(file)
    file.close()
    return data

def drawCorrMap(xlon, xlat, data):
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
    FREQ = ax.pcolormesh(xlon, xlat, data, vmin=-1, vmax=1, cmap="rainbow")
    cbar = plt.colorbar(FREQ)
    cbar.ax.tick_params(labelsize=15)
    plt.title("Correlation", fontsize=20, y=1.05)
    
    plt.title("1989-2008 JJA", loc="right", fontsize=15)
    plt.title(r"hourType={} | dBZmax$\geq${}".format(hourType, dBZthres), loc="left", fontsize=15)
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

def drawCountMap(xlon, xlat, data):
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
    ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
    FREQ = ax.pcolormesh(xlon, xlat, data, vmin=0, vmax=30, cmap="rainbow")
    cbar = plt.colorbar(FREQ)
    cbar.set_ticks([0, 5, 10, 15, 20, 25, 30])
    cbar.ax.tick_params(labelsize=15)
    plt.title("# of valid data", fontsize=20, y=1.05)

    plt.title("1989-2008 JJA", loc="right", fontsize=15)
    plt.title(r"hourType={} | dBZmax$\geq${}".format(hourType, dBZthres), loc="left", fontsize=15)
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
    plt.title(r"hourType={} | dBZmax$\geq${}".format(hourType, dBZthres), loc="left", fontsize=15)
    ax.set_xlabel("# of valid data / column", fontsize=20)
    ax.set_ylabel("Correlation", fontsize=20)
    #ax.set_xticks(np.arange(0, 15))
    ax.tick_params(axis="both", labelsize=15)
    plt.savefig("colCountCorr.jpg", dpi=300)
    
if __name__ == "__main__":
    hourType, dBZthres = 3, 40
    lengthScale = 3
    config = Config({
        "home": "/home/twsand/fskao/thunderProj/", 
        "dBZJsonDir": "%(home)sdat/varJson/dBZ_max.json", 
        "taiwanMaskDir": "%(home)sdat/taiwanMask.npy", 
        "columnDataDir": "%(home)sdat/columnData/", 
        "wrfExampleDir": "%(home)sdat/CFSR-WRF/CS/CS-"
        })

    validX = readDict(config["columnDataDir"] + "validX_hourType{}_dBZ{}.pkl".format(hourType, dBZthres), "rb")
    validY = readDict(config["columnDataDir"] + "validY_hourType{}_dBZ{}.pkl".format(hourType, dBZthres), "rb")
    correlation = np.load(config["columnDataDir"] + "coeffCorr{}_dBZ{}.npy".format(hourType, dBZthres))
    ncData = nc.Dataset(config["wrfExampleDir"] + "201005.nc")
    countMap = np.full((correlation.shape[0]//lengthScale, correlation.shape[1]//lengthScale), np.nan)
    scaleCorr = np.full(countMap.shape, np.nan)

    compressValidX = {}
    compressValidY = {}

    for i in range(len(correlation)):
        for j in range(len(correlation)):
            compressValidX["{:03d}{:03d}".format(i//2, j//2)] = []
            compressValidY["{:03d}{:03d}".format(i//2, j//2)] = []

    for i in range(correlation.shape[0]):
        for j in range(correlation.shape[1]):
            if len(validX["{:03d}{:03d}".format(i, j)]):
                compressValidX["{:03d}{:03d}".format(i//lengthScale, j//lengthScale)].extend(validX["{:03d}{:03d}".format(i, j)])
                compressValidY["{:03d}{:03d}".format(i//lengthScale, j//lengthScale)].extend(validY["{:03d}{:03d}".format(i, j)])


    for i in range(countMap.shape[0]):
        for j in range(countMap.shape[1]):
            if len(compressValidX["{:03d}{:03d}".format(i, j)]):
                lreg = stats.linregress(x=compressValidX["{:03d}{:03d}".format(i, j)], \
                                        y=compressValidY["{:03d}{:03d}".format(i, j)])
                scaleCorr[i, j] = lreg.rvalue
                countMap[i, j] = len(compressValidY["{:03d}{:03d}".format(i, j)])

    xlon = np.array(ncData["XLON"])
    xlat = np.array(ncData["XLAT"])
    scaleXLON = np.zeros(countMap.shape)
    scaleXLAT = np.zeros(countMap.shape)
    for i in range(countMap.shape[0]):
        for j in range(countMap.shape[1]):
            scaleXLON[i, j] = np.mean(xlon[lengthScale*i:lengthScale*i+lengthScale, lengthScale*j:lengthScale*j+lengthScale])
            scaleXLAT[i, j] = np.mean(xlat[lengthScale*i:lengthScale*i+lengthScale, lengthScale*j:lengthScale*j+lengthScale])

    drawCorrMap(scaleXLON, scaleXLAT, scaleCorr)
    drawCountMap(scaleXLON, scaleXLAT, countMap)
    drawScatter(countMap, scaleCorr)
