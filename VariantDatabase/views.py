from django.shortcuts import render, get_object_or_404, redirect
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.utils import timezone
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
import pysam_extract
from django.forms import modelformset_factory
import collections
from django.db import transaction
import csv

@login_required
def home_page(request):
	"""
	The homepage
	"""

	return render(request, 'VariantDatabase/home_page.html', {})

@login_required
def list_sections(request):

	"""
	This view allows the user to view a section page

	On this page the relevent worksheets will be shown.

	TODO: sort worksheets by status

	"""

	all_sections = Section.objects.all()

	return render(request, 'VariantDatabase/list_sections.html', {'all_sections': all_sections} )



@login_required
def list_worksheet_samples(request, pk_worksheet):

	"""
	This view lists the samples in a particular worksheet

	"""

	worksheet = get_object_or_404(Worksheet, pk=pk_worksheet)


	if request.method == 'POST':

		#if user is authorised
		worksheet = worksheet = get_object_or_404(Worksheet, pk=pk_worksheet)
		worksheet.status = '3'
		worksheet.save()

		return redirect(list_worksheet_samples, pk_worksheet)


	else:

		form = WorksheetStatusUpdateForm()

		quality_data = worksheet.get_quality_data()




	samples_in_worksheet = Sample.objects.filter(worksheet = worksheet, visible=True)

	return render(request, 'VariantDatabase/list_worksheet_samples.html', {'samples_in_worksheet': samples_in_worksheet, 'form': form, 'worksheet': worksheet, 'quality_data': quality_data})



@login_required
def list_sample_variants(request, pk_sample):

	"""
	This view displays the variants from a vcf file in a html table.

	The columns that are present can be configured in the user settings page.


	"""

	sample = get_object_or_404(Sample, pk=pk_sample) 

	#Get the user's settings.
	#Create a field list containing the custom INFO fields the user requires.
	#Then this will be passed to the template for rendering.

	user_settings = UserSetting.objects.filter(user=request.user)

	field_list = []
	heading_list = []

	for setting in user_settings:

		field_list.append(setting.variant_information.information.replace('.', '_')) #create a list containing the INFO field IDs needed N.B replace '.' with '_' for template
		heading_list.append(setting.variant_information.label)


	#Get the vcf file and get the data e.g. ref, chrom, INFO
	#Get the genes from the vcf file
	#Pass these to the template

	vcf_file_path = sample.vcf_file


	#avoid recalculating using cache
	data = cache.get(sample.name)

	if data == None:

		data = pysam_extract.create_master_list_canonical(vcf_file_path, sample.name) #create variant list
		cache.set(sample.name, data, 600)


	vep_annotated = pysam_extract.vep_annotated(vcf_file_path)


	paginator = Paginator(data,50)

	page = request.GET.get('page')

	try:

		variants = paginator.page(page)

	except PageNotAnInteger:

		variants =paginator.page(1)


	except:

		variants = paginator.page(paginator.num_pages)


	return render(request, 'VariantDatabase/list_sample_variants.html', {'sample': sample, 'variants': variants, 'field_list': field_list, 'heading_list': heading_list, 'vep': vep_annotated})



@login_required
def sample_summary(request, pk_sample ):

	"""
	This view displays the various information about a sample

	"""

	sample = get_object_or_404(Sample, pk=pk_sample)


	if request.method == "POST": #if the user clicked create a new report 

		form = ReportForm(request.POST)


		if form.is_valid():

			report = form.save(commit=False)
			report.sample = sample
			report.status ='1'

			report.save()

			report.initialise_report()

			return redirect(create_sample_report, sample.pk, report.pk)

	else:

		consequence = request.GET.get('consequence')
		frequency = request.GET.get('freq')
		
		if consequence == 'All':

			consequence_filter = 100

		elif consequence == 'LOF':

			consequence_filter = 8

		elif consequence == 'LOFplus': 

			consequence_filter = 13

		else:

			consequence_filter = 100

		try:

			frequency = float(frequency)

			if frequency >1.0:

				frequency_filter = 1.0

			else:

				frequency_filter = frequency

		except:

			frequency_filter = 1.0


		data = sample.get_variants(frequency_filter, consequence_filter)

		summary = sample.variant_query_set_summary(data)

		total_summary = sample.total_variant_summary()

		form = ReportForm()

		reports = Report.objects.filter(sample=sample)

		

		paginator = Paginator(data,25)

		#Pagination stuff
		page = request.GET.get('page')

		try:

			variants = paginator.page(page)

		except PageNotAnInteger:

			variants =paginator.page(1)


		except:

			variants = paginator.page(paginator.num_pages)

		return render(request, 'VariantDatabase/sample_summary.html', {'sample': sample, 'variants': variants, 'form': form, 'reports': reports, 'filter': (consequence_filter, frequency_filter), 'summary': summary, 'total_summary': total_summary})



@login_required
def variant_detail(request, pk_sample, variant_hash):

	"""
	This view displays the detial for a particular variant.

	It combines - sample specific annoation data e.g. pulled from the vcf
				- Global variant data e.g. chr, pos, ref that are associated with all variants of the type
				- Allows classification
	"""

	sample = get_object_or_404(Sample, pk=pk_sample)

	variant = get_object_or_404(Variant, variant_hash=variant_hash)

	other_alleles = variant.get_other_alleles()

	transcripts = VariantTranscript.objects.filter(variant = variant)

	classifications = Interpretation.objects.filter(variant=variant)


	if request.method == "POST": #if user has asked to do a new classification

		form = InterpretationForm(request.POST)

		if form.is_valid():

			interpretation = form.save(commit=False)
			interpretation.author = request.user
			interpretation.variant = variant
			interpretation.sample = sample
			interpretation.date = timezone.now()
			interpretation.finished = False
			interpretation.save()

			return redirect(all_questions, interpretation.pk)


	else:

		form = InterpretationForm()

	return render(request, 'VariantDatabase/variant_detail.html', {'variant': variant, 'form': form, 'classifications': classifications, 'transcripts': transcripts, 'other_alleles': other_alleles})


@login_required
def settings(request):

	"""
	This view allows the user to customise which columns they would like in the list_sample_variants view

	If the a checkbox is selected when the form is POSTed then:

		1) Delete all current user settings.
		2) Loop through the setting tickboxes in the request and create a new UserSetting
	
	Otherwise:

		1) Just display the form 


	"""

	all_fields = VariantInformation.objects.all() #get all possible columns (these will be converted to toggle boxes)


	if request.method == 'POST':

		user_settings = UserSetting.objects.filter(user=request.user) #get rid of existing user settings

		user_settings.delete()

		for key in request.POST:

			if key != 'csrfmiddlewaretoken': #then create a new UserSetting object

				variant_information = get_object_or_404(VariantInformation, information=key)

				user = request.user

				a = UserSetting(user=request.user, variant_information=variant_information)

				a.save()



		#Get what the user has just inputted and put into a dictionary - tick_box_dict.
		#This allows us to tick the tickboxes in the html template.

		current_user_settings = UserSetting.objects.filter(user=request.user)

		tick_box_dict ={}

		for setting in current_user_settings:

			tick_box_dict[setting.variant_information.information] =True

				
		return render(request, 'VariantDatabase/settings.html' ,{'all_fields': all_fields, 'tick_box_dict': tick_box_dict})


	else:

		#Get what the current user settings put into a dictionary - tick_box_dict.
		#This allows us to pre-tick the tickboxes in the html template.

		current_user_settings = UserSetting.objects.filter(user=request.user)

		tick_box_dict ={}

		for setting in current_user_settings:

			tick_box_dict[setting.variant_information.information] =True


		return render(request, 'VariantDatabase/settings.html' ,{'all_fields': all_fields, 'tick_box_dict': tick_box_dict})


@login_required
def view_all_variants(request):

	""""
	A search page for Variants.
	Similar to ExaC
	User can search by Gene

	"""
	alts =[]
	gene_name = request.GET.get('gene_name')

	if gene_name is not None:

		gene_name = gene_name.upper()

		try:

			gene = Gene.objects.get(name=gene_name)

			return redirect(view_gene, gene.name)

		except:

			alts  =Gene.objects.filter(name__icontains=gene_name)
			
			if len(alts) <5:

				alts = alts

			else:

				alts =[]

			

	return render(request, 'VariantDatabase/view_all_variants.html', {'gene_name': gene_name, 'alts': alts})


@login_required
def all_questions(request, pk_interpretation):
	"""
	Show all questions from the ACMG guidelines

	"""

	interpretation = get_object_or_404(Interpretation, pk = pk_interpretation)



	if request.method == 'POST':

		dict = {'questions_1': [1],'questions_2': [2], 'questions_3': [3], 'questions_4': [4], 
				'questions_5': [5], 'questions_6': [6], 'questions_7': [7], 'questions_8': [8], 
				'questions_9': [9], 'questions_10': [10], 'questions_11': [11], 'questions_12': [12], 
				'questions_13': [13], 'questions_14': [14], 'questions_15': [15], 'questions_16': [16], 
				'questions_17': [17], 'questions_18': [18], 'questions_19': [19], 'questions_20': [20], 
				'questions_21': [21], 'questions_22': [22], 'questions_23': [23], 'questions_24': [24], 
				'questions_25': [25], 'questions_26': [26], 'questions_27': [27], 'questions_28': [28] } #dictionary holds names of fields of AllAnswersForm along with a list holding the Question Number


		for key in dict:

			dict[key] = dict[key]+[ request.POST.get(key)] #Add the User's answer from the AllAnswersForm to the dictionary


		for key in dict:

			question_number = dict[key][0] 

			question = get_object_or_404(Question, pk = question_number)

			UserAnswer.objects.create(interpretation = interpretation, user_question = question, user_answer= dict[key][1], date = timezone.now()) #now create a UserAnswer instance with that info

		interpretation.classification = interpretation.get_classification()
		interpretation.finished = True

		interpretation.save()
		return redirect('report', pk_interpretation)


	else:


		all_questions = Question.objects.all()

		question_form = AllAnswersForm()

		list_of_fields =[]

		for field in question_form:

			list_of_fields.append(field)


		zipped = zip(all_questions, list_of_fields) #combine 


	return render(request, 'VariantDatabase/all_questions.html', {'zipped': zipped, 'interpretation': interpretation})

@login_required
def report(request, pk_interpretation):

	"""
	A report of the classification (ACMG guidlines)

	"""

	interpretation = get_object_or_404(Interpretation, pk= pk_interpretation)

	all_answers = UserAnswer.objects.filter(interpretation=pk_interpretation).order_by('user_answer', 'user_question__classification')

	classification = interpretation.get_classification()

	return render(request, 'VariantDatabase/report.html', {'all_answers' : all_answers, 'interpretation': interpretation, 'classification': classification})

@login_required
def view_gene(request, gene_pk):
	"""
	A view to allow the user to view all the Variants in a Gene.

	"""

	consequence_filter = request.GET.get('filter')

	if consequence_filter == 'all':

		consequence_filter = 100

	elif consequence_filter =='lof':

		consequence_filter = 8

	elif consequence_filter == 'lofplus':

		consequence_filter = 13

	else:

		consequence_filter =100

	gene_pk = gene_pk.upper()

	gene = Gene.objects.get(name=gene_pk)

	variants = gene.get_all_variants(consequence_filter)

	return render(request,'VariantDatabase/gene.html', {'variants': variants, 'gene': gene})

@login_required
def view_detached_variant(request, variant_hash):
	
	variant = get_object_or_404(Variant, variant_hash=variant_hash)

	other_alleles = variant.get_other_alleles()

	transcripts = VariantTranscript.objects.filter(variant = variant)

	classifications = Interpretation.objects.filter(variant=variant)

	return render(request, 'VariantDatabase/variant_view.html', {'variant': variant, 'transcripts': transcripts, 'other_alleles': other_alleles, 'classifications': classifications } )

@login_required
def create_sample_report(request, pk_sample, pk_report):
	"""
	Allow the user to create a new report and select their responses.

	Uses the Model Formset functionaility of Django to accommplish this.

	"""

	report = get_object_or_404(Report, pk=pk_report)

	ReportVariantFormset = modelformset_factory(ReportVariant, fields=('status','variant'), extra=0, widgets={"variant": forms.HiddenInput()})

	if request.method == 'POST': # if the user clicks submit

		#create a formset factory - using the ReportVariant model. Hide the variant field.

		formset = ReportVariantFormset(request.POST)

		if formset.is_valid():

			instances = formset.save()

			report.status = '2'

			report.save()

			return redirect(view_sample_report, pk_sample, pk_report)


	report_variant_formset = ReportVariantFormset(queryset=ReportVariant.objects.filter(report=report)) # populate formset

	variants = ReportVariant.objects.filter(report=report) #get the variants from the ReportVariant model.


	#Create an ordered dict. Use this to store Variants and forms together using Variant hash as key
	#For example: dict = {variant_hash:[Variant, Form]}
	#This allows us to put variants and selector drop downs from form next to each other in a HTML table.

	my_dict =collections.OrderedDict() 

	for variant in variants:

		my_dict[variant.variant.variant_hash] = [variant]

	for form in report_variant_formset:

		key = form.__dict__['initial']['variant']

		my_dict[key].append(form)

	return render(request, 'VariantDatabase/create_sample_report.html', {'formset': report_variant_formset, 'dict': my_dict} )

@login_required
def view_sample_report(request, pk_sample, pk_report):
	"""
	View a sample report i.e. the output of the create_sample_report view.
	"""

	report = get_object_or_404(Report, pk=pk_report)

	report_variants = ReportVariant.objects.filter(report=report)

	return render(request, 'VariantDatabase/view_sample_report.html' , {'report': report, 'report_variants': report_variants})


def upload_sample_sheet(request):
	"""
	Upload a SampleSheet
	First stage of the data flow

	"""

	error = [0,'None']
	def parse_sample_sheet(file):

		expected = ['Sample_ID', 'Sample_Name', 'Sample_Plate','Sample_Well', 'I7_Index_ID',  'index', 'Sample_Project']

		flag =0

		sample_list = []

		reader = csv.reader(file, delimiter=',')

		for row in reader:

			if row[0] == 'Sample_ID':

				flag =1

				for index, title in enumerate(expected):

					if title != row[index]:

						return False

			if flag ==1:

				if row[0] == "":

					return sample_list[1:]

				sample_list.append([row[0], row[1],row[2],row[3],row[4],row[5],row[6]])


		return sample_list[1:]


	if request.method == 'POST':

		

		form = SampleSheetForm(request.POST, request.FILES)

		if form.is_valid():

			list =[]

			section = form.cleaned_data['sections'][0]
			comment = form.cleaned_data['comment']
			worksheet_name = form.cleaned_data['worksheet_name']
			sample_sheet = request.FILES['sample_sheet']

			list.append(form.cleaned_data)

			#does a worksheet with that name exist?

			worksheet = Worksheet.objects.filter(name = worksheet_name)

			if worksheet.exists():

				error = [1,'Worksheet with this name already exists!']

				return render(request, 'VariantDatabase/upload_sample_sheet.html', {'form': form, 'error': error})

			else:

				with transaction.atomic():


					sample_data = parse_sample_sheet(sample_sheet)

					if sample_data == False: #does it have correct titles

						error = [2,'Could not process SampleSheet']

						return render(request, 'VariantDatabase/upload_sample_sheet.html', {'form': form, 'error': error})

					else:

						new_worksheet = Worksheet(name=worksheet_name, section=section,comment=comment, status ='1')

						new_worksheet.save()

						for sample in sample_data:

							sample_id = sample[0]
							sample_name = sample[1]
							sample_plate = sample[2]
							sample_well = sample[3]
							sample_i7_index = sample[4]
							sample_index = sample[5]
							sample_project = sample[6]

							new_sample = Sample(name= sample_name, worksheet=new_worksheet, vcf_file='None', visible=True,status='1',
							 sample_id=sample_id, sample_plate =sample_plate, sample_well=sample_well, i7_index_id=sample_i7_index, index=sample_index, sample_project=sample_project )

							new_sample.save()

						error = [3,'SampleSheet uploaded']

						return render(request, 'VariantDatabase/upload_sample_sheet.html', {'form': form, 'error': error})

	else:

		form = SampleSheetForm()
		

	return render(request, 'VariantDatabase/upload_sample_sheet.html', {'form': form, 'error': error})
