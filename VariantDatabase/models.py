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

	def get_status(self):

		pass

class Sample(models.Model):

	name = models.CharField(max_length=50)
	patient_initials = models.CharField(max_length=50)
	worksheet = models.ForeignKey(Worksheet)
	vcf_file = models.FilePathField(path='/home/cuser/Documents/Project/DatabaseData',recursive=True)
	vcf_hash = models.TextField(max_length=500)


	def __str__(self):
		return self.name

class SampleStatus(models.Model):

	name = models.CharField(max_length=100)


class WorkSheetStatus(models.Model):

	name = models.CharField(max_length=100)	



class SampleStatusUpdate(models.Model):

	sample = models.ForeignKey(Sample)
	status = models.ForeignKey(SampleStatus)
	date = models.DateTimeField(blank=True, null=True)
	user = models.ForeignKey('auth.User')


class WorksheetStatusUpdate(models.Model):

	sample = models.ForeignKey(Worksheet)
	status = models.ForeignKey(WorkSheetStatus)
	date = models.DateTimeField(blank=True, null=True)
	user = models.ForeignKey('auth.User')

