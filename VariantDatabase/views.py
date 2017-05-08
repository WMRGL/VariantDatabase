from django.shortcuts import render, get_object_or_404, redirect
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
import imp
from pysam import VariantFile
from .forms import *
from django.utils import timezone
import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
pysam_extract = imp.load_source('pysam_extract', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/Pysam/pysam_extract.py')



@login_required
def home_page(request):

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

	history = worksheet.get_history()

	if request.method == 'POST':

		form = WorksheetStatusUpdateForm(request.POST)

		if form.is_valid():

			worksheet_status = get_object_or_404(WorkSheetStatus, pk = '2')

			worksheet_update = form.save(commit=False)

			worksheet_update.worksheet = worksheet

			worksheet_update.status = worksheet_status

			worksheet_update.date = timezone.now()

			worksheet_update.user = request.user

			worksheet_update.save()

			return redirect(list_worksheet_samples, pk_worksheet)


	else:

		form = WorksheetStatusUpdateForm()





	samples_in_worksheet = Sample.objects.filter(worksheet = worksheet, visible=True)

	return render(request, 'VariantDatabase/list_worksheet_samples.html', {'samples_in_worksheet': samples_in_worksheet, 'form': form, 'worksheet': worksheet, 'history': history})



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




def sample_summary(request, pk_sample ):


	"""
	This view displays the variants from a vcf file in a html table.

	The columns that are present can be configured in the user settings page.


	"""

	sample = get_object_or_404(Sample, pk=pk_sample) 

	#Get the user's settings.
	#Create a field list containing the custom INFO fields the user requires.
	#Then this will be passed to the template for rendering
	#Get the vcf file and get the data e.g. ref, chrom, INFO
	#Get the genes from the vcf file
	#Pass these to the template

	vcf_file_path = sample.vcf_file


	#avoid recalculating using cache
	data = cache.get(sample.name+"summary")

	if data == None:

		data = VariantSample.objects.filter(sample=sample).order_by('variant__worst_consequence__impact')

		 #create variant list
		cache.set(sample.name+"summary", data, 600)


	paginator = Paginator(data,50)

	page = request.GET.get('page')

	try:

		variants = paginator.page(page)

	except PageNotAnInteger:

		variants =paginator.page(1)


	except:

		variants = paginator.page(paginator.num_pages)




	return render(request, 'VariantDatabase/sample_summary.html', {'sample': sample, 'variants': variants})




def variant_detail(request, pk_sample, variant_hash):



	"""
	This view displays the detial for a particular variant.

	It combines - sample specific annoation data e.g. pulled from the vcf
				- Global variant data e.g. chr, pos, ref that are associated with all variants of the type
				- Allows classification
	"""




	sample = get_object_or_404(Sample, pk=pk_sample)

	data = pysam_extract.create_master_list(sample.vcf_file, sample.name)

	variant_sample_data = []


	for variant in data:

		hash_id = variant['hash_id']

		if hash_id == variant_hash:

			variant_sample_data.append(variant)
			break


	variant = get_object_or_404(Variant, variant_hash=variant_hash)


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



	return render(request, 'VariantDatabase/variant_detail.html', {'variant_sample_data': variant_sample_data, 'variant': variant, 'form': form, 'classifications': classifications})




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
	View all variants - pulls from Variant Model



	"""
	
	alts =[]
	variants =[]

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

	

	return render(request, 'VariantDatabase/view_all_variants.html', {'variants': variants, 'gene_name': gene_name, 'alts': alts})






@login_required
def all_questions(request, pk_interpretation):

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

	transcripts = VariantTranscript.objects.filter(variant = variant)

	return render(request, 'VariantDatabase/variant_view.html', {'variant': variant, 'transcripts': transcripts } )