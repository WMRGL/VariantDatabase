"""
master_upload.py aims to upload a full worksheet of samples including the sample_sheet, run_qc, sample_qc, coverage_data and vcfs

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

vcf_parser = imp.load_source('vcf_parser', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/parsers/vcf_parser.py')
file_parsers = imp.load_source('file_parsers', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/parsers/file_parsers.py')
sam_stats_parser = imp.load_source('sam_stats_parser', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/parsers/sam_stats_parser.py')



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


	"""

	sample_data = sample_sheet_data[0]

	subsection_name = sample_sheet_data[1]

	worksheet_name = sample_sheet_data[2]

	#First get the SubSection object

	try:

		subsection = SubSection.objects.get(name=subsection_name)
		print "Found SubSection: name = " + subsection.name

	except SubSection.DoesNotExist:

		raise CommandError("Cannot find SubSection. Either edit SampleSheet.csv or create a new SubSection via Django Admin.")

	#Next get the Worksheet object


	worksheet = Worksheet.objects.filter(name=worksheet_name)

	if worksheet.exists():

		raise CommandError("This worksheet already exists.")

	else:

		worksheet = Worksheet(name= worksheet_name, sub_section=subsection,comment='NA', status='1')
		worksheet.save()

	#Now go through each list in sample_data and create a new SampleObject


	for sample in sample_data:


		sample_name = sample[1]
		sample_plate = sample[2]
		sample_well = sample[3]
		sample_i7_index = sample[4]
		sample_index = sample[5]
		sample_project = sample[6]


		new_sample = Sample.objects.filter(name=sample_name)

		if new_sample.exists():

			raise CommandError("Sample " + sample_name + " already exists!")

		else:

	
			#get or create worksheet object - based on Sample_Plate column


			new_sample = Sample(name= sample_name, worksheet=worksheet, visible=True,status='1',
									sample_well=sample_well, i7_index_id=sample_i7_index, index=sample_index, sample_project=sample_project )

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


		raise CommandError("Worksheet " + worksheet_name + " already has QC data attached to it. To reupload data first delete existing ReadLaneQuality objects associated with the worksheet")



	#Upload QC data

	summary = file_parsers.get_qc_run_summary(worksheet_dir)

	qc_data = file_parsers.get_all_qc_data(summary)

	for read_lane in qc_data:

		read = read_lane['read']
		lane = read_lane['lane']
		yield_g = read_lane['yield_g']
		density = read_lane['density']
		cluster_count_pf = read_lane['cluster_count_pf']
		cluster_count = read_lane['cluster_count']
		phasing = read_lane['phasing']
		prephasing = read_lane['prephasing']
		read_count = read_lane['read_count']
		reads_pf = read_lane['reads_pf']
		percent_gt_q30 = read_lane['percent_gt_q30']
		percent_aligned = read_lane['percent_aligned']
		error_rate = read_lane['error_rate']
		error_rate_35 = read_lane['error_rate_35']
		error_rate_50 = read_lane['error_rate_50']
		error_rate_75 = read_lane['error_rate_75']
		error_rate_100 = read_lane['error_rate_100']

		new_qc_model = ReadLaneQuality(worksheet=worksheet,read=read, lane=lane, yield_g=yield_g,density=density,cluster_count_pf=cluster_count_pf, cluster_count=cluster_count,
										phasing=phasing, prephasing=prephasing, read_count=read_count, reads_pf=reads_pf,percent_gt_q30=percent_gt_q30,
										percent_aligned=percent_aligned,error_rate=error_rate,error_rate_35=error_rate_35,error_rate_75=error_rate_75,error_rate_100=error_rate_100)

		new_qc_model.save()


	worksheet.status = '2'

	worksheet.save()


	return None



def upload_sample_qc(output_dir, sample_name, worksheet_name):

	"""
	Uploads the sample qc for a specific sample.

	Input:

	output_dir = The directory containing the pipeline output e.g. alignments, beds

	sample_name = A string representing the unique sample_name

	worksheet_name = A string representing the worksheet name.


	Output:

	None - uploads and returns None

	"""

	#Find sample and raise error if it cannot be found.


	try:

		sample = Sample.objects.get(name = sample_name)

	except Sample.DoesNotExist:


		raise CommandError("Cannot find a sample in the DB with name " + sample_name + ".")


	#get data from archive directory with output directory e.g. MPN/213837_v0.3.10/archive_MPN_213837/MPN_213837_QC_stats/


	stats_location = glob.glob(output_dir+ "archive_" + "*" + "/"+"*QC_stats.zip")

	if len(stats_location) != 1:

		raise CommandError("An error occured finding the stats file.")

	else:

		stats_location = stats_location[0]


	#Use sam_stats_parser to get the data and image locations

	sample_qc_stats =  sam_stats_parser.get_sam_stats(sample_name, stats_location)


	if sample_qc_stats == False:

		raise CommandError("An error occured when parsing the stats file.")


	image_names =  sam_stats_parser.get_sam_images(sample_name, stats_location)


	#Now we have the sample and the data then let's update it.

	sample.raw_total_sequences = int(sample_qc_stats['raw total sequences'])
	sample.filtered_sequences = int(sample_qc_stats['filtered sequences'])
	sample.sequences = int(sample_qc_stats['sequences'])
	sample.first_fragments = int(sample_qc_stats['1st fragments'])
	sample.last_fragments = int(sample_qc_stats['last fragments'])
	sample.reads_mapped = int(sample_qc_stats['reads mapped'])
	sample.reads_mapped_and_paired = int(sample_qc_stats['reads mapped and paired'])
	sample.reads_unmapped = int(sample_qc_stats['reads unmapped'])
	sample.reads_properly_paired = int(sample_qc_stats['reads properly paired'])
	sample.reads_paired = int(sample_qc_stats['reads paired'])
	sample.reads_duplicated = int(sample_qc_stats['reads duplicated'])
	sample.reads_MQ0 = int(sample_qc_stats['reads MQ0'])
	sample.reads_QC_failed = int(sample_qc_stats['reads QC failed'])
	sample.non_primary_alignments = int(sample_qc_stats['non-primary alignments'])
	sample.total_length = int(sample_qc_stats['total length'])
	sample.bases_mapped = int(sample_qc_stats['bases mapped'])
	sample.bases_mapped_cigar = int(sample_qc_stats['bases mapped (cigar)'])
	sample.bases_trimmed = int(sample_qc_stats['bases trimmed'])
	sample.bases_duplicated = int(sample_qc_stats['bases duplicated'])
	sample.mismatches = int(sample_qc_stats['mismatches'])
	sample.average_length = int(sample_qc_stats['average length'])
	sample.maximum_length = int(sample_qc_stats['maximum length'])
	sample.average_quality = float(sample_qc_stats['average quality'])
	sample.insert_size_average = float(sample_qc_stats['insert size average'])
	sample.insert_size_standard_deviation = float(sample_qc_stats['insert size standard deviation'])
	sample.inward_oriented_pairs = int(sample_qc_stats['inward oriented pairs'])
	sample.outward_oriented_pairs = int(sample_qc_stats['outward oriented pairs'])
	sample.pairs_with_other_orientation = int(sample_qc_stats['pairs with other orientation'])
	sample.pairs_on_different_chromosomes = int(sample_qc_stats['pairs on different chromosomes'])


	#Now upload image files


	with zipfile.ZipFile(stats_location) as myzip: 


		acgt_cycles_image = image_names['acgt_cycles_image']

		acgt_cycles_image_file = File(myzip.open(acgt_cycles_image, 'r'))

		sample.acgt_cycles_image.save(str(sample.pk)+'-acgt_cycles.png', acgt_cycles_image_file)


		coverage_image = image_names['coverage_image']

		coverage_image_file = File(myzip.open(coverage_image, 'r'))

		sample.coverage_image.save(str(sample.pk)+'-coverage_image.png', coverage_image_file)



		gc_content_image = image_names['gc_content_image']

		gc_content_image_file = File(myzip.open(gc_content_image, 'r'))

		sample.gc_content_image.save(str(sample.pk)+'-gc_content_image.png', gc_content_image_file)



		gc_depth_image = image_names['gc_depth_image']

		gc_depth_image_file = File(myzip.open(gc_depth_image, 'r'))

		sample.gc_depth_image.save(str(sample.pk)+'-gc_depth_image.png', gc_depth_image_file)



		indel_cycles_image = image_names['indel_cycles_image']

		indel_cycles_image_file = File(myzip.open(indel_cycles_image, 'r'))

		sample.indel_cycles_image.save(str(sample.pk)+'-indel_cycles_image.png', indel_cycles_image_file)



		indel_dist_image = image_names['indel_dist_image']

		indel_dist_image_file = File(myzip.open(indel_dist_image, 'r'))

		sample.indel_dist_image.save(str(sample.pk)+'-indel_dist_image.png', indel_dist_image_file)	



		insert_size_image = image_names['insert_size_image']

		insert_size_image_file = File(myzip.open(insert_size_image, 'r'))

		sample.insert_size_image.save(str(sample.pk)+'-insert_size_image.png', insert_size_image_file)	


		quality_cycle_image = image_names['quality_cycle_image']

		quality_cycle_image_file = File(myzip.open(quality_cycle_image, 'r'))

		sample.quality_cycle_image.save(str(sample.pk)+'-quality_cycle_image.png', quality_cycle_image_file)		



		quality_cycle_read_image = image_names['quality_cycle_read_image']

		quality_cycle_read_image_file = File(myzip.open(quality_cycle_read_image, 'r'))

		sample.quality_cycle_read_image.save(str(sample.pk)+'-quality_cycle_read_image.png', quality_cycle_read_image_file)	



		quality_cycle_read_freq_image = image_names['quality_cycle_read_freq_image']

		quality_cycle_read_freq_image_file = File(myzip.open(quality_cycle_read_freq_image, 'r'))

		sample.quality_cycle_read_freq_image.save(str(sample.pk)+'-quality_cycle_read_freq_image.png', quality_cycle_read_freq_image_file)	


		quality_heatmap_image = image_names['quality_heatmap_image']

		quality_heatmap_image_file = File(myzip.open(quality_heatmap_image, 'r'))

		sample.quality_heatmap_image.save(str(sample.pk)+'-quality_heatmap_image.png', quality_heatmap_image_file)	



	myzip.close()

	sample.save()

	

def upload_all_sample_qcs(output_dir, sample_names):

	"""
	This function uploads the sample specific QC data i.e. bam.stats. Calls upload_sample_qc() on all samples in sample_names.

	Uses the stats files contined within the archive*/*QC_stats directory

	Input:

	output_dir = The directory containing the pipeline output e.g. alignments, beds

	sample_names = A list containing the sample_names to be processed.


	Output:

	None - uploads and returns None


	"""

	

	pass




def upload_gene_coverage(path):

	pass


def upload_exon_coverage(path):

	pass


def upload_sample_vcf(sample_vcf_path):

	pass

class Command(BaseCommand):


	help = "This is the master uploader for the database"


	def add_arguments(self, parser):

		parser.add_argument('--worksheet_dir', '-w', action='store',help="The directory containing the folder with the samplesheet. This folder also contains InterOp folder with run QC.",)
		parser.add_argument('--output_dir', '-o', action='store',help="The directory containing the folder with the run output e.g. alignments/, /vcfs, /archive",)



	def handle(self, *args, **options):

		worksheet_dir = options['worksheet_dir']

		output_dir = options['output_dir']


		if worksheet_dir[-1] != "/":

			worksheet_dir= worksheet_dir+"/"

		if output_dir[-1] != "/":

			output_dir= output_dir+"/"






		sample_sheet_data = process_sample_sheet(worksheet_dir)

		sample_names =  file_parsers.get_sample_names(sample_sheet_data)

		worksheet_name = sample_sheet_data[2]


		with transaction.atomic():


			upload_sample_sheet(sample_sheet_data)

			self.stdout.write(self.style.SUCCESS("Uploaded SampleSheet: " +worksheet_name + " with " + str(len(sample_names)) + " samples."))
			self.stdout.write(self.style.SUCCESS("Processing run QC data"))

			upload_run_qc(worksheet_dir, worksheet_name)


			self.stdout.write(self.style.SUCCESS("Run QC data Uploaded."))


			upload_sample_qc(output_dir, sample_names[1], worksheet_name)

