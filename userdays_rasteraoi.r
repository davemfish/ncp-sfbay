### 20 Feb 2018 - DMF

## forked from globalrec/userdays.r

# major refactor of userdays.r to support SF Bay project
# for the special case of getting gridded PUD values to align with an existing raster,
# when there are far too many cells to first make a polygon representation of the raster.
# This approach takes a raster as an AOI,
# builds a rectangle geometry for each raster cell,
# queries the quadtree with one rectangle at a time, 
# writes the total PUD for each cell to a text file as it goes.

# This version is not compatible with the rest of the userdays-locations workflow.

### USAGE: set parameters in the section highlighted below


### Photo files should be like:

# photo_id,owner_name,date_taken,latitude,longitude,accuracy
# 219208114,53231487@N00,2005-04-29 18:00:41,48.208201,16.372718,12
# 219209109,46083256@N00,2005-07-10 11:18:46,37.867811,-122.25764,16
# 219211262,46083256@N00,2005-07-10 12:57:29,37.802231,-122.418015,16
# 219211144,46083256@N00,2005-07-10 12:46:06,37.800128,-122.410644,16
# 219211609,46083256@N00,2005-07-10 16:45:13,37.785766,-122.408251,15



library(SearchTrees)
# library(rgdal)
# library(rgeos)
library(raster)
library(dplyr)
library(readr)
# library(foreach)
# library(feather)

# args=(commandArgs(TRUE))

# if(length(args)!=1){
#     print("userdays.r takes only 1 argument (aoi.shp)")
#     stop
# } else {
#     aoipath <- args[1]
#     shpname <- sub(x=basename(aoipath), pattern=".shp$", replacement="")
# }

########################
### SET PARAMS BELOW:
########################

aoipath <- "~/Recdev/data/SF_Bay/data/bcdc_othernaturalareas/NaturalAreas_ForDave/nlcd_nodevt_utm.tif"
aoiname <- sub(x=basename(aoipath), pattern=".tif$", replacement="")
outpath <- file.path("~/Recdev/data/SF_Bay/data/twitter/nlcd_grid_tud/")

## Set photos by pointing to dir of csv files
# csvpath <- file.path("/home/dmf/Recdev/data/SF_Bay/data/flickr/flickr_photos_inbbox") 
# datasource <- "flickr" 
csvpath <- file.path("/home/dmf/Recdev/data/SF_Bay/data/twitter/") 
datasource <- "twitter" 

if (datasource == "twitter"){
  COL_TYPES <- list(
    id_str=col_skip(),
    owner_name=col_character(),
    date_taken=col_character(),
    latitude=col_double(),
    longitude=col_double())
  } else {
    if (datsource == "flickr"){
      COL_TYPES <- list(
    photo_id=col_skip(),
    owner_name=col_character(),
    date_taken=col_character(),
    latitude=col_double(),
    longitude=col_double(),
    accuracy=col_skip())
    } else {
      stop("invalid datasource - set as 'flickr' or 'twitter' ")
    }
}

########################


### DEFINE FUNCTIONS ####

## INTERSECT CURRENT AOI POLYGON/CELL WITH QUADTREE
LookupPUD <- function(square){
  lons <- square[[1]]
  lats <- square[[2]]
  inrect <- rectLookup(tree, xlim=lons, ylim=lats)

  if (length(inrect) == 0){
    userdays <- 0
  } else {
    df <- photos@data[inrect, ]
    userdays <- nrow(unique(df[,c("owner_name", "date_taken")]))
  }

  return(userdays)
} 

generate_square <- function(col_index, row_index){
# adapted from natcap.invest.recreation.recmodel_client._generate_polygon

  # col_index <- 0 # needs to start at 0
  # row_index <- 0

  xmin <- extent_aoi[1] + col_index * cell_size_x + 0
  xmax <- extent_aoi[1] + col_index * cell_size_x + cell_size_x
  ymin <- extent_aoi[3] + row_index * cell_size_y + 0
  ymax <- extent_aoi[3] + row_index * cell_size_y + cell_size_y
  
  lons <- c(xmin, xmax)
  lats <- c(ymin, ymax)
  return(list(lons, lats))
}
  

#### RUN SCRIPT #####

photofiles <- list.files(csvpath, pattern="*.csv$")
## OR an individual file
# photofiles <- "allpics_2100.csv"

### load the AOI
aoiraster <- raster(aoipath)

if (grepl("\\+proj=longlat\\s+\\+datum=WGS84", projection(aoiraster))){
  print("Checking AOI CRS...matches points")
  transform_points <- FALSE
} else {
  print("AOI CRS does not match photo's CRS...will transform points to match")
  transform_points <- TRUE
}


## Compute PUD values
## ## Loop through each year of photos
# ptm <- proc.time()
for (p in 1:length(photofiles)){
  print(paste("IMPORTING", photofiles[p], proc.time()[3]))
  ptm <- proc.time()
  photos <- as.data.frame(read_csv(file.path(csvpath, photofiles[p]),
    col_names=TRUE,
    col_types= COL_TYPES
    )) # as.data.frame wrapper required for passing photos to createTree()
  totaltime <- proc.time() - ptm
  
  if(nchar(photos$date_taken[1]) != 8){
      if(nchar(photos$date_taken[1]) == 19){
        newdates <- unlist(lapply(photos$date_taken, FUN=function(x){
          a <- strsplit(x, split=" ")[[1]][1]
          b <- gsub(a, pattern="-", replacement="", fixed=T)
        }))
        photos$date_taken <- newdates
      } else {
        stop("ERROR: Bad date format in photo's csv file")
      }
  }
  
  if(transform_points){
    coordinates(photos) <- c("longitude", "latitude")
    proj4string(photos) <- CRS("+init=epsg:4326") # WGS 84
    CRS.new <- CRS(projection(aoiraster))
    photos <- spTransform(photos, CRS.new)
  } else {
    coordinates(photos) <- c("longitude", "latitude")
  }
  

  ## Create quadtree
  ## ## requires ~8 Gb memory for the global flickr collection
  ## ## takes a few mins to build the tree
  # specify either maxDepth or minNodeArea
  # option: maxBucket = max points allowed in a single node (not used)
  # For the globe, Depth 11 creates leaves ~0.18 degrees on a side
  # A 1km cell is approx 0.01 degrees on a side at 23N/S latitude
  
  print(paste("BUILDING QUADTREE FOR", photofiles[p], proc.time()[3]))
  # photo_x <- which(names(photos) == "longitude")
  # photo_y <- which(names(photos) == "latitude")
  # tree <- createTree(photos, columns=c(photo_x, photo_y), dataType="point", maxDepth=11)
  tree <- createTree(coordinates(photos), dataType="point", maxDepth=11)
    
  print(paste("LOOKUP AND PUD FOR", photofiles[p], proc.time()[3]))
  
  extent_aoi <- extent(aoiraster)
  cell_size_x <- res(aoiraster)[1]
  cell_size_y <- res(aoiraster)[2]
  n_rows = ((extent_aoi[4] - extent_aoi[3]) / cell_size_y)
  n_cols = ((extent_aoi[2] - extent_aoi[1]) / cell_size_x)
  
  print(paste("cell_size", cell_size_x, cell_size_y))
  print(paste("ncells", n_rows*n_cols))
  
  fname <- file.path(outpath, paste(aoiname, sub("\\.[^.]*$", "", photofiles[p]), "lrbt.csv", sep="_"))
  fileconn <- file(fname, 'w')
  for (row_index in 0:(n_rows - 1)){
    print(paste(row_index, "/", n_rows, proc.time()[3]))
    for (col_index in 0:(n_cols - 1)){
      square = generate_square(col_index, row_index)
      ud <- LookupPUD(square)
      writeLines(as.character(ud), fileconn)
    }
  }
  close(fileconn)
}

totaltime <- proc.time() - ptm