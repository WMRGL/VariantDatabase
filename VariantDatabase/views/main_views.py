from django.shortcuts import render, get_object_or_404, redirect
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
from VariantDatabase.forms import *
from django.utils import timezone
import VariantDatabase.parsers.vcf_parser as vcf_parser
import VariantDatabase.parsers.file_parsers as parsers
import re
import VariantDatabase.utils.variant_utilities as variant_utilities
from django.db import transaction
from rolepermissions.checkers import has_permission
from django.core.exceptions import PermissionDenied
from rolepermissions.decorators import has_permission_decorator


@login_required
def home_page(request):
	"""
	The homepage
	"""

	return render(request, "VariantDatabase/home_page.html", {})

@login_required
def list_sections(request):

	"""
	This view allows the user to view a section page

	On this page the relevent worksheets will be shown.

	TODO: sort worksheets by status

	"""

	all_sections = Section.objects.all()

	return render(request, "VariantDatabase/list_sections.html",
				 {"all_sections": all_sections} )



@login_required
def list_worksheet_samples(request, pk_worksheet):

	"""
	This view lists the samples in a particular worksheet

	"""

	worksheet = get_object_or_404(Worksheet, pk=pk_worksheet)


	if request.method == "POST":

		if has_permission(request.user, 'approve_qc') == False:

			raise PermissionDenied

		#if user is authorised
		worksheet = worksheet = get_object_or_404(Worksheet, pk=pk_worksheet)
		worksheet.status = "3"
		worksheet.save()

		return redirect(list_worksheet_samples, pk_worksheet)


	else:

		form = WorksheetStatusUpdateForm()

		quality_data = worksheet.get_quality_data()


	samples_in_worksheet = (Sample
								.objects
								.filter(worksheet = worksheet, visible=True))

	return render(request,
				"VariantDatabase/list_worksheet_samples.html",
				{"samples_in_worksheet": samples_in_worksheet,
				 "form": form,
				 "worksheet": worksheet,
				 "quality_data": quality_data})



@login_required
def sample_summary(request, pk_sample):

	"""
	This view displays the various information about a sample

	"""

	sample = get_object_or_404(Sample, pk=pk_sample)

	reports = Report.objects.filter(sample=sample)

	if request.method == "POST": #if the user clicked create a new report


		if has_permission(request.user, 'create_report') == False:

			raise PermissionDenied

		if "reportform" in request.POST:

			report_form = ReportForm(request.POST)

			if report_form.is_valid():

				report = report_form.save(commit=False)
				report.sample = sample
				report.status ="1"
				report.report_creator = request.user
				report.creation_date = timezone.now()
				report.panel = sample.panel
				report.default_filter = sample.worksheet.sub_section.default_filter

				report.save()

				return redirect(create_sample_report, sample.pk, report.pk, "1")



	else:

		if "submit_filter_form" in request.GET: #if the user clicked filter

			filter_form = FilterForm(request.GET)

			if filter_form.is_valid():

				consequences =  filter_form.cleaned_data["consequences"]

				consequences_to_include = (variant_utilities
											.create_conseqences_to_include_form(consequences))

				max_af = filter_form.cleaned_data["max_af"]

				panel_pk = filter_form.cleaned_data["panels"]

				update_panel = filter_form.cleaned_data["update_panel"]

				panel = get_object_or_404(Panel, pk=panel_pk)

				if update_panel == True:

					sample.panel = panel
					sample.save()


		else:

			#use default settings for subsection
			filter_dict = sample.worksheet.sub_section.default_filter.create_filter_dict()

			consequences_to_include = variant_utilities.create_conseqences_to_include(filter_dict)

			max_af = filter_dict['freq_max_af']

			panel = sample.panel

			filter_form = FilterForm(initial={"panels": panel.pk})

			filter_form.fields["consequences"].initial = filter_dict
			filter_form.fields["max_af"].initial = filter_dict["freq_max_af"]

			
		variant_samples = VariantSample.objects.filter(sample=sample).select_related('variant')

		variants = (Variant
					.objects
					.filter(variant_hash__in= variant_samples
					.values_list("variant_id",flat=True)))

		total_summary = variant_utilities.variant_query_set_summary(variants)


		if panel.name == "None":

			variant_samples = (variant_utilities
								.get_filtered_variants(variant_samples,
													 	consequences_to_include,
													 	max_af))


		else:

			variant_samples = (variant_utilities
					.get_filtered_variants(variant_samples,
										 	consequences_to_include,
										 	max_af, panel))
										 
		variants = (Variant
					.objects
					.filter(variant_hash__in= variant_samples
					.values_list("variant_id",flat=True)))

		summary = variant_utilities.variant_query_set_summary(variants)

		gene_coverage = GeneCoverage.objects.filter(sample=sample)

		exon_coverage = ExonCoverage.objects.filter(sample=sample)

		user_settings = UserSetting.objects.filter(user=request.user)

		report_form = ReportForm()

		return render(  request,
						"VariantDatabase/sample_summary.html",
						{"sample": sample,
						"variants": variant_samples,
						"reports": reports,
						"report_form": report_form,
						"summary": summary,
						"total_summary": total_summary,
					 	"gene_coverage": gene_coverage,
					 	"exon_coverage": exon_coverage,
					 	"user_settings": user_settings,
					 	"filter_form": filter_form,
					 	"panel":panel })



@login_required
def variant_detail(request, pk_sample, variant_hash):

	"""
	This view displays the detial for a particular variant.

	It combines - sample specific annoation data e.g. pulled from the vcf
				- Global variant data e.g. chr, pos, ref, freq

	"""

	sample = get_object_or_404(Sample, pk=pk_sample)

	variant = get_object_or_404(Variant, variant_hash=variant_hash)

	other_alleles = variant.get_other_alleles()

	transcripts = VariantTranscript.objects.filter(variant = variant)

	return render(request,
					"VariantDatabase/variant_detail.html",
					{"variant": variant,
					"transcripts": transcripts,
					"other_alleles": other_alleles})

@login_required
def view_gene(request, gene_pk):
	"""
	A view to allow the user to view all the Variants in a Gene.

	"""

	gene_pk = gene_pk.upper()

	gene = Gene.objects.get(name=gene_pk)

	variants = gene.get_all_variants()

	return render(request,"VariantDatabase/gene.html", {"variants": variants, "gene": gene})

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

	return render(request,
					"VariantDatabase/variant_view.html",
					{"variant": variant,
					"transcripts": transcripts,
					"other_alleles": other_alleles,
	 				"frequency_data": frequency_data,
	 				"samples":samples } )

@login_required
def user_settings(request):
	"""
	View with a form for changing user settings.

	"""


	user_settings = UserSetting.objects.filter(user=request.user)


	if request.method == "POST":


		user_settings = user_settings[0]


		form = UserSettingsForm(request.POST, instance=user_settings)

		if form.is_valid():

			user_settings = form.save()

			return redirect("home_page")

	if user_settings.exists():

		form = UserSettingsForm(instance=user_settings[0])

	else:

		user_settings = UserSetting(user=request.user)
		user_settings.save()

		form = UserSettingsForm(instance=user_settings)

	
	return render(request, "VariantDatabase/user_settings.html" , {"form": form})

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


	#if the user has searched for something
	if request.GET.get("search") != "" and request.GET.get("search") != None: 

		#Get the query and clean it up

		search_query = request.GET.get("search").upper()

		search_query = search_query.strip()

		#Compile a number of regexes to match what the user might have searched for.
		#We can direct them to different pages depending on the match.

		#matches a variant search e.g. 22-549634966-AG-TT
		variant_search = re.compile("^([0-9]{1,2}|[XYxy])-\d{1,12}-[ATGCatgc]+-[ATGCatgc]+$") 

		#matches a string which looks like a gene name e.g. JAK2
		gene_search = re.compile("^[A-Z][A-Z0-9]+$") 

		#matches a string which looks a location e.g. 9-434343
		location_search = re.compile("^([0-9]{1,2}|[XYxy])-\d{1,12}$") 

		#matches a string which looks a region e.g. 9:646046:646086
		region_search = re.compile("^([0-9]{1,2}|[XYxy]):\d{1,12}-\d{1,12}$")  

		#matches a string which looks a sample e.g. D16-35395
		sample_search = re.compile("D[0-9]{1,2}-[0-9]{1,9}") 


		if variant_search.match(search_query): # if we have searched for a variant

			variant_list = search_query.split("-")

			chromosome = "chr"+variant_list[0]
			position = variant_list[1]
			ref = variant_list[2]
			alt = variant_list[3]

			variant_hash = variant_utilities.get_variant_hash(chromosome,position,ref,alt)

			try:

				Variant.objects.get(variant_hash=variant_hash)

			except:

				return render(request,
							"VariantDatabase/search.html",
							{"error": True, "form": form})


			return redirect(view_detached_variant, variant_hash)


		elif gene_search.match(search_query): # if we have searched for a gene

			try:

				gene = Gene.objects.get(name=search_query)

			except:

				return render(request,
							"VariantDatabase/search.html",
							{"error": True, "form": form})

			return redirect(view_gene, search_query)

		elif location_search.match(search_query): # if we have searched for a location


			return redirect(view_location_search, search_query)

		elif region_search.match(search_query): # if we have searched for a region

			search_query = search_query.replace(":", "-") #urls don"t like colons

			return redirect(view_region_search, search_query)

		elif sample_search.search(search_query): # if we have searched for a sample

			samples = Sample.objects.filter(name__contains=search_query)

			if len(samples) == 1: #If only one sample matches then go direct to that page

				return redirect(sample_summary, samples[0].pk)

			elif len(samples) ==0: #no samples match - query error

				return render(request,
							 "VariantDatabase/search.html",
							 {"error": True, "form": form})

			else: #>1 sample match - redirect to view_sample_search. Let user sort it out.

				return redirect(view_sample_search, search_query)


			return render(request, "VariantDatabase/search.html" , {"form": form})


		else:

			return render(request, "VariantDatabase/search.html" , {"error": True, "form": form})


	else:


		return render(request, "VariantDatabase/search.html" , {"form": form})


@has_permission_decorator('create_report')
@login_required
def create_sample_report(request, pk_sample, pk_report, check_number):
	"""
	A view for creating and checking sample reports.

	Sample Reports can be created from the Summary View.

	"""
	report = get_object_or_404(Report, pk=pk_report)

	sample = get_object_or_404(Sample, pk=pk_sample)

	filter_dict = report.default_filter.create_filter_dict()

	consequences_to_include = variant_utilities.create_conseqences_to_include(filter_dict)

	if report.panel.name == "None":

		panel = None

	else:

		panel = report.panel 

	variant_samples = VariantSample.objects.filter(sample=sample).select_related('variant')

	variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list("variant_id",flat=True))

	total_summary = variant_utilities.variant_query_set_summary(variants)

	variant_samples = variant_utilities.get_filtered_variants(variant_samples, consequences_to_include,filter_dict['freq_max_af'], panel)
													 
	variants = Variant.objects.filter(variant_hash__in= variant_samples.values_list("variant_id",flat=True))

	summary = variant_utilities.variant_query_set_summary(variants)

	user_settings = UserSetting.objects.filter(user=request.user)

	classifications = Classification.objects.filter(subsection=sample.worksheet.sub_section)

	return render(request,
				"VariantDatabase/create_sample_report.html",
				{"sample": sample,
				"variants": variant_samples,
				"summary": summary,
				"total_summary": total_summary,
				"user_settings": user_settings,
				"classifications": classifications,
				"report": report,
				"check_number": check_number })


@has_permission_decorator('resolve_differences')
@login_required
def resolve_check_differences(request, pk_sample, pk_report):
	"""
	A view for resolving any differences between the first and \
	second check.


	"""


	sample = get_object_or_404(Sample, pk=pk_sample)

	report = get_object_or_404(Report, pk=pk_report)

	user_settings = UserSetting.objects.filter(user=request.user)

	classifications = Classification.objects.filter(subsection=sample.worksheet.sub_section)

	#Get all the ReportVariantSampleClassifications associated with the report
	report_sample_variant_classifications = (ReportVariantSampleClassification
											.objects
											.filter(report=report))

	variant_classification_list =[]

	#Go through this list and and get the variant_sample objects associated with \
	#the filtered report_sample_variant_classifications.
	#This creates a list of tuples e.g. \
	#list = [(variant_sample, report_sample_variant_classification )]
	#List contains both items for display
	for variant_classification in report_sample_variant_classifications:

		variant_sample = get_object_or_404(VariantSample,
											variant=variant_classification.variant,
											sample=sample)

		variant_classification_list.append((variant_sample, variant_classification))


	matches =[]

	discrepencies =[]

	#Work out which match and which don't - put in different lists.
	for variant_classification in variant_classification_list:

		if variant_classification[1].classification_match() == True:

			matches.append(variant_classification)

		else:

			discrepencies.append(variant_classification)


	return render(request,
					"VariantDatabase/resolve_check_differences.html",
					{"matches": matches,
					"discrepencies": discrepencies,
					"sample": sample,
	  				"user_settings": user_settings,
	  				"classifications": classifications,
	  				"report": report, })



@login_required
def view_sample_report(request, pk_sample, pk_report):
	"""
	Allow the viewing of reports.

	"""

	sample = get_object_or_404(Sample, pk=pk_sample)
	report = get_object_or_404(Report, pk=pk_report)

	report_sample_variant_classifications = (ReportVariantSampleClassification
												.objects
												.filter(report=report))

	return render(request,
				"VariantDatabase/view_sample_report.html",
				{"report_sample_variant_classifications": report_sample_variant_classifications})


@login_required
def view_location_search(request,location):
	"""
	Displays the variant at a particular location.

	e.g. 4-5454646

	See search view for more information.

	Mainly for dealing with multi-allelic variants.

	"""

	location_list = location.split("-")

	chromosome = "chr"+location_list[0]

	position = location_list[1]

	variants = Variant.objects.filter(chromosome=chromosome, position = position)

	return render(request,
					"VariantDatabase/view_location_search.html",
					{"variants": variants, "location":location})

@login_required
def view_region_search(request,location):
	"""
	Displays the variants in a region.

	e.g. 4:5454650-5454750

	See search view for more information.

	"""

	location_list = location.split("-")

	chromosome = "chr"+location_list[0]

	start_pos = location_list[1]

	end_pos = location_list[2]

	variants = (Variant
				.objects
				.filter(chromosome=chromosome, position__gte = start_pos, position__lte=end_pos))

	return render(request,
					"VariantDatabase/view_location_search.html",
					{"variants": variants, "location":location})

@login_required
def view_sample_search(request,sample_query):
	"""
	In the event a sample search (See Search view) \
	returns more than one sample. This page allows the \
	user to discriminate between them.

	"""

	samples = Sample.objects.filter(name__contains=sample_query)

	return render(request,
				"VariantDatabase/view_sample_search.html",
				{"samples": samples,"sample_query": sample_query})

@login_required
def panel_list(request):
	"""
	A page for viewing the different gene panels.

	Contains a form for creating new panels.

	When creating a new panels user may select existing panel(s) \
	to be sued as a base for creating the new panel.

	"""

	panels = Panel.objects.all().exclude(name="None")


	#Contains the panels that a user has selected in the form
	requested_panels =  request.POST.getlist("inherit_select")


	if request.method == "POST":

		if has_permission(request.user, 'create_panel') == False:

			raise PermissionDenied

		form = CreatePanelForm(request.POST)

		if form.is_valid():

			new_panel = form.save(commit=False)

			new_panel.description = "None"

			new_panel.save()

			set_of_genes = set()

			#Go through each of the panels and add all the genes \
			#associated with it to a set (set_of_genes)
			for panel in requested_panels:

				panel = get_object_or_404(Panel, name = panel)

				genes = PanelGene.objects.filter(panel=panel)

				genes =[gene.gene for gene in genes]

				set_of_genes.update(genes)

			set_of_genes = list(set_of_genes)
			
			#create relevent panel_gene objects
			for gene in set_of_genes:

				new_panel_gene = PanelGene(gene=gene, panel=new_panel)

				new_panel_gene.save()


			return redirect(panel_edit_create, new_panel.pk)


	form = CreatePanelForm()

	return render(request,"VariantDatabase/panel_list.html", {"panels": panels, "form": form})
	


@has_permission_decorator('create_panel')
@login_required
def panel_edit_create(request, pk_panel):
	"""
	Allows the editing of gene panels.

	The form data is submitted to the ajax_update_panel view.

	"""

	panel = get_object_or_404(Panel, pk=pk_panel)

	panel_genes = PanelGene.objects.filter(panel=panel)

	already_in_genes = [panel_gene.gene for panel_gene in panel_genes]

	other_genes = list(set(Gene.objects.all()) - set(already_in_genes))

	return render(request,
				"VariantDatabase/panel_edit_create.html",
				{"panel_genes": panel_genes, "other_genes": other_genes, "panel": panel})

@login_required
def panel_view(request, pk_panel):
	"""
	View for viewing gene panels (No editing).

	"""

	panel = get_object_or_404(Panel, pk=pk_panel)

	panel_genes = PanelGene.objects.filter(panel=panel)

	return render(request,
				"VariantDatabase/panel_view.html",
				{"panel_genes": panel_genes, "panel": panel})

























