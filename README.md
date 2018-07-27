#### `recmodel` has data processing for an 'outer coast' rec model

#### `coastalprotection` has WHAFIS wrapper scripts

#### Everything else:  
Workflows for analyzing outdoor recreation, and it's exposure to sea-level rise, in San Francisco Bay Area Priority Conservation Areas.  

### pca_rec.ipynb
* Priority Conservation Areas - baseline recreation as measured by volume of geotagged social media, currently and under 10 SLR scenarios
* Photo-user-days (PUD) and Twitter-user-days (TUD) in each PCA
* Proportion of PUDs inside the inundation zone of each SLR scenario, for each PCA

### regional_recreation_slrscenarios.ipynb  
Measuring regional outdoor recreation in the Bay Area using social media, in 3 different categories of land:
Priority Conservation Areas (PCAs),
Protected Areas (Bay Area Protected Areas Database - BPAD)
Natural landcover types (NLCD)
And summarizing how much of the recreation in each category is exposed to sea-level rise, based on 10 different SLR scenarios.

This workflow depends on results from:
* `slr_rasters_align.py`
* `userdays_rasteraoi.r`
* `pud_rasterize.py`
