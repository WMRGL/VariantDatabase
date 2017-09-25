import unittest
import VariantDatabase.parsers.file_parsers as file_parsers

class TestFileParser(unittest.TestCase):

	def test_parse_sample_sheet(self):

		data1 = file_parsers.parse_sample_sheet("VariantDatabase/tests/test_files/sample_sheets/SampleSheet_valid.csv")


		self.assertEqual(data1[0][0],['1', 'Sample_1', 'MPN_213837', 'A01', '25', 'TTACCCTG', ''])
		self.assertEqual(data1[1], "MPN_SureSeq_OGT" )
		self.assertEqual(data1[2], "MPN_213837" )

		data2 = file_parsers.parse_sample_sheet("VariantDatabase/tests/test_files/sample_sheets/SampleSheet_invalid_columns.csv")


		self.assertEqual(data2, [False, 'Columns are incorrect.'])

		data3 = file_parsers.parse_sample_sheet("VariantDatabase/tests/test_files/sample_sheets/SampleSheet_invalid_header.csv")

		self.assertEqual(data3, [False, 'No worksheet name.'])

		data4 = file_parsers.parse_sample_sheet("VariantDatabase/tests/test_files/sample_sheets/SampleSheet_no_samples.csv")

		self.assertEqual(data4, [False, 'There are no samples in the SampleSheet.'])


	def test_get_sample_names(self):


		data1 = data1 = file_parsers.parse_sample_sheet("VariantDatabase/tests/test_files/sample_sheets/SampleSheet_valid.csv")

		names1 = file_parsers.get_sample_names(data1)

		output1 = ['Sample_1', 'Sample_2', 'Sample_3', 'Sample_4', 'Sample_5', 'Sample_6', 'Sample_7', 'Sample_8', 'Sample_9', 'Sample_10', 'Sample_11',
		 'Sample_12', 'Sample_13', 'Sample_14', 'Sample_15', 'Sample_16', 'Sample_17', 'Sample_18', 'Sample_19', 'Sample_20', 'Sample_21', 'Sample_22',
		  'Sample_23', 'Sample_24']


		self.assertEqual(names1, output1 )



class TestCoverageParser(unittest.TestCase):


	def test_parse_gene_coverage(self):

		data1 = file_parsers.parse_gene_coverage("VariantDatabase/tests/test_files/coverage_data/test_sample.gene-count-data.tsv.gz")



		output1 = {'400x': '4746', 'pct>500x': '100', 'Min': '578', 'Worksheet': 'Worksheet1', 'region': '4746', '500x': '4746', 'pct>600x': '99.9', '600x': '4741',
		 'Sample': 'Sample1', 'Max': '1768', 'pct>400x': '100', 'pct>200x': '100', 'pct>100x': '100', '100x': '4746', 'pct>300x': '100', '200x': '4746', 'Gene': 'ASXL1',
		  '300x': '4746', 'Mean': '1365.2'}


		output2 = {'400x': '672', 'pct>500x': '100', 'Min': '746', 'Worksheet': 'Worksheet1', 'region': '672', '500x': '672', 'pct>600x': '100', '600x': '672', 'Sample': 'Sample1',
		'Max': '1519', 'pct>400x': '100', 'pct>200x': '100', 'pct>100x': '100', '100x': '672', 'pct>300x': '100', '200x': '672', 'Gene': 'VHL', '300x': '672', 'Mean': '1171.6'}


		self.assertEqual(data1[0], output1 )
		self.assertEqual(data1[len(data1)-1], output2 )




	def test_parse_exon_coverage(self):

		data1 = file_parsers.parse_exon_coverage("VariantDatabase/tests/test_files/coverage_data/test_sample.exon-count-data.tsv.gz")

		output1 = {'400x': '481', 'pct>500x': '100', 'pct>200x': '100', 'Min': '962', 'Worksheet': 'Worksheet1', 'region': '481', '500x': '481',
		 'pct>600x': '100', '600x': '481', 'Sample': 'Sample1', 'Max': '1506', 'pct>400x': '100', 'Gene_Exon': 'CSF3R_17', 'Exon': '17', 'pct>100x': '100',
		  '100x': '481', 'pct>300x': '100', '200x': '481', 'Gene': 'CSF3R', '300x': '481', 'Mean': '1395.9'}


		output2 = {'400x': '118', 'pct>500x': '100', 'pct>200x': '100', 'Min': '579', 'Worksheet': 'Worksheet1', 'region': '118', '500x': '118', 'pct>600x': '93.2',
		 '600x': '110', 'Sample': 'Sample1', 'Max': '840', 'pct>400x': '100', 'Gene_Exon': 'JAK2_25', 'Exon': '25', 'pct>100x': '100', '100x': '118', 'pct>300x': '100',
		  '200x': '118', 'Gene': 'JAK2', '300x': '118', 'Mean': '737.3'}


		self.assertEqual(data1[0], output1 )
		self.assertEqual(data1[len(data1)-1], output2 )

