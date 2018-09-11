import yaml
import os
import django
import sys
import glob
import re
import csv
import logging
import datetime
import subprocess


#########################################################################################
# Setup the software environment
#########################################################################################

def parse_auto_config_file(config_file):
	"""
	Parse the yaml file containing the config inforamtion for this program.

	"""

	with open(config_file, 'r') as file:

		config_dict = yaml.load(file)

	file.close()

	return config_dict

# Here we load the django settings so we can access the models etc.
config_dict = parse_auto_config_file("auto_uploader/configs/auto_config.yaml")
sys.path.append(config_dict["project_dir"])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from django.conf import settings
django.setup()
from VariantDatabase.models import Worksheet

# Set up logger

logging.basicConfig(filename=config_dict["log_location"],level=logging.DEBUG)


#########################################################################################
# Main program.
#########################################################################################


def get_worksheets_for_project(project_name):

	"""
	Given a project e.g. MPN_SureSeq_OGT return the worksheets
	associated with this project already in the database

	"""

	worksheets = Worksheet.objects.filter(sub_section__name=project_name)


	worksheets = [worksheet.name for worksheet in worksheets]

	return worksheets


def get_data_in_directory(directory):
	"""
	Given a directory to monitor in the config file get all the subfolders within this.

	"""

	dirs = [directory+d for d in os.listdir(directory)  if os.path.isdir(directory+d)]

	return dirs

def parse_data_file_folders(list_files, project, folder_locations,worksheet_name_prefix ):

	"""
	Take a list of files created by get_data_in_directory() and 

	assemble it into a data structure with the actual data folder,

	the run number 

	"""

	#A list of dictionarys to fold data about the files
	list_of_file_dicts = []


	for file in list_files:

		file_dict = {}

		run_number = file.split("/")[-1]

		file_dict["run_number"] = run_number

		file_dict["file_location"] = file

		file_dict["project"] = project

		file_dict["worksheet_name_prefix"] = worksheet_name_prefix

		file_dict["folder_locations"] = folder_locations

		list_of_file_dicts.append(file_dict)

	return list_of_file_dicts

def annotate_file_dicts(list_of_file_dicts, config_dict):

	"""
	Annotate the file_dicts with information such as:

	- is the pipeline finished?
	- is the pipeline already been annotated with vep?
	- should be pipeline be excluded e.g. does it have exclusion words in the name?

	"""

	list_of_file_dicts_anno = []

	for file_dict in list_of_file_dicts:

		project = file_dict["project"]
		file_location = file_dict["file_location"]
		run_number = file_dict["run_number"]
		intermediate_prefix = config_dict["projects"][project]["intermediate_folder_prefix"]
		is_finished = config_dict["projects"][project]["is_finished"]
		folder_locations  = file_dict["folder_locations"]
		ignore_file_location = config_dict["projects"][project]["ignore_list_location"]

		int_run_number = re.findall('\d+', run_number )[0]

		file_dict["int_run_number"] = int_run_number

		# Is the pipeline finished?

		if config_dict["projects"][project]["intermediate_folder"] == True:

			finished_file_query = "{file_location}/{intermediate_prefix}{run_number}*/{is_finished}".format(
				file_location = file_location,
				run_number = run_number,
				intermediate_prefix = intermediate_prefix,
				is_finished = is_finished
				)

		else:

			finished_file_query = "{file_location}/{is_finished}".format(
				file_location = file_location,
				run_number = run_number,
				intermediate_prefix = intermediate_prefix,
				is_finished = is_finished
				)


		finished_file =  glob.glob(finished_file_query)

		if len(finished_file) == 1:

			file_dict["is_finished"] = True
			file_dict["finished_count_correct"] = True

		elif len(finished_file) > 1:

			logging.warning("{run_number} - more than one finished file found - are there multiple output directories? Not uploaded.".format(
				run_number = file_dict["run_number"]
				))

			file_dict["finished_count_correct"] = False
			file_dict["is_finished"] = True
 

		else:

			file_dict["is_finished"] = False
			file_dict["finished_count_correct"] = False
			logging.warning("{run_number} - No finished file found.".format(
				run_number = file_dict["run_number"]
				))



		#Does the folder path contain any forbidden words that indicate that the pipeline has failed?

		forbidden_words = config_dict["projects"][project]["to_exclude"]

		for word in forbidden_words:

			upper_word = word.lower()

			if upper_word in file_location.lower():

				file_dict["to_exclude"] = True
				break

			else:

				file_dict["to_exclude"] = False

		#Is the run one which has been set to be ignored

		with open(ignore_file_location, "r") as infile:

			for line in infile:

				if run_number == line.strip():

					file_dict['in_ignore_list'] = True
					break

				else:
					file_dict['in_ignore_list'] = False
					
		infile.close()



		#Get the data folder location

		if config_dict["projects"][project]["intermediate_folder"] == True:

			data_file_query = "{file_location}/{intermediate_prefix}{run_number}*/".format(
				file_location = file_location,
				run_number = int_run_number,
				intermediate_prefix = intermediate_prefix,
				)

		else:

			data_file_query = "{file_location}/*".format(
				file_location = file_location,
				run_number = int_run_number,
				intermediate_prefix = intermediate_prefix,
				)


		data_folder =  glob.glob(data_file_query)

		if len(data_folder) == 1:

			file_dict["data_folder"] = data_folder[0]
			file_dict["n_data_folders_correct"] = True

		elif len(data_folder) > 1:

			file_dict["data_folder"] = None
			file_dict["n_data_folders_correct"] = False
			logging.warning("{run_number} - No finished file found.")
 

		else:
			file_dict["data_folder"] = None
			file_dict["n_data_folders_correct"] = False

		#Get the worksheet folder location


		worksheet_folder_locations = folder_locations[0]

		worksheet_folder_query = "{worksheet_folder_locations}{run_number}/*".format(
			worksheet_folder_locations = worksheet_folder_locations,
			run_number = run_number
			)

		worksheet_folder =  glob.glob(worksheet_folder_query)

		if len(worksheet_folder) == 1:

			file_dict["worksheet_folder"] = worksheet_folder[0]
			file_dict["n_worksheet_folders_correct"] = True 

		elif len(worksheet_folder) > 1:
			file_dict["worksheet_folder"] = None
			file_dict["n_worksheet_folders_correct"] = False 
 

		else:
			file_dict["worksheet_folder"] = None
			file_dict["n_worksheet_folders_correct"] = False 

		list_of_file_dicts_anno.append(file_dict)

	return list_of_file_dicts_anno


def already_in_database(list_of_file_dicts_anno, list_of_worksheets_in_db, config_dict):
	"""
	Annotate the list of file_dicts with whether that worksheet is already in the database.

	"""

	list_of_fully_annotated_file_dicts = []

	for file_dict in list_of_file_dicts_anno:

		prefix = config_dict["projects"][file_dict["project"]]["worksheet_name_prefix"]

		worksheet_name = prefix + file_dict["run_number"]

		if worksheet_name in list_of_worksheets_in_db:

			file_dict['already_in_db'] = True

		else:

			file_dict['already_in_db'] = False

		list_of_fully_annotated_file_dicts.append(file_dict)

	return list_of_fully_annotated_file_dicts


def filter_file_dict_list(list_of_fully_annotated_file_dicts):

	"""
	Filter the list of file dicts so we only have ones we want to upload.

	"""

	return list(filter(lambda d: (d["already_in_db"]== False
	 and d["to_exclude"] == False
	 and d["in_ignore_list"] == False
	 and d["is_finished"] == True
	 and d["finished_count_correct"] ==True)
	 and d["n_data_folders_correct"] ==True
	 and d["n_worksheet_folders_correct"] == True, list_of_fully_annotated_file_dicts))

def get_all_to_upload(config_dict):
	"""
	Goes through the config dict and gets all the data we need to put in the database.

	"""

	to_upload = []

	for project in config_dict["projects"]:

		worksheets_in_db = get_worksheets_for_project(project)

		for folder in config_dict["projects"][project]["to_watch"]:

			prefix = config_dict["projects"][project]["worksheet_name_prefix"]

			data_folder = config_dict["projects"][project]["to_watch"][folder]

			data_folders_in_dir = get_data_in_directory(data_folder[1])

			parsed_data_folders = parse_data_file_folders(data_folders_in_dir, project, data_folder,prefix )

			annotated_file_dicts = annotate_file_dicts(parsed_data_folders, config_dict)

			final_annotated_file_dicts = already_in_database(annotated_file_dicts, worksheets_in_db, config_dict)

			# Create CSV log with each file as a row
			keys = final_annotated_file_dicts[0].keys()
			ts = datetime.datetime.now().timestamp()
			file_name = config_dict["csv_log_location"] +  datetime.datetime.fromtimestamp(ts).isoformat() + ".csv"
			file_name = file_name.replace(":", "-")
			with open(file_name, 'wt') as output_file:
				dict_writer = csv.DictWriter(output_file, fieldnames=keys)
				dict_writer.writeheader()
				dict_writer.writerows(annotated_file_dicts)
			output_file.close()

			filtered_file_dicts = filter_file_dict_list(final_annotated_file_dicts)

			to_upload = to_upload + filtered_file_dicts

	return to_upload


def main():

	to_upload = get_all_to_upload(config_dict)

	for file_dict in to_upload:

		#

		command = "snakemake --snakefile auto_uploader/Snakefile -d {data_folder} --config worksheet_name={worksheet_name} --printshellcmds".format(
			data_folder = file_dict["data_folder"],
			worksheet_name = file_dict["worksheet_name_prefix"] + file_dict["int_run_number"]

			)
		print (command)

		sts = subprocess.Popen(command, shell=True).wait()


		command = "python manage.py master_upload --worksheet_dir {worksheet} --output_dir {data} --sample_sheet --run_qc --sample_qc --coverage --variants --subsection_name {project}".format(
			worksheet = file_dict["worksheet_folder"],
			data = file_dict["data_folder"],
			project = file_dict["project"],

			)

		sts = subprocess.Popen(command, shell=True).wait()




main()




