from django import forms
from .models import  Worksheet, UserSetting, Consequence, SubSection, Report

from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, InlineRadios, TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset

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
	Form for creating a new report


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



class SearchForm(forms.Form):


	search = forms.CharField(required=False, max_length=255)



	def __init__(self, *args, **kwargs):
		super(SearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-data-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'

		self.helper.form_method = 'get'
		self.helper.form_action = reverse('search')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			


				Fieldset('Search',Field('search',placeholder='Search for a gene, variant, location, region or sample', title=False)))



