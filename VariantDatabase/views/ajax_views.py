from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse, Http404, JsonResponse
from django.db import transaction
import re
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.base import ContentFile
import json
from rolepermissions.decorators import has_permission_decorator
from rolepermissions.checkers import has_permission

@login_required
def ajax_detail(request):
	"""
	Ajax View - create the top div of the summary page \
	e.g. detail, IGV, evidence when a user clicks the row.

	"""

	if request.is_ajax():

		variant_hash = request.GET.get("variant_hash")
		sample_pk = request.GET.get("sample_pk")

		variant_hash = variant_hash.strip()
		sample_pk = sample_pk.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))
		sample = Sample.objects.get(pk=sample_pk)

		variant_sample = VariantSample.objects.get(variant=variant, sample=sample)

		comments =Comment.objects.filter(variant_sample=variant_sample)

		samples = variant.get_samples_with_variant()

		frequency_data = variant.get_frequency_data()

		user = request.user

		html = render_to_string("VariantDatabase/ajax_detail.html",
								{"variant": variant,
								"sample": sample,
								"comments": comments,
								"samples": samples,
								'user': user,
								"frequency_data": frequency_data})

		return HttpResponse(html)

	else:

		raise Http404


@login_required
@has_permission_decorator('add_comment')
def ajax_comments(request):
	"""
	Ajax View - when the user clicks the upload comment/file button \
	this updates the comment section of the page. 

	Clipboard paste only works on HTML5 enabled browser.

	"""

	if request.is_ajax():

		variant_hash = request.POST.get("variant_hash")
		sample_pk = request.POST.get("sample_pk")
		comment_text = request.POST.get("comment_text")

		variant_hash = variant_hash.strip()
		sample_pk = sample_pk.strip()
		comment_text = comment_text.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))
		sample = Sample.objects.get(pk=sample_pk)
		variant_sample = VariantSample.objects.get(variant=variant, sample=sample)

		if len(comment_text) >1: #Check user has entered a comment

			new_comment = Comment(user=request.user,
								text=comment_text,
								time=timezone.now(),
								variant_sample=variant_sample)

			new_comment.save()
			#Deal with files selected using the file selector html widget 
			if request.FILES.get("file", False) != False:

				file = request.FILES.get("file")

				new_evidence = Evidence()

				new_evidence.file = file

				new_evidence.comment= new_comment

				new_evidence.save()

			#Deal with images pasted in from the clipboard
			if request.POST.get("image_data") !=None: 

				image_data = request.POST.get("image_data")
				#strip of any leading characters
				image_data = image_data.strip() 

				#add appropiate file header
				dataUrlPattern = re.compile("data:image/(png|jpeg);base64,(.*)$") 

				ImageData = dataUrlPattern.match(image_data).group(2)

				ImageData = base64.b64decode(ImageData) #to binary

				new_evidence = Evidence()

				new_evidence.comment= new_comment
				#save image
				img_file_string = "{}_{}_clip_image.png".format(sample.pk,new_comment.pk)
				new_evidence.file.save(img_file_string, ContentFile(ImageData)) 

				new_evidence.save()

		comments =Comment.objects.filter(variant_sample=variant_sample)

		html = render_to_string("VariantDatabase/ajax_comments.html",
								{"comments": comments, "variant": variant, "sample": sample})

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

		variant_hash = request.GET.get("variant_hash")

		variant_hash = variant_hash.strip()

		variant= Variant.objects.get(variant_hash=str(variant_hash))

		variant_transcripts = VariantTranscript.objects.filter(variant=variant)

		html = render_to_string("VariantDatabase/ajax_table_expand.html",
								{"variant_transcripts": variant_transcripts})

		return HttpResponse(html)


	else:

		raise Http404


@has_permission_decorator('complete_check')
@login_required
def ajax_receive_classification_data(request):
	"""
	An ajax submission point for the reporting feature.


	Can take data from 3 points in the report cycle:

		1) Report 1st Check
		2) Report Second Check
		3) Report Resolve differences

	Could maybe split this down or refactor?

	"""

	if request.is_ajax():

		sample_pk = request.POST.get("sample_pk")
		report_pk = request.POST.get("report_pk")
		check_number = request.POST.get("check_number")


		sample = get_object_or_404(Sample, pk=sample_pk.strip())
		report = get_object_or_404(Report, pk = report_pk.strip())

		#If it is the submission for the first check
		if report.status == "1" and check_number.strip() =="1" :

			classifications = request.POST.get("classifications")

			classifications = json.loads(classifications)


			with transaction.atomic(): 

				for key in classifications:

					variant_hash = key.strip()

					variant = get_object_or_404(Variant, variant_hash=variant_hash)

					data = classifications[key]

					classification = data[0].strip()

					user_hgvs = data[1].strip()

					classification = get_object_or_404(Classification,
														name =classification,
														subsection = report.sample.worksheet.sub_section)

					new_report_sample_variant_classification = ReportVariantSampleClassification(

						report = report, variant=variant,classification1=classification,
						user1=request.user, date1 = timezone.now(), user_hgvs1 =user_hgvs

						)


					new_report_sample_variant_classification.save()


				report.status ="2"
				report.save()

				return HttpResponse("Done")

		#If we have the data for the second check.
		elif report.status == "2" and check_number.strip() =="2" :

			classifications = request.POST.get("classifications")

			classifications = json.loads(classifications)

			with transaction.atomic(): 

				for key in classifications:

					variant_hash = key.strip()

					variant = get_object_or_404(Variant, variant_hash=variant_hash)

					data = classifications[key]

					classification = data[0].strip()

					user_hgvs = data[1].strip()

					classification = get_object_or_404(Classification,
									name =classification,
									subsection = report.sample.worksheet.sub_section)

					report_sample_variant_classification = (ReportVariantSampleClassification
															.objects
															.filter(report=report, variant=variant))


					if len(report_sample_variant_classification) ==1:

						report_sample_variant_classification =report_sample_variant_classification[0]

						report_sample_variant_classification.classification2 = classification
						report_sample_variant_classification.user2 = request.user
						report_sample_variant_classification.date2 = timezone.now()
						report_sample_variant_classification.user_hgvs2 = user_hgvs

						report_sample_variant_classification.save()

					else:
						error_msg = "An error occured: Either >1 or no" \
									"existing report_sample_variant_classification"

						return HttpResponse(error_msg)


				#If there are no mismatches then update the final classification field and \
				#set report as finished.
				if report.number_of_mismatches() == 0:

					report_sample_variant_classifications = (ReportVariantSampleClassification
															.objects
															.filter(report=report))

					for variant_classification in report_sample_variant_classifications:

						variant_classification.final_classification = variant_classification.classification2
						variant_classification.final_user = request.user
						variant_classification.final_date = timezone.now()
						variant_classification.final_hgvs = variant_classification.user_hgvs2

						variant_classification.save()

					report.status ="4"

				else:
					
					report.status ="3"

				report.save()


				return HttpResponse("Done")

		#If we have recieved the resolve differences data
		elif report.status == "3" and check_number.strip() =="3" :


			if has_permission(user, 'resolve_differences') == False:

				raise PermissionDenied

			classifications = request.POST.get("classifications")

			classifications = json.loads(classifications)

			with transaction.atomic(): 

				for key in classifications:

					variant_hash = key.strip()

					variant = get_object_or_404(Variant, variant_hash=variant_hash)

					data = classifications[key]

					classification = data[0].strip()

					user_hgvs = data[1].strip()

					classification = get_object_or_404(Classification,
									name =classification,
									subsection = report.sample.worksheet.sub_section)

					report_sample_variant_classification = (ReportVariantSampleClassification
															.objects
															.filter(report=report, variant=variant))


					if len(report_sample_variant_classification) ==1:

						report_sample_variant_classification =report_sample_variant_classification[0]

						report_sample_variant_classification.final_classification = classification
						report_sample_variant_classification.final_user = request.user
						report_sample_variant_classification.final_date = timezone.now()
						report_sample_variant_classification.final_hgvs = user_hgvs

						report_sample_variant_classification.save()

					else:

						error_msg = "An error occured:" \
									" Either >1 or no existing report_sample_variant_classification"

						return HttpResponse(error_msg)



				report_sample_variant_classifications = (ReportVariantSampleClassification
														.objects
														.filter(report=report))

				for variant_classification in report_sample_variant_classifications:

					if variant_classification.final_classification == None:

						variant_classification.final_classification = variant_classification.classification2
						variant_classification.final_user = request.user
						variant_classification.final_date = timezone.now()
						variant_classification.final_hgvs = variant_classification.user_hgvs2

						variant_classification.save()


				report.status ="4"
				report.save()

				return HttpResponse("Done")

		else:

			return HttpResponse("Already done the check")


	return HttpResponse("ajax error")

@has_permission_decorator('create_panel')
@login_required
def ajax_update_panel(request):
	"""
	An Ajax submission point for gene panel data. 

	"""

	if request.is_ajax():

		list_of_genes = request.POST.get("genes_to_include")
		list_of_genes = json.loads(list_of_genes)
		panel = request.POST.get("panel_name")
		comment = request.POST.get("comment_box")

		panel = get_object_or_404(Panel, name=panel)

		panel.description = comment
		panel.save()


		panel_genes = PanelGene.objects.filter(panel= panel)

		#Remove existing data - easiest way to add more.
		panel_genes.delete()

		for gene in list_of_genes:

			gene = get_object_or_404(Gene,name=gene)

			new_panel_gene = PanelGene(panel= panel, gene=gene)

			new_panel_gene.save()

		return HttpResponse("Panel has been updated!")