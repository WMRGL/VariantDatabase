from django import forms
from .models import Report, Worksheet, UserSetting
from crispy_forms.helper import FormHelper

class FilterForm(forms.Form):

	upstream_gene_variant = forms.BooleanField(required=False)
	transcript_amplification = forms.BooleanField(required=False)
	transcript_ablation = forms.BooleanField(required=False)
	synonymous_variant = forms.BooleanField(required=False)
	stop_retained_variant = forms.BooleanField(required=False)
	stop_lost = forms.BooleanField(required=False)
	stop_gained = forms.BooleanField(required=False)
	start_lost = forms.BooleanField(required=False)
	splice_region_variant = forms.BooleanField(required=False)
	splice_donor_variant = forms.BooleanField(required=False)
	splice_acceptor_variant = forms.BooleanField(required=False)
	regulatory_region_variant = forms.BooleanField(required=False)
	regulatory_region_amplification = forms.BooleanField(required=False)
	regulatory_region_ablation = forms.BooleanField(required=False)
	protein_altering_variant = forms.BooleanField(required=False)
	non_coding_transcript_variant = forms.BooleanField(required=False)
	non_coding_transcript_exon_variant = forms.BooleanField(required=False)
	missense_variant = forms.BooleanField(required=False)
	mature_miRNA_variant = forms.BooleanField(required=False)
	intron_variant = forms.BooleanField(required=False)
	intergenic_variant = forms.BooleanField(required=False)
	inframe_insertion = forms.BooleanField(required=False)
	inframe_deletion = forms.BooleanField(required=False)
	incomplete_terminal_codon_variant = forms.BooleanField(required=False)
	frameshift_variant = forms.BooleanField(required=False)
	feature_truncation = forms.BooleanField(required=False)
	feature_elongation = forms.BooleanField(required=False)
	downstream_gene_variant = forms.BooleanField(required=False)
	coding_sequence_variant = forms.BooleanField(required=False)
	TF_binding_site_variant = forms.BooleanField(required=False)
	TFBS_amplification = forms.BooleanField(required=False)
	TFBS_ablation = forms.BooleanField(required=False)
	NMD_transcript_variant = forms.BooleanField(required=False)
	five_prime_UTR_variant = forms.BooleanField(required=False)
	three_prime_UTR_variant = forms.BooleanField(required=False)

	freq_max_af = forms.FloatField(initial=1.0)



class WorksheetStatusUpdateForm(forms.ModelForm):
	"""
	Form for updating the Worksheet status

	"""

	class Meta:

		model = Worksheet
		fields = ()



class ReportForm(forms.ModelForm):
	"""
	Form for creating Sample Reports

	"""

	class Meta:

		model = Report
		fields = ()


class UserSettingsForm(forms.ModelForm):
	"""
	Form for updating user settings.

	"""
	class Meta:

		model = UserSetting
		fields = ("igv_view", "columns_to_hide")




