import os
# import logging
# logging.basicConfig(level=logging.INFO)
# import pygeoprocessing as pg
import numpy as np
from osgeo import gdal, gdalconst
import datetime

def raster_to01(in_raster, out_raster):
    '''
    converts a raster of any datatype to Byte type with 0s replace nodata, 1s replacing all other data.
    '''
    print('reading 1')
    print(datetime.datetime.now())
    src = gdal.Open(in_raster)
    band1 = src.GetRasterBand(1)
    nodata = band1.GetNoDataValue()
    rows = src.RasterYSize
    cols = src.RasterXSize
    vals = band1.ReadAsArray(0, 0, cols, rows)
    driver = src.GetDriver()
    
    print('assigning 0s and 1s')
    print(datetime.datetime.now())
    vals01 = np.ones_like(vals)
    vals01[vals == nodata] = 0
    
    out_data = driver.Create(out_raster, cols, rows, 1, gdalconst.GDT_Byte)
    out_band = out_data.GetRasterBand(1)

    print('writing 1')
    print(datetime.datetime.now())
    out_band.WriteArray(vals01)
    # flush data to disk, set the NoData value and calculate stats
    out_band.FlushCache()
    # out_band.SetNoDataValue(nodata)

    # georeference the image and set the projection
    out_data.SetGeoTransform(src.GetGeoTransform())
    out_data.SetProjection(src.GetProjection())
    del out_data


def aggregate_rast01_bymode(in_raster, match_raster, out_raster):
    '''
    resamples a high-resolution binary raster to lower-resolution match_raster,
    taking the mode of 0s and 1s from the src
    '''
    # Source
    print('reading 2')
    print(datetime.datetime.now())
    src = gdal.Open(in_raster, gdalconst.GA_ReadOnly)
    src_proj = src.GetProjection()
    src_geotrans = src.GetGeoTransform()
    
    # We want source to match this:
    print('reading match raster')
    print(datetime.datetime.now())
    match_ds = gdal.Open(match_raster, gdalconst.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize
    
    # Output 
    dst = gdal.GetDriverByName('GTiff').Create(out_raster, wide, high, 1, gdalconst.GDT_Byte)
    dst.SetGeoTransform(match_geotrans)
    dst.SetProjection(match_proj)

    print('resampling 2')
    print(datetime.datetime.now())
    # Resample to 30x30 nlcd raster, taking mode of the binary (0 or 1) slr raster
    gdal.ReprojectImage(src, dst, src_proj, match_proj, gdalconst.GRA_Mode)

    del dst # Flush


slrfile = '../bcdc_slr/Inundation_BayWide_rast_108/BayArea_inundation_rast_1081_float32.tif'
nlcdfile = '../data/bcdc_othernaturalareas/NaturalAreas_ForDave/nlcd_nodevt/'

raster_to01(slrfile, '../bcdc_slr/raster_scratch/slr01.tif')
aggregate_rast01_bymode('../bcdc_slr/raster_scratch/slr01.tif', nlcdfile, '../bcdc_slr/raster_scratch/slr01_30x30.tif')

