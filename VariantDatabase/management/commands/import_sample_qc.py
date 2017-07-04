from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
import django.contrib.auth  
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
import csv
import glob
from django.core.files import File

def get_sam_stats(sample_name,folder):

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

	if folder[len(folder)-1] != '/':

		folder = folder + '/'

	images = glob.glob(folder+sample_name+'*'+'.png')

	if len(images) == 11:

		return images

	else:

		return False


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

			sample= sample[0]

			sam_stats_dict = get_sam_stats(sample_name, folder_path)

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


			#sample.acgt_cycles_image = '/home/cuser/Documents/Project/Preliminary/samstats/MPN_MPN_200500_QC_stats/WS61594_14000835.bwa.drm.realn.sorted.bam.stats-acgt-cycles.png'


			f = File(open('/home/cuser/Documents/Project/Preliminary/samstats/MPN_MPN_200500_QC_stats/WS61594_14000835.bwa.drm.realn.sorted.bam.stats-acgt-cycles.png', 'r'))

			sample.gc_content_image.save('hi.png', f)

			sample.save()






