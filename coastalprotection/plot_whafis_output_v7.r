library(ggplot2)
library(RColorBrewer)
library(foreign)
library(dplyr)

cards <- c(BU="building", #cards is created as a vector
           VE="rigid veg",
           VH="marsh veg",
           DU="natural or built elongated barrier (inc. dunes)",
           AS="above surge",
           IE="initial elev",
           ET="end transect",
           IF="elev inland fetch",
           OF="elev overland fetch")


part2names <- c("label", "location", "waveheight", "waveperiod", "wavecrest_ele")
part1names <- c("label", "location", "elevation", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11")
# I only know what the first 3 columns are in part1, and so far we're only using those - V4 to V11 are placeholders, top row V6 is SWEL


# setup color pallete for the different 'cards'/transect labels
# mycolors <- brewer.pal(6,"Set1")
mycolors <- c("red", "blue", "purple", "black", "orange", "green")
# names(mycolors) <- levels(data$label)
names(mycolors) <- c("AS", "BU", "DU", "IE", "IF", "VH")
color_scale <- scale_colour_manual(name = "label",values = mycolors)


# This function joins the two tables part1 and part2 into 1 data frame and drops columns we don't need.
# If you need more variables from the part1 or part2 tables, this function is the place to modify things.
join_parts12 <- function(workspace, f1, f2){
  part1 <- read.table(file.path(workspace, "whafis_output", f1), skip=1, sep="") #read.table loads table into dataframe 
  names(part1) <- part1names #and then uses part1names variable to assign names
  # not sure what these 'PICK' and 'SALM' rows represent, 
  # but they are not unique transect locations so drop them. 
  # also drop the columns we don't need
  part1 <- part1[!(part1$location %in% c("PICK", "SALM", "BULL", "OATS")), c("label", "location", "elevation", "V6")]
  # also drop the ET row, which I think is just a placeholder for 'end transect' and holds no real data
  part1 <- part1[part1$label != "ET",]
  #return(part1)
  
  # part2 <- read.table(file.path(workspace, "whafis_output", f2), skip=4, sep="")
  part2 <- read.fwf(file.path(workspace, "whafis_output", f2), skip=4, widths=c(40, 2, 11, 13, 13, 13))
  part2$V1 <- NULL # first col is always empty space
  names(part2) <- part2names
  # drop rows with no card info, since those locations don't appear in part1
  part2 <- part2[part2$label != "  ",] # two spaces in quotes
  
  # now part1 rows should match part2:
  if(nrow(part1) == nrow(part2)){
    # no fancy joins here, just assuming that transect positions are in correct order
    part2$elevation <- part1$elevation
    part2$V6 <- part1$V6
  } else {
    print(f1)
    print(f2)
    stop("transect points don't match 1:1 between part1 and part2 output. something wrong with one of those files?")
  }
  return(part2)
}

## Calculate summary metrics and make line plots for a single transect and two scenarios
## This function returns a dataframe with a single row and columns like this:
## county, transect, max_WH_diff, max_WC_diff
make_transect_metrics <- function(f1, baseline_dir, scenario_dir, countyname, makeplot){
  # f1 is a whafis output file e.g. "17_part1.out"
  transect_number <- as.numeric(strsplit(f1, split="_")[[1]][1]) #grabs number out of filename e.g., 17
  
  f2 <- gsub(f1, pattern="part1", replacement="part2")
  base_data <- join_parts12(baseline_dir, f1, f2) #this is running join function above using arguments baselinedir, f1, f2
  base_data$scenario <- "veg" #creates new column/variable "scenario"
  base_data$transect <- transect_number #creates a new column/variable "transect"
  base_data$SWEL <- base_data[1,"V6"] # SWEL is in first row of V6
  
  scenario_data <- join_parts12(scenario_dir, f1, f2)
  scenario_data$scenario <- "noveg"  #
  scenario_data$transect <- transect_number
  scenario_data$SWEL <- scenario_data[1,"V6"]
  
  if (nrow(scenario_data) != nrow(base_data)){  #nrow give you number of rows in a data frame and this if/else statement is quality control to make sure same no. for both scenarios
    stop("transect points don't match up 1:1 between scenarios. something wrong with a XX_part2.out file?")
  }
  
  data <- rbind(base_data, scenario_data) #rbind is stacking - stands for rowbind, giving it two data frames
  diff_WH <- scenario_data$waveheight - base_data$waveheight
  diff_WC <- scenario_data$wavecrest_ele - base_data$wavecrest_ele
  
  # create a dataframe with transect summary metrics
  df <- data.frame(county=countyname, transect=transect_number, max_WH_diff=max(diff_WH), max_WC_diff=max(diff_WC))
  df$county <- as.character(df$county)
  
  if (makeplot){
    gg <- ggplot(data, aes(group=scenario)) + #ggplot needs data frame for first input (e.g., data)
      #then specify what's plotted on x and y, because want 2 dataseries on 1 plot, then use "group" (this is part of ggplot syntax) to group rows of data
      #aes - shorthand for aesthetics, signals that arguments will refer back to information in the data frame 
      # geom_line(aes(linetype=scenario)) +
      geom_line(aes(x=location, y=waveheight), color="gray60") + #geom_line and geom_point are ggplot functions
      geom_point(aes(x=location, y=waveheight, color=label), size=1) + #label in this case refers to column in dataframe
      geom_line(aes(x=location, y=wavecrest_ele), color="gray60") + #geom_line and geom_point are ggplot functions
      geom_point(aes(x=location, y=wavecrest_ele, color=label), size=1)+
      geom_line(aes(x=location, y=SWEL), color="blue") +
      geom_line(aes(x=location, y=elevation), color="brown") +
      color_scale + #specifies color pallet; defined abov
      labs(title=transect_number) + #labs can also have x and y label, lots of other options
      theme_classic()  #how the plot looks; can remove and see default, other pre-packaged themes
    print(gg)
  }

  return(df) #this is the output of that data.frame function; four columns, 1 row
}

## This function processes an entire county/directory of transects.
## It returns a dataframe with a row for each transect in the county
process_county <- function(baseline_dir, scenario_dir, countyname, makeplot){
  part1files <- list.files(path=file.path(baseline_dir, "whafis_output"), pattern="*part1.out")

  transect_dataframes <- list()
  for(f1 in part1files){
    transect_dataframes[[f1]] <- make_transect_metrics(f1, baseline_dir, scenario_dir, countyname, makeplot)
  }
  county_transects <- do.call("rbind", transect_dataframes) #use rbind in the do.call function and can combine a bunch of dataframes
  
  return(county_transects)
}

# # modify for different counties to run all transects within the county folder
# countyname <- "alameda_north" #county name all lower case; when more than one folder for particular county then _XXX
# baseline_dir <- "C:\\Data\\SFBay\\WHAFIS_BayWide\\NearShoreModeling\\Alameda North\\Nearshore_Wave_Models_1522774504360\\WHAFIS\\Simulations\\S1Input_Output"
# scenario_dir <- "C:\\Data\\SFBay\\WHAFIS_BayWide\\NearShoreModeling\\Alameda North\\Nearshore_Wave_Models_1522774504360\\WHAFIS\\Simulations\\S1Input_Output_noveg"
#     

## Process one whole county:
cdata <- process_county(baseline_dir="C:\\Data\\SFBay\\WHAFIS_BayWide\\NearShoreModeling\\Alameda North\\Nearshore_Wave_Models_1522774504360\\WHAFIS\\Simulations\\S1Input_Output",
              scenario_dir="C:\\Data\\SFBay\\WHAFIS_BayWide\\NearShoreModeling\\Alameda North\\Nearshore_Wave_Models_1522774504360\\WHAFIS\\Simulations\\S1Input_Output_noveg",
              countyname="alameda_north",
              makeplot=FALSE)

# ## Process all the counties -- experimental, not fully working yet.
# ## these *dir_list.txt files will be produced by the python script
baseline_dir_list <- readLines("C:/Data/SFBay/WHAFIS_BayWide/NearShoreModeling/baseline_dir_list.txt")
scenario_dir_list <- readLines("C:/Data/SFBay/WHAFIS_BayWide/NearShoreModeling/scenario_dir_list.txt")

# make a list of countynames to correspond to the directories
# order them in same order as these:
print(baseline_dir_list)
countynames <- c("sonoma", "santaclara", "sanfrancisco", "marin_2153584", "marin_2153582", "marin_2144221", "contracosta_2144246", "contracosta_2144244", "alameda_north", "alameda_south")

args <- cbind(baseline_dir_list, scenario_dir_list, countynames)
#args <- args[-1,] #this line drops Sonoma from the table since Part 2 of the output from WHAFIS is mixed up

allcounties <- list()
for(i in 1:nrow(args)){
  b <- args[i,"baseline_dir_list"]
  s <- args[i,"scenario_dir_list"]
  c <- args[i,"countynames"]
 
  possibleError <- tryCatch(
    allcounties[[c]] <- process_county(baseline_dir=b, scenario_dir=s, countyname=c, makeplot=FALSE),
    error=function(e) e
  )
  if(inherits(possibleError, "error")){
    print(possibleError)
    next
  }
}
allcounties_df <- do.call("rbind", allcounties)

## join allcounties_df to the transects dbf
transects <- read.dbf('C:/Data/SFBay/WHAFIS_BayWide/NearShoreModeling/alltransects/alltransects.dbf')
transects$county <- as.character(transects$county)
transect_summary <- left_join(transects, allcounties_df, by=c("county", "transect"))

if (nrow(transects) != nrow(transect_summary)){
  print("WARNING: transects table added or lost rows, aka. something screwy happened in the join")
}

write.csv(transect_summary, file="transect_summary.csv", row.names=FALSE)

# use this to make summary table and plots for a single transect
# tdata <- make_transect_metrics(f1="4_part1.out",
#                       baseline_dir="/home/dmf/recdev/data/SF_Bay/data/coastal_protection/4Dave_062718/test",
#                       scenario_dir="/home/dmf/recdev/data/SF_Bay/data/coastal_protection/4Dave_062718/test_noveg",
#                       countyname="alameda_north",
#                       makeplot=FALSE)


# testing things on a single transect:
# baseline_dir <- "/home/dmf/recdev/data/SF_Bay/data/coastal_protection/4Dave_062718/test"
# scenario_dir <- "/home/dmf/recdev/data/SF_Bay/data/coastal_protection/4Dave_062718/test_noveg"
# f1 <- "17_part1.out"
# f1 <- "tr02100_sc2_part1.out"
# f2 <- "tr02100_sc2_part2.out"
# workspace <- "~/recdev/data/SF_Bay/data/coastal_protection/NearShoreModeling/"

  

