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
def sample_summary(request, pk_sample):

	"""
	This view displays the various information about a sample

	"""

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

				report.save()

				report.initialise_report()

				return redirect(create_sample_report, sample.pk, report.pk)




	elif 'filterform' in request.GET: #if the user clicked filter

		filter_form = FilterForm(request.GET)

		report_form = ReportForm()

		consequences_to_include =[]

		for key in request.GET:

			if key != 'csrfmiddlewaretoken' and key != 'filterform' and 'freq' not in key:


				if key == 'five_prime_UTR_variant': #can't start python variables with a number so have to change key from 5_prime_UTR_variant to five_prime_UTR_variant

					consequences_to_include.append('5_prime_UTR_variant')

				elif key == 'three_prime_UTR_variant':

					consequences_to_include.append('3_prime_UTR_variant')

				else:

					consequences_to_include.append(key)

		max_af = request.GET.get('freq_max_af')

		consequences_query_set = Consequence.objects.filter(name__in = consequences_to_include)

		variant_samples =VariantSample.objects.filter(sample=sample, variant__worst_consequence__in=consequences_query_set).filter(variant__max_af__lte=max_af).order_by('variant__worst_consequence__impact', 'variant__max_af') #performance?

		variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list('variant_id', flat=True))

		summary = sample.variant_query_set_summary(variants)

		gene_coverage = GeneCoverage.objects.filter(sample=sample)

		exon_coverage = ExonCoverage.objects.filter(sample=sample)

		user_settings = UserSetting.objects.filter(user=request.user)

		return render(request, 'VariantDatabase/sample_summary.html', {'sample': sample, 'variants': variant_samples, 'report_form': report_form, 'reports': reports,  'summary': summary, 'total_summary': total_summary,
					 'filter_form': filter_form, 'gene_coverage': gene_coverage,'exon_coverage': exon_coverage , 'user_settings': user_settings })


	else:

		filter_dict = sample.worksheet.sub_section.create_filter_dict()

		report_form = ReportForm()

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

		variant_samples =VariantSample.objects.filter(sample=sample, variant__worst_consequence__in=consequences_query_set).filter(variant__max_af__lte=filter_dict['freq_max_af']).order_by('variant__worst_consequence__impact', 'variant__max_af')

		variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list('variant_id', flat=True))

		summary = sample.variant_query_set_summary(variants)

		gene_coverage = GeneCoverage.objects.filter(sample=sample)

		exon_coverage = ExonCoverage.objects.filter(sample=sample)

		user_settings = UserSetting.objects.filter(user=request.user)

		

		return render(request, 'VariantDatabase/sample_summary.html', {'sample': sample, 'variants': variant_samples, 'report_form': report_form, 'reports': reports,  'summary': summary, 'total_summary': total_summary,
					 'filter_form': filter_form, 'filter_dict': filter_dict, 'cons': consequences_to_include, 'gene_coverage': gene_coverage,'exon_coverage': exon_coverage, 'user_settings': user_settings})



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

	form = SearchFilterForm()

	return render(request,'VariantDatabase/gene.html', {'variants': variants, 'gene': gene, 'form': form})

@login_required
def view_detached_variant(request, variant_hash):
	"""
	View a variant independent of any sample it is associated with.

	"""
	
	variant = get_object_or_404(Variant, variant_hash=variant_hash)

	other_alleles = variant.get_other_alleles()

	transcripts = VariantTranscript.objects.filter(variant = variant)


	return render(request, 'VariantDatabase/variant_view.html', {'variant': variant, 'transcripts': transcripts, 'other_alleles': other_alleles} )

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
	2) searching by gene

	"""

	form = SearchForm()

	if request.GET.get('search') != "" and request.GET.get('search') != None: #if we have typed in the main search

		search_query = request.GET.get('search').upper()

		variant_search = re.compile("^([1-9]{1,2}|[XYxy])-\d{1,10}-[ATGCatgc]+-[ATGCatgc]+$") #matches a variant search e.g. 22-549634966-AG-TT

		gene_search = re.compile("^[A-Z][A-Z1-9]+$") #matches a string which looks like a gene name


		if variant_search.match(search_query): #we have searched for a variant

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


		elif gene_search.match(search_query): #Looks like a gene

			try:

				gene = Gene.objects.get(name=search_query)

			except:

				return render(request, 'VariantDatabase/search.html' , {'error': True, 'form': form})

			return redirect(view_gene, search_query)


		else:

			return render(request, 'VariantDatabase/search.html' , {'error': True, 'form': form})


	else:


		return render(request, 'VariantDatabase/search.html' , {'form': form})

#Under development
def api_variants(request):
	"""
	API for getting all variants

	"""

	if request.method == 'GET':

		variants = Variant.objects.all()

		serializer = VariantFreqSerializer(variants, many=True)
		return JsonResponse(serializer.data, safe=False)


def additional_annotation(request, variant_sample_pk):

	variant_sample = get_object_or_404(VariantSample, pk=variant_sample_pk)

	variant = variant_sample.variant

	chromosome = variant.chromosome[3:]
	position = variant.position
	ref = variant.ref
	alt = variant.alt

	mv = myvariant.MyVariantInfo()

	q= 'chrom:'+chromosome + ' AND vcf.position:' + str(position) + ' AND vcf.ref:' + ref + ' AND vcf.alt:' + alt

	#data = mv.query(q)

	response = urllib2.urlopen('http://python.org/')
	html = response.read()


	return JsonResponse(html, safe=False)















