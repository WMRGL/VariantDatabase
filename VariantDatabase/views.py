from django.shortcuts import render, get_object_or_404, redirect
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
import imp
from pysam import VariantFile
from .forms import *
from django.utils import timezone
import hashlib





pysam_extract = imp.load_source('pysam_extract', '/home/cuser/Documents/Project/VariantDatabase/VariantDatabase/Pysam/pysam_extract.py')



@login_required
def home_page(request):

	return render(request, 'VariantDatabase/home_page.html', {})

@login_required
def list_sections(request):

	all_sections = Section.objects.all()

	return render(request, 'VariantDatabase/list_sections.html', {'all_sections': all_sections} )



@login_required
def list_worksheet_samples(request, pk_worksheet):

	worksheet = get_object_or_404(Worksheet, pk=pk_worksheet)

	samples_in_worksheet = Sample.objects.filter(worksheet = worksheet)

	return render(request, 'VariantDatabase/list_worksheet_samples.html', {'samples_in_worksheet': samples_in_worksheet})



@login_required
def list_sample_variants(request, pk_sample):

	"""
	This view displays the variants from a vcf file in a html table.

	The columns that are present can be configured in the user settings page.


	"""

	sample = get_object_or_404(Sample, pk=pk_sample) 

	#Get the user's settings
	#create a field list containing the custom INFo fields the user requires
	#this will be passed to the template for rendering

	user_settings = UserSetting.objects.filter(user=request.user)

	field_list = []

	for setting in user_settings:

		field_list.append(setting.variant_information.information.replace('.', '_')) #create a list containing the INFO field IDs needed N.B replace '.' with '_' for template


	#Get the vcf file and get the data e.g. ref, chrom, INFO
	#Get the genes from the vcf file
	#Pass these to the template


	vcf_file_path = sample.vcf_file

	data = pysam_extract.create_master_list(vcf_file_path, sample.name)

	genes = pysam_extract.get_genes_in_file(vcf_file_path, sample.name)



	return render(request, 'VariantDatabase/list_sample_variants.html', {'sample': sample, 'data': data, 'genes': genes, 'field_list': field_list})





@login_required
def variant_detail(request):

	return render(request, 'VariantDatabase/variant_detail.html', {})


@login_required
def search_page(request):

	query = request.GET.get('query')

	return render(request, 'VariantDatabase/search_results.html', {'query': query})


@login_required
def settings(request):

	"""
	View to allow user to customise which columns they would like in the list_sample_variants view


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



		#get what the user has just inputted and put into a dictionary - tick_box_dict
		#This allows us to tick the tickboxes in the html template

		current_user_settings = UserSetting.objects.filter(user=request.user)

		tick_box_dict ={}

		for setting in current_user_settings:

			tick_box_dict[setting.variant_information.information] =True

				
		return render(request, 'VariantDatabase/settings.html' ,{'all_fields': all_fields, 'tick_box_dict': tick_box_dict})


	else:

		#get what the current user settings put into a dictionary - tick_box_dict
		#This allows us to pre-tick the tickboxes in the html template

		current_user_settings = UserSetting.objects.filter(user=request.user)

		tick_box_dict ={}

		for setting in current_user_settings:

			tick_box_dict[setting.variant_information.information] =True


		return render(request, 'VariantDatabase/settings.html' ,{'all_fields': all_fields, 'tick_box_dict': tick_box_dict})


def error(request):

	message = request.GET.get('message')

	return render(request, 'VariantDatabase/error.html', {'message':message})




def upload_sample(request):


	if request.method == "POST":

		form = SampleForm(request.POST)

		if form.is_valid():

			new_sample = form.save(commit=False)

			new_sample.hash = 'None'

			new_sample.save()

			#create new SampleStatusUpdate
			#The SampleStatusUpdate will be set to 'new'

			inital_status = get_object_or_404(SampleStatus, pk=1)

			new_update = SampleStatusUpdate(sample=new_sample, status=inital_status, user=request.user, date=timezone.now())

			new_update.save()

			#Now we check whether for each of the variants in that file do we have a variant in the Variant Model
			#If not create one and then create a corresponding VariantSample record
			#Otherwise just create another VariantSample record

			data = pysam_extract.create_master_list(new_sample.vcf_file, new_sample.name)

			

			try:

				data = pysam_extract.create_master_list(vcf_file_path, new_sample.name)



			except:

				new_sample.delete()
				new_update.delete()

				return redirect('error')

			

			for variant in data:

				#see if we have this variant in the database (Variant table) already?
				#assumes normalisation and one alt allele per variant
				#assumes chromosome in same format - need to validate?

				chromosome = variant['chrom']
				pos = str(variant['pos'])
				ref = variant['reference']
				alt = variant['alt_alleles'][0]

				hash_id = hashlib.sha256(chromosome+pos+ref+alt).hexdigest()

				count = Variant.objects.filter(variant_hash=hash_id).count()

				if count ==0: # new variant

					new_variant = Variant(chromosome=chromosome, position=pos, ref= ref, alt=alt, variant_hash= hash_id)

					new_variant.save()

					new_variant_sample = VariantSample(variant=new_variant, sample=new_sample)

					new_variant_sample.save()


				else: #old variant

					existing_variant = get_object_or_404(Variant, variant_hash=hash_id)

					new_variant_sample = VariantSample(variant=existing_variant, sample=new_sample)

					new_variant_sample.save()


			return redirect('home_page')

	form = SampleForm

	return render(request, 'VariantDatabase/upload.html', {'form': form})