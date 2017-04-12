from pysam import VariantFile
import hashlib

def get_fields(csq_info_string):

	"""
	This function takes the CSQ info field from the header and breaks it up into a list


	"""

	index =  csq_info_string.index('Format:') +8

	return csq_info_string[index:len(csq_info_string)-3].split('|')


def get_variant_csq(variant_csq_string):

	"""

	This function takes the CSQ field for a particualr variant and breaks it up into a list


	"""

	return variant_csq_string.split('|')


def create_csq_dict(field_list, var_csq):
	"""
	combine the CSQ info fields from the header and the csq data for a particular variant into a dictionary


	"""

	zipped = zip(field_list, var_csq)

	dict = {}

	for info in zipped:

		dict[info[0]] = info[1]


	return dict



def validate_input(file_path, sample):

	##is it a '.vcf.gz' file
	ending = file_path[-7:]

	if ending != '.vcf.gz':

		return [False, 'Not a .vcf.gz file']

		#now check chromosomes are in right format and that sample is in file
	try:

		bcf_in = VariantFile(file_path)


		for rec in bcf_in.fetch():

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

		hash_id = hashlib.sha256(chromosome+pos+ref+alt).hexdigest()

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


			else:

				variant_data_dict[new_key] = rec.info[key]


		master_list.append(variant_data_dict)

	return master_list

def get_genes_in_file(file, sample):

	bcf_in = VariantFile(file)

	gene_list =[]

	for rec in bcf_in.fetch():

		if 'Gene.refGene' in rec.info.keys():

			for gene in rec.info['Gene.refGene']:

				gene_list.append(gene)

		else:

			return 'An error occured - can not find Gene.refGene key in info field'


	return list(set(gene_list))


def get_canonical_transcript(transcript_data):


	for transcript in transcript_data:

		if transcript_data[transcript]['PICK'] == '1':

			return transcript_data[transcript]


	return transcript_data[0]

			
def get_transcript_names(transcript_data):

	transcript_names = []

	for transcript in transcript_data:

		transcript_names.append((transcript,transcript_data[transcript]['SYMBOL'] ))


	return transcript_names



def get_variant_genes(transcript_data):


	genes =[]

	for transcript in transcript_data:

		gene_name = transcript_data[transcript]['SYMBOL']

		if gene_name != "":

			genes.append(gene_name)

		

	genes = list(set(genes))

	return ", ".join(genes)

def get_variant_genes_list(transcript_data):


	genes =[]

	for transcript in transcript_data:

		gene_name = transcript_data[transcript]['SYMBOL']

		if gene_name != "":

			genes.append(gene_name)

	return list(set(genes))

	

def create_master_list_canonical(file,sample):

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

		hash_id = hashlib.sha256(chromosome+pos+ref+alt).hexdigest()

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


	bcf_in = VariantFile(file)

	
	try:

		bcf_in.header.info['CSQ'].record

		return True

	except:

		return False

def get_hgvs(transcript_data):


	hgvs_names = []

	for transcript in transcript_data:

		hgvs = transcript_data[transcript]['HGVSc']

		if hgvs != "":

			hgvs_names.append(hgvs)


	return ", ".join(hgvs_names)


def get_rs_number(transcript_data):

	rs_numbers = []

	for transcript in transcript_data:

		rs_number = transcript_data[transcript]['Existing_variation']

		if rs_number != "":

			rs_numbers.append(rs_number)


	return "".join(list(set(rs_numbers)))

if __name__ == '__main__':



	#  create_master_list("205908-2-D16-48971-MH_S2.unified.annovar.wmrgldb-sorted.vcf.gz",'205908-2-D16-48971-MH_S2' ):

	#print create_master_list("data/out2-sorted.vcf.gz",'WS61594_14000835')

	x = create_master_list("data/out7-sorted.vcf.gz",'WS61594_14000835' )

	print get_canonical_transcript(x[1]['transcript_data'])

	print  get_transcript_names(x[1]['transcript_data'])

	print  get_variant_genes(x[1]['transcript_data'])
