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
def list_projects(request):

	all_projects = Project.objects.all()

	return render(request, 'VariantDatabase/list_projects.html', {'all_projects': all_projects} )

@login_required
def list_batches(request, pk):

	project = get_object_or_404(Project, pk=pk)

	batches_for_project = Batch.objects.filter(project=project)

	return render(request,'VariantDatabase/list_batches.html', {'batches_for_project': batches_for_project, 'project': project})


@login_required
def list_batch_samples(request, pk_project, pk_batch):

	batch = get_object_or_404(Batch, pk=pk_batch)

	samples_in_batch = Sample.objects.filter(batch = batch)

	return render(request, 'VariantDatabase/list_batch_samples.html', {'batch': batch, 'samples_in_batch' : samples_in_batch,})

@login_required
def list_sample_variants(request, pk_project, pk_batch, pk_sample):

	batch = get_object_or_404(Batch, pk=pk_batch)

	sample = get_object_or_404(Sample, pk=pk_sample)

	vcf_file_path = batch.vcf_file

	data = pysam_extract.create_master_list(vcf_file_path, sample.sample_name)

	genes = pysam_extract.get_genes_in_file(vcf_file_path, sample.sample_name)

	return render(request, 'VariantDatabase/list_sample_variants.html', {'sample': sample, 'vcf_file_path': vcf_file_path, 'data': data, 'genes': genes})


def variant_detail(request):

	return render(request, 'VariantDatabase/variant_detail.html', {})



#finish this later
def search_page(request):


	query = request.GET.get('query')


	return render(request, 'VariantDatabase/search_results.html', {'query': query})






