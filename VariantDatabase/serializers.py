from rest_framework import serializers
from .models import Variant

class VariantFreqSerializer(serializers.ModelSerializer):

	class Meta:

		model = Variant
		fields = ('chromosome', 'position', 'ref','alt', 'worst_consequence')





