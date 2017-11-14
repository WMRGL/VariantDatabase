from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from VariantDatabase.serializers import VariantFreqSerializer
from VariantDatabase.models import *



def api_variants(request):
	"""
	API for getting all variants

	"""

	if request.method == 'GET':

		variants = Variant.objects.all()

		serializer = VariantFreqSerializer(variants, many=True)
		return JsonResponse(serializer.data, safe=False)