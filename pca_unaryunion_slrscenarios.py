import geopandas as gpd
import os
import glob

basedir = '../data/pca/bcdc_slr/PCAexposure_201710/slr_scenarios/'
for scenario in os.listdir(basedir):
	print(scenario)

	pcafile = glob.glob(os.path.join(basedir, scenario, 'dis*.shp'))[0]
	shp = gpd.read_file(pcafile)
	print('dissolving', pcafile)

	geom = shp['geometry']
	unioned = gpd.GeoSeries(geom.unary_union)
	outdf = shp.iloc[0:1]
	geo_df = gpd.GeoDataFrame(outdf, crs=shp.crs, geometry=gpd.GeoSeries(unioned))

	outdir = os.path.join(basedir, scenario, 'unaryunion')
	if not os.path.exists(outdir):
	    os.makedirs(outdir)

	print(outdir)
	geo_df.to_file(os.path.join(outdir, 'diss.shp'))