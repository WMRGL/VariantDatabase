from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
import django.contrib.auth  
from django.contrib.auth.models import User
import hashlib


import imp
from django.db import transaction
from django.utils import timezone


pysam_extract = imp.load_source('pysam_extract', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/Pysam/pysam_extract.py')


class Command(BaseCommand):

	help = "imports a vcf"

	def add_arguments(self, parser):

		parser.add_argument('worksheet_id', nargs=1, type = int)
		parser.add_argument('vcf_file', nargs =1, type = str)
		parser.add_argument('sample_name', nargs=1, type = str)
		parser.add_argument('patient_initials', nargs =1, type = str)

	def handle(self, *args, **options):

		# Get the worksheet from the database
		# Display an error if we could not retrieve it and end program
		complete = False
		worksheet_pk = options['worksheet_id'][0]

		try:

			worksheet = Worksheet.objects.get(pk=worksheet_pk)
			self.stdout.write(self.style.SUCCESS("Successfully found worksheet with pk: " + str(worksheet_pk)))

		except Worksheet.DoesNotExist:

			raise CommandError('There is no worksheet with the pk: ' + str(worksheet_pk))


		# Now open the vcf file that has been provided and validate it
		# We will raise an error if this fails
		# Validation report will be of format [Boolean, message]

		vcf_file_path = options['vcf_file'][0]
		sample_name = options['sample_name'][0]

		validation_report = pysam_extract.validate_input(vcf_file_path, sample_name)

		if validation_report[0] == False:

			raise CommandError('Error opening vcf file: '+ validation_report[1])

		else:

			self.stdout.write(self.style.SUCCESS('The vcf file ' + vcf_file_path + ' was successfully opened and validated'))


		# Now we can check if there is already a sample with that name
		# Unique sample name is not enforced on the database level - but is good to check


		sample = Sample.objects.filter(name =sample_name)

		if sample.exists() == True:

			raise CommandError('Sample with name: '+sample_name + ' already exists in the DB')

		else:

			#sample = Sample.objects.get(name=sample_name)
			self.stdout.write(self.style.SUCCESS('Sample with name: '+sample_name + ' is new - proceeding'))



		# Now try to process the data into the master list using the pysam_extact create_master_list 
		# Check what type of annotations we have too and display that in terminal
		# We could check more e.g. see if they have the neccecary vep annotations 

		try:

			data = pysam_extract.create_master_list(vcf_file_path, sample_name)

			self.stdout.write(self.style.SUCCESS('Loaded data using pysam_extract - proceeding'))
			self.stdout.write(self.style.SUCCESS(str(len(data))+ ' variants detected'))

			annotation_type = pysam_extract.vep_annotated(vcf_file_path)

			self.stdout.write(self.style.SUCCESS('VEP annotation detected'))

		except:

			raise CommandError('Could not process data using pysam_extract function')


		#Check we have an admin user in the database for the next stage
		

		try:

			user = User.objects.get(pk=1) # a superuser has to have been created

			self.stdout.write(self.style.SUCCESS('User: ' + user.username + ' used for following database inserts'))

		except:


			raise CommandError('Could not find an appropiate user to use for downstream data entry - please create an admin with pk=1')


		# Now we start doing database stuff
		# Wrap in transaction so that if something goes wrong
		

		
		with transaction.atomic():

			# Create a new sample using the information we have
		
			new_sample = Sample()
			new_sample.name = sample_name
			new_sample.patient_initials = options['patient_initials'][0]
			new_sample.worksheet = worksheet
			new_sample.vcf_file = vcf_file_path
			new_sample.save()

			self.stdout.write(self.style.SUCCESS('Sample '+ new_sample.name + ' created'))

			# Create a new sample Status

			inital_status = SampleStatus.objects.get(pk=1)

			new_update = SampleStatusUpdate(sample=new_sample, status=inital_status, user=user, date=timezone.now())

			new_update.save()



			# Now loop through each variant in the vcf file and insert relevent data into the database

			new_variant_count = 0
			new_gene_count = 0
			var_count = 0

			for variant in data:

				chromosome = variant['chrom']
				pos = str(variant['pos'])
				ref = variant['reference']
				alt = variant['alt_alleles'][0]
				hash_id = hashlib.sha256(chromosome+pos+ref+alt).hexdigest()


				# Some of the following may fail so wrap in try-except
				

				try:


					gene_list = pysam_extract.get_variant_genes_list(variant['transcript_data'])

					hgvs = pysam_extract.get_hgvs(variant['transcript_data'])

					rs_number = pysam_extract.get_rs_number(variant['transcript_data'])

				except:

					gene_list = []

					hgvs = "None"

					rs_number = "None"



				#Look for a variant in the database if we have not seen it before create a new one 

				try:

					new_variant = Variant.objects.get(variant_hash=hash_id)

				except Variant.DoesNotExist:

					new_variant = Variant(chromosome=chromosome, position=pos, ref= ref, alt=alt, variant_hash= hash_id, HGVS = hgvs, rs_number=rs_number, last_updated= timezone.now())

					new_variant.save()

					new_variant_count = new_variant_count+1

					for gene in gene_list:

						try:

							gene_model = Gene.objects.get(name = gene)

						except Gene.DoesNotExist:

							gene_model = Gene(name=gene)
							gene_model.save()
							new_gene_count = new_gene_count+1
						

						new_variant_gene = VariantGene(gene =gene_model, variant = new_variant)
						
						new_variant_gene.save()


				new_variant_sample = VariantSample(variant=new_variant, sample=new_sample)

				new_variant_sample.save()

				var_count = var_count +1

			self.stdout.write(self.style.SUCCESS('Complete'))
			self.stdout.write(self.style.SUCCESS(str(var_count)+ ' variants in file'))
			self.stdout.write(self.style.SUCCESS(str(new_variant_count)+ '  new variants inserted into database'))
			self.stdout.write(self.style.SUCCESS(str(new_gene_count)+ '  new genes inserted into database'))

			complete = True


		if complete != True:

			self.stdout.write(self.style.ERROR('BAD THINGS'))