from django import forms
from .models import Sample, Interpretation, Report, Worksheet

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