"""
Tests for parsers/vcf_parser.py

"""
import unittest
import VariantDatabase.parsers.vcf_parser as vcf_parser

class TestVcfParser(unittest.TestCase):


	def test_get_fields(self):


		csq_input1 = "##INFO=<ID=CSQ,Number=.,Type=String,Description='Consequence annotations from Ensembl VEP. Format: Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|PICK|VARIANT_CLASS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|REFSEQ_MATCH|GENE_PHENO|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|AF|AFR_AF|AMR_AF|EAS_AF|EUR_AF|SAS_AF|AA_AF|EA_AF|ExAC_AF|ExAC_Adj_AF|ExAC_AFR_AF|ExAC_AMR_AF|ExAC_EAS_AF|ExAC_FIN_AF|ExAC_NFE_AF|ExAC_OTH_AF|ExAC_SAS_AF|MAX_AF|MAX_AF_POPS|CLIN_SIG|SOMATIC|PHENO|PUBMED|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE'>"
		csq_output1 = ['Allele', 'Consequence', 'IMPACT', 'SYMBOL', 'Gene', 'Feature_type', 'Feature', 'BIOTYPE', 'EXON', 'INTRON', 'HGVSc', 'HGVSp', 'cDNA_position', 'CDS_position', 'Protein_position', 'Amino_acids', 'Codons', 'Existing_variation', 'DISTANCE', 'STRAND', 'FLAGS', 'PICK', 'VARIANT_CLASS', 'SYMBOL_SOURCE', 'HGNC_ID', 'CANONICAL', 'TSL', 'APPRIS', 'CCDS', 'ENSP', 'SWISSPROT', 'TREMBL', 'UNIPARC', 'REFSEQ_MATCH', 'GENE_PHENO', 'SIFT', 'PolyPhen', 'DOMAINS', 'HGVS_OFFSET', 'AF', 'AFR_AF', 'AMR_AF', 'EAS_AF', 'EUR_AF', 'SAS_AF', 'AA_AF', 'EA_AF', 'ExAC_AF', 'ExAC_Adj_AF', 'ExAC_AFR_AF', 'ExAC_AMR_AF', 'ExAC_EAS_AF', 'ExAC_FIN_AF', 'ExAC_NFE_AF', 'ExAC_OTH_AF', 'ExAC_SAS_AF', 'MAX_AF', 'MAX_AF_POPS', 'CLIN_SIG', 'SOMATIC', 'PHENO', 'PUBMED', 'MOTIF_NAME', 'MOTIF_POS', 'HIGH_INF_POS', 'MOTIF_SCORE_CHANGE']


		csq_input2 = "##INFO=<ID=CSQ,Number=.,Type=String,Description='Consequence annotations from Ensembl VEP. Format: Allele|Consequence|IMPACT|SYMBOL'>"
		csq_output2 = ['Allele', 'Consequence', 'IMPACT', 'SYMBOL']


		csq_input3 = "##INFO=<ID=CSQ,Number=.,Type=String,Description='Consequence VEP. Format: Allele|Consequence|IMPACT|SYMBOL'>"
		csq_output3 = ['Allele', 'Consequence', 'IMPACT', 'SYMBOL']

		csq_input4 = "##INFO=<ID=CSQ,Number=.,Type=String,Description='Consequence VEP. Format: Allele|Consequence|IMPACT|SYMBOL'>      "
		csq_output4 = ['Allele', 'Consequence', 'IMPACT', 'SYMBOL']



		csq_input5 = "##INFO=<ID=CSQ,Number=.,Type=String,Description='Consequence VEP. Format:Allele|Consequence|IMPACT|SYMBOL'>      "
		csq_output5 = ['Allele', 'Consequence', 'IMPACT', 'SYMBOL']


		self.assertEqual(vcf_parser.get_fields(csq_input1), csq_output1)
		self.assertEqual(vcf_parser.get_fields(csq_input2), csq_output2)
		self.assertEqual(vcf_parser.get_fields(csq_input3), csq_output3)
		self.assertEqual(vcf_parser.get_fields(csq_input4), csq_output4)
		self.assertNotEqual(vcf_parser.get_fields(csq_input5), csq_output5)



	def test_get_variant_csq(self):

		csq_input1 = "A|B|C|D"
		csq_output1 =["A", "B", "C", "D"]

		csq_input2 = "A|B|C|D|@|$|gene|'hi'|8,6"
		csq_output2 =["A", "B", "C", "D", "@", "$", "gene", "'hi'", "8,6"]


		csq_input3 ="||||||"
		csq_output3 = ['', '', '', '', '', '', '']

		self.assertEqual(vcf_parser.get_variant_csq(csq_input1), csq_output1)
		self.assertEqual(vcf_parser.get_variant_csq(csq_input2), csq_output2)
		self.assertEqual(vcf_parser.get_variant_csq(csq_input3), csq_output3)


	def test_create_csq_dict(self):

		field_list1 = ['Allele', 'Consequence', 'IMPACT', 'SYMBOL']
		variant_csq_list1 = ['A', 'B', 'C', 'D']

		csq_dict1= {'Allele': 'A', 'Consequence': 'B', 'IMPACT':'C','SYMBOL':'D' } 

		self.assertEqual(vcf_parser.create_csq_dict(field_list1,variant_csq_list1),csq_dict1)


	def test_validate_input(self):

		input1 = vcf_parser.validate_input('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf.gz', 'WS61594_14000835')

		input2 = vcf_parser.validate_input('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input3 = vcf_parser.validate_input('VariantDatabase/tests/test_files/vcfs/vep.vcf.gz', 'WS61594_14000835')

		input4 = vcf_parser.validate_input('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf.gz', 'incorrect_sample_name')

		self.assertEqual(input1[0], True)
		self.assertEqual(input2[0], False)
		self.assertEqual(input3[0], False)


	def test_create_master_list(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')


		self.assertEqual(master_list[0]['reference'], 'C')
		self.assertEqual(master_list[0]['genotype'], '0/1')
		self.assertEqual(master_list[0]['alt_alleles'], ('A',))
		self.assertEqual(master_list[0]['filter_status'], '.')
		self.assertEqual(master_list[0]['hash_id'], 'd360384c2a1df84a02bc9b2f19ee584ed837d600081450beab17762532ce18ba')
		self.assertEqual(master_list[0]['allele_depth'], '124:124')
		self.assertEqual(master_list[0]['transcript_data']['NM_002617.3'], {'MAX_AF_POPS': 'ExAC_FIN', 'TSL': '', 'APPRIS': '', 'ExAC_AF': '0.392', 'ExAC_NFE_AF': '0.4469', 'AMR_AF': '0.4539', 'SYMBOL': 'PEX10', 'AFR_AF': '0.2859', 'ExAC_EAS_AF': '0.2793', 'Feature': 'NM_002617.3', 'Codons': '', 'MOTIF_NAME': '', 'DOMAINS': '', 'SIFT': '', 'VARIANT_CLASS': 'SNV', 'EA_AF': '0.4278', 'CDS_position': '', 'CCDS': '', 'Allele': 'A', 'PolyPhen': '', 'AA_AF': '0.2942', 'MOTIF_SCORE_CHANGE': '', 'IMPACT': 'MODIFIER', 'HGVSp': '', 'ENSP': 'NP_002608.1', 'MAX_AF': '0.5536', 'INTRON': '4/5', 'ExAC_AFR_AF': '0.3196', 'Existing_variation': 'rs3795269', 'HGVSc': 'NM_002617.3:c.776+33G>T', 'MOTIF_POS': '', 'HIGH_INF_POS': '', 'ExAC_FIN_AF': '0.5536', 'PICK': '', 'GENE_PHENO': '', 'ExAC_SAS_AF': '0.3747', 'UNIPARC': '', 'cDNA_position': '', 'PUBMED': '', 'EAS_AF': '0.253', 'Feature_type': 'Transcript', 'AF': '0.3391', 'ExAC_Adj_AF': '0.4176', 'ExAC_OTH_AF': '0.4538', 'HGNC_ID': '', 'SAS_AF': '0.3272', 'SWISSPROT': '', 'FLAGS': '', 'Consequence': 'intron_variant', 'Protein_position': '', 'Gene': '5192', 'STRAND': '-1', 'EUR_AF': '0.4274', 'DISTANCE': '', 'PHENO': '', 'SYMBOL_SOURCE': '', 'Amino_acids': '', 'ExAC_AMR_AF': '0.43', 'TREMBL': '', 'CLIN_SIG': '', 'REFSEQ_MATCH': '', 'HGVS_OFFSET': '', 'BIOTYPE': 'protein_coding', 'EXON': '', 'SOMATIC': '', 'CANONICAL': ''})
		self.assertEqual(len(master_list), 281) 


	def test_get_variant_genes_list(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input1=master_list[0]['transcript_data']

		output1= [('PEX10', '-1'), ('RER1', '1')]

		input2 = {'NM_002617.3': {'SYMBOL': 'gene1', 'STRAND':'1'}, 'NM_002614.3': {'SYMBOL': 'gene2','STRAND':'1'}}

		output2 = [('gene1', '1'), ('gene2', '1')]

		input3 = {'NM_002617.3': {'SYMBOL': '', 'STRAND':'1'}, 'NM_002614.3': {'SYMBOL': 'gene2','STRAND':'1'}}

		output3 = [('gene2','1')]

		self.assertEqual(vcf_parser.get_variant_genes_list(input1), output1)
		self.assertEqual(set(vcf_parser.get_variant_genes_list(input2)), set(output2))
		self.assertEqual(set(vcf_parser.get_variant_genes_list(input3)), set(output3))


	def test_vep_annotated(self):

		input1 = vcf_parser.vep_annotated('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf.gz')


		self.assertEqual(input1, True)


	def test_get_rs_number(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input1 = master_list[0]['transcript_data']

		output1 = 'rs3795269'

		input2 = {'NM_002617.3': {'Existing_variation': 'gene1'}, 'NM_002614.3': {'Existing_variation': 'gene2'}}

		output2 = 'gene1|gene2'

		input3 = {'NM_002617.3': {'Existing_variation': ''}, 'NM_002614.3': {'Existing_variation': 'gene2'}}

		output3 = 'gene2'

		input4 = {'NM_002617.3': {'gene1': ''}, 'NM_002614.3': {'test': 'gene2'}}

		output4 = "None"


		self.assertEqual(vcf_parser.get_rs_number(input1), output1)
		self.assertEqual(vcf_parser.get_rs_number(input2), output2)
		self.assertEqual(vcf_parser.get_rs_number(input3), output3)
		self.assertEqual(vcf_parser.get_rs_number(input4), output4)


	def test_get_max_af(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input1 = master_list[0]['transcript_data']

		input2 = {'NM_002617.3': {'MAX_AF': '0.01'}}

		input3 = {'NM_002617.3': {'MAX_AF': ''}}

		input4 = {'NM_002617.3': {'NO_MAX_AF': ''}}

		self.assertEqual(vcf_parser.get_max_af(input1) , 0.5536)
		self.assertEqual(vcf_parser.get_max_af(input2) , 0.01)
		self.assertEqual(vcf_parser.get_max_af(input3) , 0.0)
		self.assertRaises(KeyError, vcf_parser.get_max_af, input4)


	def test_get_clin_sig(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input1 = master_list[0]['transcript_data']

		input2 = {'NM_002617.3': {'CLIN_SIG': 'test2'}}

		input3 = {'NM_002617.3': {'CLIN_SIG': 'test3'}}

		input4 = {'NM_002617.3': {'NO_CLIN_SIG': 'test4'}}

		input5 = master_list[5]['transcript_data']

		self.assertEqual(vcf_parser.get_clin_sig(input1) , 'None')
		self.assertEqual(vcf_parser.get_clin_sig(input2) ,'test2')
		self.assertEqual(vcf_parser.get_clin_sig(input3) , 'test3')
		self.assertRaises(KeyError, vcf_parser.get_clin_sig, input4)
		self.assertEqual(vcf_parser.get_clin_sig(input5) , 'benign')


	def test_get_allele_frequencies(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input1 = master_list[0]['transcript_data']

		output1 = [0.3391, 0.2859, 0.4539, 0.4274, 0.253, 0.3272, 0.392, 0.4176, 0.3196, 0.43, 0.2793, 0.5536, 0.4469, 0.4538, 0.3747, 0.2942, 0.4278]

		self.assertEqual(vcf_parser.get_allele_frequencies(input1) , output1)


	def test_worst_consequence(self):

		master_list = vcf_parser.create_master_list('VariantDatabase/tests/test_files/vcfs/vep_annotated_test_vcf.vcf', 'WS61594_14000835')

		input1 = master_list[0]['transcript_data']
		input2 = {'NM_002617.3': {'Consequence': 'transcript_ablation'}, 'NM_002614.3': {'Consequence': 'splice_acceptor_variant'}}
		input3 = {'NM_002617.3': {'Consequence': 'transcript_ablation'}, 'NM_002614.3': {'Consequence': 'splice_acceptor_variant&splice_donor_variant'},  'NM_002684.3': {'Consequence': 'inframe_deletion'}}
		input4 = {'NM_002617.3': {'Consequence': 'stop_gained'}, 'NM_002614.3': {'Consequence': 'splice_acceptor_variant'}}
		input5 = {'NM_002617.3': {'Consequence': 'frameshift_variant'}, 'NM_002614.3': {'Consequence': 'splice_acceptor_variant'}}
		input6 = {'NM_002617.3': {'Consequence': 'intron_variant&missense_variant&non_coding_transcript_variant'}, 'NM_002614.3': {'Consequence': 'frameshift_variant'}}
		input7 = {'NM_002617.3': {'Consequence': 'transcript_amplification'}, 'NM_002614.3': {'Consequence': 'inframe_insertion'}}
		input8 = {'NM_002617.3': {'Consequence': 'inframe_insertion'}, 'NM_002614.3': {'Consequence': 'incomplete_terminal_codon_variant&incomplete_terminal_codon_variant'}}
		input9 = {'NM_002617.3': {'Consequence': 'feature_elongation'}, 'NM_002614.3': {'Consequence': 'intergenic_variant'}}
		input10 = {'NM_002617.3': {'Consequence': 'feature_truncation'}, 'NM_002614.3': {'Consequence': 'intergenic_variant'}}
		input11 = {'NM_002617.3': {'Consequence': 'stop_lost'}, 'NM_002614.3': {'Consequence': 'stop_lost'}}



		self.assertEqual(vcf_parser.worst_consequence(input1) , 'intron_variant')
		self.assertEqual(vcf_parser.worst_consequence(input2) , 'transcript_ablation')
		self.assertEqual(vcf_parser.worst_consequence(input3) , 'transcript_ablation')
		self.assertEqual(vcf_parser.worst_consequence(input4) , 'splice_acceptor_variant')
		self.assertEqual(vcf_parser.worst_consequence(input5) , 'splice_acceptor_variant')
		self.assertEqual(vcf_parser.worst_consequence(input6) , 'frameshift_variant')
		self.assertEqual(vcf_parser.worst_consequence(input7) , 'transcript_amplification')
		self.assertEqual(vcf_parser.worst_consequence(input8) , 'inframe_insertion')
		self.assertEqual(vcf_parser.worst_consequence(input9) , 'feature_elongation')
		self.assertEqual(vcf_parser.worst_consequence(input10) , 'feature_truncation')
		self.assertEqual(vcf_parser.worst_consequence(input11) , 'stop_lost')


	def test_extract_codon_from_hgvs(self):

		input1 = "ENSCAFP00000040171.1:p.Thr92Asn"

		self.assertEqual(vcf_parser.extract_codon_from_hgvs(input1) , ('ENSCAFP00000040171.1', '92'))




if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
	unittest.TextTestRunner(verbosity=3).run(suite)