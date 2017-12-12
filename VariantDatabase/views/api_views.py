from VariantDatabase.serializers import *
from VariantDatabase.models import *
from django.http import JsonResponse
from rest_framework import generics




class VariantListView(generics.ListAPIView):
	"""
	This is an API endpoint for viewing Variant objects within the database.

	Options:

	chr = chromosome ID e.g. chr3 or X
	start = start position
	end = end position


	"""

	model = Variant
	serializer_class = VariantSerializer
	
	def get_queryset(self):

		queryset = Variant.objects.all()

		chromosome = self.request.query_params.get('chr', None)

		start = self.request.query_params.get('start', None)

		end = self.request.query_params.get('end', None)

		if chromosome is not None and start is not None and end is not None:

			start = start.split(".")[0]
			end = end.split(".")[0]

			queryset = queryset.filter(chromosome=chromosome)

			queryset = queryset.filter(position__range=(start,end))

		return queryset

class VariantView(generics.RetrieveAPIView):
	"""
	This is an API end point for getting a particular variant

	"""

	queryset = Variant.objects.all()
	serializer_class = VariantSerializer
	lookupfield = "variant_hash"







class WorksheetListView(generics.ListAPIView):
	"""
	This is an API endpoint for viewing Worksheet objects within the database.

	"""

	model = Worksheet
	queryset = Worksheet.objects.all()
	serializer_class = WorkSheetSerializer
	


