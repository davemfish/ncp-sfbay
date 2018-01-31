## unary union for all the PCA x SLR intersections,
## these unioned PCA networks will support 'system-level'
## PUD counting for each scenario.

## after this step, need to remove developed lulc types from these networks

# source activate geowork

import geopandas as gpd
import os
import glob

basedir = '../data/pca/bcdc_slr/PCAexposure_201710/slr_scenarios/'
for scenario in os.listdir(basedir):
	print(scenario)
	outdir = os.path.join(basedir, scenario, 'unaryunion')
	if not os.path.exists(outdir):

		pcafile = glob.glob(os.path.join(basedir, scenario, 'dis*.shp'))[0]
		shp = gpd.read_file(pcafile)
		print('buffering', pcafile)
		
		print('dissolving', pcafile)
		geom = shp['geometry']
		geom = geom.buffer(0)
		unioned = gpd.GeoSeries(geom.unary_union)
		outdf = shp.iloc[0:1]
		geo_df = gpd.GeoDataFrame(outdf, crs=shp.crs, geometry=gpd.GeoSeries(unioned))

		print(outdir)
		os.makedirs(outdir)
		geo_df.to_file(os.path.join(outdir, 'diss.shp'))