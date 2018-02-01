# For each SLR scenario, make shapefiles that represent the entire PCA network
# but are missing all areas of development


import geopandas as gpd
from shapely.geometry.polygon import Polygon
from shapely.geometry import MultiPolygon
from shapely.errors import TopologicalError
from shapely.ops import unary_union
import datetime
import os
import glob


# shapefile representing whole PCA network with developed landuse categories already cut-out
pca_nodev_path = '../data/bcdc_othernaturalareas/System_level_AOIs_Recmodeling/PCA_notdevt.shp'
nodevshp = gpd.read_file(pca_nodev_path)
nodevshp['pca_key'] = nodevshp['fipco'] + nodevshp['joinkey']

BASEDIR = '../PCAexposure_201710/slr_scenarios/'

def intersect_byeach_pca(scenario):

    print(scenario)
    scenariodir = os.path.join(BASEDIR, scenario)
    outdir = os.path.join(scenariodir, 'nodevt')
    if not os.path.exists(outdir):
        # the pca network intersection with the SLR scenario
        pcafile = glob.glob(os.path.join(scenariodir, 'dis*.shp'))[0]
        pcashp = gpd.read_file(pcafile)

    #     pcashp.crs == nodevshp.crs
    #     proj4string = '+proj=utm +zone=10 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'

    #     # table linking scenario polygon id (TARGET_FID) and master PCA unique id (joinkey, fipco)
    #     # TARGET_FID == FID_spjoin
    #     fidspjoin_joinkey_crswlk = gpd.read_file(glob.glob(os.path.join(scenariodir, 'spjoi*.dbf'))[0])
    #     fidspjoin_joinkey_crswlk = fidspjoin_joinkey_crswlk[['TARGET_FID', 'joinkey', 'fipco', 'name']]
    #     fidspjoin_joinkey_crswlk['pca_key'] = fidspjoin_joinkey_crswlk['fipco'] + fidspjoin_joinkey_crswlk['joinkey']

    #     ## for each pca in pcashp, find the corresponding geom from nodevshp, intersect, save geometry
    #     collection = []
    #     fids = []
    #     for index, row in pcashp.iterrows():
    #         fid = row['FID_spjoin']
    #         fids.append(fid)
    #         intersector_key = fidspjoin_joinkey_crswlk[fidspjoin_joinkey_crswlk['TARGET_FID'] == fid]['pca_key']
    #         if len(intersector_key) == 1:
    #             intersector_key = intersector_key.values[0]
    #             print(intersector_key)
    #         else:
    #             print('more than one pca matched')
    #         intersector_geoseries = nodevshp[nodevshp['pca_key'] == intersector_key]['geometry']
    #         intersector_geom = intersector_geoseries.unary_union
    #         print(datetime.datetime.now())
    #         geom1 = row['geometry'].buffer(0)
    #         geom2 = intersector_geom.buffer(0)
    #         try:
    #             result_geom = geom1.intersection(geom2)
    #         except TopologicalError:
    #             print('found topology error, trying buffer of 1 millimeter')
    #             result_geom = geom1.intersection(geom2.buffer(0.001))
    #         collection.append(result_geom)

        os.makedirs(outdir)
    #     outgeo = gpd.GeoSeries(collection)
    #     outdf = gpd.GeoDataFrame(data={'FID_spjoin':fids}, geometry=outgeo, crs=proj4string)
    #     outdf = outdf[~outdf['geometry'].is_empty]

        outdf = pcashp
        outdf.to_file(os.path.join(outdir, 'diss_nodevt.shp'))




scenario_list = ['12inches']
for s in scenario_list:
    intersect_byeach_pca(s)