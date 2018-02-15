from VariantDatabase.serializers import *
from VariantDatabase.models import *
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound


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

class VariantViewHash(generics.RetrieveAPIView):
	"""
	This is an API end point for getting a particular variant using its sha256 hash

	To create the hash use:

	sha256(chromosome+" "+pos+" "+ref+" "+alt)

	"""

	queryset = Variant.objects.all()
	serializer_class = IndividualVariantSerializer
	lookupfield = "variant_hash"

class VariantViewLocation(generics.RetrieveAPIView):
	"""
	This is an API end point for getting a particular variant using it's position:

	Options:

	chr = chromosome ID e.g. chr3 or X
	position = genomic location
	ref = reference sequence
	alt = alternative sequence

	"""

	queryset = Variant.objects.all()
	serializer_class = IndividualVariantSerializer
	

	def get_object(self):

		chromosome = self.request.query_params.get('chr', None)
		position = self.request.query_params.get('position', None)
		ref = self.request.query_params.get('ref', None)
		alt = self.request.query_params.get('alt', None)

		variant = get_object_or_404(Variant, chromosome=chromosome, position=position, ref=ref,alt=alt)

		return variant




class WorksheetListView(generics.ListAPIView):
	"""
	This is an API endpoint for viewing Worksheet objects within the database.

	"""

	model = Worksheet
	queryset = Worksheet.objects.all()
	serializer_class = WorkSheetSerializer
	


