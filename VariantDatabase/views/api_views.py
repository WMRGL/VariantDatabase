from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from VariantDatabase.serializers import VariantFreqSerializer
from VariantDatabase.models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def api_variants(request):
	"""
	API for getting all variants

	"""

	if request.method == "GET":

		chromosome = request.GET.get('chr')
		start = request.GET.get('start')
		end = request.GET.get('end')



		variants = Variant.objects.filter(chromosome=chromosome)
		variants = variants.filter(position__range=(start,end))


		serializer = VariantFreqSerializer(variants, many=True)
		return JsonResponse(serializer.data, safe=False)



def api_variants_igv(request):

	data = [{"chr":1, "pos":60000}]


	if request.method == "GET":

		return JsonResponse(data, safe=False)