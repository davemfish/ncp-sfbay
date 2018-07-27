
# coding: utf-8

# In[1]:


import geopandas as gpd
import pandas as pd


# In[2]:


# these are defined in pg. 101 (or 95) of METADATA.pdf here:
# https://drive.google.com/drive/u/0/folders/0Byybp7XR8oPDZzByOFJSSEZ4TjA?ogsrc=32

#     "1A":"Exposed Rocky Shores",
#     "1B":"Exposed Solid Man-madeStructures",
#     "2A":"Exposed Wave-cut Platforms",
#     "3A":"Fine- to Medium-grained Sand Beaches",
#     "3B":"Scarps and Steep Slopes in Sand" 
#     "4":"Coarse-grained Sand Beaches",
#     "5":"Mixed Sand and Gravel Beaches",
#     "6A":"Gravel Beaches",
#     "6B":"Riprap",
#     "6D":"Boulder Rubble",
#     "7":"Exposed Tidal Flats",
#     "8A":"Sheltered Rocky Shores",
#     "8B":"Sheltered Solid Man-madeStructures",
#     "8C":"Sheltered Riprap",
#     "9A":"Sheltered Tidal Flats",
#     "9B":"Vegetated Low Riverine Banks",
#     "9C": not listed in metadata,
#     "10A":"Salt- and Brackish-water marshes",
#     "10B":"Freshwater Marshes",
#     "10C": not listed in metadata
#     "10D":"Scrub-shrub Wetlands",
#     "U":"Unranked"


# In[3]:


## Change this reclassification to suit your needs, I didn't give it much thought and some things are misrepresented. 
# The goal is to reduce the categories to just what we want to measure the effects of in a rec model.
esi_reclass = {
    "1A":"rock_cliff",
    "1B":"structures",
    "2A":"rock_cliff",
    "3A":"beach",
    "3B":"rock_cliff",
    "4":"beach",
    "5":"beach",
    "6A":"beach",
    "6B":"riprap",
    "6D":"riprap",
    "7":"marsh_wetland",
    "8A":"rock_cliff",
    "8B":"structures",
    "8C":"riprap",
    "9A":"marsh_wetland",
    "9B":"marsh_wetland",
    "9C":"unknown",
    "10A":"marsh_wetland",
    "10B":"marsh_wetland",
    "10D":"marsh_wetland",
    "10C":"unknown",
    "U":"unknown"
}
SHORE_CLASSES = list(set(esi_reclass.values()))


# In[4]:


## load ESI data and reclassify the codes
esil = gpd.read_file("../../data/recdata/scratch/esil_entirecoast_utm.shp")
esil = esil[['ESI', 'geometry']]
## single features can have many codes (e.g. '10D/6B/4'), split them apart
codes = esil['ESI'].str.split('/', expand=True)


# In[5]:


## and then reclassify and attach to esil geodataframe

def reclass_func(x):
    if x: 
        return esi_reclass[x]
    else:
        return x
    
reclassed = codes.applymap(reclass_func)
esil[list(reclassed)] = reclassed
esil.head()


# In[6]:


## load polygon segments to intersect - 
## note we're using the full buffers here, not the versions cut-off by the land
segments = gpd.read_file("./model_data/aoi/ne_ca_coastline_1k_segments_buff400m.shp")
segments.head()


# In[7]:


# one:many join of polygon segments to all the esil line segments they intersect
# this allows one polygon to capture many esil segments, 
# and allows an esil segment to be joined to multiple polygons
esil_seg = gpd.sjoin(segments[['geometry', 'pid']], esil, op='intersects', how='left')
print(segments.shape)
print(esil_seg.shape)


# In[8]:


## now reduce back to single row per polygon, grouping on pid and combining esil segments 
def combine_shoretypes(df):
    alltypes = df[0].tolist() + df[1].tolist() + df[2].tolist()
    alltypes = [str(x) for x in alltypes if x is not None]
    alltypes = [str(x) for x in alltypes if str(x) != 'nan']
    if alltypes:
        return ','.join(set(alltypes))
    else:
        return None

# testing this func:
# df = esil_seg.loc[esil_seg['pid'] == 16]
# combine_shoretypes(df[list(reclassed)])

grouped_types = pd.DataFrame(esil_seg.groupby('pid').apply(combine_shoretypes)).reset_index()
grouped_types.rename(columns={0:'shoretype'}, inplace=True)


# In[9]:


## Fill a presence/absence table of shoretypes for each segment
segments2 = segments.reindex(columns=list(segments) + SHORE_CLASSES)
segments3 = pd.merge(segments2, grouped_types, on='pid', how='left')
# segments3.head()


# In[10]:


def fill_presence_absence(df):
    for sc in SHORE_CLASSES:
        if df['shoretype'] is not None:
            if sc in df['shoretype']:
                df[sc] = 1
            else:
                df[sc] = 0
    return(df)

segments_shoretypes = segments3.apply(fill_presence_absence, axis=1)
segments_shoretypes.tail()


# In[11]:


segments_shoretypes[['pid'] + SHORE_CLASSES].to_csv('model_data/predictors/shoreline_type.csv', index=False)

