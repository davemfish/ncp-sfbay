
# do some memory efficient polygon intersections and area calculations
# using functions built for invest rec

# requires a python2 environment

from osgeo import ogr
import shapely
import natcap.invest.recreation.recmodel_client as rec


def shapely_intersect(aoi_path, intersector_path, output_csv_path):

    response_vector_path = (aoi_path)
    response_vector = ogr.Open(response_vector_path)
    response_layer = response_vector.GetLayer()
    response_polygons_lookup = {}  # maps FID to prepared geometry
    for response_feature in response_layer:
        feature_geometry = response_feature.GetGeometryRef()
        feature_polygon = shapely.wkt.loads(feature_geometry.ExportToWkt())
        feature_geometry = None
        response_polygons_lookup[response_feature.GetFID()] = feature_polygon
    response_layer = None

    aoi_intersecting_areas = rec._polygon_area('area', response_polygons_lookup, intersector_path)
    CSV ="\n".join([str(k)+','+''.join(str(v)) for k,v in aoi_intersecting_areas.items()])
    with open(output_csv_path, "w") as file:
        file.write('pid' + ',' + 'area_m2' + '\n')
        file.write(CSV)
        
    return(0)


aoi_path = '../twitter/shp/Priority_Conservation_Areas_current_dissolve_pid.shp'
intersector_path = '../slr/CA_MTR23_slr_6ft.shp'
output_csv_path = 'pca_area_inundated_slr6ft.csv'
shapely_intersect(aoi_path, intersector_path, output_csv_path)