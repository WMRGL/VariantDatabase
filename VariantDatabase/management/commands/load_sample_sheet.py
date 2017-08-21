from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
import csv
from django.db import transaction

def parse_sample_sheet(file):

	expected = ['Sample_ID', 'Sample_Name', 'Sample_Plate','Sample_Well', 'I7_Index_ID',  'index', 'Sample_Project']

	flag =0

	sample_list = []

	with open(file) as csvfile:

		reader = csv.reader(csvfile, delimiter=',')

		for row in reader:

			if row[0] == 'Sample_ID':

				flag =1

				for index, title in enumerate(expected):

					if title != row[index]:

						return False

			if flag ==1:

				sample_list.append([row[0], row[1],row[2],row[3],row[4],row[5],row[6]])


	return sample_list[1:]


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

			sample_data = parse_sample_sheet(sample_sheet)

			for sample in sample_data:

				sample_id = sample[0]
				sample_name = sample[1]
				sample_plate = sample[2]
				sample_well = sample[3]
				sample_i7_index = sample[4]
				sample_index = sample[5]
				sample_project = sample[6]

				sample_model = Sample.objects.filter(name =sample)

				if sample_model.exists() == True:

					raise CommandError('Sample with name: '+sample[1] + ' already exists in the DB')

				else:

					self.stdout.write(self.style.SUCCESS('Sample with name: '+sample[1] + ' is new - proceeding'))


				new_sample = Sample(name= sample_name, worksheet=new_worksheet, vcf_file='None', visible=True,status='1',
				 sample_id=sample_id, sample_plate =sample_plate, sample_well=sample_well, i7_index_id=sample_i7_index, index=sample_index, sample_project=sample_project )

				new_sample.save()






		self.stdout.write(self.style.SUCCESS('Complete'))