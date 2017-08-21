from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
import django.contrib.auth  
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
import csv
import glob
from django.core.files import File


"""
This import managment function allows the QC for a single sample to be imported.
The QC Data imported is the sam stats data created by the samtools stats and plot-bamstats programs.


"""


def get_sam_stats(sample_name,folder):
	"""
	Get the data from the sam stats file e.g. D16-41708_S15.bwa.drm.realn.sorted.bam.stats

	Returns a dictionary containing the relevent summary information.

	Needs sample name and the folder path containing the data

	"""

	file_name = sample_name+'.bwa.drm.realn.sorted.bam.stats'

	if folder[len(folder)-1] != '/':

		folder = folder + '/'

	file_path = folder+file_name

	data_dict ={}

	with open(file_path, 'rb') as csvfile:

		reader = csv.reader(csvfile, delimiter='\t')

		for row in reader:

			if row[0] == 'SN':

				data_dict[row[1][:-1]] = row[2]

	return data_dict




def get_sam_images(sample_name, folder):
	"""
	This functions returns the fiel paths of the image files needed for import.

	Returns a dictionary containing all the file paths.

	"""

	image_name_dict ={}

	if folder[len(folder)-1] != '/':

		folder = folder + '/'


	image_name_dict['acgt_cycles_image'] = glob.glob(folder+sample_name+'*'+'stats-acgt-cycles.png')
	image_name_dict['coverage_image'] = glob.glob(folder+sample_name+'*'+'stats-coverage.png')
	image_name_dict['gc_content_image'] = glob.glob(folder+sample_name+'*'+'stats-gc-content.png')
	image_name_dict['gc_depth_image'] = glob.glob(folder+sample_name+'*'+'stats-gc-depth.png')
	image_name_dict['indel_cycles_image'] = glob.glob(folder+sample_name+'*'+'stats-indel-cycles.png')
	image_name_dict['indel_dist_image'] = glob.glob(folder+sample_name+'*'+'stats-indel-dist.png')
	image_name_dict['insert_size_image'] = glob.glob(folder+sample_name+'*'+'stats-insert-size.png')
	image_name_dict['quality_cycle_image'] = glob.glob(folder+sample_name+'*'+'stats-quals.png')
	image_name_dict['quality_cycle_read_image'] = glob.glob(folder+sample_name+'*'+'stats-quals2.png')
	image_name_dict['quality_cycle_read_freq_image'] = glob.glob(folder+sample_name+'*'+'stats-quals3.png')
	image_name_dict['quality_heatmap_image'] = glob.glob(folder+sample_name+'*'+'stats-quals-hm.png')

	for key in image_name_dict: # Check we've only found a single image for each key

		if len(image_name_dict[key]) == 1:

			image_name_dict[key] =image_name_dict[key][0]

		else:

			return False


	return image_name_dict


class Command(BaseCommand):

	help = "imports samstats data"

	def add_arguments(self, parser):

		parser.add_argument('folder_path', nargs=1, type = str)
		parser.add_argument('sample_name', nargs=1, type = str)
		parser.add_argument('worksheet_id', nargs=1, type = str)

	def handle(self, *args, **options):

		folder_path = options['folder_path'][0]
		sample_name = options['sample_name'][0]
		worksheet_name = options['worksheet_id'][0]

		#Get relvent model instances e.g. workbook

		try:

			worksheet = Worksheet.objects.get(name=worksheet_name)
			self.stdout.write(self.style.SUCCESS("Successfully found worksheet with pk: " + worksheet_name))

		except Worksheet.DoesNotExist:

			raise CommandError('There is no worksheet with the pk: ' + worksheet_name)

		sample = Sample.objects.filter(worksheet = worksheet, name=sample_name)

		if len(sample) ==1:

			self.stdout.write(self.style.SUCCESS('Found sample ' +sample[0].name +  ' in worksheet ' + worksheet.name))

		else:

			raise CommandError('Error either no sample or >1 sample')


		with transaction.atomic():


			#Do the summary stats import

			sample= sample[0]

			sam_stats_dict = get_sam_stats(sample_name, folder_path)

			if sam_stats_dict == False:

				raise CommandError('An error occured whilst parsing the sam stats file')

			sample.raw_total_sequences = int(sam_stats_dict['raw total sequences'])
			sample.filtered_sequences = int(sam_stats_dict['filtered sequences'])
			sample.sequences = int(sam_stats_dict['sequences'])
			sample.first_fragments = int(sam_stats_dict['1st fragments'])
			sample.last_fragments = int(sam_stats_dict['last fragments'])
			sample.reads_mapped = int(sam_stats_dict['reads mapped'])
			sample.reads_mapped_and_paired = int(sam_stats_dict['reads mapped and paired'])
			sample.reads_unmapped = int(sam_stats_dict['reads unmapped'])
			sample.reads_properly_paired = int(sam_stats_dict['reads properly paired'])
			sample.reads_paired = int(sam_stats_dict['reads paired'])
			sample.reads_duplicated = int(sam_stats_dict['reads duplicated'])
			sample.reads_MQ0 = int(sam_stats_dict['reads MQ0'])
			sample.reads_QC_failed = int(sam_stats_dict['reads QC failed'])
			sample.non_primary_alignments = int(sam_stats_dict['non-primary alignments'])
			sample.total_length = int(sam_stats_dict['total length'])
			sample.bases_mapped = int(sam_stats_dict['bases mapped'])
			sample.bases_mapped_cigar = int(sam_stats_dict['bases mapped (cigar)'])
			sample.bases_trimmed = int(sam_stats_dict['bases trimmed'])
			sample.bases_duplicated = int(sam_stats_dict['bases duplicated'])
			sample.mismatches = int(sam_stats_dict['mismatches'])
			sample.average_length = int(sam_stats_dict['average length'])
			sample.maximum_length = int(sam_stats_dict['maximum length'])
			sample.average_quality = float(sam_stats_dict['average quality'])
			sample.insert_size_average = float(sam_stats_dict['insert size average'])
			sample.insert_size_standard_deviation = float(sam_stats_dict['insert size standard deviation'])
			sample.inward_oriented_pairs = int(sam_stats_dict['inward oriented pairs'])
			sample.outward_oriented_pairs = int(sam_stats_dict['outward oriented pairs'])
			sample.pairs_with_other_orientation = int(sam_stats_dict['pairs with other orientation'])
			sample.pairs_on_different_chromosomes = int(sam_stats_dict['pairs on different chromosomes'])


			#Now do the image import


			images = get_sam_images(sample_name, folder_path)

			if images == False:

				raise CommandError('An error occured whilst parsing the sam stats images')



			acgt_cycles_image = images['acgt_cycles_image']

			acgt_cycles_image_file = File(open(acgt_cycles_image, 'r'))

			sample.acgt_cycles_image.save(str(sample.pk)+'-acgt_cycles.png', acgt_cycles_image_file)



			coverage_image = images['coverage_image']

			coverage_image_file = File(open(coverage_image, 'r'))

			sample.coverage_image.save(str(sample.pk)+'-coverage_image.png', coverage_image_file)



			gc_content_image = images['gc_content_image']

			gc_content_image_file = File(open(gc_content_image, 'r'))

			sample.gc_content_image.save(str(sample.pk)+'-gc_content_image.png', gc_content_image_file)



			gc_depth_image = images['gc_depth_image']

			gc_depth_image_file = File(open(gc_depth_image, 'r'))

			sample.gc_depth_image.save(str(sample.pk)+'-gc_depth_image.png', gc_depth_image_file)



			indel_cycles_image = images['indel_cycles_image']

			indel_cycles_image_file = File(open(indel_cycles_image, 'r'))

			sample.indel_cycles_image.save(str(sample.pk)+'-indel_cycles_image.png', indel_cycles_image_file)



			indel_dist_image = images['indel_dist_image']

			indel_dist_image_file = File(open(indel_dist_image, 'r'))

			sample.indel_dist_image.save(str(sample.pk)+'-indel_dist_image.png', indel_dist_image_file)	



			insert_size_image = images['insert_size_image']

			insert_size_image_file = File(open(insert_size_image, 'r'))

			sample.insert_size_image.save(str(sample.pk)+'-insert_size_image.png', insert_size_image_file)	


			quality_cycle_image = images['quality_cycle_image']

			quality_cycle_image_file = File(open(quality_cycle_image, 'r'))

			sample.quality_cycle_image.save(str(sample.pk)+'-quality_cycle_image.png', quality_cycle_image_file)		



			quality_cycle_read_image = images['quality_cycle_read_image']

			quality_cycle_read_image_file = File(open(quality_cycle_read_image, 'r'))

			sample.quality_cycle_read_image.save(str(sample.pk)+'-quality_cycle_read_image.png', quality_cycle_read_image_file)	



			quality_cycle_read_freq_image = images['quality_cycle_read_freq_image']

			quality_cycle_read_freq_image_file = File(open(quality_cycle_read_freq_image, 'r'))

			sample.quality_cycle_read_freq_image.save(str(sample.pk)+'-quality_cycle_read_freq_image.png', quality_cycle_read_freq_image_file)	


			quality_heatmap_image = images['quality_heatmap_image']

			quality_heatmap_image_file = File(open(quality_heatmap_image, 'r'))

			sample.quality_heatmap_image.save(str(sample.pk)+'-quality_heatmap_image.png', quality_heatmap_image_file)	

			sample.save()



			self.stdout.write(self.style.SUCCESS('Complete'))


