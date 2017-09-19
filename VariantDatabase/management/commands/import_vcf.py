from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
from django.contrib.auth.models import User
import hashlib
import imp
from django.db import transaction
from django.utils import timezone


vcf_parser = imp.load_source('vcf_parser', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/parsers/vcf_parser.py')


class Command(BaseCommand):

	help = "imports a vcf"

	def add_arguments(self, parser):

		parser.add_argument('worksheet_id', nargs=1, type = str)
		parser.add_argument('vcf_file', nargs =1, type = str)
		parser.add_argument('sample_name', nargs=1, type = str)

	def handle(self, *args, **options):

		# Get the worksheet from the database
		# Display an error if we could not retrieve it and end program
		complete = False
		worksheet_name = options['worksheet_id'][0]

		try:

			worksheet = Worksheet.objects.get(name=worksheet_name)
			self.stdout.write(self.style.SUCCESS("Successfully found worksheet with pk: " + worksheet_name))

		except Worksheet.DoesNotExist:

			raise CommandError('There is no worksheet with the pk: ' + worksheet_name)


		# Now open the vcf file that has been provided and validate it
		# We will raise an error if this fails
		# Validation report will be of format [Boolean, message]

		vcf_file_path = options['vcf_file'][0]
		sample_name = options['sample_name'][0]

		validation_report = vcf_parser.validate_input(vcf_file_path, sample_name)


		if validation_report[0] == False:

			raise CommandError('Error opening vcf file: '+ validation_report[1])

		else:

			self.stdout.write(self.style.SUCCESS('The vcf file ' + vcf_file_path + ' was successfully opened and validated'))



		# Now try to process the data into the master list using the pysam_extact create_master_list 
		# Check what type of annotations we have too and display that in terminal
		# We could check more e.g. see if they have the neccecary vep annotations 

		try:

			data = vcf_parser.create_master_list(vcf_file_path, sample_name)
			total_variants = len(data)
			self.stdout.write(self.style.SUCCESS('Loaded data using vcf_parser - proceeding'))
			self.stdout.write(self.style.SUCCESS(str(total_variants)+ ' variants detected'))





			annotation_type = vcf_parser.vep_annotated(vcf_file_path)

			self.stdout.write(self.style.SUCCESS('VEP annotation detected'))

		except:

			raise CommandError('Could not process data using vcf_parser function')


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
		
			sample = Sample.objects.filter(worksheet = worksheet, name=sample_name)

			if len(sample) ==1:

				self.stdout.write(self.style.SUCCESS('Found sample ' +sample[0].name +  ' in worksheet ' + worksheet.name))

			else:


				raise CommandError('Error either no sample or >1 sample')


			sample = sample[0]

			"""

			if sample.vcf_file != None:

				raise CommandError('Sample ' + sample.name + ' has been processed before. Ending.')

			"""

			sample.vcf_file = vcf_file_path

			sample.save()

			self.stdout.write(self.style.SUCCESS('Processing Variants'))


			# Now loop through each variant in the vcf file and insert relevent data into the database

			new_variant_count = 0
			new_gene_count = 0
			var_count = 0
			var_sample_count = 0

			for variant in data:


				chromosome = variant['chrom']
				pos = str(variant['pos'])
				ref = variant['reference']
				alt = variant['alt_alleles'][0]
				hash_id = hashlib.sha256(chromosome+" "+pos+" "+ref+" "+alt).hexdigest()

				#print chromosome, pos				


				gene_list = vcf_parser.get_variant_genes_list(variant['transcript_data'])

				hgvsc = vcf_parser.get_hgvsc(variant['transcript_data'])

				hgvsp = vcf_parser.get_hgvsp(variant['transcript_data'])

				rs_number = vcf_parser.get_rs_number(variant['transcript_data'])

				worst_consequence = vcf_parser.worst_consequence(variant['transcript_data'])

				worst_consequence = Consequence.objects.get(name=worst_consequence)

				canonical = vcf_parser.get_canonical_transcript_name(variant['transcript_data'])

				max_af = vcf_parser.get_max_af(variant['transcript_data'])

				allele_frequencies = vcf_parser.get_allele_frequencies(variant['transcript_data'])

				clin_sig = vcf_parser.get_clin_sig(variant['transcript_data'])

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

					new_variant = Variant(chromosome=chromosome, position=pos,
					 ref= ref, alt=alt, variant_hash= hash_id, HGVSc = hgvsc, rs_number=rs_number,
					 last_updated= timezone.now(), HGVSp= hgvsp, worst_consequence=worst_consequence,
					 max_af= max_af,  af=af,  afr_af=afr_af, amr_af=amr_af,
					 eur_af=eur_af, eas_af=eas_af, sas_af=sas_af, exac_af=exac_af, exac_adj_af=exac_adj_af,
					 exac_afr_af= exac_afr_af, exac_amr_af=exac_amr_af,exac_eas_af=exac_eas_af, exac_fin_af=exac_fin_af,
					 exac_nfe_af = exac_nfe_af, exac_oth_af=exac_oth_af, exac_sas_af=exac_sas_af,esp_aa_af=esp_aa_af,esp_ea_af=esp_ea_af,clinical_sig=clin_sig)

					new_variant.save()

					new_variant_count = new_variant_count+1


					for gene in gene_list:

						try:

							gene_model = Gene.objects.get(name = gene[0])

						except Gene.DoesNotExist:

							gene_model = Gene(name=gene[0])
							gene_model.save()
							new_gene_count = new_gene_count+1


						
					#Now create transcripts


					for transcript_key in variant['transcript_data']:

						if transcript_key == "":

							try:

								transcript_model = Transcript.objects.get(name='no_transcript')

							except Transcript.DoesNotExist:

								transcript_model = Transcript(name = 'no_transcript', canonical=False)

								transcript_model.save()

						else:

							try:

								transcript_model = Transcript.objects.get(name=transcript_key)

							except Transcript.DoesNotExist:


								canonical = variant['transcript_data'][transcript_key]['CANONICAL']

								if canonical == 'YES':

									canonical = True
								else:

									canonical = False


								gene = variant['transcript_data'][transcript_key]['SYMBOL']

								if gene != "":


									gene = Gene.objects.get(name=gene)

									transcript_model = Transcript(name = transcript_key, canonical=canonical, gene =gene)

									transcript_model.save()

								else:
									transcript_model = Transcript(name = transcript_key, canonical=canonical)

									transcript_model.save()


						#now create transcriptvariant model

						consequence = variant['transcript_data'][transcript_key]['Consequence']
						exon = variant['transcript_data'][transcript_key]['EXON']
						intron = variant['transcript_data'][transcript_key]['INTRON']
						hgvsc_t = variant['transcript_data'][transcript_key]['HGVSc']
						hgvsp_t = variant['transcript_data'][transcript_key]['HGVSp']
						codons = variant['transcript_data'][transcript_key]['Codons']
						cdna_position = variant['transcript_data'][transcript_key]['cDNA_position']
						cds_position = variant['transcript_data'][transcript_key]['CDS_position']
						protein_position = variant['transcript_data'][transcript_key]['Protein_position']
						amino_acids = variant['transcript_data'][transcript_key]['Amino_acids']
						picked = variant['transcript_data'][transcript_key]['PICK']

						if picked == '1':

							picked = True

						else:

							picked =False

						#print chromosome, pos, type(transcript_model), transcript_model.pk

						variant_transcript = VariantTranscript(variant = new_variant, transcript=transcript_model, consequence=consequence, exon=exon, intron = intron, hgvsc =hgvsc_t, hgvsp = hgvsp_t,codons=codons,cdna_position=cdna_position, protein_position=protein_position, amino_acids=amino_acids, picked =picked)
											

						variant_transcript.save()




				genotype = variant['genotype']
				caller = variant['Caller']
				allele_depth = variant['allele_depth']
				filter_status = variant['filter_status']
				total_count_forward = variant['TCF']
				total_count_reverse = variant['TCR']
				vafs = ":".join(str(x) for x in variant['VAFS'])

				new_variant_sample = VariantSample(variant=new_variant, sample=sample, genotype = genotype, caller=caller, allele_depth=allele_depth, filter_status=filter_status, total_count_forward=total_count_forward, total_count_reverse=total_count_reverse,vafs=vafs )

				new_variant_sample.save()

				var_sample_count = var_sample_count +1

				var_count = var_count +1


			self.stdout.write(self.style.SUCCESS('Complete'))
			self.stdout.write(self.style.SUCCESS(str(var_count)+ ' variants in file'))
			self.stdout.write(self.style.SUCCESS(str(new_variant_count)+ '  new variants inserted into database'))
			self.stdout.write(self.style.SUCCESS(str(new_gene_count)+ '  new genes inserted into database'))
			self.stdout.write(self.style.SUCCESS(str(var_sample_count)+ ' variants in summary   '))

			complete = True


			#raise CommandError('Sample ' + sample.name + ' has been processed before. Ending.')

		if complete != True:

			self.stdout.write(self.style.ERROR('BAD THINGS'))