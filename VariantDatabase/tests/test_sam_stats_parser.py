import unittest
import VariantDatabase.parsers.sam_stats_parser as sam_stats_parser

class SamStatsParser(unittest.TestCase):

	def test_get_sam_stats(self):

		data = sam_stats_parser.get_sam_stats("sample1", "VariantDatabase/tests/test_files/stats/sample1_QC_stats.zip")

		output = {'reads properly paired': '870650', 'bases mapped': '122224608', 'outward oriented pairs': '30280', 'mismatches': '370862',
		'is sorted': '1', 'bases mapped (cigar)': '117336090', 'sequences': '876351', 'maximum length': '150', 'reads MQ0': '18060', 'bases duplicated': '0',
		'insert size average': '196.4', 'non-primary alignments': '1391', 'average quality': '36.9', 'insert size standard deviation': '52.8', 'reads mapped and paired': '876104',
		'reads paired': '876351', '1st fragments': '438254', 'reads QC failed': '0', 'last fragments': '438097', 'total length': '122241709', 'reads duplicated': '0', 'raw total sequences': '876351',
		'pairs with other orientation': '127', 'average length': '139', 'bases trimmed': '0', 'reads mapped': '876212', 'filtered sequences': '0', 'inward oriented pairs': '327679', 'error rate': '0.003160682',
		'pairs on different chromosomes': '1361', 'reads unmapped': '139'}

		self.assertEqual(data, output)
