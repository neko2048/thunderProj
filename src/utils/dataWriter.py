import numpy as np
import netCDF4 as nc

class TxtOutputer(object):
    """save numpy array to txt data"""
    def __init__(self, outputDir):
        self.outputDir = outputDir

    def saveData(self, var, fileName):
        fileDir = self.outputDir + fileName + ".txt"
        np.savetxt(fileDir, var)
        print("Save to: {}".format(fileDir))
        return None

class NCwriter(object):
    def __init__(self):
        pass

    def writeNC(self, ncOutputName, lonOpt, latOpt, hourOpt, hourType, freqArr):
        ds = nc.Dataset(ncOutputName, 'w', format='NETCDF4')
        ds.description = 'Frequency of CG Thunder'
        time = ds.createDimension('time', len(hourOpt))
        LON = ds.createDimension('LON', lonOpt.shape[1])
        LAT = ds.createDimension('LAT', lonOpt.shape[0])

        times = ds.createVariable('time', 'i8', ('time',))
        XLAT = ds.createVariable('XLAT', 'f4', ('LAT', 'LON'))
        XLON = ds.createVariable('XLON', 'f4', ('LAT', 'LON'))
        CGFREQ = ds.createVariable('CGFRQ', 'i8', ('time', 'LAT', 'LON',))

        intHourOpt = np.array([("{:04d}{:02d}{:02d}{:02d}").\
                      format(t.year, t.month, t.day, t.hour) for t in hourOpt], dtype=int)
        times[:] = np.array(intHourOpt)#np.array(wrfData["time"])
        XLAT[:, :] = np.array(lonOpt)#np.array(wrfData["XLON"])
        XLON[:, :] = np.array(latOpt)#np.array(wrfData["XLAT"])
        CGFREQ[:, :, :] = freqArr
        ds.close()
        print("    -> {FN} WRITEN".format(FN=ncOutputName))
        return False

    def writeToNC(self, ncOutputName, lonOpt, latOpt, hourOpt, arr, varName, varDescrip):
        ds = nc.Dataset(ncOutputName, 'w', format='NETCDF4')
        ds.description = varDescrip
        time = ds.createDimension('time', len(hourOpt))
        LON = ds.createDimension('LON', lonOpt.shape[1])
        LAT = ds.createDimension('LAT', lonOpt.shape[0])

        times = ds.createVariable('time', 'i8', ('time',))
        XLAT = ds.createVariable('XLAT', 'f4', ('LAT', 'LON'))
        XLON = ds.createVariable('XLON', 'f4', ('LAT', 'LON'))
        CGFREQ = ds.createVariable(varName, 'i8', ('time', 'LAT', 'LON',))

        intHourOpt = np.array([("{:04d}{:02d}{:02d}{:02d}").\
                      format(t.year, t.month, t.day, t.hour) for t in hourOpt], dtype=int)
        times[:] = np.array(intHourOpt)
        XLAT[:, :] = np.array(lonOpt)
        XLON[:, :] = np.array(latOpt)
        CGFREQ[:, :, :] = arr
        ds.close()
        print("    -> {FN} WRITEN".format(FN=ncOutputName))
        return False
