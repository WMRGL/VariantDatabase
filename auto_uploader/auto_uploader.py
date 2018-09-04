import yaml
import os, django
import sys
import glob
import re


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
config_dict = parse_auto_config_file("auto_uploader/auto_config.yaml")
sys.path.append(config_dict["project_dir"])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from django.conf import settings
django.setup()
from VariantDatabase.models import Worksheet

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

	files =  glob.glob(directory+"*")

	return files

def parse_data_file_folders(list_files, project, folder_locations):

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

		elif len(finished_file) > 1:

			raise ValueError("There appears to be more than one end of run file - please investigate.")
 

		else:

			file_dict["is_finished"] = False


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

		elif len(data_folder) > 1:

			raise ValueError("There appears to be more than one data folder - please investigate.")
 

		else:

			raise ValueError("There appears to be no data folder - please investigate.")

		#Get the worksheet folder location


		worksheet_folder_locations = folder_locations[0]

		worksheet_folder_query = "{worksheet_folder_locations}{run_number}/*".format(
			worksheet_folder_locations = worksheet_folder_locations,
			run_number = int_run_number
			)

		worksheet_folder =  glob.glob(worksheet_folder_query)


		if len(worksheet_folder) == 1:

			file_dict["worksheet_folder"] = worksheet_folder[0]

		elif len(worksheet_folder) > 1:

			raise ValueError("There appears to be more than one worksheet folder - please investigate.")
 

		else:

			raise ValueError("There appears to be no worksheet folder - please investigate.")


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


wk = get_worksheets_for_project("MPN_SureSeq_OGT")

x = get_data_in_directory(config_dict["projects"]["MPN_SureSeq_OGT"]["to_watch"]["folder1"][1])

y = parse_data_file_folders(x, "MPN_SureSeq_OGT", ["/home/joseph/Documents/variantdb_data/folder1_worksheet/", "/home/joseph/Documents/variantdb_data/folder1_data/"])

z =  annotate_file_dicts(y, config_dict)


print already_in_database(z, wk, config_dict )
