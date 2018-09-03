from rest_framework import serializers
from .models import Variant, Worksheet

class VariantSerializer(serializers.ModelSerializer):
	"""
	A serialiser to be used on lists of variants.

	Used by the IGV.js API

	"""


	chr = serializers.SerializerMethodField('get_chr_name')
	start = serializers.SerializerMethodField('get_start_name')
	end = serializers.SerializerMethodField('get_end_name')
	lab_frequency = serializers.SerializerMethodField('get_var_freq')
	last_classification = serializers.SerializerMethodField('get_prev_class')


	class Meta:

		model = Variant
		fields = ("position", "ref","alt", "worst_consequence", "chr", "start", "end", "lab_frequency", "last_classification")


	def get_chr_name(self, variant):

		return variant.chromosome

	def get_start_name(self, variant):

		length = max(len(variant.ref), len(variant.alt))

		if length ==1:

			return variant.position-1

		else:

			return variant.position

	def get_end_name(self, variant):

		length = max(len(variant.ref), len(variant.alt))

		return variant.position+length-1


	def get_var_freq(self, variant):

		return round(variant.get_frequency_data()['global'][2],5)

	def get_prev_class(self, variant):

		classifications =  variant.previous_classifications()

		if classifications.exists():

			return classifications[0].final_classification.name

		else:

			return "NA"


class WorkSheetSerializer(serializers.ModelSerializer):
	"""
	Worksheet serializer

	"""


	class Meta:

		model = Worksheet
		fields = "__all__"


class IndividualVariantSerializer(serializers.ModelSerializer):
	"""
	Gets the info for a particualr variant

	"""

	lab_frequency = serializers.SerializerMethodField('get_var_freq')
	classifications = serializers.SerializerMethodField('get_class')

	class Meta:

		model = Variant
		fields = (
		"variant_hash",
		"chromosome",
		"position",
		"ref",
		"alt",
		"worst_consequence",
		"lab_frequency",
		"classifications")

	def get_var_freq(self, variant):

		return variant.get_frequency_data()


	def get_class(self, variant):

		classifications =  variant.previous_classifications()

		classifications = [{"report_pk":classification.report.pk, "final_classification":classification.final_classification.name}  for classification in classifications]

		return classifications