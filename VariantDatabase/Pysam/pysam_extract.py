from pysam import VariantFile


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


		for key in rec.info.keys():

			new_key = key.replace('.', '_')

			my_dict[new_key] = rec.info[key]


		master_list.append(my_dict) 


		#print my_dict['genotype'], my_dict['pos'], my_dict['chrom'],my_dict['reference'], my_dict['alt_alleles'], my_dict['format']

	return master_list


if __name__ == '__main__':


	create_master_list("merged-sorted.vcf.gz",'205908-3-D17-01112-JH_S3' )    