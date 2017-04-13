from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from variant_classifier import classify


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

		if status == 'Awaiting QC Check' or status == 'No Status Found':

			return True

		else:

			return False





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
	vcf_hash = models.CharField(max_length=64) #could we use a hash to check whether the vcf has changed?


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

class Variant(models.Model):

	"""
	The Variant model holds unique variants.

	If a variant is seen in another vcf it will not appear twice in this model.

	The variant_hash field is used as a key (sha256)


	"""

	chromosome  = models.CharField(max_length=25)
	position  = models.IntegerField()
	ref = models.TextField()
	alt = models.TextField()
	variant_hash = models.CharField(max_length=64, db_index=True, unique=True)
	HGVS =models.TextField()
	last_updated =  models.DateTimeField(default = timezone.now)
	rs_number = models.CharField(max_length =50)
	



	def __str__(self):
		return self.chromosome + str(self.position) + self.ref + self.alt


	def get_samples_with_variant(self):

		samples =VariantSample.objects.filter(variant=self)

		return samples


	def get_genes(self):

		genes = VariantGene.objects.filter(variant =self)

		return genes



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


class Gene(models.Model):

	"""
	Stores genes that have been seen before


	"""

	name = models.CharField(max_length=50, db_index=True, unique=True)



class VariantGene(models.Model):

	"""
	Allows genes and variants to be associated

	"""

	gene = models.ForeignKey(Gene)
	variant = models.ForeignKey(Variant)

	def __str__(self):

		return self.gene.name