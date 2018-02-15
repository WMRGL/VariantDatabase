"""
master_upload.py aims to upload a full worksheet of samples including:

	-the sample_sheet
	-run_qc,
	-sample_qc,
	-coverage_data
	 -vcfs

"""

from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
from django.contrib.auth.models import User
import hashlib
import imp
from django.db import transaction
from django.utils import timezone
import glob
import zipfile
from django.core.files import File

import VariantDatabase.parsers.vcf_parser as vcf_parser
import VariantDatabase.parsers.file_parsers as file_parsers
import VariantDatabase.parsers.sam_stats_parser as sam_stats_parser
import VariantDatabase.utils.variant_utilities as variant_utilities


def process_sample_sheet(worksheet_dir):
	"""
	Calls file_parsers.parse_sample_sheet()

	Input:

	worksheet_dir = The directory containing the SampleSheet.csv


	Output:

	sample_sheet_data = Output from the file_parsers.parse_sample_sheet() function

	"""

	sample_sheet_path = worksheet_dir+ "/SampleSheet.csv"

	sample_sheet_data = file_parsers.parse_sample_sheet(sample_sheet_path)

	if sample_sheet_data[0] == False:

		raise CommandError("Error: " + sample_sheet_data[1] )


	else:


		return sample_sheet_data


def upload_sample_sheet(sample_sheet_data):
	"""
	Handles the Uploading of the SampleSheet data.


	Input:

	sample_sheet_data = The output of the process_sample_sheet() function.


	Output:

	None: uploads data and returns.


	N.B - Not all sample information is uploaded at this stage e.g. QC, vcf file_path
	N.B - At the moment it assumes all samples are in the same project \
		  i.e. the subsection is found in the header. This may need to change.

	"""

	sample_data = sample_sheet_data[0]

	subsection_name = sample_sheet_data[1]

	worksheet_name = sample_sheet_data[2]

	#First get the SubSection object

	try:

		subsection = SubSection.objects.get(name="MPN_SureSeq_OGT") #change after mass upload!
		print "Found SubSection: name = " + subsection.name

	except SubSection.DoesNotExist:

		error = "Cannot find SubSection. Either edit SampleSheet.csv"  \
				"or create a new SubSection via Django Admin."

		raise CommandError(error)

	#Next get the Worksheet object


	worksheet = Worksheet.objects.filter(name=worksheet_name)

	if worksheet.exists():

		raise CommandError("This worksheet already exists.")

	else:

		worksheet = Worksheet(name= worksheet_name, sub_section=subsection,comment="NA", status="1")
		worksheet.save()

	#Now go through each list in sample_data and create a new SampleObject


	for sample in sample_data:


		sample_name = sample[1]
		sample_plate = sample[2]
		sample_well = sample[3]
		sample_i7_index = sample[4]
		sample_index = sample[5]
		panel = sample[6]


		new_sample = Sample.objects.filter(name=sample_name)

		if new_sample.exists():

			raise CommandError("Sample " + sample_name + " already exists!")

		else:

	
			#get or create worksheet object - based on Sample_Plate column

			if panel == "":

				panel = "None"

			try:

				panel = Panel.objects.get(name= panel)

			except:

				raise CommandError("Could not find sample gene filter.")


			new_sample = Sample( name= sample_name,
								 worksheet=worksheet,
								 visible=True,status="1",
								 sample_well=sample_well,
								 i7_index_id=sample_i7_index,
								 index=sample_index,
								 panel=panel )

			new_sample.save()


	return None




def upload_run_qc(worksheet_dir, worksheet_name):
	"""
	Handles the uploading of the Run QC. This is the QC located in the InterOp illumina files.

	Input:

	worksheet_dir = Path to the directory containing the run QC data.
	worksheet_name = Unique name of the worksheet.

	Output:

	None: uploads data and returns 


	"""

	#get WorkSheet object and raise error if it does not exist

	try:

		worksheet = Worksheet.objects.get(name=worksheet_name)

	except Worksheet.DoesNotExist:

		raise CommandError("Worksheet " + worksheet_name + " does not exist.")


	#Check if worksheet already has data attached to it


	worksheet_qc = ReadLaneQuality.objects.filter(worksheet=worksheet)

	if worksheet_qc.exists():

		error = "Worksheet " + worksheet_name + " already has QC data attached to it." \
				" To reupload data first delete existing ReadLaneQuality " \
				 "objects associated with the worksheet."


		raise CommandError(error)



	#Upload QC data

	summary = file_parsers.get_qc_run_summary(worksheet_dir)

	qc_data = file_parsers.get_all_qc_data(summary)

	for read_lane in qc_data:

		read = read_lane["read"]
		lane = read_lane["lane"]
		yield_g = read_lane["yield_g"]
		density = read_lane["density"]
		cluster_count_pf = read_lane["cluster_count_pf"]
		cluster_count = read_lane["cluster_count"]
		phasing = read_lane["phasing"]
		prephasing = read_lane["prephasing"]
		read_count = read_lane["read_count"]
		reads_pf = read_lane["reads_pf"]
		percent_gt_q30 = read_lane["percent_gt_q30"]
		percent_aligned = read_lane["percent_aligned"]
		error_rate = read_lane["error_rate"]
		error_rate_35 = read_lane["error_rate_35"]
		error_rate_50 = read_lane["error_rate_50"]
		error_rate_75 = read_lane["error_rate_75"]
		error_rate_100 = read_lane["error_rate_100"]

		new_qc_model = ReadLaneQuality( worksheet=worksheet,
										read=read,
										lane=lane,
										yield_g=yield_g,
										density=density,
										cluster_count_pf=cluster_count_pf,
										cluster_count=cluster_count,
										phasing=phasing,
										prephasing=prephasing,
										read_count=read_count,
										reads_pf=reads_pf,
										percent_gt_q30=percent_gt_q30,
										percent_aligned=percent_aligned,
										error_rate=error_rate,
										error_rate_35=error_rate_35,
										error_rate_75=error_rate_75,
										error_rate_100=error_rate_100)

		new_qc_model.save()


	worksheet.status = "2"

	worksheet.save()


	return None



def upload_sample_qc(output_dir, sample_name):

	"""
	Uploads the sample qc for a specific sample.

	Input:

	output_dir = The directory containing the pipeline output e.g. alignments, beds

	sample_name = A string representing the unique sample_name


	Output:

	None - uploads and returns None

	"""

	#Find sample and raise error if it cannot be found.


	try:

		sample = Sample.objects.get(name = sample_name)

	except Sample.DoesNotExist:


		raise CommandError("Cannot find a sample in the DB with name " + sample_name + ".")


	#get data from archive directory with output directory. \
	#e.g. MPN/213837_v0.3.10/archive_MPN_213837/MPN_213837_QC_stats/


	stats_location = glob.glob(output_dir+ "archive" + "*" + "/"+"*QC_stats.zip")


	if len(stats_location) != 1:

		raise CommandError("An error occured finding the stats file.")

	else:

		stats_location = stats_location[0]


	#Use sam_stats_parser to get the data and image locations

	sample_qc_stats =  sam_stats_parser.get_sam_stats(sample_name, stats_location)


	if sample_qc_stats == False:

		raise CommandError("An error occured when parsing the stats file.")


	image_names =  sam_stats_parser.get_sam_images(sample_name, stats_location)


	#Now we have the sample and the data then let"s update it.

	sample.raw_total_sequences = int(sample_qc_stats["raw total sequences"])
	sample.filtered_sequences = int(sample_qc_stats["filtered sequences"])
	sample.sequences = int(sample_qc_stats["sequences"])
	sample.first_fragments = int(sample_qc_stats["1st fragments"])
	sample.last_fragments = int(sample_qc_stats["last fragments"])
	sample.reads_mapped = int(sample_qc_stats["reads mapped"])
	sample.reads_mapped_and_paired = int(sample_qc_stats["reads mapped and paired"])
	sample.reads_unmapped = int(sample_qc_stats["reads unmapped"])
	sample.reads_properly_paired = int(sample_qc_stats["reads properly paired"])
	sample.reads_paired = int(sample_qc_stats["reads paired"])
	sample.reads_duplicated = int(sample_qc_stats["reads duplicated"])
	sample.reads_MQ0 = int(sample_qc_stats["reads MQ0"])
	sample.reads_QC_failed = int(sample_qc_stats["reads QC failed"])
	sample.non_primary_alignments = int(sample_qc_stats["non-primary alignments"])
	sample.total_length = int(sample_qc_stats["total length"])
	sample.bases_mapped = int(sample_qc_stats["bases mapped"])
	sample.bases_mapped_cigar = int(sample_qc_stats["bases mapped (cigar)"])
	sample.bases_trimmed = int(sample_qc_stats["bases trimmed"])
	sample.bases_duplicated = int(sample_qc_stats["bases duplicated"])
	sample.mismatches = int(sample_qc_stats["mismatches"])
	sample.average_length = int(sample_qc_stats["average length"])
	sample.maximum_length = int(sample_qc_stats["maximum length"])
	sample.average_quality = float(sample_qc_stats["average quality"])
	sample.insert_size_average = float(sample_qc_stats["insert size average"])
	sample.insert_size_standard_deviation = float(sample_qc_stats["insert size standard deviation"])
	sample.inward_oriented_pairs = int(sample_qc_stats["inward oriented pairs"])
	sample.outward_oriented_pairs = int(sample_qc_stats["outward oriented pairs"])
	sample.pairs_with_other_orientation = int(sample_qc_stats["pairs with other orientation"])
	sample.pairs_on_different_chromosomes = int(sample_qc_stats["pairs on different chromosomes"])


	#Now upload image files


	with zipfile.ZipFile(stats_location) as myzip:

		acgt_cycles_image = image_names["acgt_cycles_image"]

		acgt_cycles_image_file = File(myzip.open(acgt_cycles_image, "r"))

		sample.acgt_cycles_image.save(str(sample.pk)+"-acgt_cycles.png", acgt_cycles_image_file)


		coverage_image = image_names["coverage_image"]

		coverage_image_file = File(myzip.open(coverage_image, "r"))

		sample.coverage_image.save(str(sample.pk)+"-coverage_image.png", coverage_image_file)



		gc_content_image = image_names["gc_content_image"]

		gc_content_image_file = File(myzip.open(gc_content_image, "r"))

		sample.gc_content_image.save(str(sample.pk)+"-gc_content_image.png", gc_content_image_file)



		gc_depth_image = image_names["gc_depth_image"]

		gc_depth_image_file = File(myzip.open(gc_depth_image, "r"))

		sample.gc_depth_image.save(str(sample.pk)+"-gc_depth_image.png", gc_depth_image_file)



		indel_cycles_image = image_names["indel_cycles_image"]

		indel_cycles_image_file = File(myzip.open(indel_cycles_image, "r"))

		sample.indel_cycles_image.save(str(sample.pk)+"-indel_cycles_image.png", indel_cycles_image_file)



		indel_dist_image = image_names["indel_dist_image"]

		indel_dist_image_file = File(myzip.open(indel_dist_image, "r"))

		sample.indel_dist_image.save(str(sample.pk)+"-indel_dist_image.png", indel_dist_image_file)	



		insert_size_image = image_names["insert_size_image"]

		insert_size_image_file = File(myzip.open(insert_size_image, "r"))

		sample.insert_size_image.save(str(sample.pk)+"-insert_size_image.png", insert_size_image_file)	


		quality_cycle_image = image_names["quality_cycle_image"]

		quality_cycle_image_file = File(myzip.open(quality_cycle_image, "r"))

		sample.quality_cycle_image.save(str(sample.pk)+"-quality_cycle_image.png", quality_cycle_image_file)		



		quality_cycle_read_image = image_names["quality_cycle_read_image"]

		quality_cycle_read_image_file = File(myzip.open(quality_cycle_read_image, "r"))

		sample.quality_cycle_read_image.save(str(sample.pk)+"-quality_cycle_read_image.png", quality_cycle_read_image_file)	



		quality_cycle_read_freq_image = image_names["quality_cycle_read_freq_image"]

		quality_cycle_read_freq_image_file = File(myzip.open(quality_cycle_read_freq_image, "r"))

		sample.quality_cycle_read_freq_image.save(str(sample.pk)+"-quality_cycle_read_freq_image.png", quality_cycle_read_freq_image_file)	


		quality_heatmap_image = image_names["quality_heatmap_image"]

		quality_heatmap_image_file = File(myzip.open(quality_heatmap_image, "r"))

		sample.quality_heatmap_image.save(str(sample.pk)+"-quality_heatmap_image.png", quality_heatmap_image_file)	



	myzip.close()

	sample.save()

	

def upload_all_sample_qcs(output_dir, sample_names):

	"""
	This function uploads the sample specific QC data i.e. bam.stats. 
	Calls upload_sample_qc() on all samples in sample_names.

	Uses the stats files contined within the archive*/*QC_stats directory

	Input:

	output_dir = The directory containing the pipeline output e.g. alignments, beds

	sample_names = A list containing the sample_names to be processed.


	Output:

	None - uploads and returns None


	"""


	for sample in sample_names:

		upload_sample_qc(output_dir,sample)

	return None




def upload_gene_coverage(output_dir, sample_name):

	"""
	Uploads the gene coverage for a sample.
	This is stored within the re_analysis folder in the file named *gene-count-data.tsv.gz 

	Input:


	output_dir = The pipeline output directory.
	sample_name = The unique sample name.


	Output:

	None - Uploads and returns None.

	"""

	#Get the sample  - if we cannot find it then raise and error.
	try:

		sample = Sample.objects.get(name = sample_name)

	except Sample.DoesNotExist:


		raise CommandError("Cannot find a sample in the DB with name " + sample_name + ".")


	#Check if coverage data is already uploaded against this sample

	coverage = GeneCoverage.objects.filter(sample=sample)

	if coverage.exists():

		raise CommandError("Gene coverage data already uploaded for sample: " + sample_name + ".")


	#Get the file


	query = output_dir +   "/reanalysis_data*/" + sample_name +".gene-count-data.tsv.gz"

	gene_data_file = glob.glob(query)

	#Check glob has found only one file

	if len(gene_data_file) != 1:

		raise CommandError("Found more than one file for sample: " + sample_name)

	else:

		gene_data_file = gene_data_file[0]


	gene_coverage_data = file_parsers.parse_gene_coverage(gene_data_file)


	if gene_coverage_data == False:

		raise CommandError("Could not parse the coverage data file: " + gene_data_file)

	#Go through each sample and insert a GeneCoverage instance into DB
	for sample_data in gene_coverage_data: 


		gene = sample_data["Gene"]


		try:

			gene = Gene.objects.get(name=gene)

		except Gene.DoesNotExist:

			gene = Gene(name=gene)

			gene.save()

		gene_coverage = GeneCoverage(sample=sample,
									gene=gene,
									x100=sample_data["100x"],
									x200=sample_data["200x"],
									x300=sample_data["300x"],
									x400=sample_data["400x"],
									x500=sample_data["500x"],
									x600=sample_data["600x"],
									min_coverage= sample_data["Min"],
									max_coverage = sample_data["Max"],
									mean_coverage= sample_data["Mean"],
									number_of_regions = sample_data["region"] )

		gene_coverage.save()

	return None


def upload_exon_coverage(output_dir, sample_name):

	"""
	Uploads the exon coverage for a sample.
	This is stored within the re_analysis folder in the file named *exon-count-data.tsv.gz 

	Input:


	output_dir = The pipeline output directory.
	sample_name = The unique sample name.


	Output:

	None - Uploads and returns None.

	"""

	#Get the sample  - if we cannot find it then raise and error.
	try:

		sample = Sample.objects.get(name = sample_name)

	except Sample.DoesNotExist:


		raise CommandError("Cannot find a sample in the DB with name " + sample_name + ".")


	#Check if coverage data is already uploaded against this sample

	coverage = ExonCoverage.objects.filter(sample=sample)

	if coverage.exists():

		raise CommandError("Exon coverage data already uploaded for sample: " + sample_name + ".")


	#Get the file

	query = output_dir +   "/reanalysis_data*/" + sample_name +".exon-count-data.tsv.gz"

	exon_data_file = glob.glob(query)

	#Check glob has found only one file

	if len(exon_data_file) != 1:

		raise CommandError("Found more than one file for sample: " + sample_name)

	else:

		exon_data_file = exon_data_file[0]


	exon_coverage_data = file_parsers.parse_exon_coverage(exon_data_file)

	if exon_coverage_data == False:

		raise CommandError("Could not parse the coverage data file: " + exon_data_file)

	#Go through each exon coverage and insert a ExonCoverage instance into DB
	for sample_data in exon_coverage_data:

		gene = sample_data["Gene"]


		try:

			gene = Gene.objects.get(name=gene)

		except Gene.DoesNotExist:

			gene = Gene(name=gene)

			gene.save()

		exon_coverage = ExonCoverage(sample=sample,
									gene=gene,
									x100=sample_data["100x"],
									x200=sample_data["200x"],
									x300=sample_data["300x"],
									x400=sample_data["400x"],
									x500=sample_data["500x"],
									x600=sample_data["600x"],
									min_coverage= sample_data["Min"],
									max_coverage = sample_data["Max"],
									mean_coverage= sample_data["Mean"],
									number_of_regions = sample_data["region"],
									exon = sample_data["Exon"] )

		exon_coverage.save()

	return None



def upload_all_exon_gene_coverage(output_dir, sample_names):


	"""
	Calls upload_exon_coverage() and upload_gene_coverage() on all samples in sample_list

	Input:

	output_dir = The directory containing the pipeline output e.g. alignments, beds

	sample_names = A list containing the sample_names to be processed.


	Output:

	None - uploads and returns None


	"""

	for sample in sample_names:

		upload_exon_coverage(output_dir, sample)

		upload_gene_coverage(output_dir, sample)

	return None




def upload_sample_vcf(output_dir, sample_name):

	"""
	Takes a VEP annotated vcf and uploads the variants contained within it.

	Input:

	output_dir = The directory containing the pipline output.
	sample_name = A string representing the unique sample name.


	Output:

	None - uploads and returns None.


	"""


	#Get the sample  - if we cannot find it then raise and error.
	try:

		sample = Sample.objects.get(name = sample_name)

	except Sample.DoesNotExist:


		raise CommandError("Cannot find a sample in the DB with name " + sample_name + ".")



	already_uploaded = VariantSample.objects.filter(sample=sample)


	if already_uploaded.exists():

		raise CommandError("Stuff already uploaded against this sample.")


	#Find VCF file

	query = output_dir +   "vcfs*vep*/" + sample_name +"*.vcf.gz"

	vcf_file_path = glob.glob(query)


	if len(vcf_file_path) != 1:

		raise CommandError("Found more than one file for sample: " + sample_name)

	else:

		vcf_file_path = vcf_file_path[0]

	#validate vcf

	validation_report = vcf_parser.validate_input(vcf_file_path, sample_name)


	if validation_report[0] == False:

		raise CommandError("Error opening vcf file: "+ validation_report[1])


	if vcf_parser.vep_annotated(vcf_file_path) == False:

		raise CommandError("No VEP annotations detected in vcf")


	#Check we have an admin user in the database for the next stage
		

	try:

		user = User.objects.get(pk=1) # a superuser has to have been created

	except:

		error = "Could not find an appropiate user to use for downstream data entry" \
		 		" - please create an admin with pk=1"

		raise CommandError(error)


	#Try and parse the vcf using the vcf_parser
	try:

		vcf_data = vcf_parser.create_master_list(vcf_file_path, sample_name)

	except:

		raise CommandError("Could not process data using vcf_parser function")


	#update sample information e.g. vcf location.

	sample.vcf_file = vcf_file_path

	sample.save()

	for variant in vcf_data:

		chromosome = variant["chrom"]
		pos = str(variant["pos"])
		ref = variant["reference"]
		alt = variant["alt_alleles"][0]

		hash_id = variant_utilities.get_variant_hash(chromosome, pos,ref,alt)

		gene_list = vcf_parser.get_variant_genes_list(variant["transcript_data"])

		rs_number = vcf_parser.get_rs_number(variant["transcript_data"])

		worst_consequence = vcf_parser.worst_consequence(variant["transcript_data"])

		worst_consequence = Consequence.objects.get(name=worst_consequence)

		max_af = vcf_parser.get_max_af(variant["transcript_data"])

		allele_frequencies = vcf_parser.get_allele_frequencies(variant["transcript_data"])

		clin_sig = vcf_parser.get_clin_sig(variant["transcript_data"])

		af = allele_frequencies[0]
		afr_af = allele_frequencies[1]
		amr_af = allele_frequencies[2]
		eur_af = allele_frequencies[3]
		eas_af = allele_frequencies[4]
		sas_af = allele_frequencies[5]
		exac_af = allele_frequencies[6]
		exac_adj_af = allele_frequencies[7]
		exac_afr_af = allele_frequencies[8]
		exac_amr_af = allele_frequencies[9]
		exac_eas_af = allele_frequencies[10]
		exac_fin_af = allele_frequencies[11]
		exac_nfe_af = allele_frequencies[12]
		exac_oth_af = allele_frequencies[13]
		exac_sas_af = allele_frequencies[14]
		esp_aa_af = allele_frequencies[15]
		esp_ea_af = allele_frequencies[16]

		#Look for a variant in the database if we have not seen it before create a new one 

		try:

			new_variant = Variant.objects.get(variant_hash=hash_id)


		except Variant.DoesNotExist:

			new_variant = Variant(chromosome=chromosome,
								position=pos,
			 					ref= ref,
			 					alt=alt,
			 					variant_hash= hash_id,
			 					rs_number=rs_number,
			 					last_updated= timezone.now(),
			 					worst_consequence=worst_consequence,
			 					max_af= max_af,
			 					af=af,
			 					afr_af=afr_af,
			 					amr_af=amr_af,
			 					eur_af=eur_af,
			 					eas_af=eas_af,
			 					sas_af=sas_af,
			 					exac_af=exac_af,
			 					exac_adj_af=exac_adj_af,
			 					exac_afr_af= exac_afr_af,
			 					exac_amr_af=exac_amr_af,
			 					exac_eas_af=exac_eas_af,
			 					exac_fin_af=exac_fin_af,
			 					exac_nfe_af = exac_nfe_af,
			 					exac_oth_af=exac_oth_af,
			 					exac_sas_af=exac_sas_af,
			 					esp_aa_af=esp_aa_af,
			 					esp_ea_af=esp_ea_af,
			 					clinical_sig=clin_sig)

			new_variant.save()


			for gene in gene_list:

				try:

					gene_model = Gene.objects.get(name = gene[0])

				except Gene.DoesNotExist:

					gene_model = Gene(name=gene[0])
					gene_model.save()



			#Now create transcripts


			for transcript_key in variant["transcript_data"]:

				if transcript_key == "":

					try:

						transcript_model = Transcript.objects.get(name="no_transcript")

					except Transcript.DoesNotExist:

						transcript_model = Transcript(name = "no_transcript", canonical=False)

						transcript_model.save()

				else:

					try:

						transcript_model = Transcript.objects.get(name=transcript_key)

					except Transcript.DoesNotExist:


						canonical = variant["transcript_data"][transcript_key]["CANONICAL"]

						if canonical == "YES":

							canonical = True
						else:

							canonical = False


						gene = variant["transcript_data"][transcript_key]["SYMBOL"]

						if gene != "":

							gene = Gene.objects.get(name=gene)

							transcript_model = Transcript(name = transcript_key,
															canonical=canonical,
															gene =gene)

							transcript_model.save()

						else:

							transcript_model = Transcript(name = transcript_key,
															canonical=canonical)

							transcript_model.save()


				#now create transcriptvariant model

				consequence = variant["transcript_data"][transcript_key]["Consequence"]
				exon = variant["transcript_data"][transcript_key]["EXON"]
				intron = variant["transcript_data"][transcript_key]["INTRON"]
				hgvsc_t = variant["transcript_data"][transcript_key]["HGVSc"]
				hgvsp_t = variant["transcript_data"][transcript_key]["HGVSp"]
				codons = variant["transcript_data"][transcript_key]["Codons"]
				cdna_position = variant["transcript_data"][transcript_key]["cDNA_position"]
				cds_position = variant["transcript_data"][transcript_key]["CDS_position"]
				protein_position = variant["transcript_data"][transcript_key]["Protein_position"]
				amino_acids = variant["transcript_data"][transcript_key]["Amino_acids"]
				picked = variant["transcript_data"][transcript_key]["PICK"]

				if picked == "1":

					picked = True

				else:

					picked =False


				variant_transcript = VariantTranscript(variant = new_variant,
														transcript=transcript_model,
														consequence=consequence,
														exon=exon,
														intron = intron,
														hgvsc =hgvsc_t,
														hgvsp = hgvsp_t,
														codons=codons,
														cdna_position=cdna_position,
														protein_position=protein_position,
														amino_acids=amino_acids,
														picked =picked)
									
				variant_transcript.save()


		genotype = variant["genotype"]
		caller = variant["Caller"]
		allele_depth = variant["allele_depth"]
		filter_status = variant["filter_status"]
		total_count_forward = variant["TCF"]
		total_count_reverse = variant["TCR"]
		vafs = ":".join(str(x) for x in variant["VAFS"])

		new_variant_sample = VariantSample(variant=new_variant,
											sample=sample,
											genotype = genotype,
											caller=caller,
											allele_depth=allele_depth,
										 	filter_status=filter_status,
										 	total_count_forward=total_count_forward,
										 	total_count_reverse=total_count_reverse,
										 	vafs=vafs )

		new_variant_sample.save()

	return None



def upload_all_sample_variants(output_dir, sample_names):
	"""	
	Calls the upload_sample_vcf() function on each sample in the list sample_names

	Input:

	output_dir = The directory containing the pipeline output.
	sample_names = A list containing the sample_names.


	Output: 


	None - uploads and returns None.

	"""

	for sample in sample_names:

		print sample

		upload_sample_vcf(output_dir, sample)


	return None


class Command(BaseCommand):


	help = "This is the master uploader for the database."


	def add_arguments(self, parser):

		parser.add_argument("--worksheet_dir", "-w", action="store",help="The directory containing the folder with the samplesheet. This folder also contains InterOp folder with run QC.")
		parser.add_argument("--output_dir", "-o", action="store",help="The directory containing the folder with the run output e.g. alignments/, /vcfs, /archive")

		parser.add_argument("--sample_sheet", action="store_true",default= False ,help="""Add this option to import the information within the SampleSheet.csv file into the database.
																						 This will import a new worksheet and create sample objects as specified in the SampleSheet.""")

		parser.add_argument("--run_qc", action="store_true",default= False ,help="Add this option to import the run QC information into the database. This is the information contained within the InterOp files.")
		parser.add_argument("--sample_qc", action="store_true",default= False ,help="Add this option to import the sample QC information into the database. This is the information created by the SamStats program.")
		parser.add_argument("--coverage", action="store_true",default= False ,help="dd this option to import the Gene and Exon coverage information into the database.")
		parser.add_argument("--variants", action="store_true",default= False ,help="Add this option to import the variant information contained within the VEP annotated vcf files.")

		parser.add_argument("--single_sample", action="store" ,help="Upload the data for only this sample. Assumes Sample already exists in DB. N.B - sample_sheet and run_qc inactive with this option.")


	def handle(self, *args, **options):

		worksheet_dir = options["worksheet_dir"]

		output_dir = options["output_dir"]

		if worksheet_dir == None or output_dir == None:

			raise CommandError("Please enter appropriate arguments. See help for detail.")


		if worksheet_dir[-1] != "/":

			worksheet_dir= worksheet_dir+"/"

		if output_dir[-1] != "/":

			output_dir= output_dir+"/"


		sample_sheet_data = process_sample_sheet(worksheet_dir)

		sample_names =  file_parsers.get_sample_names(sample_sheet_data)

		worksheet_name = sample_sheet_data[2]


		with transaction.atomic():


			if options["single_sample"] == None:


				if options["sample_sheet"] ==True:

					upload_sample_sheet(sample_sheet_data)

					output_string = ("Uploaded SampleSheet: {} with {} samples."
									.format(worksheet_name, len(sample_names)))
																							

					self.stdout.write(output_string)


				if options["run_qc"] == True:


					self.stdout.write(self.style.SUCCESS("Processing run QC data."))

					upload_run_qc(worksheet_dir, worksheet_name)

					self.stdout.write(self.style.SUCCESS("Run QC data successfully uploaded."))



				if options["sample_qc"] == True:


					self.stdout.write(self.style.SUCCESS("Processing sample QC data."))

					upload_all_sample_qcs(output_dir, sample_names)

					self.stdout.write(self.style.SUCCESS("Sample QC data uploaded."))


				if options["coverage"] == True:

					self.stdout.write(self.style.SUCCESS("Processing gene/exon coverage data."))

					upload_all_exon_gene_coverage(output_dir, sample_names)

					self.stdout.write(self.style.SUCCESS("Run Exon/Gene coverage data uploaded."))


				if options["variants"] == True:

					self.stdout.write(self.style.SUCCESS("Processing variant data."))

					upload_all_sample_variants(output_dir, sample_names)


					self.stdout.write(self.style.SUCCESS("Variant upload complete."))

				self.stdout.write(self.style.SUCCESS("Upload Complete"))

				return None

			else:


				#This is if the user has selected the single_sample option

				samp = options["single_sample"]

				self.stdout.write(self.style.SUCCESS("Processing data for single sample: " + samp))

				if options["sample_qc"] == True:

					self.stdout.write(self.style.SUCCESS("Processing sample QC data."))

					upload_sample_qc(output_dir, options["single_sample"])

					self.stdout.write(self.style.SUCCESS("Sample QC data uploaded."))


				if options["coverage"] == True:

					self.stdout.write(self.style.SUCCESS("Processing gene/exon coverage data."))

					upload_gene_coverage(output_dir, options["single_sample"])
					upload_exon_coverage(output_dir, options["single_sample"])


					self.stdout.write(self.style.SUCCESS("Run Exon/Gene coverage data uploaded."))


				if options["variants"] == True:

					self.stdout.write(self.style.SUCCESS("Processing variant data."))

					upload_sample_vcf(output_dir, options["single_sample"])


					self.stdout.write(self.style.SUCCESS("Variant upload complete."))

				self.stdout.write(self.style.SUCCESS("Upload Complete"))

				return None

