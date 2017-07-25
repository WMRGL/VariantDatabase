from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from variant_classifier import classify
from django.db.models import Q
import pysam_extract
from django.contrib.contenttypes.models import ContentType
from auditlog.models import LogEntry
from auditlog.registry import auditlog

class Section(models.Model):
	"""
	The Section model represents a section within the WMRGL laboratory e.g. Germline
	This is stored in the database to allow flexibility.
	Each Section can contain many Worksheets.

	"""

	owner = models.ForeignKey('auth.User')
	title = models.CharField(max_length=200)
	description = models.TextField()

	def __str__(self):
		return self.title


	def get_worksheets(self):

		"""
		Return all worksheets related 

		"""

		all_worksheets = Worksheet.objects.filter(sub_section__section=self)

		return all_worksheets



class SubSection(models.Model):
	"""
	A Model to represent a subsection.
	This is similar to the concept of a project e.g. MPN
	Can also represent a panel or chemisry for example.

	"""
	name = models.CharField(max_length=25, primary_key=True)
	section = models.ForeignKey(Section)
	

	#QC sample pass info - the levels needed for a sample to pass

	min_read_count = models.IntegerField()
	min_average_read_length = models.IntegerField()
	max_average_read_length = models.IntegerField()
	min_mapped_rate = models.FloatField()
	max_error_rate = models.FloatField()

	#filter settings

	stop_lost = models.BooleanField()
	stop_gained = models.BooleanField()
	start_lost = models.BooleanField()
	splice_region_variant = models.BooleanField()
	splice_donor_variant = models.BooleanField()
	splice_acceptor_variant = models.BooleanField()
	regulatory_region_variant = models.BooleanField()
	regulatory_region_amplification = models.BooleanField()
	regulatory_region_ablation = models.BooleanField()
	protein_altering_variant = models.BooleanField()
	non_coding_transcript_variant = models.BooleanField()
	non_coding_transcript_exon_variant = models.BooleanField()
	missense_variant = models.BooleanField()
	mature_miRNA_variant = models.BooleanField()
	intron_variant = models.BooleanField()
	intergenic_variant = models.BooleanField()
	inframe_insertion = models.BooleanField()
	inframe_deletion = models.BooleanField()
	incomplete_terminal_codon_variant = models.BooleanField()
	frameshift_variant = models.BooleanField()
	feature_truncation = models.BooleanField()
	feature_elongation = models.BooleanField()
	downstream_gene_variant = models.BooleanField()
	coding_sequence_variant = models.BooleanField()
	TF_binding_site_variant = models.BooleanField()
	TFBS_amplification = models.BooleanField()
	TFBS_ablation = models.BooleanField()
	NMD_transcript_variant = models.BooleanField()
	five_prime_UTR_variant = models.BooleanField()
	three_prime_UTR_variant = models.BooleanField()
	freq_max_af = models.FloatField()


	def __str__(self):
		return self.name

	def create_filter_dict(self):
		"""
		Return a dictionary with all the filter settings in e.g. stop_lost=False

		"""


		

class Worksheet(models.Model):
	"""
	The Worksheet model represents a laboratory worksheet.
	Each Worksheet belongs to a Section.
	Each Worksheet can have many Samples assigned to it.

	"""

	choices =(
			('1', 'New Worksheet - Awaiting Sequencing'),
			('2', 'Awaiting QC Check'),
			('3', 'Analysis Underway'),
			('4', 'Complete'),
			('5', 'Failed'))
			

	name = models.CharField(max_length=100, unique=True)
	sub_section = models.ForeignKey(SubSection)
	comment = models.TextField()
	status = models.CharField(max_length=1, choices = choices)


	def __str__(self):
		return self.name

	def get_status(self):
		"""
		Returns current status.
		"""
		choices =(
				('1', 'New Worksheet - Awaiting Sequencing'),
				('2', 'Awaiting QC Check'),
				('3', 'Analysis Underway'),
				('4', 'Complete'),
				('5', 'Failed'))

		try:

			return choices[int(self.status)-1][1]

		except:

			return None

	def awaiting_qc_approval(self):
		"""
		Returns True if we are at the first stage i.e 'New Worksheet'.
		"""

		if self.status == '1':

			return True

		else:

			return False

	def get_history(self):
		"""
		Returns entire history from the audit log.
		"""

		content_type = ContentType.objects.get(app_label ='VariantDatabase', model='worksheet')

		return LogEntry.objects.filter(object_pk = self.pk, content_type=content_type)

	def get_creation_date(self):
		"""
		Returns creation date.
		"""

		try:

			content_type = ContentType.objects.get(app_label ='VariantDatabase', model='worksheet')

			return LogEntry.objects.filter(object_pk = self.pk, content_type=content_type, action=0).order_by('timestamp')[0].timestamp

		except:

			return None


	def get_quality_data(self):

		data = ReadLaneQuality.objects.filter(worksheet=self).order_by('read', 'lane')

		data_list = []

		read_num = None

		for read_lane in data:

			if read_lane.read != read_num:

				read_num = read_lane.read

				data_list.append([read_lane])

			else:

				data_list[len(data_list)-1].append(read_lane)


		return data_list

	def qc_present(self):
		"""
		Returns True if QC has been uploaded.
		"""

		data = ReadLaneQuality.objects.filter(worksheet=self)

		if data.exists():

			return True

		else:

			return False





class Sample(models.Model):
	"""
	The Sample model holds information on a particular sample
	There can be many samples in a Worksheet.
	Each sample must have a unique name.
	Each sample contains a link to a VCF file where the data is (originally) stored.

	"""
	choices =(
			('1', 'New Sample'),
			('2', 'Awaiting 1st Check'),
			('3', 'Awaiting 2nd Check'),
			('4', 'Complete'))


	name = models.CharField(max_length=50)
	worksheet = models.ForeignKey(Worksheet)
	vcf_file = models.TextField() 
	visible = models.BooleanField() #To allow the hiding of a sample
	status = models.CharField(max_length=1, choices = choices)

	sample_id = models.CharField(max_length=50) #from sample sheet
	sample_plate = models.CharField(max_length =50)
	sample_well = models.CharField(max_length =10)
	i7_index_id = models.IntegerField()
	index = models.CharField(max_length =50)
	sample_project = models.CharField(max_length =50, null=True, blank=True)

	#QC data from SamStats

	raw_total_sequences = models.IntegerField(null=True)
	filtered_sequences = models.IntegerField(null=True)
	sequences = models.IntegerField(null=True)
	first_fragments = models.IntegerField(null=True)
	last_fragments = models.IntegerField(null=True)
	reads_mapped = models.IntegerField(null=True)
	reads_mapped_and_paired = models.IntegerField(null=True)
	reads_unmapped = models.IntegerField(null=True)
	reads_properly_paired = models.IntegerField(null=True)
	reads_paired = models.IntegerField(null=True)
	reads_duplicated = models.IntegerField(null=True)
	reads_MQ0 = models.IntegerField(null=True)
	reads_QC_failed = models.IntegerField(null=True)
	non_primary_alignments = models.IntegerField(null=True)
	total_length = models.IntegerField(null=True)
	bases_mapped = models.IntegerField(null=True)
	bases_mapped_cigar = models.IntegerField(null=True)
	bases_trimmed = models.IntegerField(null=True)
	bases_duplicated = models.IntegerField(null=True)
	mismatches = models.IntegerField(null=True)
	average_length = models.IntegerField(null=True)
	maximum_length = models.IntegerField(null=True)
	average_quality = models.FloatField(null=True)
	insert_size_average = models.FloatField(null=True)
	insert_size_standard_deviation = models.FloatField(null=True)
	inward_oriented_pairs = models.IntegerField(null=True)
	outward_oriented_pairs = models.IntegerField(null=True)
	pairs_with_other_orientation = models.IntegerField(null=True)
	pairs_on_different_chromosomes = models.IntegerField(null=True)

	#QC images from SamStats

	acgt_cycles_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	coverage_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	gc_content_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	gc_depth_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	indel_cycles_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	indel_dist_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	insert_size_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	quality_cycle_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	quality_cycle_read_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	quality_cycle_read_freq_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	quality_heatmap_image = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)

	def __str__(self):
		return self.name

	def already_exists(self, query_name):

		"""
		Checks if a sample with that name already exists so can be rejected.
		Used in the import_vcf.py management command.

		"""

		count = Sample.objects.filter(name=query_name).count()

		if count >0:

			return True

		else:

			return False


	def get_variants(self):
		"""
		Look in all VariantSample objects.
		Return all variants linked with this sample.
		"""
		variant_samples =VariantSample.objects.filter(sample=self).values_list('variant_id', flat=True)

		variants = Variant.objects.filter(variant_hash__in= variant_samples).order_by('worst_consequence__impact', 'max_af')

		return variants


	def get_status(self):
		"""
		Returns current status.
		"""
		choices =(
				('1', 'New Sample'),
				('2', 'Awaiting 1st Check'),
				('3', 'Awaiting 2nd Check'),
				('4', 'Complete'))

		try:

			return choices[int(self.status)-1][1]

		except:

			return None


	def variant_query_set_summary(self, variant_query_set):
		"""
		Summerises the data in a variant queryset e.g. how many variants.

		"""

		summary_dict = {}

		summary_dict['total'] = variant_query_set.count()

		summary_dict['missense_count'] = variant_query_set.filter(worst_consequence__name='missense_variant').count()

		summary_dict['indel_count'] = variant_query_set.filter(Q(worst_consequence__name='inframe_deletion') | Q(worst_consequence__name='inframe_insertion') | Q(worst_consequence__name='frameshift_variant') ).count()

		summary_dict['lof_count'] = variant_query_set.filter(worst_consequence__impact__lte=8).count()
		summary_dict['synonymous'] = variant_query_set.filter(worst_consequence__name='synonymous_variant').count()

		return summary_dict

	def total_variant_summary(self):

		variants = self.get_variants()

		return self.variant_query_set_summary(variants)


	def get_error_rate(self):

		if self.mismatches == None or self.bases_mapped_cigar == None:

			return None

		else:

			return self.mismatches /float(self.bases_mapped_cigar)




	def get_mapped_percentage(self):
		"""
		Get percentage of reads mapped
		"""
		if self.reads_mapped == None or self.raw_total_sequences ==None:

			return None

		else:

			return float(self.reads_mapped)/float(self.raw_total_sequences)


	def sample_qc_passed(self):

		if (self.raw_total_sequences == None or 
			self.average_length == None or
			self.get_mapped_percentage() == None or
			self.get_error_rate() == None):

			return 'NO QC'

		else:

			subsection = self.worksheet.sub_section

			if (self.raw_total_sequences < subsection.min_read_count or 
				self.average_length < subsection.min_average_read_length or 
				self.average_length > subsection.max_average_read_length or
				self.get_mapped_percentage() < subsection.min_mapped_rate or
				self.get_error_rate() > subsection.max_error_rate):


				return 'FAIL'

			else:

				return 'PASS'




class VariantInformation(models.Model):

	"""
	Model for holding an annotation type in the vcf.
	
	If a user has a VariantInformation object connected with them in the UserSetting model then that field will be displayed in the VCF.

	"""

	information  = models.CharField(max_length=50)
	label = models.CharField(max_length=50, null=True, blank=True)
	description  = models.TextField()

	def __str__(self):
		return self.information

class UserSetting(models.Model):

	"""

	A user's current settings. If a VariantInformation model is present in this for a user 
	then that column will be displayed in the views_sample_variants view e.g view vcf


	"""
	user = models.ForeignKey('auth.User')
	variant_information = models.ForeignKey(VariantInformation)

	def __str__(self):
		return self.variant_information.information + " " + self.user.user_name

class Consequence(models.Model):
	"""
	A model to hold the VEP consequences see : http://www.ensembl.org/info/genome/variation/predicted_data.html
	The worst_consequence field in the Variant model links to an object in this model.

	"""

	name = models.CharField(max_length = 100, primary_key =True)
	impact = models.IntegerField() #number giving impact rating 1-28

	def __str__(self):
		return self.name

class Gene(models.Model):

	"""
	Stores genes that have been seen before.
	Each Transcript links to a Gene.
	Each Variant can fall in many Transcripts - VariantTranscript 


	"""

	name = models.CharField(max_length=50, db_index=True, unique=True)
	strand = models.IntegerField() # 1 or -1


	def __str__(self):
		return self.name



	def get_all_variants(self, consequence_filter):
		"""
		Returns all variants within a Gene.
		The consequence filter allows the function to return only variants below a certain impact e.g. loss of function

		"""
		variants = VariantTranscript.objects.filter(transcript__gene = self).values('variant').distinct()

		variants = Variant.objects.filter(variant_hash__in=variants).filter(worst_consequence__impact__lte=consequence_filter)

		if self.strand == -1:

			variants = variants.order_by('-position')

		else:

			variants = variants.order_by('position')

		return variants


	def get_canonical_transcript(self):
		"""
		A Gene may have multiple Transcripts assosiated with it.
		This function returns the canonical Transcript for the gene

		"""

		canonical = Transcript.objects.filter(gene=self, canonical=True)

		return canonical

	def get_transcripts(self):
		"""
		Return all Transcripts assosiated with a Gene.

		"""

		return Transcript.objects.filter(gene=self)




class Transcript(models.Model):
	"""
	Each Gene can be associated with one or more Transcripts.
	A Transcript can be associated with a Gene, although this is not required.

	"""

	name = models.CharField(max_length=64, primary_key=True)
	canonical = models.BooleanField()
	gene = models.ForeignKey(Gene, null=True)

	def __str__(self):
		return self.name

	def get_gene(self):
		"""
		Return the gene that a Transcript falls within.
		Returns None if the Transcript is not associated with a Gene.

		"""

		if self.gene is not None:

			return self.gene.name

		else:

			return None


class Variant(models.Model):

	"""
	The Variant model holds unique variants.

	If a variant is seen in another vcf it will not appear twice in this model.

	The variant_hash field is used as a key (sha256) chr+pos+ref+alt N.B note the "+" symbol is actually used e.g chr + '+' + pos


	"""
	#Variant Data
	variant_hash = models.CharField(max_length=64, primary_key = True)
	chromosome  = models.CharField(max_length=25)
	position  = models.IntegerField()
	ref = models.TextField()
	alt = models.TextField()
	HGVSc =models.TextField()
	HGVSp = models.TextField()
	last_updated =  models.DateTimeField(default = timezone.now)
	rs_number = models.CharField(max_length =50)
	worst_consequence = models.ForeignKey(Consequence)
	clinical_sig = models.TextField()

	#Frequency Data
	max_af = models.FloatField()
	af = models.FloatField()
	afr_af = models.FloatField()
	amr_af = models.FloatField()
	eur_af = models.FloatField()
	eas_af = models.FloatField()
	sas_af = models.FloatField()
	exac_af = models.FloatField()
	exac_adj_af = models.FloatField()
	exac_afr_af = models.FloatField()
	exac_amr_af = models.FloatField()
	exac_eas_af = models.FloatField()
	exac_fin_af = models.FloatField()
	exac_nfe_af = models.FloatField()
	exac_oth_af = models.FloatField()
	exac_sas_af = models.FloatField()
	esp_ea_af = models.FloatField()
	esp_aa_af = models.FloatField()

	#Counts 
	allele_count = models.IntegerField()
	sample_count = models.IntegerField()

	def __str__(self):
		return self.chromosome + " " + str(self.position) + " " +  self.ref + " " +self.alt


	def get_samples_with_variant(self):
		"""
		Returns all samples in which the Variant has been found.
		Note that VariantSample objects are only created for variants that meat certain conditions e.g < 5% freq and not synomynous

		"""

		samples =VariantSample.objects.filter(variant=self)

		return samples


	def get_genes(self):
		"""
		Return all Genes that a variant is found in.

		"""

		variant_transcripts = VariantTranscript.objects.filter(variant =self)

		my_list = []

		for var in variant_transcripts:

			if var.transcript.gene is not None:

				my_list.append(var.transcript.gene)


		return list(set(my_list))

	def hgvsc_list(self):
		"""
		Return hgvs cDNA as a list
		"""

		hgvs_list = []

		split = self.HGVSc.split(",")

		return split

	def hgvsp_list(self):
		"""
		Return hgvs Protein as a list

		"""

		hgvs_list = []

		split = self.HGVSp.split(",")

		return split


	def display_ids(self):
		"""
		Return IDs as a list e.g ids seperated by & symbols
		"""

		variant_ids = self.rs_number.split("&")

		return variant_ids


	def rated_as_pathogenic(self):
		"""	
		Check through ACMG sections and see if the variant has ever been classified as pathogenic.

		Note that this does not inlcude the new Reporting section.

		TODO: update to include reporting section. Need to do more requirements capturing to see if this is necessary.  
		"""


		classifications = Interpretation.objects.filter(variant=self)

		path_classifications = ["Pathogenic (Ia)","Pathogenic (Ib)","Pathogenic (Ic)", "Pathogenic (Id)", "Pathogenic (II)", "Pathogenic (IIIa)",
							"Pathogenic (IIIb)", "Pathogenic (IIIc)", "Likely Pathogenic (I)", "Likely Pathogenic (II)", "Likely Pathogenic (III)",
							"Likely Pathogenic (IV)", "Likely Pathogenic (V)", "Likely Pathogenic (VI)"
							]

		if classifications == False:

			return False

		else:

			for classification in classifications:

				if classification.classification in path_classifications:

					return True


		return False



	def same_codon_missense(self):
		"""
		Is the variant in the same codon as an existing variant in the DB?

		How does this work?

		1) Only look at missense variants
		2) Get all variants that could be in the same codon e.g. +2 or -2 in position.
		3) Get the hgvsp for our variant
		4) For each of the variants that are nearby i.e. the query in part 2
			4a) only look at missense variants
			4b) get the hgvp for that variant
			4c) for each of the hgvsp for that variant
				4d) See if the codon is the same as the original
				4e) if so then add to list to be returned


		"""

		if self.worst_consequence.name == 'missense_variant':

			same_codon = []

			position_range =2

			variant_list = Variant.objects.filter(chromosome=self.chromosome, position__range=(self.position-position_range,self.position+position_range )).exclude(variant_hash =self.variant_hash)

			transcript_list =[]

			self_hgvsp = self.hgvsp_list()

			for hgvsp in self_hgvsp:

				transcript, codon = pysam_extract.extract_codon_from_hgvs(hgvsp)

				if transcript == False:

					return None

				transcript_list.append((transcript.strip(), codon))


			for variant in variant_list:

				if variant.worst_consequence.name == 'missense_variant':

					variant_hgvsp_list = variant.hgvsp_list()

					transcript_list_vars =[]

					for hgvsp in variant_hgvsp_list:

						transcript, codon = pysam_extract.extract_codon_from_hgvs(hgvsp)

						transcript_list_vars.append((transcript.strip(),codon))

						both = set(transcript_list) & set(transcript_list_vars)


						if len(both) >0:

							same_codon.append(variant)

			if len(list(set(same_codon))) == 0:

				return None

			else:

				return list(set(same_codon))



	def get_other_alleles(self):
		"""	
		Returns any other variants at the same position
		"""

		other_alleles = Variant.objects.filter(chromosome=self.chromosome,position=self.position).exclude(variant_hash =self.variant_hash)

		return other_alleles


	def get_similar(self):

		"""
		if variant is missense returns variants in the same codon
		elif codon is frameshift, transcript ablation, stop-gained, stop-lost, start-lost returns similar in the same gene
		elif splice returns splice in the same gene
		elif inframe indels returns same in same gene
		elif transcript amplification returns others in same gene

		"""

		variants = None

		condition_one = ['missense_variant']
		condition_two = ['transcript_ablation', 'stop_gained' ,'frameshift_variant','stop_lost','start_lost']
		condition_three = ['splice_acceptor_variant', 'splice_donor_variant', 'splice_region_variant']
		condition_four =['inframe_insertion', 'inframe_deletion']
		condition_five = ['transcript_amplification']


		if self.worst_consequence.name in condition_one :

			return self.same_codon_missense()

		elif self.worst_consequence.name in condition_two:

			my_list =[]

			genes = self.get_genes()

			for gene in genes:

				variants = VariantTranscript.objects.filter(transcript__gene = gene).values('variant').distinct() #get variants in same gene

				variants = Variant.objects.filter(variant_hash__in=variants).filter(Q(worst_consequence__name = 'transcript_ablation') |  Q(worst_consequence__name = 'stop_gained') | Q(worst_consequence__name = 'frameshift_variant')| Q(worst_consequence__name = 'stop_lost')| Q(worst_consequence__name = 'start_lost'))

				variants = variants.exclude(variant_hash =self.variant_hash)

				my_list.append(variants)

			return list(set(my_list))


		elif self.worst_consequence.name in condition_three:

			my_list =[]

			genes = self.get_genes()

			for gene in genes:

				variants = VariantTranscript.objects.filter(transcript__gene = gene).values('variant').distinct() #get variants in same gene

				variants = Variant.objects.filter(variant_hash__in=variants).filter(Q(worst_consequence__name = 'splice_acceptor_variant') |  Q(worst_consequence__name = 'splice_donor_variant') | Q(worst_consequence__name = 'splice_region_variant'))

				variants = variants.exclude(variant_hash =self.variant_hash)

				my_list.append(variants)

			return list(set(my_list))

		elif self.worst_consequence.name in condition_four:

			my_list =[]

			genes = self.get_genes()

			for gene in genes:

				variants = VariantTranscript.objects.filter(transcript__gene = gene).values('variant').distinct() #get variants in same gene

				variants = Variant.objects.filter(variant_hash__in=variants).filter(Q(worst_consequence__name = 'inframe_insertion') |  Q(worst_consequence__name = 'inframe_deletion'))

				variants = variants.exclude(variant_hash =self.variant_hash)

				my_list.append(variants)

			return list(set(my_list))

		elif self.worst_consequence.name in condition_five:

			my_list =[]

			genes = self.get_genes()

			for gene in genes:

				variants = VariantTranscript.objects.filter(transcript__gene = gene).values('variant').distinct() #get variants in same gene

				variants = Variant.objects.filter(variant_hash__in=variants).filter(Q(worst_consequence__name = 'transcript_amplification'))

				variants = variants.exclude(variant_hash =self.variant_hash)

				my_list.append(variants)

			return list(set(my_list))

		else:

			return None

	def get_picked_transcript(self):

		"""
		Return the transcript that has been picked by VEP
		This is the variant with '1' in the PICK field of the VEP annotation
		Data stoed in VariantTranscript model

		"""

		picked = VariantTranscript.objects.filter(variant=self).filter(picked=True)[0].transcript.name

		return picked






class VariantSample(models.Model):

	"""
	The VariantSample model stores whcih samples a Variant has appeared in.


	Allows queries such as 'which other samples have we seen this variant in?'

	"""

	variant = models.ForeignKey(Variant)
	sample = models.ForeignKey(Sample)

	def __str__(self):
		return self.variant + self.sample
		



class ClassificationCode(models.Model):
	"""
	For the ACMG guidlines e.g PVS1

	"""

	text = models.CharField(max_length = 25)

	def __str__(self):
		return self.text

class Question(models.Model):
	"""
	Question in the ACMG guidelines
	"""

	text = models.CharField(max_length =300)
	description = models.TextField()
	start = models.BooleanField()
	end = models.BooleanField()
	classification = models.ForeignKey(ClassificationCode, null=True)

	def __str__(self):
		return self.text


class Interpretation(models.Model):
	"""
	An interpretation from the ACMG guidlines
	"""

	author = models.ForeignKey('auth.User')
	variant = models.ForeignKey(Variant)
	sample = models.ForeignKey(Sample)
	finished = models.BooleanField()
	date = models.DateTimeField(default = timezone.now)
	classification = models.CharField(max_length =25)

	def __str__(self):

		return str(self.pk)


	def get_classification(self):
		"""
		Returns the final classification of the Interpretation e.g. likely pathogenic

		"""

		all_answers = UserAnswer.objects.filter(interpretation=self.pk)

		classifications =[]

		for answer in all_answers:

			if answer.user_answer ==  '1':

				classifications.append(answer.user_question.classification.text)

		final_classification =classify(classifications)

		return final_classification


class UserAnswer(models.Model):
	"""
	Stores the answers to the questions of the ACMG guidelines
	"""

	interpretation = models.ForeignKey(Interpretation)
	user_question = models.ForeignKey(Question, null=True )
	date = models.DateTimeField(default = timezone.now)
	user_answer = models.CharField(max_length=30, default="")


	def __str__(self):

		return str(self.pk)

class VariantTranscript(models.Model):
	"""
	A Variant can be in mutiple Transcripts.
	This model holds the information on how a particular Variant affects a Transcript.

	"""

	variant = models.ForeignKey(Variant)
	transcript = models.ForeignKey(Transcript)
	consequence = models.TextField()
	exon = models.CharField(max_length =25)
	intron = models.CharField(max_length =25)
	hgvsc = models.TextField()
	hgvsp = models.TextField()
	picked =models.BooleanField()
	codons = models.TextField()
	cdna_position = models.CharField(max_length=20)
	protein_position = models.CharField(max_length=20)
	amino_acids = models.TextField()

	def __str__(self):

		return self.variant.chromosome+str(self.variant.position)

class Report(models.Model):
	"""
	A user can create a Report for a particular Sample

	"""
	choices =(
			('1', 'New Report'),
			('2', 'Awaiting 1st Check'),
			('3', 'Awaiting 2nd Check'),
			('4', 'Complete'))

	sample = models.ForeignKey(Sample)
	status = models.CharField(max_length=1, choices = choices)


	def get_history(self):

		content_type = ContentType.objects.get(app_label ='VariantDatabase', model='report')

		return LogEntry.objects.filter(object_pk = self.pk, content_type=content_type)

	def get_creation_date(self):

		content_type = ContentType.objects.get(app_label ='VariantDatabase', model='report')

		return LogEntry.objects.filter(object_pk = self.pk, content_type=content_type, action=0).order_by('timestamp')[0].timestamp

	def get_author(self):

		content_type = ContentType.objects.get(app_label ='VariantDatabase', model='report')

		return LogEntry.objects.filter(object_pk = self.pk, content_type=content_type, action=0).order_by('timestamp')[0].actor

	def get_status(self):

		choices =(
			('1', 'New Report'),
			('2', 'Awaiting 1st Check'),
			('3', 'Awaiting 2nd Check'),
			('4', 'Complete'))

		return choices[int(self.status)-1][1]

	def initialise_report(self):
		"""
		Create ReportVariant Objects for the report

		"""
		variants = self.sample.get_variants()

		for variant in variants:

			new_report_variant = ReportVariant(variant=variant, report=self, status='1')

			new_report_variant.save()

		return None

class ReportVariant(models.Model):
	"""
	Stores what the user has decided for each Variant in a sample.

	"""
	choices =(
			('1', 'None'),
			('2', 'Pathogenic'),
			('3', 'Benign'),
			('4', 'VUS'))

	variant = models.ForeignKey(Variant)
	report = models.ForeignKey(Report)
	status = models.CharField(max_length=1, choices = choices) #e.g pathogenic


	def get_status(self):

		choices =(
			('1', 'None'),
			('2', 'Pathogenic'),
			('3', 'Benign'),
			('4', 'VUS'))

		return choices[int(self.status)-1][1]


class ReadLaneQuality(models.Model):

	worksheet = models.ForeignKey(Worksheet)
	read = models.IntegerField()
	lane = models.IntegerField()

	yield_g = models.FloatField()
	density = models.FloatField()
	cluster_count_pf = models.FloatField()
	cluster_count = models.FloatField()
	phasing = models.FloatField()
	prephasing = models.FloatField()
	read_count = models.FloatField()
	reads_pf = models.FloatField()
	percent_gt_q30 = models.FloatField(null=True)
	percent_aligned = models.FloatField(null=True)
	error_rate = models.FloatField(null=True)
	error_rate_35 = models.FloatField(null=True)
	error_rate_50 = models.FloatField(null=True)
	error_rate_75 = models.FloatField(null=True)
	error_rate_100 = models.FloatField(null=True)


	def format_density(self):

		return self.density/1000

	def cluster_pf_percent(self):

		return (self.cluster_count_pf/self.cluster_count)*100

	def format_reads(self):

		return self.read_count/1000000

	def format_reads_pf(self):

		return self.reads_pf/1000000




auditlog.register(Report)
auditlog.register(Worksheet)