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

	name = models.CharField(max_length=50)
	patient_initials = models.CharField(max_length=50)
	worksheet = models.ForeignKey(Worksheet)
	vcf_file = models.FilePathField(path='/home/cuser/Documents/Project/DatabaseData',recursive=True)
	vcf_hash = models.TextField(max_length=500)


	def __str__(self):
		return self.name





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
	then that column will be displayed


	"""
	user = models.ForeignKey('auth.User')
	variant_information = models.ForeignKey(VariantInformation)


