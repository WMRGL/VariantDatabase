from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
from django.db import transaction
import glob
import imp

parsers = imp.load_source('parsers', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/parsers/parsers.py')


class Command(BaseCommand):

	help = "imports a the coverage data for a particular sample"

	def add_arguments(self, parser):

		parser.add_argument('folder_path', nargs =1, type = str)
		parser.add_argument('sample_name', nargs=1, type = str)

	def handle(self, *args, **options):


		folder_path = options['folder_path'][0]
		sample_name = options['sample_name'][0]

		#first find the file with the gene data in

		gene_data_file = glob.glob(folder_path+'/' + sample_name+'.gene-count-data.tsv.gz')

		#Second find the file with the exon data in

		exon_data_file = glob.glob(folder_path+'/' + sample_name+'.exon-count-data.tsv.gz')


		if len(gene_data_file) ==1 and len(exon_data_file) ==1:

			gene_data_file = gene_data_file[0]
			exon_data_file = exon_data_file[0]


			self.stdout.write(self.style.SUCCESS("Successfully found both files"))

		else:

			raise CommandError('Files not found')


		gene_coverage_data = parsers.parse_gene_coverage(gene_data_file)

		if gene_coverage_data == False:

			raise CommandError('Gene Coverage File is in wrong format')



		exon_coverage_data = parsers.parse_exon_coverage(exon_data_file)

		if exon_coverage_data == False:

			raise CommandError('Exon Coverage File is in wrong format')


		with transaction.atomic():


			for sample_data in gene_coverage_data: #GO through each sample and insert a GeneCoverage instance into DB


				worksheet = sample_data['Worksheet']
				sample = sample_data['Sample']
				gene = sample_data['Gene']


				worksheet = Worksheet.objects.get(name =worksheet)
				sample = Sample.objects.get(name=sample, worksheet=worksheet)

				try:

					gene = Gene.objects.get(name=gene)

				except Gene.DoesNotExist:

					gene = Gene(name=gene)

					gene.save()

				gene_coverage = GeneCoverage(sample=sample, gene=gene, x100=sample_data['100x'],x200=sample_data['200x'], x300=sample_data['300x'], x400=sample_data['400x'], x500=sample_data['500x'],
												x600=sample_data['600x'], min_coverage= sample_data['Min'], max_coverage = sample_data['Max'], mean_coverage= sample_data['Mean'], number_of_regions = sample_data['region'] )

				gene_coverage.save()


			for sample_data in exon_coverage_data: #GO through each sample and insert a ExonCoverage instance into DB


				worksheet = sample_data['Worksheet']
				sample = sample_data['Sample']
				gene = sample_data['Gene']


				worksheet = Worksheet.objects.get(name =worksheet)
				sample = Sample.objects.get(name=sample, worksheet=worksheet)

				try:

					gene = Gene.objects.get(name=gene)

				except Gene.DoesNotExist:

					gene = Gene(name=gene)

					gene.save()

				exon_coverage = ExonCoverage(sample=sample, gene=gene, x100=sample_data['100x'],x200=sample_data['200x'], x300=sample_data['300x'], x400=sample_data['400x'], x500=sample_data['500x'],
												x600=sample_data['600x'], min_coverage= sample_data['Min'], max_coverage = sample_data['Max'], mean_coverage= sample_data['Mean'], number_of_regions = sample_data['region'],exon = sample_data['Exon'] )

				exon_coverage.save()

			self.stdout.write(self.style.SUCCESS("Complete"))