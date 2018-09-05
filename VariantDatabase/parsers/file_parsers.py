import csv
import gzip
from interop import py_interop_run_metrics, py_interop_run, py_interop_summary

"""
This file contains parsers for various files that are required by the project.

Contains:

1) Functions for parsing Interop QC data files.
2) Functions for parsing the SampleSheet.csv file.
3) Functions for parsing the gene and exon coverage files.

	"""

def get_read_lane_data(read, lane, summary):
	"""
	Gets the read QC data for an individual read/lane.

	Input:

	read = an integer representing the read number.
	lane = an integer representing the lane.
	summary = The InterOp summary object created by the get_qc_run_summary() function.
	  

	Output:

	qc_data = A dictionary containing the QC data for the read/lane/summary combination that is specified in the input.


	"""

	qc_data ={}

	yield_g = summary.at(read).at(lane).yield_g()
	density = summary.at(read).at(lane).density().mean()
	cluster_count_pf = summary.at(read).at(lane).cluster_count_pf().mean()
	cluster_count = summary.at(read).at(lane).cluster_count().mean()
	phasing = summary.at(read).at(lane).phasing().median()
	prephasing = summary.at(read).at(lane).prephasing().median()
	read_count = summary.at(read).at(lane).reads()
	reads_pf = summary.at(read).at(lane).reads_pf()
	percent_gt_q30 = summary.at(read).at(lane).percent_gt_q30()
	percent_aligned = summary.at(read).at(lane).percent_aligned().mean()
	error_rate = summary.at(read).at(lane).error_rate().mean()
	error_rate_35 = summary.at(read).at(lane).error_rate_35().mean()
	error_rate_50 = summary.at(read).at(lane).error_rate_50().mean()
	error_rate_75 = summary.at(read).at(lane).error_rate_75().mean()
	error_rate_100 = summary.at(read).at(lane).error_rate_100().mean()

	qc_data["read"] = read
	qc_data["lane"] = lane
	qc_data["yield_g"] = yield_g
	qc_data["density"] = density
	qc_data["cluster_count_pf"] = cluster_count_pf
	qc_data["cluster_count"] = cluster_count
	qc_data["phasing"] = phasing
	qc_data["prephasing"] = prephasing
	qc_data["read_count"] = read_count
	qc_data["reads_pf"] = reads_pf
	qc_data["percent_gt_q30"] = percent_gt_q30
	qc_data["percent_aligned"] = percent_aligned
	qc_data["error_rate"] = error_rate
	qc_data["error_rate_35"] = error_rate_35
	qc_data["error_rate_50"] = error_rate_50  
	qc_data["error_rate_75"] = error_rate_75
	qc_data["error_rate_100"] = error_rate_100


	return qc_data

def get_all_qc_data(summary):
	"""
	Gets the qc data for all the read/lane combinations for that particular run.

	Input:

	summmary = The InterOp summary object created by get_qc_run_summary()

	Output:

	data = A list containing the qc_data (created by get_read_lane_data()) for each read/lane combination in the run.

	"""

	data =[]

	lane_count = summary.lane_count()
	read_count = summary.size()

	for read in range(read_count):

		for lane in range(lane_count):

			read_lane_data = get_read_lane_data(read, lane, summary)

			data.append(read_lane_data)

	return data


def get_qc_run_summary(ngs_folder_path):
	"""
	Creates the InterOp summary object.

	Input:

	ngs_folder_path = The Illumina folder containing the QC data. Should contain the following:

		1) InterOp/ containing *MetricsOut.bin files.
		2) RunInfo.xml
		3) RunParameters.xml

	Output:

	Returns False if an error occurs otherwise:

	summary = The InterOp simmary object.



	See https://github.com/Illumina/interop/blob/master/docs/src/Tutorial_01_Intro.ipynb

	"""

	try:

		run_folder = ngs_folder_path

	except:

		return False #An error has occured.

	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)

	run_folder = run_metrics.read(run_folder, valid_to_load)

	summary = py_interop_summary.run_summary()
	py_interop_summary.summarize_run_metrics(run_metrics, summary)

	return summary



def parse_sample_sheet(file):
	"""
	Parses the SampleSheet.csv file and extracts the necessary information.

	This is how the database gets the sample names as well as the work_sheet id and SubSection id.

	Input:

	file = The path to the SampleSheet.csv file. 

	Output:

	Returns a list containing:

		1) sample_list= A list containing information on all the samples e.g. sample_id, sample_plate, index.
		2) subsection = The Subsection name. This is also called the Project Name or Project. e.g. OGT_MPN
		3) worksheet = The worksheet name. This is under experiment name.

	The first item in the list will be False if an error has occured.


	Note: The SubSection should be in the header under project name e.g. MPN_SureSeq_OGT
	Note: The worksheet name should in the header under experiment_name MPN_213837


	See VariantDatabase/test/test_files/sample_sheets/SampleSheet_valid.csv for a correctly formatted sample sheet.


	"""

	#The expected columns.
	expected = ["Sample_ID", "Sample_Name", "Sample_Plate","Sample_Well", "I7_Index_ID",  "index", "Sample_Project"]

	flag =0

	sample_list = []





	with open(file, "rb") as csvfile:


		reader = csv.reader(csvfile, delimiter=",")


		subsection = ""

		worksheet = ""

		for row in reader:

			if row[0] == "Project Name" or row[0] == "Project":

				#If the row is Project_name or Project we set the subsection variable.

				subsection = row[1]

				if subsection =="":

					return [False, "No subsection."]



			if row[0] == "Experiment Name":

				#If the row is Experiment Name  we set the worksheet variable.

				worksheet = row[1]

				if worksheet =="":

					return [False, "No worksheet name."]




			if row[0] == "Sample_ID":

				flag =1 #Set the plag to say we have now got to the samples.

				for index, title in enumerate(expected):

					if title != row[index]:

						return [False, "Columns are incorrect."]

			if flag ==1:

				
				if row[0] == "" and flag ==1: #we have got to the end

					if len(sample_list[1:]) == 0: # empty SampleSheet.csv

						return [False, "There are no samples in the SampleSheet."]

					else:

						return [sample_list[1:], subsection, worksheet]

				else:

					sample_name = row[1]

					sample_name = row[1].replace("_", "-") +'_S'+str(row[0]) #change sample name to same as in files

					sample_name = sample_name.replace(".", "-")

					sample_list.append([row[0], sample_name,row[2],row[3],row[4],row[5],row[6]])


		if len(sample_list[1:]) == 0: # empty SampleSheet.csv

			
			return [False, "There are no samples in the SampleSheet."]

		else:

			return [sample_list[1:], subsection, worksheet]




def get_sample_names(sample_list):

	"""
	Returns a list of the sample_names.

	Input: 

	sample_list = The sample_list returned by parse_sample_sheet(). 

	Output:

	sample_names = A list containing the sample names


	"""

	sample_names =[]

	for sample in sample_list[0]:

		sample_names.append(sample[1])

	return sample_names




def parse_gene_coverage(file_path):
	"""
	Parses the gene coverage file.

	Input:

	file_path = The path to the *.gene-count-data.tsv.gz file. This is contained within the reanalysis_data_run_id folder.

	Output:

	Returns False if an error occurs otherwise:

	master_list = A list containing the coverage data for each gene.



	"""

	master_list =[]

	with gzip.open(file_path, "rb") as f:

		reader = csv.DictReader(f, delimiter="\t")

		if  reader.fieldnames == ["Worksheet", "Sample", "Gene", "100x", "200x", "300x", "400x", "500x", "600x", "Min", "Max", "Mean", "region", "pct>100x", "pct>200x", "pct>300x", "pct>400x", "pct>500x", "pct>600x"]:

			for row in reader:

				master_list.append(row)

			return master_list


		else:

			return False



def parse_exon_coverage(file_path):
	"""
	Parses the exon coverage file.

	Input:

	file_path = The path to the *.exon-count-data.tsv.gz file. This is contained within the reanalysis_data* folder.

	Output:

	Returns False if an error occurs otherwise:

	master_list = A list containing the coverage data for each gene.


	"""

	master_list =[]

	with gzip.open(file_path, "rb") as f:

		reader = csv.DictReader(f, delimiter="\t")

		if reader.fieldnames == ["Worksheet", "Sample", "Gene", "Exon", "Gene_Exon", "100x", "200x", "300x", "400x", "500x", "600x", "Min", "Max", "Mean", "region", "pct>100x", "pct>200x", "pct>300x", "pct>400x", "pct>500x", "pct>600x"]:

			for row in reader:

				master_list.append(row)

			return master_list

		else:

			return False