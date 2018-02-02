
# unary union for all the PCA x SLR intersections,
# these unioned PCA networks will support 'system-level'
# PUD counting for each scenario.

## after this step, need to remove developed lulc types from these networks

# source activate geowork

import geopandas as gpd
import os
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('basedir')
args = parser.parse_args()

BASEDIR = args.basedir

for shpfile in os.listdir(BASEDIR):
	if shpfile.endswith(".shp"):
		print(shpfile)
		outdir = os.path.join(BASEDIR, 'unaryunion')
		if not os.path.exists(outdir):

			shp = gpd.read_file(os.path.join(BASEDIR, shpfile))
			geom = shp['geometry']

			print('buffering', shpfile)
			geom = geom.buffer(0)

			print('dissolving', shpfile)
			unioned = gpd.GeoSeries(geom.unary_union)

			outdf = shp.iloc[0:1]
			geo_df = gpd.GeoDataFrame(outdf, crs=shp.crs, geometry=gpd.GeoSeries(unioned))

			print(outdir)
			os.makedirs(outdir)
			geo_df.to_file(os.path.join(outdir, shpfile))

