from django.shortcuts import render, get_object_or_404, redirect
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import parsers.vcf_parser as vcf_parser
import parsers.file_parsers as parsers
from django.forms import modelformset_factory
import collections
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404, JsonResponse
import re
import base64
from django.core.files.base import ContentFile
from django.core.files import File
import VariantDatabase.utils.variant_utilities as variant_utilities


from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from VariantDatabase.serializers import VariantFreqSerializer
import myvariant
import urllib2

import json
from django.db import transaction


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

	return render(request,
				'VariantDatabase/list_worksheet_samples.html',
				{'samples_in_worksheet': samples_in_worksheet, 'form': form, 'worksheet': worksheet, 'quality_data': quality_data})



@login_required
def sample_summary(request, pk_sample):

	"""
	This view displays the various information about a sample

	"""

	#print request.GET.get('consequences'), 'hi'

	sample = get_object_or_404(Sample, pk=pk_sample)

	total_summary = sample.total_variant_summary()

	reports = Report.objects.filter(sample=sample)

	if request.method == "POST": #if the user clicked create a new report 

		if 'reportform' in request.POST:

			report_form = ReportForm(request.POST)

			if report_form.is_valid():

				report = report_form.save(commit=False)
				report.sample = sample
				report.status ='1'
				report.user = request.user

				report.save()

				return redirect(create_sample_report, sample.pk, report.pk, '1')

	elif 'submit_filter_form' in request.GET: #if the user clicked filter

		filter_form = FilterForm(request.GET)

		if filter_form.is_valid():

			consequences =  filter_form.cleaned_data['consequences']

			consequences_to_include =[]

			for consequence in consequences:

				if consequence == 'five_prime_UTR_variant': #can't start python variables with a number so have to change key from 5_prime_UTR_variant to five_prime_UTR_variant

					consequences_to_include.append('5_prime_UTR_variant')

				elif consequence == 'three_prime_UTR_variant':

					consequences_to_include.append('3_prime_UTR_variant')

				else:

					consequences_to_include.append(consequence)

			max_af = request.GET.get('max_af')

			consequences_query_set = Consequence.objects.filter(name__in = consequences_to_include)


			if sample.sample_gene_filter.name == 'None':

				apply_gene_filter = False

			else:

				apply_gene_filter = True 

			variant_samples = sample.get_filtered_variants(consequences_query_set,max_af, apply_gene_filter)

			variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list('variant_id', flat=True))

			summary = sample.variant_query_set_summary(variants)

			gene_coverage = GeneCoverage.objects.filter(sample=sample)

			exon_coverage = ExonCoverage.objects.filter(sample=sample)

			user_settings = UserSetting.objects.filter(user=request.user)

			report_form = ReportForm()


			return render(request,
						 'VariantDatabase/sample_summary.html',
						  {'sample': sample, 'variants': variant_samples,
							'reports': reports, 'report_form': report_form,
							'summary': summary, 'total_summary': total_summary,
						 	'gene_coverage': gene_coverage,
						 	'exon_coverage': exon_coverage , 'user_settings': user_settings, 'filter_form': filter_form })

	else:

		filter_dict = sample.worksheet.sub_section.create_filter_dict()

		consequences_to_include =[]

		for key in filter_dict:

			if 'freq' not in key and filter_dict[key] ==True:

				if key == 'five_prime_UTR_variant':

					consequences_to_include.append('5_prime_UTR_variant')

				elif key == 'three_prime_UTR_variant':

					consequences_to_include.append('3_prime_UTR_variant')

				else:

					consequences_to_include.append(key)


		consequences_query_set = Consequence.objects.filter(name__in = consequences_to_include)

		if sample.sample_gene_filter.name == 'None':

			apply_gene_filter = False

		else:

			apply_gene_filter = True 

		variant_samples = sample.get_filtered_variants(consequences_query_set,filter_dict['freq_max_af'], apply_gene_filter)
														 
		variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list('variant_id', flat=True))

		summary = sample.variant_query_set_summary(variants)

		gene_coverage = GeneCoverage.objects.filter(sample=sample)

		exon_coverage = ExonCoverage.objects.filter(sample=sample)

		user_settings = UserSetting.objects.filter(user=request.user)

		report_form = ReportForm()

		filter_form = FilterForm()

		filter_form.fields['consequences'].initial = filter_dict
		filter_form.fields['max_af'].initial = filter_dict['freq_max_af']

		return render(request,
					 'VariantDatabase/sample_summary.html',
					  {'sample': sample, 'variants': variant_samples,
						'reports': reports, 'report_form': report_form,  'summary': summary,
						'total_summary': total_summary, 'gene_coverage': gene_coverage,
						'exon_coverage': exon_coverage, 'user_settings': user_settings, 'filter_form': filter_form})


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

	return render(request, 'VariantDatabase/variant_detail.html', {'variant': variant, 'transcripts': transcripts, 'other_alleles': other_alleles})

@login_required
def view_gene(request, gene_pk):
	"""
	A view to allow the user to view all the Variants in a Gene.

	"""

	gene_pk = gene_pk.upper()

	gene = Gene.objects.get(name=gene_pk)

	variants = gene.get_all_variants()

	return render(request,'VariantDatabase/gene.html', {'variants': variants, 'gene': gene})

@login_required
def view_detached_variant(request, variant_hash):
	"""
	View a variant independent of any sample it is associated with.

	"""
	
	variant = get_object_or_404(Variant, variant_hash=variant_hash)

	other_alleles = variant.get_other_alleles()

	transcripts = VariantTranscript.objects.filter(variant = variant)

	frequency_data = variant.get_frequency_data()

	samples = variant.get_samples_with_variant()


	return render(request, 'VariantDatabase/variant_view.html', {'variant': variant, 'transcripts': transcripts, 'other_alleles': other_alleles,
	 			'frequency_data': frequency_data, 'samples':samples } )


@login_required
def ajax_detail(request):
	"""
	Ajax View - create the top div of the summary page e.g. detial, IGV, evidence when a user clicks the row.

	"""

	if request.is_ajax():

		variant_hash = request.GET.get('variant_hash')
		sample_pk = request.GET.get('sample_pk')

		variant_hash = variant_hash.strip()
		sample_pk = sample_pk.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))
		sample = Sample.objects.get(pk=sample_pk)

		variant_sample = VariantSample.objects.get(variant=variant, sample=sample)

		comments =Comment.objects.filter(variant_sample=variant_sample)

		perms = request.user.has_perm('VariantDatabase.add_comment')


		html = render_to_string('VariantDatabase/ajax_detail.html', {'variant': variant, 'sample': sample, 'comments': comments, 'perms': perms})

		return HttpResponse(html)

	else:

		raise Http404

@login_required
def ajax_comments(request):
	"""
	Ajax View - when the user clicks the upload comment/file button this updates the comment section of the page.

	Clipboard paste only works on HTML5 enabled browser

	"""

	if request.is_ajax():

		variant_hash = request.POST.get('variant_hash')
		sample_pk = request.POST.get('sample_pk')
		comment_text = request.POST.get('comment_text')

		variant_hash = variant_hash.strip()
		sample_pk = sample_pk.strip()
		comment_text = comment_text.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))
		sample = Sample.objects.get(pk=sample_pk)
		variant_sample = VariantSample.objects.get(variant=variant, sample=sample)

		if len(comment_text) >1: #Check user has entered a comment

			new_comment = Comment(user=request.user, text=comment_text, time=timezone.now(),variant_sample=variant_sample )

			new_comment.save()

			if request.FILES.get('file', False) != False: #Deal with files selected using the file selector html widget 

				file = request.FILES.get('file')

				new_evidence = Evidence()

				new_evidence.file = file

				new_evidence.comment= new_comment

				new_evidence.save()


			if request.POST.get('image_data') !=None: #deal with images pasted in from the clipboard

				image_data = request.POST.get('image_data')

				image_data = image_data.strip() #strip of any leading characters

				dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$') #add appropiate header

				ImageData = dataUrlPattern.match(image_data).group(2)

				ImageData = base64.b64decode(ImageData) #to binary

				new_evidence = Evidence()

				new_evidence.comment= new_comment

				new_evidence.file.save(str(sample.pk)+"_"+str(new_comment.pk)+"_clip_image.png", ContentFile(ImageData)) #save image

				new_evidence.save()

		comments =Comment.objects.filter(variant_sample=variant_sample)

		html = render_to_string('VariantDatabase/ajax_comments.html', {'comments': comments, 'variant': variant, 'sample': sample})

		return HttpResponse(html)

	else:

		raise Http404



@login_required
def ajax_table_expand(request):
	"""
	An AJAX view for the child rows in the Summary page view.

	It returns the HTML data that goes in the child row.


	"""

	if request.is_ajax():

		variant_hash = request.GET.get('variant_hash')

		variant_hash = variant_hash.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))

		variant_transcripts = VariantTranscript.objects.filter(variant=variant)

		html = render_to_string('VariantDatabase/ajax_table_expand.html', {'variant_transcripts': variant_transcripts})

		return HttpResponse(html)


	else:

		raise Http404

@login_required
def user_settings(request):
	"""
	View with a form for changing user settings.

	"""


	user_settings = UserSetting.objects.filter(user=request.user)


	if request.method == 'POST':


		user_settings = user_settings[0]


		form = UserSettingsForm(request.POST, instance=user_settings)

		if form.is_valid():

			user_settings = form.save()

			return redirect('home_page')

	if user_settings.exists():

		form = UserSettingsForm(instance=user_settings[0])

	else:

		user_settings = UserSetting(user=request.user)
		user_settings.save()

		form = UserSettingsForm(instance=user_settings)

	
	return render(request, 'VariantDatabase/user_settings.html' , {'form': form})

@login_required
def search(request):
	"""
	Main search page for the database.

	Currently allows :

	1) searching by variant  e.g. 2-4634636-A-T
	2) searching by gene e.g. JAK2
	3) search by location e.g. 4-649636
	4) search by region e.g. 9:646046:646086
	4) search by sample e.g. D16-35395

	"""

	form = SearchForm()

	if request.GET.get('search') != "" and request.GET.get('search') != None: #if the user has searched for something

		#Get the query and clean it up

		search_query = request.GET.get('search').upper()

		search_query = search_query.strip()

		#Compile a number of regexes to match what the user might have searched for.
		#We can direct them to different pages depending on the match.

		variant_search = re.compile("^([0-9]{1,2}|[XYxy])-\d{1,12}-[ATGCatgc]+-[ATGCatgc]+$") #matches a variant search e.g. 22-549634966-AG-TT

		gene_search = re.compile("^[A-Z][A-Z0-9]+$") #matches a string which looks like a gene name e.g. JAK2

		location_search = re.compile('^([0-9]{1,2}|[XYxy])-\d{1,12}$') #matches a string which looks a location e.g. 9-434343

		region_search = re.compile('^([0-9]{1,2}|[XYxy]):\d{1,12}-\d{1,12}$')  #matches a string which looks a region e.g. 9:646046:646086

		sample_search = re.compile('D[0-9]{1,2}-[0-9]{1,9}') #matches a string which looks a sample e.g. D16-35395


		if variant_search.match(search_query): # if we have searched for a variant

			variant_list = search_query.split('-')

			chromosome = 'chr'+variant_list[0]
			position = variant_list[1]
			ref = variant_list[2]
			alt = variant_list[3]

			variant_hash = variant_utilities.get_variant_hash(chromosome,position,ref,alt)

			try:

				Variant.objects.get(variant_hash=variant_hash)

			except:

				return render(request, 'VariantDatabase/search.html' , {'error': True, 'form': form})


			return redirect(view_detached_variant, variant_hash)


		elif gene_search.match(search_query): # if we have searched for a gene

			try:

				gene = Gene.objects.get(name=search_query)

			except:

				return render(request, 'VariantDatabase/search.html' , {'error': True, 'form': form})

			return redirect(view_gene, search_query)

		elif location_search.match(search_query): # if we have searched for a location


			return redirect(view_location_search, search_query)

		elif region_search.match(search_query): # if we have searched for a region

			search_query = search_query.replace(':', '-') #urls don't like colons

			return redirect(view_region_search, search_query)

		elif sample_search.search(search_query): # if we have searched for a sample

			samples = Sample.objects.filter(name__contains=search_query)

			if len(samples) == 1: #If only one sample matches then go direct to that page

				return redirect(sample_summary, samples[0].pk)

			elif len(samples) ==0: #no samples match - query error

				return render(request, 'VariantDatabase/search.html' , {'error': True, 'form': form})

			else: #>1 sample match - redirect to view_sample_search. Let user sort it out.

				return redirect(view_sample_search, search_query)


			return render(request, 'VariantDatabase/search.html' , {'form': form})


		else:

			return render(request, 'VariantDatabase/search.html' , {'error': True, 'form': form})


	else:


		return render(request, 'VariantDatabase/search.html' , {'form': form})


def create_sample_report(request, pk_sample, pk_report, check_number):
	"""
	A view for creating and checking sample reports.

	Sample Reports can be created from the Summary View.




	"""
	report = get_object_or_404(Report, pk=pk_report)

	sample = get_object_or_404(Sample, pk=pk_sample)

	total_summary = sample.total_variant_summary()

	filter_dict = sample.worksheet.sub_section.create_filter_dict()

	filter_form = FilterForm(initial=filter_dict)

	consequences_to_include =[]

	for key in filter_dict:

		if 'freq' not in key and filter_dict[key] ==True:

			if key == 'five_prime_UTR_variant':

				consequences_to_include.append('5_prime_UTR_variant')

			elif key == 'three_prime_UTR_variant':

				consequences_to_include.append('3_prime_UTR_variant')

			else:

				consequences_to_include.append(key)


	consequences_query_set = Consequence.objects.filter(name__in = consequences_to_include)

	if sample.sample_gene_filter.name == 'None':

		apply_gene_filter = False

	else:

		apply_gene_filter = True 

	variant_samples =sample.get_filtered_variants(consequences_query_set, filter_dict['freq_max_af'], apply_gene_filter)

	variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list('variant_id', flat=True))

	summary = sample.variant_query_set_summary(variants)

	user_settings = UserSetting.objects.filter(user=request.user)

	classifications = Classification.objects.filter(subsection=sample.worksheet.sub_section)

	return render(request,
				'VariantDatabase/create_sample_report.html',
				{'sample': sample, 'variants': variant_samples,  'summary': summary,
				'total_summary': total_summary, 'user_settings': user_settings,
				'classifications': classifications, 'report': report, 'check_number': check_number })


def ajax_receive_classification_data(request):

	if request.is_ajax():

		sample_pk = request.POST.get('sample_pk')
		report_pk = request.POST.get('report_pk')
		check_number = request.POST.get('check_number')


		sample = get_object_or_404(Sample, pk=sample_pk.strip())
		report = get_object_or_404(Report, pk = report_pk.strip())


		if report.status == '1' and check_number.strip() =='1' :

			classifications = request.POST.get('classifications')

			classifications = json.loads(classifications)


			with transaction.atomic(): 

				for key in classifications:

					variant_hash = key.strip()

					variant = get_object_or_404(Variant, variant_hash=variant_hash)

					data = classifications[key]

					classification = data[0].strip()

					user_hgvs = data[1].strip()

					classification = get_object_or_404(Classification, name =classification)


					new_report_sample_variant_classification = ReportVariantSampleClassification(

						report = report, variant=variant,classification1=classification,
						user1=request.user, date1 = timezone.now(), user_hgvs1 =user_hgvs

						)


					new_report_sample_variant_classification.save()


				report.status ='2'
				report.save()

				return HttpResponse('Done')

		elif report.status == '2' and check_number.strip() =='2' :

			classifications = request.POST.get('classifications')

			classifications = json.loads(classifications)


			with transaction.atomic(): 

				for key in classifications:

					variant_hash = key.strip()

					variant = get_object_or_404(Variant, variant_hash=variant_hash)

					data = classifications[key]

					classification = data[0].strip()

					user_hgvs = data[1].strip()

					classification = get_object_or_404(Classification, name =classification)

					report_sample_variant_classification = ReportVariantSampleClassification.objects.filter(report=report, variant=variant)


					if len(report_sample_variant_classification) ==1:

						report_sample_variant_classification =report_sample_variant_classification[0]

						report_sample_variant_classification.classification2 = classification
						report_sample_variant_classification.user2 = request.user
						report_sample_variant_classification.date2 = timezone.now()
						report_sample_variant_classification.user_hgvs2 = user_hgvs

						report_sample_variant_classification.save()

					else:

						return HttpResponse('An error occured: Either >1 or no existing report_sample_variant_classification')



				if report.number_of_mismatches() == 0:


					report_sample_variant_classifications = ReportVariantSampleClassification.objects.filter(report=report)

					for variant_classification in report_sample_variant_classifications:

						variant_classification.final_classification = variant_classification.classification2
						variant_classification.final_user = request.user
						variant_classification.final_date = timezone.now()
						variant_classification.final_hgvs = variant_classification.user_hgvs2

						variant_classification.save()


					report.status ='4'





				else:
					
					report.status ='3'

				report.save()


				return HttpResponse('Done')

		elif report.status == '3' and check_number.strip() =='3' :

			classifications = request.POST.get('classifications')

			classifications = json.loads(classifications)

			with transaction.atomic(): 

				for key in classifications:

					variant_hash = key.strip()

					variant = get_object_or_404(Variant, variant_hash=variant_hash)

					data = classifications[key]

					classification = data[0].strip()

					user_hgvs = data[1].strip()

					classification = get_object_or_404(Classification, name =classification)

					report_sample_variant_classification = ReportVariantSampleClassification.objects.filter(report=report, variant=variant)


					if len(report_sample_variant_classification) ==1:

						report_sample_variant_classification =report_sample_variant_classification[0]

						report_sample_variant_classification.final_classification = classification
						report_sample_variant_classification.final_user = request.user
						report_sample_variant_classification.final_date = timezone.now()
						report_sample_variant_classification.final_hgvs = user_hgvs

						report_sample_variant_classification.save()

					else:

						return HttpResponse('An error occured: Either >1 or no existing report_sample_variant_classification')



				report_sample_variant_classifications = ReportVariantSampleClassification.objects.filter(report=report)

				for variant_classification in report_sample_variant_classifications:

					if variant_classification.final_classification == None:

						variant_classification.final_classification = variant_classification.classification2
						variant_classification.final_user = request.user
						variant_classification.final_date = timezone.now()
						variant_classification.final_hgvs = variant_classification.user_hgvs2

						variant_classification.save()


				report.status ='4'
				report.save()

				return HttpResponse('Done')

		else:

			return HttpResponse('Already done the check')


	return HttpResponse('ajax error')

def resolve_check_differences(request, pk_sample, pk_report):


	sample = get_object_or_404(Sample, pk=pk_sample)

	report = get_object_or_404(Report, pk=pk_report)

	user_settings = UserSetting.objects.filter(user=request.user)

	classifications = Classification.objects.filter(subsection=sample.worksheet.sub_section)

	report_sample_variant_classifications = ReportVariantSampleClassification.objects.filter(report=report)

	variant_classification_list =[]

	for variant_classification in report_sample_variant_classifications:

		variant_sample = get_object_or_404(VariantSample, variant=variant_classification.variant, sample=sample)

		variant_classification_list.append((variant_sample, variant_classification))


	matches =[]

	discrepencies =[]


	for variant_classification in variant_classification_list:

		if variant_classification[1].classification_match() == True:

			matches.append(variant_classification)

		else:

			discrepencies.append(variant_classification)


	return render(request, 'VariantDatabase/resolve_check_differences.html', {'matches': matches, 'discrepencies': discrepencies,'sample': sample,
	  			'user_settings': user_settings,'classifications': classifications, 'report': report, })




def view_sample_report(request, pk_sample, pk_report):
	"""
	Allow the viewing of reports

	"""


	sample = get_object_or_404(Sample, pk=pk_sample)
	report = get_object_or_404(Report, pk=pk_report)


	list =[]

	report_sample_variant_classifications = ReportVariantSampleClassification.objects.filter(report=report)

	list.append(report_sample_variant_classifications)




	return render(request, 'VariantDatabase/view_sample_report.html', {'list': list})



def view_location_search(request,location):

	location_list = location.split('-')

	chromosome = 'chr'+location_list[0]

	position = location_list[1]

	variants = Variant.objects.filter(chromosome=chromosome, position = position)

	return render(request,'VariantDatabase/view_location_search.html', {'variants': variants, 'location':location})

def view_region_search(request,location):

	location_list = location.split('-')

	chromosome = 'chr'+location_list[0]

	start_pos = location_list[1]

	end_pos = location_list[2]

	variants = Variant.objects.filter(chromosome=chromosome, position__gte = start_pos, position__lte=end_pos)

	return render(request,'VariantDatabase/view_location_search.html', {'variants': variants, 'location':location})

def view_sample_search(request,sample_query):

	samples = Sample.objects.filter(name__contains=sample_query)


	return render(request,'VariantDatabase/view_sample_search.html', {'samples': samples,'sample_query': sample_query})





def api_variants(request):
	"""
	API for getting all variants

	"""

	if request.method == 'GET':

		variants = Variant.objects.all()

		serializer = VariantFreqSerializer(variants, many=True)
		return JsonResponse(serializer.data, safe=False)
















