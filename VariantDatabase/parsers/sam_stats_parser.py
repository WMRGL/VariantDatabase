import csv
import zipfile
"""
This file contains functions for parsing the SamStats files and images.

These files are typically stored within the reanalysis_data folder within the pipeline output directory

The QC Data imported is the sam stats data created by the samtools stats and plot-bamstats programs.


"""

def get_sam_stats(sample_name, stats_location):
	"""
	Get the data from the sam stats file e.g. D16-41708_S15.bwa.drm.realn.sorted.bam.stats

	Returns a dictionary containing the relevent summary information.

	Needs sample name and the folder path containing the data.


	Input: 


	sample_name = The name of the sample to be processed.

	stats_location = The path to the zip file containing the .stats file.


	Output:

	sample_qc_dict = A dictionary containing the sample qc data.


	"""

	inner_folder = stats_location.split("/")[-1][:-4] +"/" #get the inner folder name of the zip file

	file_name = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats" #Find the file.

	sample_qc_dict ={}

	

	with zipfile.ZipFile(stats_location) as myzip:

		with myzip.open(file_name, "r") as csvfile:

			reader = csv.reader(csvfile, delimiter="\t")

			for row in reader:

				if row[0] == "SN":

					sample_qc_dict[row[1][:-1]] = row[2]


		csvfile.close()

	myzip.close()



	if len(sample_qc_dict) ==0:

		return False

	else:

		return sample_qc_dict




	

def get_sam_images(sample_name, stats_location):
	"""
	Returns a dictionary of the file locations. Dict Key is the image_type.

	Input: 


	sample_name = The name of the sample to be processed.

	stats_location = The path to the zip file containing the .stats file.


	Output:

	image_name_dict = A dictionary containing the sample qc data.


	"""

	inner_folder = stats_location.split("/")[-1][:-4] +"/" #get the inner folder name of the zip file


	image_name_dict ={}

	image_name_dict["acgt_cycles_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-acgt-cycles.png"
	image_name_dict["coverage_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-coverage.png"
	image_name_dict["gc_content_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-gc-content.png"
	image_name_dict["gc_depth_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-gc-depth.png"
	image_name_dict["indel_cycles_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-indel-cycles.png"
	image_name_dict["indel_dist_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-indel-dist.png"
	image_name_dict["insert_size_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-insert-size.png"
	image_name_dict["quality_cycle_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-quals.png"
	image_name_dict["quality_cycle_read_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-quals2.png"
	image_name_dict["quality_cycle_read_freq_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-quals3.png"
	image_name_dict["quality_heatmap_image"] = inner_folder + sample_name+".bwa.drm.realn.sorted.bam.stats-quals-hm.png"


	return image_name_dict














"""

def get_sam_images(sample_name, folder):
	""""""
	This functions returns the fiel paths of the image files needed for import.

	Returns a dictionary containing all the file paths.

	""""""

	image_name_dict ={}

	if folder[len(folder)-1] != "/":

		folder = folder + "/"


	image_name_dict["acgt_cycles_image"] = glob.glob(folder+sample_name+"*"+"stats-acgt-cycles.png")
	image_name_dict["coverage_image"] = glob.glob(folder+sample_name+"*"+"stats-coverage.png")
	image_name_dict["gc_content_image"] = glob.glob(folder+sample_name+"*"+"stats-gc-content.png")
	image_name_dict["gc_depth_image"] = glob.glob(folder+sample_name+"*"+"stats-gc-depth.png")
	image_name_dict["indel_cycles_image"] = glob.glob(folder+sample_name+"*"+"stats-indel-cycles.png")
	image_name_dict["indel_dist_image"] = glob.glob(folder+sample_name+"*"+"stats-indel-dist.png")
	image_name_dict["insert_size_image"] = glob.glob(folder+sample_name+"*"+"stats-insert-size.png")
	image_name_dict["quality_cycle_image"] = glob.glob(folder+sample_name+"*"+"stats-quals.png")
	image_name_dict["quality_cycle_read_image"] = glob.glob(folder+sample_name+"*"+"stats-quals2.png")
	image_name_dict["quality_cycle_read_freq_image"] = glob.glob(folder+sample_name+"*"+"stats-quals3.png")
	image_name_dict["quality_heatmap_image"] = glob.glob(folder+sample_name+"*"+"stats-quals-hm.png")

	for key in image_name_dict: # Check we"ve only found a single image for each key

		if len(image_name_dict[key]) == 1:

			image_name_dict[key] =image_name_dict[key][0]

		else:

			return False


	return image_name_dict

"""