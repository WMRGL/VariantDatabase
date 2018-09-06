from django import forms
from .models import  *
from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, InlineRadios, TabHolder, Tab,InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset
from django.contrib.auth.forms import PasswordChangeForm
from django.forms.widgets import DateInput
from rolepermissions.roles import RolesManager
from django.contrib.auth.models import User

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



class CustomPasswordChangeForm(PasswordChangeForm):
	"""
	Put this form as a crispy form.

	"""


	def __init__(self, *args, **kwargs):
		super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = "password-change-form"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-6"
		self.helper.form_method = "POST"
		self.helper.add_input(Submit("submit", "Submit", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"


class SearchForm(forms.Form):
	"""
	A search form.
	See the seach view for more information.

	"""
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

					Field(
						"search",
						placeholder="Search for a gene, variant, location, region or sample", title=False))



class FilterForm(forms.Form):
	"""	
	A form for filtering variants in the summary page.

	Allows the user to:

		1) Choose consequences and AFs to filter by.
		2) Select a panel to gene filter by.
		3) Optionally save that panel change.

	"""


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
	""""
	A form for ccreating panels.

	See the Panel page for display.

	User can:

		1) Name new Panel.
		2) Select an optional subsection to assosiate the panel with.
		3) Select (multiple) existing panels to inherit from.


	"""

	inherit_select = forms.MultipleChoiceField(required=False)

	def __init__(self, *args, **kwargs):

		super(CreatePanelForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = "search-data-form"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-8"
		self.fields["inherit_select"].choices = [
					(panel.name, panel.name) for panel in Panel.objects.all().exclude(name="None")]
		self.helper.form_method = "POST"
		self.helper.form_action = reverse("panel_list")
		self.helper.add_input(Submit("Create", "Create", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			
				Field("name"),Div("subsection"), Div("inherit_select"))

	class Meta:

		model = Panel
		fields = ("name","subsection",)



class ChangeWorksheetStatus(forms.ModelForm):
	"""
	Form for manually updating the worksheet status.

	"""

	def __init__(self, *args, **kwargs):

		super(ChangeWorksheetStatus, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = "change-worksheet-status"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-8"
		self.helper.form_method = "POST"
		self.helper.form_action = ""
		self.helper.add_input(Submit("submit-change-status", "Submit", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			
				Field("status"))

	class Meta:

		model = Worksheet
		fields = ("status",)

class ChangeSampleStatus(forms.ModelForm):
	"""
	Form for manually updating the sample status.

	"""

	def __init__(self, *args, **kwargs):

		super(ChangeSampleStatus, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = "change-worksheet-status"
		self.helper.label_class = "col-lg-2"
		self.helper.field_class = "col-lg-8"
		self.helper.form_method = "POST"
		self.helper.form_action = ""
		self.helper.add_input(Submit("submit-sample-status", "Submit", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			
				Field("status"))

	class Meta:

		model = Sample
		fields = ("status",)



			
class WorksheetFilterForm(forms.Form):
	"""	
	A form for filtering variants in the summary page.

	Allows the user to:

		1) Choose consequences and AFs to filter by.
		2) Select a panel to gene filter by.
		3) Optionally save that panel change.

	"""

	view_complete = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):

		super(WorksheetFilterForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = "search-filter-form"
		self.helper.label_class = "col-lg-1"
		self.helper.field_class = "col-lg-2"
		self.helper.form_method = "GET"
		self.helper.form_action = ""
		self.helper.add_input(Submit("submit_filter_form", "Submit", css_class="btn-success"))
		self.helper.form_class = "form-horizontal"
		self.helper.layout = Layout(
			
			Field("view_complete"))


class ChangeUserGroupForm(forms.Form):

	available_roles = RolesManager.get_roles_names()
	roles_choices = [(role, role) for role in available_roles]
	roles_field = forms.ChoiceField(choices=roles_choices)
	users = User.objects.all()


	def __init__(self, *args, **kwargs):

			super(ChangeUserGroupForm, self).__init__(*args, **kwargs)
			self.helper = FormHelper()
			self.helper.form_id = "configure_user_roles"
			self.helper.label_class = "col-lg-2"
			self.helper.field_class = "col-lg-8"
			self.helper.form_method = "post"
			self.helper.form_action = ""
			self.helper.add_input(Submit("submit_configure_user_roles", "Submit", css_class="btn-success"))
			self.helper.form_class = "form-horizontal"
			self.helper.layout = Layout(
				
				Field("roles_field"),Div("user_field") )
