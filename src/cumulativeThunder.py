import numpy as np
import netCDF4 as nc
import  matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from os import path

class DrawSys(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.fontsize = 15
        self.titlesize = 25

    def stratify(self, historyThunder, levels):
        startifiedThunder = np.zeros(historyThunder.shape)
        for i, level in enumerate(levels):
            startifiedThunder[historyThunder >= level] = i
        return startifiedThunder

    def drawFreqMap(self, historyThunder):
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
        ax.set_extent([np.min(xlat), np.max(xlat), np.min(xlon), np.max(xlon)])

        levels = [0, 25, 50, 75, 100, 200, 350, 500, 750, 1000, 1500, 2000, 2100]
        #levels = [0, 5, 10, 20, 30, 50, 75, 100, 150, 200, 250, 300, 400]
        startifiedThunder = self.stratify(historyThunder, levels)
        cmap = ListedColormap(["#FFFFFF", "#ECF4A8", "#B0D46E", "#FCEF00", "#FDEE89", "#F8AC51", "#F29141", "#F40041", "#F652AB", "#697CFA", "#86A1FF", "#B9D0FF"])
        #FREQ = ax.pcolormesh(xlat, xlon, historyThunder, vmin=0, cmap=cmap)
        FREQ = ax.pcolormesh(xlat, xlon, startifiedThunder, cmap=cmap)
        cbar = plt.colorbar(FREQ, extend="max")
        cbar.set_ticks(np.arange(len(levels)))
        cbar.set_ticklabels([str(x) for x in levels[:-1]] + [""])
        cbar.ax.tick_params(labelsize=self.fontsize)
        plt.title("Cumulative Distribution", fontsize=self.titlesize, y=1.05)
        plt.title("COUNT: {}".\
                  format(int(np.sum(historyThunder))), 
                  fontsize=self.fontsize, 
                  zorder=3, loc="left")
        plt.title("JJA from {} to {}".\
                  format(validDateOpt[0].year, validDateOpt[-1].year), 
                  fontsize=self.fontsize, 
                  zorder=3, loc="right")
        ax.set_xlabel("Longitude", fontsize=self.fontsize)
        ax.set_ylabel("Latitude", fontsize=self.fontsize)
        ax.gridlines(draw_labels=False, alpha=0.75, 
                     xlocs=np.arange(np.min(xlat), np.max(xlat), 1), 
                     ylocs=np.arange(np.min(xlon), np.max(xlon), 1), color="grey")
        ax.set_xticks([np.ceil(x) for x in np.arange(np.min(xlat), np.max(xlat), 1)])
        ax.set_yticks([round(x, 1) for x in np.arange(np.min(xlon), np.max(xlon), 1)])
        ax.xaxis.set_tick_params(labelsize=self.fontsize)
        ax.yaxis.set_tick_params(labelsize=self.fontsize)

        ax.coastlines(resolution="10m")
        plt.savefig(self.outputDir + "historyThunder.jpg", dpi=250)
        plt.clf()
        print("Save Fig historyThunder.jpg")

if __name__ == "__main__":
    hourType = 3
    config = {
        "hourType": str(hourType), 
        "CGFreqDir": "../dat/TDFRQ_{HT}HR/".format(HT=hourType), 
        "outputDir": "./"#"../fig/TDFRQ_{HT}HR/".format(HT=hourType), 
        }

    dateRange = pd.date_range("1980-03-01", end="2012-11-01", freq="1m")
    #dateRange = pd.date_range("2004-03-01", end="2012-11-01", freq="1m")
    exampeNCdata = nc.Dataset(config["CGFreqDir"] + "199005.nc")
    xlon, xlat = exampeNCdata["XLON"], exampeNCdata["XLAT"]
    historyThunder = np.zeros(shape=np.array(xlon).shape)
    monthOpt = [6, 7, 8]

    validDateOpt = []
    for date in dateRange:
        dataDir = config["CGFreqDir"] + "{YEAR}{MONTH:02d}.nc".\
                  format(YEAR=date.year, MONTH=date.month)
        if path.exists(dataDir) and date.month in monthOpt:
            data = nc.Dataset(dataDir)
            validDateOpt.append(date)
            historyThunder += np.sum(data["CGFRQ"], axis=0)
        else:
            continue

    validDateOpt = pd.to_datetime(validDateOpt)
    drawSys = DrawSys(config["outputDir"])
    drawSys.drawFreqMap(historyThunder)