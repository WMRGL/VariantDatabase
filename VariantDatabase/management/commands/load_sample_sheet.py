from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
import csv
from django.db import transaction
def get_sample_ids(file):

	flag =0

	sample_ids =[]

	with open(file) as csvfile:

		reader = csv.reader(csvfile, delimiter=',')

		for row in reader:

			if row[0] == 'Sample_ID':

				flag =1

			if flag ==1:

				sample_ids.append(row[0])



	return sample_ids[1:]

class Command(BaseCommand):

	help = "create a worksheet and parse a samplesheet"

	def add_arguments(self, parser):

		parser.add_argument('sample_sheet_path', nargs =1, type = str)
		parser.add_argument('worksheet_name', nargs =1, type = str)
		parser.add_argument('worksheet_section', nargs =1, type = str)
		parser.add_argument('comment', nargs =1, type = str)

	def handle(self, *args, **options):


		with transaction.atomic():

			sample_sheet = options['sample_sheet_path'][0]

			worksheet_name = options['worksheet_name'][0]

			worksheet_section = int(options['worksheet_section'][0])

			worksheet_comment = options['comment'][0]

			try:

				section = Section.objects.get(pk=worksheet_section)

			except:

				raise CommandError('Could not find that Section: Enter a number e.g.1-5')



			new_worksheet = Worksheet(name=worksheet_name, section=section,comment=worksheet_comment, status ='1')

			new_worksheet.save()

			sample_names = get_sample_ids(sample_sheet)

			for sample in sample_names:

				

				sample_model = Sample.objects.filter(name =sample)

				if sample_model.exists() == True:

					raise CommandError('Sample with name: '+sample + ' already exists in the DB')

				else:

					#sample = Sample.objects.get(name=sample_name)
					self.stdout.write(self.style.SUCCESS('Sample with name: '+sample + ' is new - proceeding'))


				new_sample = Sample(name= sample, patient_initials='NA', worksheet=new_worksheet, vcf_file='None', visible=True,status='1')

				new_sample.save()






		self.stdout.write(self.style.SUCCESS('Complete'))