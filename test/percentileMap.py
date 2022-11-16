import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.pyplot import *
import netCDF4 as nc
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import cartopy.crs as ccrs

class DrawSys(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.fontsize = 15
        self.titlesize = 25

    def stratify(self, historyThunder, levels):
        startifiedThunder = np.zeros(historyThunder.shape)
        temp = historyThunder[taiwanMask != 0]
        for i, level in enumerate(levels):
            startifiedThunder[historyThunder >= np.percentile(temp, level)] = i
        return startifiedThunder

    def drawPercentileMap(self, historyThunder, percentile):
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
        ax.set_extent([np.min(xlat), np.max(xlat), np.min(xlon), np.max(xlon)])

        startifiedThunder = self.stratify(historyThunder, percentile)
        startifiedThunder = np.ma.masked_array(startifiedThunder, taiwanMask == 0)
        cmap = ListedColormap(["#000182", "#0100bd", "#0000ee", "#014bfb", "#08bbf8", "#27fdcd", "#b8fb3d", "#d4f322", "#fbc303", "#f10900", "#b91307"])
        FREQ = ax.pcolormesh(xlat, xlon, startifiedThunder, cmap=cmap, vmin=0, vmax=len(percentile))
        cbar = plt.colorbar(FREQ)
        cbar.set_ticks(np.arange(len(percentile))+0.5)
        cbar.set_ticklabels([str(x) + "-" + str(x+9) for x in percentile[:-1]] + ["100"])
        cbar.ax.tick_params(labelsize=self.fontsize)
        plt.title("Percentile Distribution", fontsize=self.titlesize, y=1)
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

    def drawHist(self, historyThunder):
        temp = historyThunder[taiwanMask != 0]
        plt.hist(temp, bins=np.arange(0.5, np.max(temp)+0.5, 20))
        plt.xlim(0, np.max(temp)+0.5)
        plt.xlabel("# of CG", fontsize=self.fontsize)
        plt.ylabel("Frequency", fontsize=self.fontsize)
        plt.savefig(self.outputDir + "thunderHist.jpg", dpi=250)

if __name__ == "__main__":
    exampeNCdata = nc.Dataset("../dat/TDFRQ_3HRfull/" + "199005.nc")
    taiwanMask = np.load("/home/twsand/fskao/thunderProj/dat/taiwanMask.npy")
    data = np.load("/home/twsand/fskao/thunderProj/dat/freqMap.npy")

    xlon, xlat = exampeNCdata["XLON"], exampeNCdata["XLAT"]
    percentile = [x for x in range(0, 101, 10)]
    startifiedThunder = np.zeros(data.shape)
    for i, p in enumerate(percentile):
        startifiedThunder[data >= np.percentile(data, p)] = i

    startifiedThunder = np.ma.masked_array(startifiedThunder, taiwanMask == 0)
    drawSys = DrawSys(outputDir="./")
    drawSys.drawPercentileMap(data, percentile)
    drawSys.drawHist(data)





