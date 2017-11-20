from django import forms
from .models import  *

from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, InlineRadios, TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset



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
		self.helper.form_id = "search-data-form"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-8"

		self.helper.form_method = "get"
		self.helper.form_action = reverse("search")
		self.helper.add_input(Submit("submit", "Submit", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			


				Fieldset("Search",Field("search",placeholder="Search for a gene, variant, location, region or sample", title=False)))



class FilterForm(forms.Form):


	try:
	
		consequences_list = Consequence.objects.all()
		panels_list = Panel.objects.all()
		choices_panels = [(panel.pk, panel.name) for panel in panels_list]
		choices_consequence = [(consequence.name, consequence.name) for consequence in consequences_list]
		consequences = forms.MultipleChoiceField(choices_consequence)
		max_af = forms.FloatField(required=True, max_value=1, min_value=0)
		panels = forms.ChoiceField(choices=choices_panels)
		update_panel = forms.BooleanField(required=False)

	except:

		pass

	
	def __init__(self, *args, **kwargs):


		super(FilterForm, self).__init__(*args, **kwargs)

		

		self.helper = FormHelper()
		self.helper.form_id = "search-filter-form"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-8"
		self.helper.form_method = "get"
		self.helper.form_action = ""
		self.helper.add_input(Submit("submit_filter_form", "Submit", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			
			Field("max_af"), Div("consequences"), Div("panels"), Div("update_panel") )


class CreatePanelForm(forms.ModelForm):


	inherit_select = forms.MultipleChoiceField(required=False)

	def __init__(self, *args, **kwargs):
		super(CreatePanelForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = "search-data-form"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-8"


		self.fields["inherit_select"].choices = [(panel.name, panel.name) for panel in Panel.objects.all().exclude(name="None")]

		self.helper.form_method = "POST"
		self.helper.form_action = reverse("panel_list")
		self.helper.add_input(Submit("Create", "Create", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			
				Field("name"),Div("subsection"), Div("inherit_select"))

	class Meta:

		model = Panel
		fields = ("name","subsection",)