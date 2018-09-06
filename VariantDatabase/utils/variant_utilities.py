"""
Various utility functions for processing variant data e.g. create variant hash.


"""
import hashlib
from VariantDatabase.models import *

def get_variant_hash(chromosome, pos, ref,alt):
	"""
	Generates a sha256 hash of the variant. Used as promary key in Variant model.

	Input: chromosome, pos, ref,alt - self explanatory

	Output:

	hash_id = The sha256 hash of the chromosome + " " + pos + " " + ref + " " + alt

	Note The space between the 4 inputs. This stops problem of Chr1 12 A G and Chr11 2 A G being same hash e.g. hash(Chr112AG)

	"""

	hash_string = bytes("{chr} {pos} {ref} {alt}".format(chr =chromosome, pos=pos, ref=ref, alt=alt), 'utf-8')

	hash_id = hashlib.sha256(hash_string).hexdigest()

	return hash_id

def variant_query_set_summary(variant_query_set):
	"""
	Summarises the data in a variant queryset e.g. how many variants.

	"""

	summary_dict = {}

	summary_dict["total"] = variant_query_set.count()

	summary_dict["missense_count"] = (variant_query_set
										.filter(worst_consequence__name="missense_variant")
										.count())

	summary_dict["indel_count"] = (variant_query_set
		.filter(Q(worst_consequence__name="inframe_deletion") | Q(worst_consequence__name="inframe_insertion") | Q(worst_consequence__name="frameshift_variant"))
		.count())

	summary_dict["lof_count"] = (variant_query_set.
									filter(worst_consequence__impact__lte=8)
									.count())
	summary_dict["synonymous"] = (variant_query_set
									.filter(worst_consequence__name="synonymous_variant")
									.count())

	return summary_dict

def get_filtered_variants(variant_samples, consequences_query_set, max_frequency, panel=None):
	"""
	Gets all the variants for a sample and applies the following filters:

	1) Consequences
	2) Frequency (ExAC)
	3) Gene

	Input :

	variant_samples = A queryset containg the VariantSample objects.
	consequences_query_set = A query set containing the consequences to include
	max_frequency = The maximum frequency i.e. exclude variants with max_af > this.
	apply_gene_filter = Boolean - whether to apply gene filter

	Output:

	variant_samples = A queryset containing the filtered VariantSample Objects.


	"""

	variant_samples = (variant_samples
			.filter(variant__worst_consequence__in=consequences_query_set)
			.filter(variant__max_af__lte=max_frequency)
			.order_by("variant__worst_consequence__impact", "variant__max_af")
			.select_related("variant"))

	if panel != None:

		panel_genes = (PanelGene
							.objects
							.filter(panel=panel)
							.select_related("gene"))

		panel_genes =[panel_gene.gene for panel_gene in panel_genes]

		variants = [variant_sample.variant for variant_sample in variant_samples]

		variant_transcripts = (VariantTranscript
						.objects
						.filter(variant__in=variants)
						.filter(transcript__gene__in=panel_genes)
						.select_related("variant"))

		variants = [variant_transcript.variant.variant_hash for variant_transcript
					 in variant_transcripts]

		variant_samples = variant_samples.filter(variant__variant_hash__in=variants)

		return variant_samples

	else:

		return variant_samples

def create_conseqences_to_include(filter_dict):
	"""
	Takes the filter_dict created by create_filter_dict() method \
	and returns a queryset containing the consequences

	"""

	consequences_to_include =[]

	for key in filter_dict:

		if "freq" not in key and filter_dict[key] ==True:

			if key == "five_prime_UTR_variant":

				consequences_to_include.append("5_prime_UTR_variant")

			elif key == "three_prime_UTR_variant":

				consequences_to_include.append("3_prime_UTR_variant")

			else:

				consequences_to_include.append(key)


	consequences_query_set = Consequence.objects.filter(name__in = consequences_to_include)

	return consequences_query_set

def create_conseqences_to_include_form(form_data):
	"""
	Does the same as create_conseqences_to_include() except \
	for form data submitted by filter_form on the summary page.

	"""

	consequences_to_include =[]

	for consequence in form_data:

		#can"t start python variables with a number  \
		#so have to change key from 5_prime_UTR_variant to five_prime_UTR_variant
		if consequence == "five_prime_UTR_variant": 

			consequences_to_include.append("5_prime_UTR_variant")

		elif consequence == "three_prime_UTR_variant":

			consequences_to_include.append("3_prime_UTR_variant")

		else:

			consequences_to_include.append(consequence)


	consequences_query_set = Consequence.objects.filter(name__in = consequences_to_include)

	return consequences_query_set

def get_column_config_dict(location):
	"""
	Find the column config file (conf/columns.txt) \
	and convert to a dictionary.

	"""

	columns_dict ={}

	file = open("conf/columns.txt", "r")

	for line in file:

		columns_dict[line.strip()] = True

	return columns_dict

def process_user_settings(user_settings_string, columns_dict):

	"""
	Processes the user_settings string that the user can use \
	to configure which columns they want to see.

	"""

	final_list =[]

	final_string = ""

	user_settings = user_settings_string.split(",")

	for column in user_settings:

		if column.strip() in columns_dict:

			final_list.append(column.strip())


	return ",".join(list(set(final_list)))


