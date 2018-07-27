
# coding: utf-8

# In[1]:


import geopandas as gpd
import fiona
from shapely.geometry import MultiPolygon, shape, mapping
# from shapely.prepared import prep
from shapely.ops import unary_union


# In[2]:


## note, sometimes these buffers do not respect the buffer() arguments and just make plain rounded buffers
## clearing the environment and restarting the kernel and running again solves it.


# ## Segment the coastline
# coastline source: https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/physical/ne_10m_coastline.zip  
# In QGIS, I selected just the CA coast and transformed to nad83 UTM Zone 10N.  
# Then used `grass` `v.split.length` from within QGIS to cut the line at 1km intervals  
# The result is this:

# In[3]:


coastlines = gpd.read_file("../../data/recdata/scratch/ne_ca_coastline_1k_segments.shp")


# ## Create polygons from line segments
# Buffer the line segment by fixed width. This buffers on either side of the line. An asymmetrical buffer that extends far offshore but not too far onshore would be better. That way we avoid counting PUDs and TUDs from onshore sites like parts of cities. So after buffering, we'll cut the buffer away with a land polygon. And first we'll 'shrink' the land polygon with a negative buffer, because we do want some onshore area to stay in the coast segments.

# In[4]:


## Set these parameters, including locations for the output files

bufferwidth = 400 # all units are meters since we're always using NAD83 UTM Zone 10N
shrinklandwidth = -100
buffer_segments_uri = "./model_data/aoi/ne_ca_coastline_1k_segments_buff" + str(bufferwidth) + "m.shp"
finalcut_segments_uri = "./model_data/aoi/ne_ca_coastline_1k_segments_buff" + str(bufferwidth) + "m_cut.shp"


# #### Buffer segments

# In[5]:


buffers = coastlines.geometry.apply(lambda x: x.buffer(bufferwidth, cap_style=2, join_style=1))
coastsegments = coastlines
coastsegments['geometry'] = buffers

# I'll always use 'pid' as the unique key for polygons in all tables
coastsegments['pid'] = coastsegments.index
# don't need these cols
coastsegments.drop(labels=['featurecla', 'scalerank', 'min_zoom'], axis=1, inplace=True)

coastsegments.to_file(buffer_segments_uri)


# #### Erase land area

# In[6]:


coastsegments = gpd.read_file(buffer_segments_uri)


# In[7]:


land_uri = "../../data/recdata/scratch/ca_adm1_utm.shp"
land = fiona.open(land_uri)
geoms = []
for pol in land:
    geom = shape(pol['geometry']).buffer(shrinklandwidth)
    geoms.append(geom)
shrunkland = unary_union(geoms).buffer(0)


# In[8]:


# intersecting coast segment buffers with a land polygon, removing the land area from the segment.
# this takes a couple minutes
diffs = coastsegments.geometry.apply(lambda x: x.difference(shrunkland))


# In[9]:


# clean up the mixed bag of geometry types that resulted from the intersection by converted all to MultiPolygon
geoms = []
for geom, idx in zip(diffs, range(len(diffs))):
    if geom.geom_type == 'MultiPolygon':
        geoms.append(geom)
        continue
    if geom.geom_type == 'Polygon':
        geoms.append(MultiPolygon([geom]))
        continue
    if geom.geom_type == 'GeometryCollection':
        if geom.wkt == 'GEOMETRYCOLLECTION EMPTY':
            geoms.append(MultiPolygon([]))
            continue
    print(geom.geom_type, idx) # if stuff prints, then probably need more 'if' clauses to catch more misc types


# In[10]:


# write cut segments to file
with fiona.open(buffer_segments_uri, 'r') as input:
    meta = input.meta # The output file has the same crs, schema as input file
    with fiona.open(finalcut_segments_uri, 'w', **meta) as output:
        for item, g in zip(input, geoms):
            output.write({'geometry':mapping(g), 'properties': item['properties']})


# The final cut segments are what we'll want as an AOI for counting PUDs and TUDs. But the larger uncut segments might be best for spatial joins with ESI shore lines or YourCoast points. The larger segments give a little more wiggle room with those overlays, which is useful since all our coastal data come from different sources and don't align perfectly.
