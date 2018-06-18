## DMF - June 18, 2018

## call WHAFIS executable for all input files found in a set of directories.
## this script creates an output file with the same name as the input file (but with '.out' extension)
## outputs are created in a new folder called 'whafis_output' inside each of the input directories

## USAGE:
# python batch_whafis.py

import os
import subprocess

## the location of the whafis executable
WHAFIS = 'path/to/whafis4.exe'

## A list of the directories that hold input files. 
## These paths are relative to location of this script.
## Input files may have ".dat" or ".in" extension
input_dirs = [
"Sonoma/May_2013_SONOMA/whafis/input_files/", 
"Santa Clara/NearshoreWaveModels/WHAFIS/Simulations/S1/", 
"San Francisco/Nearshore_Wave_Models/WHAFIS/Simulations/S1Input-Output", 
"Marin/2153584/SanFranciscoBay/CentralBay--MarinCounty/Nearshore_Wave_Models/WHAFIS/Simulations/S1Input-Output", 
"Marin/2153582/WHAFIS/input_files",
"Marin/2144221/20110411_MarinCo_Submittal_FINAL/WHAFIS/Scenario1Input-Output",
"Contra Costa/2144244/WHAFIS/input_files",
"Contra Costa/2144246/20130118_ContraCostaCo_Analysis_BKR/SanFranciscoBay/Nearshore_Wave_Models/WHAFIS/Simulations/Scenario1Input-Output",
"Alameda North/WHAFIS/Simulations/S1Input_Output"
]



def run_whafis_dir(input_dir):
	output_dir = os.path.join(input_dir, "whafis_output")
	os.mkdir(output_dir)
	file_list = os.listdir(os.path.join(input_dir))
	for f in file_list:
		## we don't want to run whafis with an 'mg.dat' input
		if 'mg' in f:
			continue
		if f.endswith(".dat") or f.endswith(".in"):
			infile = os.path.join(input_dir, f)
			outfile = os.path.join(output_dir, f.rsplit(".", 1)[0] + ".out")
			subprocess.call(['echo', infile, outfile])
			# subprocess.call([WHAFIS, infile, outfile])


# run_whafis_dir("Sonoma/May_2013_SONOMA/whafis/input_files/")
for d in input_dirs:
	run_whafis_dir(d)
