from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
import imp
from django.db import transaction
import csv



#pysam_extract = imp.load_source('pysam_extract', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/Pysam/pysam_extract.py')


class Command(BaseCommand):

	help = "imports a vcf"

	def add_arguments(self, parser):

		parser.add_argument('genefile', nargs=1, type = str)


	def handle(self, *args, **options):

		file_path = options['genefile'][0]

		data_reader = csv.DictReader(open(file_path), delimiter='\t')

		count =0

		with transaction.atomic():


			for row in data_reader:


				if row['entrez_id'] != "":


					new_gene = Gene()

					new_gene.name = row['symbol']

					new_gene.entrez_id = row['entrez_id']

					new_gene.alias = row['alias_symbol']

					new_gene.description = row['name']

					new_gene.save()

					count = count+1



		self.stdout.write(self.style.SUCCESS('Finished :' + str(count)+ " genes inserted"))
		
