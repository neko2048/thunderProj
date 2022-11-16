import numpy as np
import netCDF4 as nc
import  matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from os import path

class DrawSys(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.fontsize = 15
        self.titlesize = 25

    def stratify(self, data, levels):
        startifiedData = np.zeros(data.shape)
        for i, level in enumerate(levels):
            startifiedData[data >= level] = i
        return startifiedData

    def drawFreqMap(self, ncData, threshold):
        time = np.array(ncData["time"])
        xlon = np.array(ncData["XLON"])
        xlat = np.array(ncData["XLAT"])
        var = np.array(ncData["dBZ"])
        for i in range(len(time))[::8]:
            print(np.max(var[i]))
            if np.max(var[i]) < threshold:
                continue
            t = pd.to_datetime(time[i], format="%Y%m%d%H")
            print(t)

            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
            ax.set_extent([np.min(xlon), np.max(xlon), np.min(xlat), np.max(xlat)])
            #ax.set_extent([119, 122, 20, 30])

            levels = [x for x in range(-15, 80, 5)]
            stratifiedCS = self.stratify(var[i], levels)
            colorList = ["#fefefe", "#8c56ba", "#bb98d9","#9a9a9a","#747474","#e5abac","#9c858e","#b36f70","#8efa94","#68b92c","#fefe78","#cece66","#cece66", "#df6056","#b90000","#930000","#0400ef","#fefefe","#c02ae9"]
            cmap = LinearSegmentedColormap.from_list("", colorList)
            norm = BoundaryNorm(np.arange(len(colorList)), cmap.N)
            FREQ = ax.pcolormesh(xlon, xlat, stratifiedCS, cmap=cmap, norm=norm, vmin=0, vmax=len(levels)+1)
            cbar = plt.colorbar(FREQ, extend="both")
            cbar.set_ticks(np.arange(len(levels)))
            cbar.set_ticklabels([""] + [str(x) for x in np.arange(-10, 80, 5)])
            cbar.ax.tick_params(labelsize=self.fontsize)
            plt.title("{}".format(t), fontsize=self.titlesize, y=1.05)

            plt.title("Max Reflectivity [dBZ]", \
                      fontsize=self.fontsize, \
                      zorder=3, loc="right")
            ax.set_xlabel("Longitude", fontsize=self.fontsize)
            ax.set_ylabel("Latitude", fontsize=self.fontsize)
            ax.gridlines(draw_labels=False, alpha=0.75, 
                         xlocs=np.arange(np.min(xlat), np.max(xlat), 1), 
                         ylocs=np.arange(np.min(xlon), np.max(xlon), 1), color="grey")
            ax.set_yticks([round(x, 1) for x in np.arange(np.min(xlat), np.max(xlat), 1)])
            ax.set_xticks([np.ceil(x) for x in np.arange(np.min(xlon), np.max(xlon), 1)])
            ax.coastlines(resolution="10m")
            plt.savefig(self.outputDir + "{}_{:.2f}.jpg".format(time[i], np.max(var[i])), dpi=250)
            plt.clf()
            print("Save Fig {}.jpg".format(time[i]))

if __name__ == "__main__":
    config = {
        "dir": "../dat/CFSR-WRF/dBZ_max/dBZ-Max-", 
        "outputDir": "./"#"../fig/TDFRQ_{HT}HR/".format(HT=hourType), 
        }

    #dateRange = pd.date_range("1980-03-01", end="2010-11-01", freq="1m")
    dateRange = pd.date_range("2009-07-01", end="2009-09-01", freq="1MS")
    threshold = 1
    for date in dateRange:
        print(date)
        dataDir = config["dir"] + "{YEAR}{MONTH:02d}.nc".\
                  format(YEAR=date.year, MONTH=date.month)
        print(dataDir, path.exists(dataDir))
        if path.exists(dataDir):
            data = nc.Dataset(dataDir)
        else:
            continue
        drawSys = DrawSys(config["outputDir"])
        drawSys.drawFreqMap(data, 15)

