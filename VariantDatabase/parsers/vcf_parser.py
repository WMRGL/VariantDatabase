"""
A series of functions for parsing VEP annotated vcf files.

Typically annotated using the following command:

vep -i input_vcf -o output.vcf --cache --fork 4 --refseq --vcf --flag_pick --exclude_predicted --everything --dont_skip --total_length --offline --fasta fasta_location

Uses Pysam as a VCF parser - see URL below for detail:

http://pysam.readthedocs.io/en/latest/usage.html#working-with-vcf-bcf-formatted-files

"""

from pysam import VariantFile
import hashlib
import re


def get_fields(csq_info_string):

	"""
	This function takes the CSQ info field from the header and breaks it up into a list.

	Input:

	csq_info_string = A string representing the CSQ field from the VCF header e.g. 

	"##INFO=<ID=CSQ,Number=.,Type=String,Description='Consequence annotations from Ensembl VEP. Format: Allele|Consequence|IMPACT|SYMBOL'>"


	Output:

	csq_info_list = A list containing the annoatation titles from the Format : part of the csq_info_string e.g.

	['Allele', 'Consequence', 'IMPACT', 'SYMBOL']


	"""

	csq_info_string = csq_info_string.strip()

	index =  csq_info_string.index('Format:') +8


	csq_info_list = csq_info_string[index:len(csq_info_string)-2].split('|')

	return csq_info_list


def get_variant_csq(variant_csq_string):

	"""

	This function takes the CSQ field for a particular variant and breaks it up into a list.

	Input:

	variant_csq_string = A string containing the csq annotations for a particular sampel within the vcf e.g.

	"A|B|C|D"

	Output:

	A list containing the variant_csq_string split up.

	"""

	return variant_csq_string.split('|')


def create_csq_dict(field_list, variant_csq_list):
	"""
	Combine the csq_info_list from the header and the csq data for a particular variant into a dictionary.

	Input:

	field_list = Output from get_fields()

	variant_csq_list = Output from get_variant_csq()

	Output:

	csq_dict = A dictionary combing the two inputs - field_list items are the keys.

	
	"""

	zipped = zip(field_list, variant_csq_list)

	csq_dict = {}

	for info in zipped:

		csq_dict[info[0]] = info[1]


	return csq_dict



def validate_input(file_path, sample):
	"""
	Validates a vcf file.

	Input:

	file_path = The path to the vcf file

	sample = sample name

	Output:

	list = A list where the first item is either True or False

	"""

	##is it a '.vcf.gz' file
	ending = file_path[-7:]

	if ending != '.vcf.gz':

		return [False, 'Not a .vcf.gz file']

	#now check chromosomes are in right format and that sample is in file
	try:

		bcf_in = VariantFile(file_path)


		for rec in bcf_in.fetch():

			#Check that the chromomes and alts are in correct format - chr1

			chrom = rec.chrom
			alt = rec.alts

			if chrom[:3] != 'chr':

				return [False, 'Incorrect chromosome']

			elif len(alt) >1:

				return [False, 'Too many alts']

	except:

		return [False, 'Could not open file']


	try:

		sample_vcf = rec.samples[sample]

	except:

		return [False, 'Sample name does not match file']


	return [True, 'Success']



def create_master_list(file,sample):
	"""
	Create a list containing each variant in the vcf.

	Each variant is a dictionary within the list e.g.

	[{variant1:},{variant1:}]

	Each variant dict consists of sub dictionarys for different transcripts e.g.

	{"variant_hash": "xyz", "chr" :1, "pos": 434353, "transcript_data: {"NM_0001": {"consequence": "intron"}, "NM_0002": {"consequence": "splice_site"}} }


	Input:


	file = A path to the vcf file to be loaded/

	sample = The sample name

	Output:


	master_list = A list containing dictionaries with all the information on all the variants in the vcf.

	"""


	bcf_in = VariantFile(file)



	try:

		csq_fields = str(bcf_in.header.info['CSQ'].record)

		csq_fields = get_fields(csq_fields)


	except:

		raise ValueError('Problem parsing CSQ header in vcf.')

	master_list =[]


	for rec in bcf_in.fetch():

		variant_data_dict = {}

		sample_vcf = rec.samples[sample]

		genotype = sample_vcf['GT']


		if sample_vcf.phased == True:

			variant_data_dict['genotype'] = "|".join(str(x) for x in genotype )

		else:

			variant_data_dict['genotype'] = "/".join(str(x) for x in genotype )


		variant_data_dict['pos'] = rec.pos

		variant_data_dict['chrom'] = rec.chrom

		variant_data_dict['reference'] = rec.ref

		variant_data_dict['format'] = rec.format.keys()

		variant_data_dict['alt_alleles'] = rec.alts

		variant_data_dict['quality'] = rec.qual

		filter_status = rec.filter

		if len(filter_status.keys()) == 0:

			variant_data_dict['filter_status'] = "."

		else:
			variant_data_dict['filter_status'] =  ";".join(filter_status.keys())


		variant_data_dict['allele_depth'] = ":".join(str(x) for x in sample_vcf['AD'])

		chromosome = variant_data_dict['chrom']
		pos = str(variant_data_dict['pos'])
		ref = variant_data_dict['reference']
		alt = variant_data_dict['alt_alleles'][0]

		hash_id = hashlib.sha256(chromosome+" "+pos+" "+ref+" "+alt).hexdigest()

		variant_data_dict['hash_id'] = hash_id

		
		for key in rec.info.keys():

			new_key = key.replace('.', '_')

			if key == 'CSQ':

				csq_data = rec.info['CSQ']

				#print csq_data

				all_transcript__dict ={}

				for transcript in csq_data:

					transcript_data = get_variant_csq(transcript)

					transcript_dict =  create_csq_dict(csq_fields, transcript_data)
					
					transcript_name = transcript_dict['Feature']

					all_transcript__dict[transcript_name] = transcript_dict

				variant_data_dict['transcript_data'] = all_transcript__dict


			else:

				variant_data_dict[new_key] = rec.info[key]


		master_list.append(variant_data_dict)

	return master_list


def get_canonical_transcript(transcript_data):
	"""
	Returns the transcript with where the 'PICK' flag is set to 1

	Note - Used by create_master_list_canonical()

	"""

	for transcript in transcript_data:

		if transcript_data[transcript]['PICK'] == '1':

			return transcript_data[transcript]


	return transcript_data[0]


def get_variant_genes(transcript_data):
	"""
	Returns a string containing all the genes names for a variant.

	Input:

	transcript_data = The dictionary containing the transcript_data.

	Output:

	A string of all the genes in the vcf seperated by a comma.


	"""


	genes =[]

	for transcript in transcript_data:

		gene_name = transcript_data[transcript]['SYMBOL']

		if gene_name != "":

			genes.append(gene_name)


	genes = list(set(genes))

	return ", ".join(genes)

def get_variant_genes_list(transcript_data):
	"""
	Creates a list containing all the genes within a vcf.

	Input:

	transcript_data = The transcript data section of the variant dictionary.


	Output:

	A list of the unique genes in the vcf. List contains tuples with gene name and strand e.g. [(BRCA1, 1), (P53, 1)]


	"""

	genes =[]

	for transcript in transcript_data:

		gene_name = transcript_data[transcript]['SYMBOL']
		strand = transcript_data[transcript]['STRAND']

		if gene_name != "":

			genes.append((gene_name, strand))

	return list(set(genes))

	

def create_master_list_canonical(file,sample):

	"""
	Same purpose as create_master_list() except only gets picked transcript.

	"""

	bcf_in = VariantFile(file)

	try:

		csq_fields = str(bcf_in.header.info['CSQ'].record)

		csq_fields = get_fields(csq_fields)

	except:

		pass

	master_list =[]


	for rec in bcf_in.fetch():

		variant_data_dict = {}

		sample_vcf = rec.samples[sample]

		variant_data_dict['genotype'] = sample_vcf['GT']

		variant_data_dict['pos'] = rec.pos

		variant_data_dict['chrom'] = rec.chrom

		variant_data_dict['reference'] = rec.ref

		variant_data_dict['format'] = rec.format.keys()

		variant_data_dict['alt_alleles'] = rec.alts

		variant_data_dict['quality'] = rec.qual

		chromosome = variant_data_dict['chrom']
		pos = str(variant_data_dict['pos'])
		ref = variant_data_dict['reference']
		alt = variant_data_dict['alt_alleles'][0]

		hash_id = hashlib.sha256(chromosome+" "+pos+" "+ref+" "+alt).hexdigest()

		variant_data_dict['hash_id'] = hash_id

		
		for key in rec.info.keys():

			new_key = key.replace('.', '_')

			if key == 'CSQ':

				csq_data = rec.info['CSQ']

				all_transcript__dict ={}

				for transcript in csq_data:



					transcript_data = get_variant_csq(transcript)

					transcript_dict =  create_csq_dict(csq_fields, transcript_data)

					
					
					transcript_name = transcript_dict['Feature']

					all_transcript__dict[transcript_name] = transcript_dict


				variant_data_dict['transcript_data'] = all_transcript__dict

				variant_data_dict['all_genes'] = get_variant_genes(variant_data_dict['transcript_data'])


				variant_data_dict['transcript_data'] = get_canonical_transcript(   variant_data_dict['transcript_data'])

				for k in variant_data_dict['transcript_data']:

					variant_data_dict[k] = variant_data_dict['transcript_data'][k]

				variant_data_dict['transcript_data'] =""


			else:

				variant_data_dict[new_key] = rec.info[key]


		master_list.append(variant_data_dict)

	return master_list


def vep_annotated(file):
	"""
	Returns True if CSQ annotations are present.

	Input:

	file = path to vcf file

	Output:

	Returns True if CSQ is in header else False.

	"""

	bcf_in = VariantFile(file)

	try:

		bcf_in.header.info['CSQ'].record

		return True

	except:

		return False


def get_rs_number(transcript_data):
	"""
	Gets the rs number of other variant ID contained within the transcript_data dict


	Input:

	transcript_data = The dictionary containing all the transcript_data - see create_master_list()

	Output:

	Either a string of all unique ids or "None" if an error occurs or they cannot be found.
	"""

	rs_numbers = []

	for transcript in transcript_data:

		try:

			rs_number = transcript_data[transcript]['Existing_variation']

		except:

			rs_number = "None"



		if rs_number != "":

			rs_numbers.append(rs_number)

	if rs_number == False:

		return "None"


	return "|".join(list(set(rs_numbers)))


def get_max_af(transcript_data):
	"""
	Simply returns the MAX_AF from the transcript_data dict for a variant - see create_master_list()

	Input:

	transcript_data = The dictionary containing all the transcript_data - see create_master_list()

	Output:

	Float of the max allele frequency

	"""


	for transcript in transcript_data:

		max_af = transcript_data[transcript]['MAX_AF']

		break

	if max_af =="":

		return 0.0

	else:

		return float(max_af)


def get_clin_sig(transcript_data):

	"""
	Simply returns the clinical significance from the transcript_data dict for a variant - see create_master_list()

	Input:

	transcript_data = The dictionary containing all the transcript_data - see create_master_list()

	Output:

	String of the clinical significance

	"""

	for transcript in transcript_data:

		clin_sig = transcript_data[transcript]['CLIN_SIG']

		break

	if clin_sig =="":

		return "None"

	else:

		return clin_sig

def get_allele_frequencies(transcript_data):
	"""
	Gets a list containing all the allelle frequencies for a variant e..g Exac, AF, AA_AF

	Input:

	transcript_data = The dictionary containing all the transcript_data - see create_master_list()

	Output:

	List containing all the allele frequencies as floats.


	Note: If the AF freq is listed as '' i.e. blank we put 0.0 is this correct?


	"""


	for transcript in transcript_data:

		af = transcript_data[transcript]['AF']
		afr_af = transcript_data[transcript]['AFR_AF']
		amr_af = transcript_data[transcript]['AMR_AF']
		eur_af = transcript_data[transcript]['EUR_AF']
		eas_af = transcript_data[transcript]['EAS_AF']
		sas_af = transcript_data[transcript]['SAS_AF']
		exac_af = transcript_data[transcript]['ExAC_AF']
		exac_adj_af = transcript_data[transcript]['ExAC_Adj_AF']
		exac_afr_af = transcript_data[transcript]['ExAC_AFR_AF']
		exac_amr_af = transcript_data[transcript]['ExAC_AMR_AF']
		exac_eas_af = transcript_data[transcript]['ExAC_EAS_AF']
		exac_fin_af = transcript_data[transcript]['ExAC_FIN_AF']
		exac_nfe_af = transcript_data[transcript]['ExAC_NFE_AF']
		exac_oth_af = transcript_data[transcript]['ExAC_OTH_AF']
		exac_sas_af = transcript_data[transcript]['ExAC_SAS_AF']
		esp_aa_af = transcript_data[transcript]['AA_AF']
		esp_ea_af = transcript_data[transcript]['EA_AF']

		break



	allele_freqs = [af,afr_af, amr_af,eur_af,eas_af,sas_af,exac_af,exac_adj_af,exac_afr_af,exac_amr_af,exac_eas_af,exac_fin_af,exac_nfe_af,exac_oth_af,exac_sas_af, esp_aa_af, esp_ea_af]

	new_allele_freqs =[]

	for allele_freq in allele_freqs: # covert to floats - in addition some AFs are formatted 0.1&0.1 for some reason so split them up


		if '&' in allele_freq:

			allele_freq = allele_freq.split('&')

			new_allele_freqs.append(float(max(allele_freq)))


		elif allele_freq == "":

			new_allele_freqs.append(0.0)


		else:

			new_allele_freqs.append(float(allele_freq))


	return new_allele_freqs




def worst_consequence(transcript_data):
	"""
	Looks through all the transcripts for a variant and returns the worst_consequence. e.g. if the consequence in one
	transcript is stop_gained and in the other missense_variant then the function will return stop_gained.

	Input:

	transcript_data = The dictionary containing all the transcript_data - see create_master_list()

	Output:

	vep_consequences[worst] = The worst VEP consequence for that variant. 


	See URL below for more detail:

	https://www.ensembl.org/info/genome/variation/predicted_data.html


	"""

	vep_consequences = ["transcript_ablation", "splice_acceptor_variant", "splice_donor_variant",  "stop_gained", "frameshift_variant",
						"stop_lost", "start_lost", "transcript_amplification", "inframe_insertion", "inframe_deletion", "missense_variant",
						"protein_altering_variant", "splice_region_variant", "incomplete_terminal_codon_variant", "stop_retained_variant",
						"synonymous_variant", "coding_sequence_variant", "mature_miRNA_variant", "5_prime_UTR_variant", "3_prime_UTR_variant",
						"non_coding_transcript_exon_variant", "intron_variant", "NMD_transcript_variant", "non_coding_transcript_variant",
						"upstream_gene_variant", "downstream_gene_variant", "TFBS_ablation", "TFBS_amplification", "TF_binding_site_variant",
						"regulatory_region_ablation", "regulatory_region_amplification", "feature_elongation", "regulatory_region_variant",
						"feature_truncation", "intergenic_variant"]

	consequences = []

	for transcript in transcript_data:

		try:

			consequence = transcript_data[transcript]['Consequence']

		except:

			return "None"


		if consequence != "":

			consequence = consequence.split('&') #split when formatted like regulatory_region_amplification&feature_elongation

			for x in consequence:

				consequences.append(x)


	if consequences == False:

		return "None"


	worst = 1000 #longer than vep_consequences

	for consequence in consequences:

		index = vep_consequences.index(consequence)

		if index < worst:

			worst = index

	return vep_consequences[worst]


def extract_codon_from_hgvs(hgvsp):
	"""
	Given the HGVS for a variant get the codon number. Only works for missense!

	Input:

	hgvsp = A string of the HGVSp

	Output:

	transcript: The transcript

	codon: the codon number

	See - Variant.same_codon_missense() in Models.py


	"""

	try:

		transcript, codon= hgvsp.split(':p.')[0], hgvsp.split(':p.')[1]

	except:

		return False, False

	return transcript, re.findall(r'\d+', codon)[0]


if __name__ == '__main__':


	x = create_master_list("/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/tests/test_files/vep_annotated_test_vcf.vcf",'WS61594_14000835' )

