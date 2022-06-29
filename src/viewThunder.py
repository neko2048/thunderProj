import numpy as np
import netCDF4 as nc
import  matplotlib.pyplot as plt
import pandas as pd
import cartopy.crs as ccrs
from matplotlib.colors import LinearSegmentedColormap
from os import path

class DrawSys(object):
    def __init__(self, outputDir):
        self.outputDir = outputDir
        self.fontsize = 15
        self.titlesize = 25

    def drawFreqMap(self, ncData, threshold):
        time = np.array(ncData["time"])
        xlon = np.array(ncData["XLON"])
        xlat = np.array(ncData["XLAT"])
        freq = np.array(ncData["CGFRQ"])
        for i in range(len(time)):
            if np.max(freq[i]) < threshold:
                continue
            t = pd.to_datetime(time[i], format="%Y%m%d%H%M")
            lowTimeBound = t - pd.Timedelta(hours=round(hourType/2, 1))
            highTimeBound = t + pd.Timedelta(hours=round(hourType/2, 1)) - pd.Timedelta(seconds=1)
            
            interval = np.hstack([np.linspace(0, 0.1, 5), np.linspace(0.4, 1, 95)])
            colors = plt.cm.viridis(interval)
            cmap = LinearSegmentedColormap.from_list('name', colors)
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()}, dpi=250)
            ax.set_extent([np.min(xlat), np.max(xlat), np.min(xlon), np.max(xlon)])

            FREQ = ax.pcolormesh(xlat, xlon, freq[i], vmin=0, vmax=10, cmap=cmap)
            cbar = plt.colorbar(FREQ, extend="max")
            cbar.ax.tick_params(labelsize=self.fontsize)
            plt.title("{}".format(t), fontsize=self.titlesize, y=1.05)
            plt.title("COUNT: {}".\
                      format(np.sum(freq[i])), 
                      fontsize=self.fontsize, 
                      zorder=3, loc="left")
            plt.title(r"$\Delta$T: {} hr(s)".\
                      format(hourType), 
                      fontsize=self.fontsize, 
                      zorder=3, loc="right")
            ax.set_xlabel("Longitude", fontsize=self.fontsize)
            ax.set_ylabel("Latitude", fontsize=self.fontsize)
            ax.gridlines(draw_labels=False, alpha=0.75, 
                         xlocs=np.arange(np.min(xlat), np.max(xlat), 1), 
                         ylocs=np.arange(np.min(xlon), np.max(xlon), 1), color="grey")
            ax.set_xticks([np.ceil(x) for x in np.arange(np.min(xlat), np.max(xlat), 1)])
            ax.set_yticks([round(x, 1) for x in np.arange(np.min(xlon), np.max(xlon), 1)])
            ax.coastlines(resolution="10m")
            plt.savefig(self.outputDir + "{}_{:02d}.jpg".format(time[i], np.sum(freq[i])), dpi=250)
            plt.clf()
            print("Save Fig {}.jpg".format(time[i]))

if __name__ == "__main__":
    hourType = 3
    config = {
        "hourType": str(hourType), 
        "CGFreqDir": "../dat/TDFRQ_{HT}HR/".format(HT=hourType), 
        "outputDir": "../fig/TDFRQ_{HT}HR/".format(HT=hourType), 
        }

    dateRange = pd.date_range("1980-03-01", end="2010-11-01", freq="1m")

    for date in dateRange:
        dataDir = config["CGFreqDir"] + "{YEAR}{MONTH:02d}.nc".\
                  format(YEAR=date.year, MONTH=date.month)
        if path.exists(dataDir):
            data = nc.Dataset(dataDir)
        else:
            continue

        drawSys = DrawSys(config["outputDir"])
        drawSys.drawFreqMap(data, 10)
