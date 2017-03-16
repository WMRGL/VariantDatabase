from pysam import VariantFile
import hashlib

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

			if chrom[:3] != 'chr':

				print chrom

				return [False, 'Incorrect chromosome']

	except:

		return [False, 'Could not open file']


	try:

		sample_vcf = rec.samples[sample]

	except:

		return [False, 'Sample name does not match file']


	return [True, 'Success']



def create_master_list(file,sample):

	bcf_in = VariantFile(file)

	master_list =[]

	for rec in bcf_in.fetch():

		my_dict = {}

		sample_vcf = rec.samples[sample]

		my_dict['genotype'] = sample_vcf['GT']

		my_dict['pos'] = rec.pos

		my_dict['chrom'] = rec.chrom

		my_dict['reference'] = rec.ref

		my_dict['format'] = rec.format.keys()

		my_dict['alt_alleles'] = rec.alts

		my_dict['quality'] = rec.qual

		chromosome = my_dict['chrom']
		pos = str(my_dict['pos'])
		ref = my_dict['reference']
		alt = my_dict['alt_alleles'][0]

		hash_id = hashlib.sha256(chromosome+pos+ref+alt).hexdigest()

		my_dict['hash_id'] = hash_id


		for key in rec.info.keys():

			new_key = key.replace('.', '_')

			my_dict[new_key] = rec.info[key]


		master_list.append(my_dict) 



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


	print create_master_list("merged-sorted.vcf.gz",'205908-3-D17-01112-JH_S3' )