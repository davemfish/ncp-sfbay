
# coding: utf-8

# In[1]:


import geopandas as gpd
import pandas as pd
import numpy as np


# In[2]:


points = gpd.read_file("../../data/recdata/scratch/coastal_access_locations_utm.shp")
points.head()


# In[3]:


access_vars = ['BIKE_PATH','BLFTP_PRK','BLFTP_TRLS','BLUFF','BOATING',
 'BT_FACIL_T','Bch_whlchr','CAMPGROUND','DOG_FRIEND','DSABLDACSS','DUNES',
 'EZ4STROLLE','FEE','FISHING','PARKING','PCNC_AREA','PTH_BEACH','RESTROOMS',
 'RKY_SHORE','SNDY_BEACH','STRS_BEACH','TIDEPOOL','VISTOR_CTR','VOLLEYBALL','WLDLFE_VWG']

## ditch the 'BT_FACIL_T' var rather than clean it up.
## it states the type of facility present rather than 'yes' or 'no'.
## we have another 'BOATING' variable with the yes/no, 
## so I don't think we care enough about the type of facility to process it.
if 'BT_FACIL_T' in access_vars: access_vars.remove('BT_FACIL_T')


# In[4]:


points = points[access_vars + ['geometry']]


# In[5]:


## load polygon segments to intersect - 
## note we're using the full buffers here, not the versions cut-off by the land
segments = gpd.read_file("./model_data/aoi/ne_ca_coastline_1k_segments_buff400m.shp")
segments.head()


# In[6]:


# one:many join of polygon segments to all the access points
# this allows one polygon to capture many points
access_seg = gpd.sjoin(segments[['geometry', 'pid']], points, op='intersects', how='left')
print(segments.shape)
print(access_seg.shape)


# In[7]:


## Now we want to convert all the vars to 1s or 0s (presence/absence)
## And then summarize the count of 1s for each variable in each polygon


# In[8]:


# wasn't exactly sure what pd.get_dummies does so didn't use it, but could be handy
# dummy = pd.get_dummies(access_seg[access_vars])


# In[9]:


## first cleanup the wheelchair var
## it often has a phone number and statement that access is provided if you call first.
## I'm not sure if that counts as access or not, decide here:
def wheelchair(x):
    if x:
        if str(x) in ['nan', 'No', 'no', 'Yes', 'yes']:
            return x
#         print(x) # all the rest are the phone numbers
        return 'no' # pick yes or no
    return x

access_seg[['Bch_whlchr']] = access_seg[['Bch_whlchr']].applymap(wheelchair)


# In[10]:


def make_presence_absence(x):
    if x:
        if str(x) != 'nan':
            x = x.lower()
            if x in ['no']:
                return 0
            if x in ['yes']:
                return 1
            if x in ['yes?', '?']:
                return np.nan
            print(x) # should print nothing if we've caught all the weird values
        return np.nan # if it was nan to begin with
    return np.nan # if it was None to begin with

access_seg[access_vars] = access_seg[access_vars].applymap(make_presence_absence)


# In[11]:


access_seg.head()


# In[13]:


## for each col, group rows by pid, sum down the column
## and put result back into segments dataframe, which has 1 row per polygon/pid

## do a np.nansum unless they are all nan, in which case return nan.
## np.nansum treats nan as 0
def nansum_all(df, var):
    x = df[var]
    if np.all(np.isnan(x)):
        return np.nan
    else:
        return np.nansum(x)
    
for av in access_vars:
    segments[av] = access_seg[['pid'] + [av]].groupby('pid').apply(nansum_all, av)


# In[14]:


segments.describe()


# In[17]:


segments[['pid'] + access_vars].to_csv('model_data/predictors/access_yourcoast.csv', index=False)

