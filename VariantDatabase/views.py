from django.shortcuts import render, get_object_or_404
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required
import imp
from pysam import VariantFile
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


	sample = get_object_or_404(Sample, pk=pk_sample)

	vcf_file_path = sample.vcf_file

	data = pysam_extract.create_master_list(vcf_file_path, sample.name)

	genes = pysam_extract.get_genes_in_file(vcf_file_path, sample.name)

	return render(request, 'VariantDatabase/list_sample_variants.html', {'sample': sample, 'data': data, 'genes': genes})


def variant_detail(request):

	return render(request, 'VariantDatabase/variant_detail.html', {})



#finish this later
def search_page(request):


	query = request.GET.get('query')


	return render(request, 'VariantDatabase/search_results.html', {'query': query})






