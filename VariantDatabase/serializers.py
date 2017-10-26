from rest_framework import serializers
from .models import Variant

class VariantFreqSerializer(serializers.ModelSerializer):

	class Meta:

		model = Variant
		fields = ('variant_hash', 'max_af', 'worst_consequence', 'chromosome', 'position', 'ref','alt')





