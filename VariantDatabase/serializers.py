from rest_framework import serializers
from .models import Variant

class VariantSerializer(serializers.ModelSerializer):

	frequency  = serializers.SerializerMethodField('var_frequency')

	def var_frequency(self, variant):

		return variant.get_frequency_data()

	class Meta:

		model = Variant
		fields = ("variant_hash", "chromosome", "position", "ref","alt", "worst_consequence", "frequency")





