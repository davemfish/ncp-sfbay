# BASEDIR='../data/bcdc_othernaturalareas/System_level_AOIs_Recmodeling/AOI_intersections/BPAD/unaryunion/'
# BASEDIR='../data/bcdc_othernaturalareas/System_level_AOIs_Recmodeling/AOI_intersections/Natural_Lands/unaryunion/'
BASEDIR='../data/bcdc_othernaturalareas/System_level_AOIs_Recmodeling/MergedAOI_noDevt/'


for shp in $BASEDIR/*.shp ;
	do
		aoi=$shp
		echo $aoi
		workspace=$BASEDIR/$(basename $aoi .shp)
		echo $workspace
		if [ ! -d $workspace ]; then
			mkdir $workspace
			echo $workspace
			Rscript --vanilla userdays.r $aoi $workspace > userdays.out

			# cd $workspace
			mkdir $workspace/tmp_users
			allusers=$workspace/users_allyears.csv

			head -1 $workspace/*2005_users.csv | cat >> $allusers
			for file in $workspace/*users.csv
			do
				echo $file
				wc -l $file
				tail -n +2 $file | cat >> $allusers
				mv $file $workspace/tmp_users/
			done
			# cd ..
		fi
	done