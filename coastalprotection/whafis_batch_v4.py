## DMF - June 18, 2018

## call WHAFIS executable for all input files found in a set of directories.
## this script creates an output file with the same name as the input file (but with '.out' extension)
## outputs are created in a new folder called 'whafis_output' inside each of the input directories

## USAGE:
# python batch_whafis.py

import os
import subprocess

## the location of the whafis executable
WHAFIS = 'C:/Data/SFBay/WHAFIS_BayWide/NearShoreModeling/WHAFIS4.exe'

## A list of the directories that hold input files. 
## These paths are relative to location of this script.
## Input files may have ".dat" or ".in" extension
baseline_list = [
"Sonoma/May_2013_SONOMA/whafis/input_files/" ,
"Santa Clara/NearshoreWaveModels/WHAFIS/Simulations/S1/", 
"San Francisco/Nearshore_Wave_Models/WHAFIS/Simulations/S1Input-Output", 
"Marin/2153584/SanFranciscoBay/CentralBay--MarinCounty/Nearshore_Wave_Models//WHAFIS/Simulations/S1Input-Output/", 
"Marin/2153582/SanFranciscoBay/CentralBay--MarinCounty/Nearshore_Wave_Models/WHAFIS/input_files",
"Marin/2144221/SanFranciscoBay/CentralBay--MarinCounty/Nearshore_Wave_Models/20110411_MarinCo_Submittal_FINAL/WHAFIS/Scenario1Input-Output",
"Contra Costa/2144244/WHAFIS/input_files",
"Contra Costa/2144246/Nearshore_Wave_Models/WHAFIS/Simulations/Scenario1Input-Output",
"Alameda North/WHAFIS/Simulations/S1Input_Output"
]

# baseline_list = ["/home/dmf/recdev/data/SF_Bay/data/coastal_protection/4Dave_062718/test"]


def modify_dat(infilename, outfilename):
	'''
	infilename (string): path to an existing whafis input file (.dat or .in)
	outfilename (string): path to a new whafis output file that will be created (must be ".out" extension)
	'''
	with open(infilename, 'r') as infile:
	    with open(outfilename, 'w') as outfile:
	        for line in infile:
	            if 'MG' in line:
	            	# remove line by not writing it to output table
	                continue
	            if 'VH' in line:
	            	# modify by replacing VH with IF, and values with 0s
	                line = 'IF' + line[2:16] + '    0.00    0.00    0.00    0.00' + line[48:]
	            outfile.write(line)

def run_whafis_dir(input_dir, output_dir):
	file_list = os.listdir(os.path.join(input_dir))
	for f in file_list:
		#print(f)
		## we don't want to run whafis with an 'mg.dat' input
		if 'mg' in f:
			continue
		if f.endswith(".dat") or f.endswith(".in"):
			infile = os.path.join(input_dir, f)
			outfile = os.path.join(output_dir, f.rsplit(".", 1)[0] + ".out")
			#print(WHAFIS + " " + infile + " " + outfile)
			# subprocess.call(['echo', infile, outfile], shell=True)
			subprocess.call([WHAFIS, infile, outfile])

def parse_output_part1(outfilename, part1filename):
	with open(part1filename, 'w') as part1file:
		with open(outfilename, 'r') as file:
			part = 0 
			for line in file:
				if "PART" in line:
					part += 1
				if part == 1:
					if line.startswith('1'):
						break
					if not line.isspace():
						part1file.write(line)


def parse_output_part2(outfilename, part2filename):
	with open(part2filename, 'w') as part2file:
	    with open(outfilename, 'r') as file:
	        part = 0 
	        for line in file:
	            if "PART" in line:
	                part += 1
	            if part == 2:
	                if not line.isspace():
	                    # print(line)
	                    part2file.write(line)


## Create a pair of SLR scenarios that modify each veg and no veg input dir 
## by adding some number of feet to the swel in the input


## STEP 1 ##
## Make 1 new scenario folder for each folder in baseline_list
## It gets the same name as the baseline folder, with "_noveg" suffix
print("MAKING SCENARIO INPUTS....for the following directories")
scenario_list = []
with open('baseline_dir_list.txt', 'w') as file1:
	with open('scenario_dir_list.txt', 'w') as file2:
		for d in baseline_list:
			file1.write(d + "\n")
			print(d)
			## make an empty folder for each noveg scenario
			dirname = os.path.basename(os.path.normpath(d))
			scenario_path = os.path.join(os.path.dirname(os.path.normpath(d)), dirname + "_noveg")
			if not os.path.exists(scenario_path):
				os.mkdir(scenario_path)

			## Comment this next block if you already have modifed inputs for scenarios 
			## but still want to make the list of scenario directories for STEP 2 & 3
			## make noveg input file for the scenario
			## this may overwrite exisiting contents of a "_noveg" folder
			## don't make a new folder if one exists already

			# for f in os.listdir(d):
			# 	if 'mg' in f:
			# 		continue
			# 	if f.endswith('.dat') or f.endswith(".in"):
			# 		# create new dat file with modifications
			# 		infilename = os.path.join(d, f)
			# 		outfilename = os.path.join(scenario_path, f)
			# 		modify_dat(infilename, outfilename)

			## Add scenario path to a list of dirs where we'll run whafis
			scenario_list.append(scenario_path)
			file2.write(scenario_path + "\n")


# ## STEP 2 ##
# ## Run whafis on all input directories
# ## This may overwrite existing contents of output folders
# print("......")
# print("MAKING OUTPUT DIRECTORIES & RUNNING WHAFIS....on these input directories")
# all_input_dirs = baseline_list + scenario_list
# all_output_dirs = []
# for in_dir in all_input_dirs:
# 	out_dir = os.path.join(in_dir, "whafis_output")
# 	if not os.path.exists(out_dir):
# 		os.mkdir(out_dir)
# 	print(in_dir)

# 	## comment next line if you don't want to re-run whafis, 
# 	## but do want to make the list of output directories for STEP 3:
# 	# run_whafis_dir(in_dir, out_dir)

# 	all_output_dirs.append(out_dir)


# ## STEP 3 ##
# ## Parse output tables, extracting only the "PART 2" section.
# ## for each "XX.out" file found, this creates a corresponding "XX_part2.out"
# print("......")
# print("PARSING OUTPUT FILES....in these directories")
# for whafis_output in all_output_dirs:
# 	print(whafis_output)
# 	for out in os.listdir(whafis_output):
# 		if out.endswith('.out'):
# 			if '_part' not in out:
# 				out_part1 = out.replace('.out', '_part1.out')
# 				out_part2 = out.replace('.out', '_part2.out')
# 				parse_output_part1(os.path.join(whafis_output, out), os.path.join(whafis_output, out_part1))
# 				parse_output_part2(os.path.join(whafis_output, out), os.path.join(whafis_output, out_part2))


# run_whafis_dir("Sonoma/May_2013_SONOMA/whafis/input_files/")
