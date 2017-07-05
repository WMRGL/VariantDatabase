import csv


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