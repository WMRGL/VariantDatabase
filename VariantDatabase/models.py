from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

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



class Sample(models.Model):


	"""
	The Sample model holds information on a particlar sample

	There can be many samples in a Worksheet

	Each sample has a vcf file associated with it


	"""


	name = models.CharField(max_length=50)
	patient_initials = models.CharField(max_length=50)
	worksheet = models.ForeignKey(Worksheet)
	vcf_file = models.FilePathField(path='/home/cuser/Documents/Project/DatabaseData',recursive=True)
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

		 current_status = SampleStatusUpdate.objects.filter(sample=self).order_by('-date')[0].status.name

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

	sample = models.ForeignKey(Worksheet)
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
	variant_hash = models.CharField(max_length=64, db_index=True, unique=True) #indexed, but do we do more lookups than insertions over time?

	def __str__(self):
		return self.chromosome + str(self.position) + self.ref + self.alt


	def get_samples_with_variant(self):

		samples =VariantSample.objects.filter(variant=self)

		return samples



class VariantSample(models.Model):

	"""
	The VariantSample model stores whcih samples a Variant has appeared in.


	Allows queries such as 'which other samples have we seen this variant in?'

	"""

	variant = models.ForeignKey(Variant)
	sample = models.ForeignKey(Sample)
