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
from django.http import HttpResponse, Http404
import re
import base64
from django.core.files.base import ContentFile
from django.core.files import File


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
def search(request):

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

			

	return render(request, 'VariantDatabase/search.html', {'gene_name': gene_name, 'alts': alts})


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

	if request.is_ajax():

		variant_hash = request.GET.get('variant_hash')
		sample_pk = request.GET.get('sample_pk')

		variant_hash = variant_hash.strip()
		sample_pk = sample_pk.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))
		sample = Sample.objects.get(pk=sample_pk)

		variant_sample = VariantSample.objects.get(variant=variant, sample=sample)

		comments =Comment.objects.filter(variant_sample=variant_sample)

		html = render_to_string('VariantDatabase/ajax_detail.html', {'variant': variant, 'sample': sample, 'comments': comments})

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

		form = UserSettingsForm(user=request.user)

	
	return render(request, 'VariantDatabase/user_settings.html' , {'form': form})
