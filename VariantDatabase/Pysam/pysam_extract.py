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

	This funtion takes the CSQ field for a particualr variant and breaks it up into a list


	"""

	variant_csq_string = variant_csq_string.split(',') # if we ahev more than one transcript break it up

	master_list =[]

	for string in variant_csq_string:

		master_list.append(string.split('|'))


	return master_list


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

			if key == 'CSQ':

				csq_data = str(rec.info['CSQ'][0]) #if we ahve annoated with merged then there will be possibley more than 1 annotation for each transcript

				csq_data = get_variant_csq(csq_data)

				csq_dict = create_csq_dict(csq_fields, csq_data[0]) 

				for key in csq_dict:

					new_key = key.replace('.', '_')

					variant_data_dict['vep-'+new_key] = csq_dict[key]

			else:



				new_key = key.replace('.', '_')

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




if __name__ == '__main__':


	for x in create_master_list("data/205908-2-D16-48971-MH_S2.unified.annovar.wmrgldb-sorted.vcf.gz",'205908-2-D16-48971-MH_S2' ):

		print ""

		print x

	

    #  create_master_list("205908-2-D16-48971-MH_S2.unified.annovar.wmrgldb-sorted.vcf.gz",'205908-2-D16-48971-MH_S2' ):

    #create_master_list("data/out2-sorted.vcf.gz",'WS61594_14000835'