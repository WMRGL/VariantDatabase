from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *


class Command(BaseCommand):

	help = "creates a new worksheet"

	def add_arguments(self, parser):

		pass

	def handle(self, *args, **options):

		section = Section.objects.get(pk=1)

		worksheet =Worksheet()

		worksheet.name = "Worksheet 2"
		worksheet.section = section
		worksheet.comment = "None"
		worksheet.status = '1'

		worksheet.save()

		self.stdout.write(self.style.SUCCESS("Done"))
