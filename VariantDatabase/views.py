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





	samples_in_worksheet = Sample.objects.filter(worksheet = worksheet)

	return render(request, 'VariantDatabase/list_worksheet_samples.html', {'samples_in_worksheet': samples_in_worksheet, 'form': form, 'worksheet': worksheet})



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

	data = pysam_extract.create_master_list(vcf_file_path, sample.name) #create variant list


	paginator = Paginator(data,50)

	page = request.GET.get('page')

	try:

		variants = paginator.page(page)

	except PageNotAnInteger:

		variants =paginator.page(1)


	except:

		variants = paginator.page(paginator.num_pages)



	genes = pysam_extract.get_genes_in_file(vcf_file_path, sample.name)

	return render(request, 'VariantDatabase/list_sample_variants.html', {'sample': sample, 'variants': variants, 'genes': genes, 'field_list': field_list, 'heading_list': heading_list})


@login_required
def variant_detail(request, pk_sample, variant_hash):

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


	if request.method == "POST":

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
def search_page(request):

	"""
	This view will allows the user to search for worksheets, samples and variants

	"""

	query = request.GET.get('query')

	return render(request, 'VariantDatabase/search_results.html', {'query': query})


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


def error(request):

	return render(request, 'VariantDatabase/error.html')


def upload_sample(request):

	"""
	This allows the user to upload a new sample.
	Ideally an automated process will be set up e.g. take automatically from folder. This can be combined with worksheet creation.


	The following occurs when a user uploads a new sample:

		1) new_sample object is created.

		2) new SampleStatusUpdate is created and set to 'new'.

		3) Get all data in vcf and lop through each variant:

			a) If that variant has been seen before then just add another VariantSample instance
			b) If that variant is new then create a new Variant and VariantSample instance.


	"""


	if request.method == "POST":

		form = SampleForm(request.POST)

		if form.is_valid():

			new_sample = form.save(commit=False)

			new_sample.hash = 'None'

			input_validation = pysam_extract.validate_input(new_sample.vcf_file, new_sample.name) 

			if new_sample.already_exists(new_sample.name) ==True:

				message = 'A sample with that name already exists'

				return render(request, 'VariantDatabase/upload.html', {'form': form, 'message': message})

			elif input_validation[0] == False:

				message = input_validation[1]

				return render(request, 'VariantDatabase/upload.html', {'form': form, 'message': message})


			new_sample.save()

			#Create new SampleStatusUpdate
			#The SampleStatusUpdate will be set to 'new'

			inital_status = get_object_or_404(SampleStatus, pk=1)

			new_update = SampleStatusUpdate(sample=new_sample, status=inital_status, user=request.user, date=timezone.now())

			new_update.save()

			#Now we check whether for each of the variants in that file do we have a variant in the Variant Model
			#If not create one and then create a corresponding VariantSample record
			#Otherwise just create another VariantSample record


			#catch failures
			try:

				data = pysam_extract.create_master_list(new_sample.vcf_file, new_sample.name)

			except:

				new_sample.delete()
				new_update.delete()

				message = 'Could not extract data from that file (Pysam error)'

				return render(request, 'VariantDatabase/upload.html', {'form': form, 'message': message})
			
			

			for variant in data:

				#See if we have this variant in the database (Variant table) already?
				#Assumes normalisation and one alt allele per variant
				#Assumes chromosome in same format - need to validate?

				chromosome = variant['chrom']
				pos = str(variant['pos'])
				ref = variant['reference']
				alt = variant['alt_alleles'][0]

				hash_id = hashlib.sha256(chromosome+pos+ref+alt).hexdigest()


				try:

					new_variant = Variant.objects.get(variant_hash=hash_id)

				except ObjectDoesNotExist:

					new_variant = Variant(chromosome=chromosome, position=pos, ref= ref, alt=alt, variant_hash= hash_id)

					new_variant.save()


				new_variant_sample = VariantSample(variant=new_variant, sample=new_sample)

				new_variant_sample.save()	

						

			message = new_sample.name + " was successfully uploaded"

			return  render(request, 'VariantDatabase/upload.html', {'form': form, 'message': message})

	form = SampleForm

	return render(request, 'VariantDatabase/upload.html', {'form': form})

def view_all_variants(request):

	all_variants = Variant.objects.all()

	paginator = Paginator(all_variants,15)

	page = request.GET.get('page')

	try:

		variants = paginator.page(page)

	except PageNotAnInteger:

		variants =paginator.page(1)


	except:

		variants = paginator.page(paginator.num_pages)



	return render(request, 'VariantDatabase/view_all_variants.html', {'variants': variants})


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

def report(request, pk_interpretation):

	interpretation = get_object_or_404(Interpretation, pk= pk_interpretation)

	all_answers = UserAnswer.objects.filter(interpretation=pk_interpretation).order_by('user_answer', 'user_question__classification')

	classification = interpretation.get_classification()

	return render(request, 'VariantDatabase/report.html', {'all_answers' : all_answers, 'interpretation': interpretation, 'classification': classification})