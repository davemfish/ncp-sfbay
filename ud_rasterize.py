## Post-processing for userdays_rasteraoi.r 
## loads text files of userdays per grid cell,
## sums values to get total PUD per cell
## create a raster to hold the PUDs

import numpy as np
import os
import glob
import subprocess
from osgeo import gdal
gdal.UseExceptions()


## these are the outputs from userdays_rasteraoi.r
fileroot = "../data/twitter/nlcd_grid_tud/"
filelist = glob.glob(os.path.join(fileroot, '*_lrbt.csv'))
out_csv_file = os.path.join(fileroot, 'nlcd_sfbay_2012_2016_totaltud.csv')
out_raster_file = os.path.join(fileroot, 'tud_nlcdgrid.tif')

## this is the same AOI used as input to userdays_rasteraoi.r
ds = gdal.Open('/home/dmf/Recdev/data/SF_Bay/data/bcdc_othernaturalareas/NaturalAreas_ForDave/nlcd_nodevt_utm.tif')

# determine shape of array from line count of one input file
wc = subprocess.Popen('wc -l ' + filelist[0], shell=True, stdout=subprocess.PIPE)
wc_str = wc.stdout.read().decode('ascii')
nlines = int(wc_str.split()[0])
totals = np.zeros(shape=(nlines,), dtype='int')

openlist = []
for f in filelist:
    openlist.append(open(f, 'rt'))

i = 0
for row in zip(*openlist):
    x = np.array([r.rstrip('\n') for r in row])
    x = x.astype(np.int)
    totals[i] = np.sum(x)
    i += 1
    if (i % 1000000==0):
        print(i)

np.savetxt(out_csv_file, totals, fmt="%i")

for f in openlist:
    f.close()

## If for some reason need to remake the raster but not the big csv, can start from here:
# totals = np.loadtxt(out_csv_file, dtype='int')

ds.RasterXSize*ds.RasterYSize == len(totals)

# how to call reshape in order to 
# fill each row from left to right, starting with bottom row and moving up
# test = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
# np.flip(np.reshape(test, (4, 3)), 0) # default order of reshape works, then flip along 0 axis
totalmatrix = np.flip(np.reshape(totals, (ds.RasterYSize, ds.RasterXSize)), 0)

driver = gdal.GetDriverByName('GTiff')
new_ds = driver.Create(out_raster_file,
    ds.RasterXSize, # x size
    ds.RasterYSize, # y size
    1, # number of bands
    gdal.GDT_Int32)


new_band = new_ds.GetRasterBand(1)
new_band.WriteArray(totalmatrix)
# flush data to disk, set the NoData value and calculate stats
new_band.FlushCache()
# new_band.SetNoDataValue(nodata)

# georeference the image and set the projection
new_ds.SetGeoTransform(ds.GetGeoTransform())
new_ds.SetProjection(ds.GetProjection())
del new_ds

