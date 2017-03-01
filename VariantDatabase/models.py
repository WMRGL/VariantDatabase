from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

class Project(models.Model):

	project_owner = models.ForeignKey('auth.User')
	project_title = models.CharField(max_length=200)
	project_description = models.TextField()
	created_date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.project_title


class Batch(models.Model):
	batch_name = models.CharField(max_length=100, default = " ")
	project = models.ForeignKey(Project)
	batch_date = models.DateTimeField(blank=True, null=True)
	batch_comment = models.TextField()
	vcf_file = models.FilePathField(path='/home/cuser/Documents/Project/DatabaseData',recursive=True)
	vcf_hash = models.TextField(max_length=200)

	def __str__(self):
		return self.batch_name

class Sample(models.Model):

	sample_name = models.CharField(max_length=50)
	patient_initials = models.CharField(max_length=50)
	batch = models.ForeignKey(Batch)

	def __str__(self):
		return self.sample_name




