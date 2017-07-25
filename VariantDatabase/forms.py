from django import forms
from .models import Sample, Interpretation, Report, Worksheet, Section


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









class InterpretationForm(forms.ModelForm):
	"""
	Form for creating a new Interpretation (ACMG guidlines)

	"""

	class Meta:

		model = Interpretation
		fields = ()

class WorksheetStatusUpdateForm(forms.ModelForm):
	"""
	Form for updating the Worksheet status

	"""

	class Meta:

		model = Worksheet
		fields = ()

class AllAnswersForm(forms.Form):
	"""
	Form for getting the User's answers to the ACMG guidline questions
	"""

	questions_1 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_2 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_3 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_4 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_5 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_6 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_7 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_8 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_9 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_10 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_11 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_12 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_13 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_14 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_15 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_16 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_17 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_18 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_19 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_20 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_21 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_22 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_23 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_24 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_25 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_26 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_27 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))
	questions_28 = forms.ChoiceField(((4, "Not Answered"), (3,"Unknown"), (2, "No"), (1, "Yes")))

class ReportForm(forms.ModelForm):
	"""
	Form for creating Sample Reports

	"""

	class Meta:

		model = Report
		fields = ()



class SampleSheetForm(forms.Form):


	worksheet_name = forms.CharField(max_length=150)
	sample_sheet = forms.FileField()
	comment = forms.CharField(max_length=500)
