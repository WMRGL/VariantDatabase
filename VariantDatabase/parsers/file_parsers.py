import csv
import gzip


def parse_sample_sheet(file):

	expected = ['Sample_ID', 'Sample_Name', 'Sample_Plate','Sample_Well', 'I7_Index_ID',  'index', 'Sample_Project']

	flag =0

	sample_list = []

	reader = csv.reader(file, delimiter=',')

	subsection = ""

	for row in reader:

		if row[0] == 'Project Name' or row[0] == 'Project':

			subsection = row[1]

		if row[0] == 'Sample_ID':



			flag =1

			for index, title in enumerate(expected):

				if title != row[index]:

					return False

		if flag ==1:

			
			if row[0] == "" and flag ==1:

				return sample_list[1:], subsection

			else:

				sample_list.append([row[0], row[1],row[2],row[3],row[4],row[5],row[6]])

	return sample_list[1:], subsection 


def parse_gene_coverage(file_path):

	master_list =[]

	with gzip.open(file_path, 'rb') as f:

		reader = csv.DictReader(f, delimiter='\t')

		if  reader.fieldnames == ['Worksheet', 'Sample', 'Gene', '100x', '200x', '300x', '400x', '500x', '600x', 'Min', 'Max', 'Mean', 'region', 'pct>100x', 'pct>200x', 'pct>300x', 'pct>400x', 'pct>500x', 'pct>600x']:

			for row in reader:

				master_list.append(row)

			return master_list

		else:

			return False



def parse_exon_coverage(file_path):

	master_list =[]

	with gzip.open(file_path, 'rb') as f:

		reader = csv.DictReader(f, delimiter='\t')

		if reader.fieldnames == ['Worksheet', 'Sample', 'Gene', 'Exon', 'Gene_Exon', '100x', '200x', '300x', '400x', '500x', '600x', 'Min', 'Max', 'Mean', 'region', 'pct>100x', 'pct>200x', 'pct>300x', 'pct>400x', 'pct>500x', 'pct>600x']:

			for row in reader:

				master_list.append(row)

			return master_list

		else:

			return False