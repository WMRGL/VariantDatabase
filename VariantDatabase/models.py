from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from variant_classifier import classify
import imp

pysam_extract = imp.load_source('pysam_extract', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/Pysam/pysam_extract.py')


class Section(models.Model):

	owner = models.ForeignKey('auth.User')
	title = models.CharField(max_length=200)
	description = models.TextField()

	def __str__(self):
		return self.title


	def get_worksheets(self):

		all_worksheets = Worksheet.objects.filter(section=self)

		return all_worksheets



class Worksheet(models.Model):

	name = models.CharField(max_length=100, default = " ")
	section = models.ForeignKey(Section)
	comment = models.TextField()


	def __str__(self):
		return self.name


	def get_status(self):

		try:

	 		current_status = WorksheetStatusUpdate.objects.filter(worksheet=self).order_by('-date')[0].status.name

	 	except:

	 		current_status = 'No Status Found'

	 	return current_status




	def awaiting_qc_approval(self):


		status = self.get_status()

		if status == 'New Worksheet -  Awaiting QC Check' or status == 'No Status Found':

			return True

		else:

			return False

	def get_history(self):

		try:

	 		current_status = WorksheetStatusUpdate.objects.filter(worksheet=self).order_by('date')

	 	except:

	 		current_status = []

	 	return current_status



class Sample(models.Model):


	"""
	The Sample model holds information on a particlar sample

	There can be many samples in a Worksheet

	Each sample has a vcf file associated with it


	"""


	name = models.CharField(max_length=50)
	patient_initials = models.CharField(max_length=50)
	worksheet = models.ForeignKey(Worksheet)
	vcf_file = models.TextField()
	visible = models.BooleanField()


	def __str__(self):
		return self.name

	def already_exists(self, query_name):

		"""
		Checks if a sample with that name already exists so can be rejected

		"""
		count = Sample.objects.filter(name=query_name).count()

		if count >0:

			return True

		else:

			return False


	def get_status(self):

		try:

			current_status = SampleStatusUpdate.objects.filter(sample=self).order_by('-date')[0].status.name

		except:


			current_status = 'No Status Found'

		return current_status



	def get_history(self):

		try:

			current_status = SampleStatusUpdate.objects.filter(sample=self).order_by('-date')

		except:


			current_status = []

		return current_status




class SampleStatus(models.Model):

	"""

	Model to hold all possible sample statuses e.g. 'undergoing analysis', 'complete'

	"""

	name = models.CharField(max_length=100)

	def __str__(self):
		return self.name


class WorkSheetStatus(models.Model):

	"""

	Model to hold all possible worksheet statuses e.g. 'undergoing analysis', 'complete'

	"""

	name = models.CharField(max_length=100)	

	def __str__(self):
		return self.name

class SampleStatusUpdate(models.Model):

	"""
	Model to hold the status changes of a sample

	When a the sample is created or its status updated a new edition will be inserted

	Allows the tracking of the sample status


	"""



	sample = models.ForeignKey(Sample)
	status = models.ForeignKey(SampleStatus)
	date = models.DateTimeField(blank=True, null=True)
	user = models.ForeignKey('auth.User')


class WorksheetStatusUpdate(models.Model):


	"""
	Model to hold the status changes of a sample

	When a the sample is created or its status updated a new edition will be inserted

	Allows the tracking of the sample status


	"""

	worksheet = models.ForeignKey(Worksheet)
	status = models.ForeignKey(WorkSheetStatus)
	date = models.DateTimeField(blank=True, null=True)
	user = models.ForeignKey('auth.User')

class VariantInformation(models.Model):

	"""
	Model for holding an annotation type in the vcf.
	
	User can then select which of these they want to view.


	"""

	information  = models.CharField(max_length=50)
	label = models.CharField(max_length=50, null=True, blank=True)
	description  = models.TextField()


class UserSetting(models.Model):

	"""

	A user's current settings. If a VariantInformation model is present in this for a user 
	then that column will be displayed in the views_sample_variants view


	"""
	user = models.ForeignKey('auth.User')
	variant_information = models.ForeignKey(VariantInformation)



class Consequence(models.Model):

	name = models.CharField(max_length = 100, primary_key =True)
	impact = models.IntegerField()

	def __str__(self):
		return self.name








class Gene(models.Model):

	"""
	Stores genes that have been seen before


	"""

	name = models.CharField(max_length=50, db_index=True, unique=True)
	strand = models.IntegerField()


	def __str__(self):
		return self.name



	def get_all_variants(self):


		variants = VariantTranscript.objects.filter(transcript__gene = self).values('variant').distinct()

		variants = Variant.objects.filter(variant_hash__in=variants)

		if self.strand == -1:

			variants = variants.order_by('-position')

		else:

			variants = variants.order_by('position')

		return variants









class Transcript(models.Model):

	name = models.CharField(max_length=64, primary_key=True)
	canonical = models.BooleanField()
	gene = models.ForeignKey(Gene, null=True)

	def __str__(self):
		return self.name










class Variant(models.Model):

	"""
	The Variant model holds unique variants.

	If a variant is seen in another vcf it will not appear twice in this model.

	The variant_hash field is used as a key (sha256) chr+pos+ref+alt


	"""
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

	allele_count = models.IntegerField()

	def __str__(self):
		return self.chromosome + str(self.position) + self.ref + self.alt


	def get_samples_with_variant(self):

		samples =VariantSample.objects.filter(variant=self)

		return samples


	def get_genes(self):

		variant_transcripts = VariantTranscript.objects.filter(variant =self)

		my_list = []

		for var in variant_transcripts:

			if var.transcript.gene is not None:

				my_list.append(var.transcript.gene)


		return list(set(my_list))




	def hgvsc_list(self):

		hgvs_list = []

		split = self.HGVSc.split(",")

		return split

	def hgvsp_list(self):

		hgvs_list = []

		split = self.HGVSp.split(",")

		return split


	def display_ids(self):

		variant_ids = self.rs_number.split("&")

		return variant_ids


	def rated_as_pathogenic(self):


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


	def variants_in_same_position(self):

		variant_list = Variant.objects.filter(chromosome=self.chromosome, position =self.position).exclude(variant_hash =self.variant_hash)

		return variant_list


	def variants_in_similar_position(self):

		range = 50

		variant_list = Variant.objects.filter(chromosome=self.chromosome, position__range=(self.position-range,self.position+range )).exclude(variant_hash =self.variant_hash)

		return variant_list



	def same_codon_missense(self):
		"""
		Is the variant in the same codon as an existing variant in the DB?

		"""

		if self.worst_consequence.name == 'missense_variant':

			same_codon = []

			range =2

			variant_list = variant_list = Variant.objects.filter(chromosome=self.chromosome, position__range=(self.position-range,self.position+range )).exclude(variant_hash =self.variant_hash)

			
			transcript_list =[]

			self_var_hgvsp = self.hgvsp_list()

			for hgvsp in self_var_hgvsp:

				transcript, codon = pysam_extract.extract_codon_from_hgvs(hgvsp)

				transcript_list.append((transcript.strip(), codon))


			for variant in variant_list:

				if variant.worst_consequence.name == 'missense_variant':

					var_hgvsp_list = variant.hgvsp_list()

					transcript_list_vars =[]

					for hgvsp in var_hgvsp_list:

						transcript, codon = pysam_extract.extract_codon_from_hgvs(hgvsp)

						transcript_list_vars.append((transcript.strip(),codon))

						both = set(transcript_list) & set(transcript_list_vars)


						if len(both) >0:

							same_codon.append(variant)

			if len(list(set(same_codon))) == 0:

				return None
			else:


				return list(set(same_codon))




class VariantSample(models.Model):

	"""
	The VariantSample model stores whcih samples a Variant has appeared in.


	Allows queries such as 'which other samples have we seen this variant in?'

	"""

	variant = models.ForeignKey(Variant)
	sample = models.ForeignKey(Sample)







class ClassificationCode(models.Model):

	text = models.CharField(max_length = 25)

	def __str__(self):

		return self.text

class Question(models.Model):

	text = models.CharField(max_length =300)
	description = models.TextField()
	start = models.BooleanField()
	end = models.BooleanField()
	classification = models.ForeignKey(ClassificationCode, null=True)

	def __str__(self):
		return self.text


class Interpretation(models.Model):

	author = models.ForeignKey('auth.User')
	variant = models.ForeignKey(Variant)
	sample = models.ForeignKey(Sample)
	finished = models.BooleanField()
	date = models.DateTimeField(default = timezone.now)
	classification = models.CharField(max_length =25)

	def __str__(self):

		return str(self.pk)


	def get_classification(self):

		all_answers = UserAnswer.objects.filter(interpretation=self.pk)

		classifications =[]

		for answer in all_answers:

			if answer.user_answer ==  '1':

				classifications.append(answer.user_question.classification.text)

		final_classification =classify(classifications)

		return final_classification


class UserAnswer(models.Model):

	interpretation = models.ForeignKey(Interpretation)
	user_question = models.ForeignKey(Question, null=True )
	date = models.DateTimeField(default = timezone.now)
	user_answer = models.CharField(max_length=30, default="")


	def __str__(self):

		return str(self.pk)





class VariantGene(models.Model):

	"""
	Allows genes and variants to be associated

	"""

	gene = models.ForeignKey(Gene)
	variant = models.ForeignKey(Variant)

	def __str__(self):

		return self.gene.name


class VariantTranscript(models.Model):

	variant = models.ForeignKey(Variant)
	transcript = models.ForeignKey(Transcript)
	consequence = models.TextField()
	exon = models.CharField(max_length =25)
	intron = models.CharField(max_length =25)
	hgvsc = models.TextField()
	hgvsp = models.TextField()

	def __str__(self):

		return self.variant.chromosome+str(self.variant.position)





