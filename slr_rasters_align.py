
## Pre-processing for  a batch of sea-level-rise rasters, 
## Convert each to presence(1) absence(0) grids - presence being 'inundated areas'
## align to the NLCD grid, the base grid for regional recreation analysis

import numpy as np
from osgeo import gdal
gdal.UseExceptions()
import pygeoprocessing.geoprocessing as pgp
import os
import glob


nlcd_uri = '../data/bcdc_othernaturalareas/NaturalAreas_ForDave/nlcd_nodevt_utm.tif'

def raster_to01(in_raster, out_raster):
    '''
    converts a raster of any datatype to Byte type with 0s replace nodata, 1s replacing all other data.
    '''
    print('reading 1')
    src = gdal.Open(in_raster)
    band1 = src.GetRasterBand(1)
    nodata = band1.GetNoDataValue()
    rows = src.RasterYSize
    cols = src.RasterXSize
    vals = band1.ReadAsArray(0, 0, cols, rows)
    driver = src.GetDriver()
    
    print('assigning 0s and 1s')
    vals01 = np.ones_like(vals)
#     vals01[vals == nodata] = 0 # nodata was massive flt, this equality not happenin'
    vals01[vals <= 0] = 0
    
    out_data = driver.Create(out_raster, cols, rows, 1, gdal.GDT_Byte)
    out_band = out_data.GetRasterBand(1)

    print('writing 1')
    out_band.WriteArray(vals01)
    # flush data to disk, set the NoData value and calculate stats
    out_band.FlushCache()
    # out_band.SetNoDataValue(nodata)

    # georeference the image and set the projection
    out_data.SetGeoTransform(src.GetGeoTransform())
    out_data.SetProjection(src.GetProjection())
    del out_data


## convert to presence/absence rasters
slr_root = '../data/pca/bcdc_slr/raster/'
slr_names = [os.path.basename(x) for x in glob.glob(os.path.join(slr_root,'*.tif'))]
slr_in_files = [os.path.join(slr_root, x) for x in slr_names]
slr_out_files = [os.path.join(slr_root, 'zeros_and_ones', x) for x in slr_names]

[raster_to01(f1, f2) for f1, f2 in zip(slr_in_files, slr_out_files)]


## align presence/absence rasters to the nlcd grid
align_rasters = [nlcd_uri] + [os.path.join(slr_root, 'zeros_and_ones', x) for x in slr_names]
target_rasters = [os.path.join(slr_root, 'aligned', 'nlcd_utm.tif')] + [os.path.join(slr_root, 'aligned', x) for x in slr_names]

pixel_size = pgp.get_raster_info(nlcd_uri)['pixel_size']
bbox = pgp.get_raster_info(nlcd_uri)['bounding_box']

pgp.align_and_resize_raster_stack(align_rasters, target_rasters, \
    ["nearest"]*len(align_rasters), pixel_size, bbox, raster_align_index=0)

