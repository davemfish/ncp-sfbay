## Post-processing for userdays_rasteraoi.r 
## loads text files of userdays per grid cell,
## sums values to get total PUD per cell
## create a raster to hold the PUDs

import numpy as np
import os
from osgeo import gdal
gdal.UseExceptions()


fileroot = "../data/flickr/nlcd_grid_pud/"
filelist = ['nlcd_nodevt_utm_SF_bay_AOI_2005-2014_lrbt.csv', 'nlcd_nodevt_utm_SF_bay_AOI_2015_lrbt.csv', 'nlcd_nodevt_utm_SF_bay_AOI_2016_lrbt.csv', 'nlcd_nodevt_utm_SF_bay_AOI_2017_lrbt.csv']

get_ipython().system(' wc -l ../data/flickr/nlcd_grid_pud/nlcd_nodevt_utm_SF_bay_AOI_2005-2014_lrbt.csv')

totals = np.zeros(shape=(116888070,), dtype='int')  # from line count of one input file

f1 = open(os.path.join(fileroot, filelist[0]),'rt')
f2 = open(os.path.join(fileroot, filelist[1]),'rt')
f3 = open(os.path.join(fileroot, filelist[2]),'rt')
f4 = open(os.path.join(fileroot, filelist[3]),'rt')

i = 0
for a, b, c, d in zip(f1, f2, f3, f4):
    x = np.array([a.rstrip('\n'), b.rstrip('\n'), c.rstrip('\n'), d.rstrip('\n')])
    x = x.astype(np.int)
    totals[i] = np.sum(x)
    i += 1
    if (i % 1000000==0):
        print(i)

np.savetxt(os.path.join(fileroot, 'nlcd_sfbay_2005_2017_totalpud.txt'), totals, fmt="%i")

# totals = np.loadtxt(os.path.join(fileroot, 'nlcd_sfbay_2005_2017_totalpud.txt'), dtype='int')

ds = gdal.Open('/home/dmf/Recdev/data/SF_Bay/data/bcdc_othernaturalareas/NaturalAreas_ForDave/nlcd_nodevt_utm.tif')

ds.RasterXSize*ds.RasterYSize == len(totals)

# how to call reshape in order to 
# fill each row from left to right, starting with bottom row and moving up
# test = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
# np.flip(np.reshape(test, (4, 3)), 0) # default order of reshape works, then flip along 0 axis
totalmatrix = np.flip(np.reshape(totals, (ds.RasterYSize, ds.RasterXSize)), 0)

driver = gdal.GetDriverByName('GTiff')
new_ds = driver.Create(os.path.join(fileroot, 'pud_nlcdgrid.tif'),
    ds.RasterXSize, # x size
    ds.RasterYSize, # y size
    1, # number of bands
    gdal.GDT_Int16)


new_band = new_ds.GetRasterBand(1)
new_band.WriteArray(totalmatrix)
# flush data to disk, set the NoData value and calculate stats
new_band.FlushCache()
# new_band.SetNoDataValue(nodata)

# georeference the image and set the projection
new_ds.SetGeoTransform(ds.GetGeoTransform())
new_ds.SetProjection(ds.GetProjection())
del new_ds

